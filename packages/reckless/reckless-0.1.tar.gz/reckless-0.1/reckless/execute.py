from __future__ import print_function, unicode_literals

import types
import dis
import struct
import sys


def execute(frame, *rv):
    # we need a frame because it contains the lasti
    co = frame.f_code
    consts = co.co_consts
    # if we're to fake a return from a function call, NOP out the function call as well
    # it'll be the next 3 bytes at the instruction pointer, so just increase that by 3.
    if rv:
        lasti = frame.f_lasti + 3
        new = chr(dis.opmap['NOP']) * lasti + co.co_code[lasti:]
        # insert a new constant and load it
        nc = len(consts)
        consts = consts + (rv[0],)
        bc = struct.pack('<BH'.encode('ascii'), dis.opmap['LOAD_CONST'], nc)
        new = bc + new[len(bc):]
    else:
        new = chr(dis.opmap['NOP']) * frame.f_lasti + co.co_code[frame.f_lasti:]
    newco = types.CodeType(
        co.co_argcount,
        co.co_nlocals,
        co.co_stacksize,
        co.co_flags,
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
    return eval(newco, frame.f_globals, frame.f_locals)


def advance_frame(frame):
    oldtrace = frame.f_trace
    try:
        frame.f_trace = sys.gettrace()
        frame.f_lineno += 1
    finally:
        frame.f_trace = oldtrace

