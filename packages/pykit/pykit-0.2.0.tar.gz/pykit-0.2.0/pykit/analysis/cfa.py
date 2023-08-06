# -*- coding: utf-8 -*-

"""
Contruct a control flow graph and compute the SSA graph, reflected through
phi Operations in the IR.
"""

from __future__ import print_function, division, absolute_import
import collections

from pykit.ir import ops, Builder, Undef, Op, blocks
from pykit.transform import dce
from pykit.utils import mergedicts

import networkx as nx

#===------------------------------------------------------------------===
# Data Flow
#===------------------------------------------------------------------===

def run(func, env=None):
    CFG = cfg(func)
    ssa(func, CFG)

def ssa(func, cfg):
    """Remove all alloca/load/store where possible and insert phi values"""
    # transpose_cfg = cfg.reverse() # reverse edges
    allocas = find_allocas(func)
    move_allocas(func, allocas)
    phis = insert_phis(func, cfg, allocas)
    compute_dataflow(func, cfg, allocas, phis)
    prune_phis(func, phis)
    simplify(func, cfg)
    return phis

def cfg(func, view=False, exceptions=True):
    """
    Compute the control flow graph for `func`
    """
    cfg = nx.DiGraph()

    for block in func.blocks:
        # -------------------------------------------------
        # Deduce CFG edges from block terminator

        targets = deduce_successors(block)

        # -------------------------------------------------
        # Deduce CFG edges from exc_setup

        for op in block.leaders:
            if op.opcode == 'exc_setup' and exceptions:
                [exc_handlers] = op.args
                targets.extend(exc_handlers)

        # -------------------------------------------------
        # Add node and edges to CFG

        cfg.add_node(block)
        for target in targets:
            cfg.add_edge(block, target)

    if view:
        import matplotlib.pyplot as plt
        nx.draw(cfg)
        plt.draw()

    return cfg

def deduce_successors(block):
    """Deduce the successors of a basic block"""
    op = block.terminator
    if op.opcode == 'jump':
        successors = [op.args[0]]
    elif op.opcode == 'cbranch':
        cond, ifbb, elbb = op.args
        successors = [ifbb, elbb]
    else:
        assert op.opcode in (ops.ret, ops.exc_throw)
        successors = []

    return successors

def find_allocas(func):
    """
    Find allocas that can be promoted to registers. We do this only if the
    alloca is used only in load and store operations.
    """
    allocas = set()
    for op in func.ops:
        if (op.opcode == 'alloca' and
                all(u.opcode in ('load', 'store') for u in func.uses[op])):
            allocas.add(op)

    return allocas

def move_allocas(func, allocas):
    """Move all allocas to the start block"""
    builder = Builder(func)
    builder.position_at_beginning(func.startblock)
    for alloca in allocas:
        if alloca.block != func.startblock:
            alloca.unlink()
            builder.emit(alloca)

def insert_phis(func, cfg, allocas):
    """Insert φs in the function given the set of promotable stack variables"""
    builder = Builder(func)
    phis = {} # phi -> alloca
    for block in func.blocks:
        if len(cfg.predecessors(block)) > 1:
            with builder.at_front(block):
                for alloca in allocas:
                    phi = builder.phi(alloca.type.base, [], [])
                    phis[phi] = alloca

    return phis

def compute_dataflow(func, cfg, allocas, phis):
    """
    Compute the data flow by eliminating load and store ops (given allocas set)

    :param allocas: set of alloca variables to optimize ({Op})
    :param phis:    { φ Op -> alloca }
    """
    values = collections.defaultdict(dict) # {block : { stackvar : value }}

    # Track block values and delete load/store
    for block in func.blocks:
        # Copy predecessor outgoing values into current block values
        preds = cfg.predecessors(block)
        predvars = [values[pred] for pred in preds]
        blockvars = mergedicts(*predvars)

        for op in block.ops:
            if op.opcode == 'alloca' and op in allocas:
                # Initialize to Undefined
                blockvars[op] = Undef(op.type.base)
            elif op.opcode == 'load' and op.args[0] in allocas:
                # Replace load with value
                alloca, = op.args
                op.replace_uses(blockvars[alloca])
                op.delete()
            elif op.opcode == 'store' and op.args[1] in allocas:
                # Delete store and register result
                value, alloca = op.args
                blockvars[alloca] = value
                op.delete()
            elif op.opcode == 'phi' and op in phis:
                alloca = phis[op]
                blockvars[alloca] = op

        values[block] = blockvars

    # Update phis incoming values
    for phi in phis:
        preds = list(cfg.predecessors(phi.block))
        incoming = []
        for block in preds:
            alloca = phis[phi]
            value = values[block][alloca] # value leaving predecessor block
            incoming.append(value)

        phi.set_args([preds, incoming])

    # Remove allocas
    for alloca in allocas:
        alloca.delete()

def prune_phis(func, phis):
    """Delete unnecessary phis (all incoming values equivalent)"""
    # TODO: Exploit sparsity
    changed = True
    while changed:
        changed = _prune_phis(func, phis)

    prune_undef(func, phis)

