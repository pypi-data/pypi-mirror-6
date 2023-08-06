from __future__ import division, print_function, unicode_literals

import types
import dis
import os
import struct
import sys


def _unpack(s):
    if len(s) == 2:
        return struct.unpack(b'<H', s)[0]
    else:
        return struct.unpack(b'<B', s)[0]


def readop(buf, i):
    """read an opcode. return (name, argument, length in bytes)"""
    op = _unpack(buf[i])
    if op < dis.HAVE_ARGUMENT:
        return (dis.opname[op], None, 1)
    if op == dis.EXTENDED_ARG:
        arg = _unpack(buf[i+1:i+3]) * (2**16) + _unpack(buf[i+4:i+6])
        op = _unpack(buf[i+3])
        return (dis.opname[op], arg, 6)
    return (dis.opname[op], _unpack(buf[i+1:i+3]), 3)


def makeop(op, arg=None, len_=None):
    """build an opcode. if len_ is specified, pad with NOP until it's
    long enough, or error if it's longer"""
    if not isinstance(op, (int, long)):
        op = dis.opmap[op]
    if op < dis.HAVE_ARGUMENT:
        assert arg is None
        s = struct.pack(b'<B', op)
    else:
        assert arg is not None
        if arg >= 2**16:
            s = struct.pack(b'<BHBH', dis.EXTENDED_ARG, arg >> 16, op, arg & 0xFFFF)
        else:
            s = struct.pack(b'<BH', op, arg)
    if len_ is not None:
        assert len(s) <= len_
        while len(s) < len_:
            s += dis.opmap['NOP']
    return s


def _get_plain():
    def plain():
        pass
    return plain


def get_function_in_context(g):
    """make a function with no local variables or closures with a given __globals__"""
    return eval(_get_plain.__code__, g, {})


def execute(frame, *rv):
    """jump back into a frame, and execute it until it next returns.

    if anything is passed for 'rv', it should be a single object, which we will pretend
    was just returned from a function. for this to work, the frame's instruction pointer
    must be pointing at a CALL_FUNCTION or similar opcode.

    won't work on generators."""
    # we need a frame because it contains the lasti
    co = frame.f_code
    lo = frame.f_locals
    consts = co.co_consts
    # if we're to fake a return from a function call, we NOP out the function call as well
    # it's always the instruction at the instruction pointer; we can read this one and
    # make sure it's a function call operation.
    # we then add an extra constant (which might not really be constant) to the code object,
    # and add an instruction to load that constant (so it takes the place in the stack of
    # the return value).
    if rv:
        # insert a new constant and load it
        consts = consts + (rv[0],)

        # read the function call op, just to make sure it doesn't have >65535 arguments...
        op = readop(co.co_code, frame.f_lasti)
        assert op[0] in ('CALL_FUNCTION', 'CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW', 'CALL_FUNCTION_VAR_KW')

        initial = makeop('LOAD_CONST', len(consts) - 1)
        lasti = frame.f_lasti + op[2]
    else:
        initial = b''
        lasti = frame.f_lasti
    # we need to load our locals
    # attempt to jump over our NOPs if we have room
    jump = makeop('JUMP_FORWARD', lasti - len(initial) - 3, 3)
    if len(initial + jump) < lasti:
        initial = initial + jump
    # NOP out the code body leading up to the last executed instruction
    # (or possibly the instruction after that, if we're faking a return)
    new = initial + chr(dis.opmap['NOP']) * (lasti - len(initial)) + co.co_code[lasti:]
    # give the new code all its locals as arguments
    # (it's the only sane way to get python to recognize them)
    argcount = co.co_nlocals
    argseq = [lo.get(n, None) for n in co.co_varnames]
    # build the new code object)
    flags = co.co_flags & ~12
    newco = types.CodeType(
        argcount,
        co.co_nlocals,
        co.co_stacksize,
        flags,
        new,
        consts,
        co.co_names,
        co.co_varnames,
        co.co_filename,
        co.co_name,
        co.co_firstlineno,
        co.co_lnotab,
        co.co_freevars,
        co.co_cellvars)
    if 'RECKLESS_DEBUG' in os.environ:
        # we have to hack sys.stdout because 'dis' doesn't have an option to disassemble
        # to a string
        stdout = sys.stdout
        sys.stdout = sys.stderr
        print('\n== showing bytecode-patching information for {0} in {1} =='.format(co.co_name, co.co_filename), file=sys.stderr)
        print('before:', file=sys.stderr)
        dis.dis(co)
        print('after:', file=sys.stderr)
        dis.dis(newco)
        print('\n', file=sys.stderr)
        sys.stdout = stdout
    # bake a new function, replace its code object with the hacked up one above, and
    # execute it with the local variables from the original frame as its args
    context = get_function_in_context(frame.f_globals)
    context.__code__ = newco
    return context(*argseq)


def advance_frame(frame):
    """trick python into advancing a frame's instruction pointer by one line"""
    oldtrace = frame.f_trace
    try:
        frame.f_trace = sys.gettrace()
        frame.f_lineno += 1
    finally:
        frame.f_trace = oldtrace

