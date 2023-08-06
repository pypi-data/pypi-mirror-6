from __future__ import print_function, unicode_literals

import types
import dis
import os
import struct
import sys

import reckless


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
        if arg > 0xFFFF:
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
    """make a function with no local variables or closures with a given
    __globals__"""
    return eval(_get_plain.__code__, g, {})


def execute(frame, *rv):
    """jump back into a frame, and execute it until it next returns.

    if anything is passed for 'rv', it should be a single object, which we
    will pretend was just returned by the current operation.

    won't work on generators."""
    # a brief explanation of what all this does:
    # we can't arbitrarily jump into frames, so we try to fake it by executing
    # a new code object. this object is identical to the one in the given
    # frame, with some differences:
    # - in order to get python to load the local variables correctly, it takes
    #   all its local variables as arguments
    # - the code preceding the instruction pointer is replaced by NOP (and, if
    #   possible, skipped with a JUMP_FORWARD)
    # - if we need to fake a return value (i.e. from another operation we
    #   faked), we append the object to return at the end of the code object's
    #   co_consts, and inject a LOAD_CONST instruction into the code.
    # this code is then executed as a function call to a new function with
    # patched __code__. we have to jump through a couple of hoops to get this
    # function right; see get_function_in_context above.

    # it's possible any of this might fail. if so, we don't want the excepthook
    # to start trying to operate on itself...
    try:
        # we need a frame because it contains the lasti
        co = frame.f_code
        lo = frame.f_locals
        consts = co.co_consts
        # if we're to fake a return from another operation, NOP out that
        # operation too. it's always the instruction at the instruction
        # pointer; we can read this one and then add an extra constant (which
        # might not really be constant) to the code object, and add an
        # instruction to load that constant (so it takes the place in the
        # stack of the return value).
        if rv:
            # insert a new constant and load it
            consts = consts + (rv[0],)
            # read the function call op, just to make sure it doesn't have
            # >65535 arguments...
            op = readop(co.co_code, frame.f_lasti)
            if 'RECKLESS_DEBUG' in os.environ:
                oarg = '' if op[1] is None else op[1]
                print('skipping over {0}({1}) to return {2}'.format(
                    op[0], oarg, rv[0]), file=sys.stderr)
            initial = makeop('LOAD_CONST', len(consts) - 1)
            lasti = frame.f_lasti + op[2]
        else:
            initial = b''
            lasti = frame.f_lasti
        # we need to load our locals
        # attempt to jump over our NOPs if we have room
        if lasti - len(initial) > 3:
            jump = makeop('JUMP_FORWARD', lasti - len(initial) - 3, 3)
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
            dis.disassemble(co, frame.f_lasti)
            print('after:', file=sys.stderr)
            dis.dis(newco)
            print('\n', file=sys.stderr)
            sys.stdout = stdout
        # bake a new function, replace its code object with the hacked up one above, and
        # execute it with the local variables from the original frame as its args
        context = get_function_in_context(frame.f_globals)
        context.__code__ = newco
    except Exception as e:
        raise reckless._recklessException(e.message)
    return context(*argseq)


def advance_frame(frame, count=1):
    """trick python into advancing a frame's instruction pointer by one line"""
    oldtrace = frame.f_trace
    try:
        frame.f_trace = sys.gettrace()
        frame.f_lineno += count
    finally:
        frame.f_trace = oldtrace

