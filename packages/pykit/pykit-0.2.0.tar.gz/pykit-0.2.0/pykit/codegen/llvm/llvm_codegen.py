# -*- coding: utf-8 -*-

"""
LLVM code generation.
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from pykit import error, types
from pykit import ir
from pykit.ir import vvisit, ArgLoader, verify_lowlevel
from pykit.ir import defs, opgrouper
from pykit.types import Boolean, Integral, Real, Pointer, Function, Int64, Struct
from pykit.codegen.llvm.llvm_types import llvm_type
from pykit.utils import make_temper

import llvm.core as lc
from llvm.core import Type, Constant

#===------------------------------------------------------------------===
# Definitions
#===------------------------------------------------------------------===

compare_float = {
    '>':  lc.FCMP_OGT,
    '<':  lc.FCMP_OLT,
    '==': lc.FCMP_OEQ,
    '>=': lc.FCMP_OGE,
    '<=': lc.FCMP_OLE,
    '!=': lc.FCMP_ONE,
}

compare_signed_int = {
    '>':  lc.ICMP_SGT,
    '<':  lc.ICMP_SLT,
    '==': lc.ICMP_EQ,
    '>=': lc.ICMP_SGE,
    '<=': lc.ICMP_SLE,
    '!=': lc.ICMP_NE,
}

compare_unsiged_int = {
    '>':  lc.ICMP_UGT,
    '<':  lc.ICMP_ULT,
    '==': lc.ICMP_EQ,
    '>=': lc.ICMP_UGE,
    '<=': lc.ICMP_ULE,
    '!=': lc.ICMP_NE,
}

compare_bool = {
    '==' : lc.ICMP_EQ,
    '!=' : lc.ICMP_NE
}

# below based on from npm/codegen

def integer_invert(builder, val, valtype):
    return builder.not_(val)

def integer_usub(builder, val, valtype):
    return builder.sub(make_constant(0, valtype), val)

def integer_not(builder, value, valtype):
    return builder.icmp(lc.ICMP_EQ, value, make_constant(0, valtype))

def float_usub(builder, val, valtype):
    return builder.fsub(make_constant(0, valtype), val)

def float_not(builder, val, valtype):
    return builder.fcmp(lc.FCMP_OEQ, val, make_constant(0, valtype))


# operators

binop_int  = {
     '+': (lc.Builder.add, lc.Builder.add),
     '-': (lc.Builder.sub, lc.Builder.sub),
     '*': (lc.Builder.mul, lc.Builder.mul),
     '/': (lc.Builder.sdiv, lc.Builder.udiv),
     '//': (lc.Builder.sdiv, lc.Builder.udiv),
     '%': (lc.Builder.srem, lc.Builder.urem),
     '&': (lc.Builder.and_, lc.Builder.and_),
     '|': (lc.Builder.or_, lc.Builder.or_),
     '^': (lc.Builder.xor, lc.Builder.xor),
     '<<': (lc.Builder.shl, lc.Builder.shl),
     '>>': (lc.Builder.ashr, lc.Builder.lshr),
}

binop_float = {
     '+': lc.Builder.fadd,
     '-': lc.Builder.fsub,
     '*': lc.Builder.fmul,
     '/': lc.Builder.fdiv,
     '//': lc.Builder.fdiv,
     '%': lc.Builder.frem,
}

unary_bool = {
    '!': integer_not,
}

unary_int = {
    '~': integer_invert,
    '!': integer_not,
    "+": lambda builder, arg, valtype: arg,
    "-": integer_usub,
}

unary_float = {
    '!': float_not,
    "+": lambda builder, arg, valtype: arg,
    "-": float_usub,
}

#===------------------------------------------------------------------===
# Utils
#===------------------------------------------------------------------===

i1, i16, i32, i64 = map(Type.int, [1, 16, 32, 64])

def const_int(type, value):
    return Constant.int(type, value)

const_i32 = partial(const_int, i32)
const_i64 = partial(const_int, i64)
zero = partial(const_int, value=0)
one = partial(const_int, value=1)

def sizeof(builder, ty, intp):
    ptr = Type.pointer(ty)
    null = Constant.null(ptr)
    offset = builder.gep(null, [Constant.int(Type.int(), 1)])
    return builder.ptrtoint(offset, intp)

def gep(builder, struct_type, p, attr):
    index = struct_type.names.index(attr)
    return builder.gep(p, [const_i32(0), const_i32(index)])
 
#===------------------------------------------------------------------===
# Translator
#===------------------------------------------------------------------===

class Translator(object):
    """
    Translate a function in low-level form.
    This means it can only use values of type Bool, Int, Float, Struct or
    Pointer. Values of type Function may be called.
    """

    def __init__(self, func, env, lfunc, llvm_typer, llvm_module):
        self.func = func
        self.env = env
        self.lfunc = lfunc
        self.llvm_type = llvm_typer
        self.lmod = llvm_module
        self.builder = None
        self.phis = [] # [pykit_phi]

    def blockswitch(self, newblock):
        if not self.builder:
            self.builder = lc.Builder.new(newblock)
        self.builder.position_at_end(newblock)

    # __________________________________________________________________

    def op_arg(self, arg):
        return self.lfunc.args[self.func.args.index(arg)]

    # __________________________________________________________________

    def op_unary(self, op, arg):
        t = op.type.base if op.type.is_vector else op.type
        opmap = { Boolean: unary_bool,
                  Integral: unary_int,
                  Real: unary_float }[type(t)]
        unop = defs.unary_opcodes[op.opcode]
        return opmap[unop](self.builder, arg, op.type)

    def op_binary(self, op, left, right):
        t = op.type.base if op.type.is_vector else op.type
        binop = defs.binary_opcodes[op.opcode]
        if t.is_int:
            genop = binop_int[binop][t.unsigned]
        else:
            genop = binop_float[binop]
        return genop(self.builder, left, right, op.result)

    def op_compare(self, op, left, right):
        cmpop = defs.compare_opcodes[op.opcode]
        type = op.args[0].type
        type = type.base if type.is_vector else type
        if type.is_int and type.unsigned:
            cmp, lop = self.builder.icmp, compare_unsiged_int[cmpop]
        elif type.is_int or type.is_bool:
            cmp, lop = self.builder.icmp, compare_signed_int[cmpop]
        else:
            cmp, lop = self.builder.fcmp, compare_float[cmpop]

        return cmp(lop, left, right, op.result)

    # __________________________________________________________________

    def op_packvector(self, op, arr):
        return self.op_bitcast(op, arr)

    def op_unpackvector(self, op, vec):
        return self.op_bitcast(op, vec)

    # __________________________________________________________________

    def op_convert(self, op, arg):
        if op.args[0].type == op.type:
            return arg
        t = op.type.base if op.type.is_vector else op.type
        from llpython.byte_translator import LLVMCaster
        unsigned = t.is_int and t.unsigned
        # The float cast doesn't accept this keyword argument
        kwds = {'unsigned': unsigned} if unsigned else {}
        return LLVMCaster.build_cast(self.builder, arg,
                                     self.llvm_type(t), **kwds)

    def op_bitcast(self, op, val):
        if op.args[0].type == op.type:
            return val
        return self.builder.bitcast(val, self.llvm_type(op.type))

    # __________________________________________________________________

    def op_call(self, op, function, args):
        # Get the callee LLVM function from the cache. This is put there by
        # pykit.codegen.codegen
        if isinstance(function, ir.Function):
            cache = self.env["codegen.cache"]
            lfunc = cache[function]

            # Declare the function if it is not from this module
            if lfunc.module is not self.lmod:
                lfunc = self.lmod.get_or_insert_function(lfunc.type.pointee,
                                                         lfunc.name)

            for func_arg, arg, param in zip(function.args, args, lfunc.args):
                if arg.type != param.type:
                    import pdb; pdb.set_trace()
                    raise TypeError(
                        "Function %s called with type %s, "
                        "expected %s for argument %r" % (function.name,
                                                         arg.type,
                                                         param.type,
                                                         func_arg.result))
        else:
            lfunc = function # function pointer

        call = self.builder.call(lfunc, args)
        return call

    def op_call_math(self, op, name, args):
        # Math is resolved by an LLVM postpass
        argtypes = [arg.type for arg in op.args[1]]
        lfunc_type = self.llvm_type(Function(op.type, argtypes, False))
        lfunc = self.lmod.get_or_insert_function(
            lfunc_type, 'pykit.math.%s.%s' % (map(str, argtypes), name.lower()))
        return self.builder.call(lfunc, args, op.result)

    # __________________________________________________________________

    def op_get(self, op, target, idx):
        # convert constants
        idx = [i.s_ext_value for i in idx]
        target_type = op.args[0].type

        # handle depending on target type
        if target_type.is_pointer:
            p = self.builder.gep(p, [0] + idx)
            r = self.builder.load(p, name=op.result)
        elif target_type.is_array or target_type.is_struct:
            r = self.builder.extract_value(target, idx, name=op.result)
        elif target_type.is_vector:
            assert len(idx) == 1
            r = self.builder.extract_element(target, idx[0], name=op.result)
        else:
            raise TypeError()
        return r

    def op_set(self, op, target, value, idx):
        # convert constants
        idx = [i.s_ext_value for i in idx]
        target_type = op.args[0].type

        # handle depending on target type
        if target_type.is_pointer:
            p = self.builder.gep(p, [0] + idx)
            self.builder.store(p, name=op.result)
            r = None
        elif target_type.is_array or target_type.is_struct:
            r = self.builder.insert_value(target, value, idx, name=op.result)
        elif target_type.is_vector:
            assert len(idx) == 1
            r = self.builder.insert_element(target, value, idx[0], name=op.result)
        else:
            raise TypeError()
        return r

    # __________________________________________________________________

    def op_getfield(self, op, p, attr):
        struct_type = op.args[0].type.base
        result = gep(self.builder, struct_type, p, attr)
        lty = llvm_type(op.type)
        if result.type == lty:
            return result
        return self.builder.load(result)

    def op_setfield(self, op, p, attr, value):
        struct_type = op.args[0].type.base
        p = gep(self.builder, struct_type, p, attr)
        lty = value.type
        if not (lc.Type.pointer(lty) == p.type):
            value = self.builder.load(value)
        self.builder.store(value, p)

    # __________________________________________________________________

    def op_extractfield(self, op, struct, attr):
        struct_type = op.args[0].type
        index = struct_type.names.index(attr)
        return self.builder.extract_value(struct, index, op.result)

    def op_insertfield(self, op, struct, attr, value):
        struct_type = op.args[0].type
        index = struct_type.names.index(attr)
        return self.builder.insert_value(struct, value, index, op.result)

    # __________________________________________________________________

    def op_extractvalue(self, op, val, indices):
        assert isinstance(indices, list)
        return self.builder.extract_value(val, [i.s_ext_value for i in indices], op.result)

    def op_insertvalue(self, op, val, elt, indices):
        assert isinstance(indices, list)
        return self.builder.insert_value(val, elt, [i.s_ext_value for i in indices], op.result)

    def op_gep(self, op, ptr, indices):
        assert isinstance(indices, list)
        return self.builder.gep(ptr, indices)

    # __________________________________________________________________

    def op_shufflevector(self, op, a, b, mask, idx):
        return self.builder.shuffle_vector(val, a, b, mask, op.result)

    # __________________________________________________________________

    def op_getindex(self, op, array, indices):
        return self.builder.gep(array, indices, op.result)

    def op_setindex(self, op, array, indices, value):
        ptr = self.builder.gep(array, indices)
        self.builder.store(ptr, value)

    # __________________________________________________________________

    def op_alloca(self, op, numItems):
        if numItems is not None:
            return self.builder.alloca_array(self.llvm_type(ty), numItems, name=op.result)
        return self.builder.alloca(self.llvm_type(op.type.base), name=op.result)

    def op_load(self, op, stackvar):
        return self.builder.load(stackvar, op.result)

    def op_store(self, op, value, stackvar):
        self.builder.store(value, stackvar)

    # __________________________________________________________________

    def op_jump(self, op, block):
        self.builder.branch(block)

    def op_cbranch(self, op, test, true_block, false_block):
        self.builder.cbranch(test, true_block, false_block)

    def op_phi(self, op):
        phi = self.builder.phi(self.llvm_type(op.type), op.result)
        self.phis.append(op)
        return phi

    def op_ret(self, op, value):
        if value is None:
            assert self.func.type.restype.is_void
            self.builder.ret_void()
        else:
            self.builder.ret(value)

    # __________________________________________________________________

    def op_sizeof(self, op, expr):
        int_type = self.llvm_type(op.type)
        return sizeof(self.builder, expr.type, int_type)

    def op_addressof(self, op, func):
        assert func.address
        addr = const_int(i64, func.address)
        return self.builder.inttoptr(
            addr, self.llvm_type(types.Pointer(types.Void)))

    # __________________________________________________________________

    def op_ptradd(self, op, ptr, val):
        return self.builder.gep(ptr, [val], op.result)

    def op_ptrload(self, op, ptr):
        return self.builder.load(ptr, op.result)

    def op_ptrstore(self, op, val, ptr):
        return self.builder.store(val, ptr)

    def op_ptrcast(self, op, val):
        ltype = self.llvm_type(op.type)
        if op.type.is_int:
            return self.builder.ptrtoint(val, ltype)
        else:
            return self.builder.bitcast(val, ltype, op.result)

    def op_ptr_isnull(self, op, val):
        intval = self.builder.ptrtoint(val, self.llvm_type(Int64))
        return self.builder.icmp(lc.ICMP_EQ, intval, zero(intval.type), op.result)

    # __________________________________________________________________

    def op_exc_setup(self, op, *args):
        raise error.CompileError("exc_setup should have been replaced")

    def op_exc_throw(self, op, *args):
        raise error.CompileError("exc_throw should have been replaced")

    def op_exc_catch(self, op, *args):
        raise error.CompileError("exc_catch should have been replaced")


def allocate_blocks(llvm_func, pykit_func):
    """Return a dict mapping pykit blocks to llvm blocks"""
    blocks = {}
    for block in pykit_func.blocks:
        blocks[block] = llvm_func.append_basic_block(pykit_func.name)

    return blocks

def update_phis(phis, valuemap, argloader):
    """
    Update LLVM phi values given a list of pykit phi values and block and
    value dicts mapping pykit values to LLVM values
    """
    for phi in phis:
        llvm_phi = valuemap[phi.result]
        llvm_blocks = map(argloader.load_op, phi.args[0])
        llvm_values = map(argloader.load_op, phi.args[1])
        for llvm_block, llvm_value in zip(llvm_blocks, llvm_values):
            llvm_phi.add_incoming(llvm_value, llvm_block)


#===------------------------------------------------------------------===
# Argument loading
#===------------------------------------------------------------------===

class LLVMArgLoader(ArgLoader):
    """
    Load Operation arguments as LLVM values passed and extra *args to the
    Translator.
    """

    def __init__(self, store, engine, llvm_module, lfunc, blockmap):
        super(LLVMArgLoader, self).__init__(store)
        self.engine = engine
        self.llvm_module = llvm_module
        self.lfunc = lfunc
        self.blockmap = blockmap

    def load_GlobalValue(self, arg):
        if arg.external:
            fnty = llvm_type(arg.type)
            value = self.llvm_module.get_or_insert_function(fnty,
                                                            name=arg.name)
            if arg.address:
                self.engine.add_global_mapping(value, arg.address)
        else:
            assert arg.value
            value = arg.value.const

        return value

    def load_Block(self, arg):
        return self.blockmap[arg]

    def load_Constant(self, arg):
        return make_constant(arg.const, arg.type)

    def load_Pointer(self, arg):
        return const_i64(arg.addr).inttoptr(llvm_type(arg.type))

    def load_Struct(self, arg):
        return make_constant(arg, arg.type)

    def load_Undef(self, arg):
        return lc.Constant.undef(llvm_type(arg.type))


def unwrap(c):
    if isinstance(c, ir.Const):
        return c.const
    return c

def make_constant(value, ty):
    lty = llvm_type(ty)

    if type(ty) == Pointer:
        value = value.addr
        if value == 0:
            return lc.Constant.null(lty)
        elif isinstance(value, (int, long)):
            return const_i64(value).inttoptr(lty)
        else:
            raise ValueError(
                "Cannot create constant pointer to value '%s'" % (value,))
    elif type(ty) == Integral:
        if ty.unsigned:
            return lc.Constant.int(lty, value)
        else:
            return lc.Constant.int_signextend(lty, value)
    elif type(ty) == Real:
        return lc.Constant.real(lty, value)
    elif type(ty) == Boolean:
        return lc.Constant.int(lty, value)
    elif type(ty) == Struct:
        return lc.Constant.struct([make_constant(unwrap(c), c.type)
                                       for c in value.values])
    elif ty.is_vector:
        const = make_constant(value, ty.base)
        return lc.Constant.vector([const] * ty.count)
    else:
        raise NotImplementedError("Constants for", type(ty))

#===------------------------------------------------------------------===
# Entry points
#===------------------------------------------------------------------===

mangle = make_temper()

def initialize(func, env):
    verify_lowlevel(func)
    llvm_module = env["codegen.llvm.module"]
    return llvm_module.add_function(llvm_type(func.type), mangle(func.name))

def translate(func, env, lfunc):
    engine, llvm_module = env["codegen.llvm.engine"], env["codegen.llvm.module"]
    blockmap = allocate_blocks(lfunc, func)

    ### Create visitor ###
    translator = Translator(func, env, lfunc, llvm_type, llvm_module)
    visitor = opgrouper(translator)

    ### Codegen ###
    argloader = LLVMArgLoader(None, engine, llvm_module, lfunc, blockmap)
    valuemap = vvisit(visitor, func, argloader)
    update_phis(translator.phis, valuemap, argloader)

    return lfunc