def _prune_phis(func, phis):
    changed = []

    def delete(op):
        op.delete()
        changed.append(op)
        if op in phis:
            # Pruning newly introduced phi, delete from phi map
            del phis[op]

    for op in func.ops:
        if op.opcode == 'phi':
            blocks, args = op.args
            if not func.uses[op]:
                delete(op)
            elif len(set(args)) == 1:
                [arg] = set(args)
                op.replace_uses(arg)
                delete(op)
            elif len(args) == 2 and op in args:
                [arg] = set(args) - set([op])
                op.replace_uses(arg)
                delete(op)

    return bool(changed)

def candidate(v):
    return isinstance(v, Undef) or (isinstance(v, Op) and v.opcode == 'phi')

def prune_undef(func, phis):
    """
    Prune cycles of dead phis which only have Undef inputs.
    """
    candidates = set()  # { phi }

    for phi in phis:
        blocks, values = phi.args
        if all(candidate(val) for val in values):
            candidates.add(phi)

    n = 0
    while n != len(candidates):
        n = len(candidates)
        for phi in list(candidates):
            blocks, values = phi.args
            for v in values:
                if isinstance(v, Op):
                    assert v.opcode == 'phi'
                    if v not in candidates:
                        candidates.remove(phi)
                        break

    for phi in candidates:
        phi.set_args([])
    for phi in candidates:
        phi.delete()

# ______________________________________________________________________

def compute_dominators(func, cfg):
    """
    Compute the dominators for the CFG, i.e. for each basic block the
    set of basic blocks that dominate that block. This means that every path
    from the entry block to that block must go through the blocks in the
    dominator set.

        dominators(root) = {root}
        dominators(x) = {x} ∪ (∩ dominators(y) for y ∈ preds(x))
    """
    dominators = collections.defaultdict(set) # { block : {dominators} }

    # Initialize
    dominators[func.startblock] = set([func.startblock])
    for block in func.blocks:
        dominators[block] = set(func.blocks)

    blocks = list(cfg)
    preds = dict((block, cfg.predecessors(block)) for block in blocks)

    # Solve equation
    changed = True
    while changed:
        changed = False
        for block in blocks:
            pred_doms = [dominators[pred] for pred in preds[block]]
            new_doms = set([block]) | set.intersection(*pred_doms or [set()])
            if new_doms != dominators[block]:
                dominators[block] = new_doms
                changed = True

    return dominators

#===------------------------------------------------------------------===
# Control Flow Simplification
#===------------------------------------------------------------------===

unmergable = ('exc_setup', 'exc_catch')

def merge_blocks(func, pred, succ):
    """Merge two consecutive blocks (T2 transformation)"""
    assert pred.terminator.opcode == 'jump', pred.terminator.opcode
    assert pred.terminator.args[0] == succ
    pred.terminator.delete()
    pred.extend(succ)
    func.del_block(succ)

def simplify(func, cfg):
    """
    Simplify control flow. Merge consecutive blocks where the parent has one
    child, the child one parent, and both have compatible instruction leaders.
    """
    for block in reversed(list(func.blocks)):
        if (len(cfg.predecessors(block)) == 1 and not
                any(l.opcode in unmergable for l in block.leaders)):
            [pred] = cfg.predecessors(block)
            successors = cfg.neighbors(block)
            exc_block = any(op.opcode in ('exc_setup',) for op in pred.leaders)
            if not exc_block and len(cfg[pred]) == 1:
                blocks.patch_phis(block, pred, successors)
                del_phis(block)
                merge_blocks(func, pred, block)
                cfg.remove_edge(pred, block)
                for succ in successors:
                    cfg.remove_edge(block, succ)
                    cfg.add_edge(pred, succ)


def del_phis(block):
    """
    Delete leading phis during block merge, where we merge with our only
    predecessor.
    """
    for op in block.leaders:
        if op.opcode == 'phi':
            [val] = op.args[1]
            op.replace_uses(val)
            op.delete()


#===------------------------------------------------------------------===
# Block Removal
#===------------------------------------------------------------------===

def find_dead_blocks(func, cfg):
    """Find all immediate dead blocks"""
    return [block for block in cfg if not cfg.predecessors(block)
                      if block != func.startblock]

def delete_blocks(func, cfg, deadblocks):
    """
    Remove unreachable code blocks listed by `deadblocks`.
    """
    for block in deadblocks:
        func.del_block(block)
        for succ in cfg.successors(block):
            # Remove CFG edge from dead block to successor
            cfg.remove_edge(block, succ)

            # Delete associated phis from successor blocks
            for leader in succ.leaders:
                if leader.opcode == 'phi':
                    blocks, values = map(list, leader.args)
                    while block in blocks:
                        idx = blocks.index(block)
                        blocks.remove(block)
                        values.pop(idx)
                    leader.set_args([blocks, values])

    dce.dce(func)
    simplify(func, cfg)