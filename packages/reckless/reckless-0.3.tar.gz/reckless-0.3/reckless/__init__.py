from __future__ import print_function, unicode_literals

import blessings
import bpdb
import bpython
import sys

from execute import advance_frame, execute


term = blessings.Terminal()


class _recklessException(Exception):
    pass


class _LocalProxyDict(dict):
    """a mapping that allows bpython's shell to operate on local and global
    variables correctly. only subclasses dict to fool python - we actually
    implement everything ourselves"""
    def __init__(self, varnames, locals_, globals_):
        self.varnames = set(varnames)
        self.locals_ = locals_
        self.globals_ = globals_

        for name in ('keys', 'values', 'items', 'iterkeys', 'itervalues',
                     'iteritems', '__str__', '__repr__'):
            def wrapper(self, *a, **kw):
                return getattr(self._combined(), name)
            setattr(self, name, wrapper)

    def __getitem__(self, k):
        if k in self.varnames:
            return self.locals_[k]
        else:
            return self.globals_[k]

    def __setitem__(self, k, v):
        if k in self.varnames:
            self.locals_[k] = v
        else:
            self.globals_[k] = v

    def _combined(self):
        c = dict(self.globals_)
        for n in self.varnames:
            if n in self.locals_:
                c[n] = self.locals_[n]
            else:
                del c[n]
        return c


def fancy_print(msg):
    for l in msg.splitlines():
        print("{t.red}[reckless] {msg}{t.normal}".format(msg=l, t=term))


def install():
    if not term.is_a_tty:
        return  # we don't want to use an interactive debugger thing in a non-terminal

    global _old_hook
    _old_hook = sys.excepthook
    sys.excepthook = excepthook


def isinteractive():
    return getattr(sys, 'argv', [None])[0] == '' or hasattr(sys, 'ps1')


def prompt():
    if _old_hook is sys.__excepthook__:
        hook_name = ''
    else:
        hook_name = ' ({0})'.format(_old_hook.__name__)
    sys.stderr.write('''{t.white} c : continue execution {t.red}(insane){t.white}
 d : debugger (bpdb)
 e : exit
[n]: do nothing
 r : retry {t.red}(insane){t.white}
 s : shell (bpython){t.normal}
'''.format(hook_name, t=term))
    cmd = False
    while cmd not in set('cdenrs'):
        sys.stderr.write('what now? ')
        try:
            cmd = raw_input().lower()
        except KeyboardInterrupt:
            cmd = 'e'
            sys.stderr.write('\n')
        except:
            cmd = False
            sys.stderr.write('\n')
    return cmd


def continue_(traceback, sameline=False):
    first = True
    t = traceback
    while t.tb_next:
        t = t.tb_next
    f = t.tb_frame
    try:
        advance_frame(f, 0 if sameline else 1)
    except ValueError as e:
        raise _recklessException("couldn't reposition instruction pointer: " + e.message)
    ancy_print('resuming execution')
    while f:
        try:
            if first:
                value = execute(f)
            else:
                value = execute(f, value)
            first = False
        except:
            return sys.exc_info()
        f = f.f_back
        if f and f.f_code == execute.__code__:
            break
    fancy_print('reached end of program')


def excepthook(type_, value, traceback):
    newexc = True
    while True:
        try:
            if isinteractive() or type_ is KeyboardInterrupt:
                return _old_hook(type_, value, traceback)
            if newexc:
                fancy_print('intercepting an exception:')
                sys.__excepthook__(type_, value, traceback)
                newexc = False
            cmd = prompt()
            if cmd in 'cr':
                exc = continue_(traceback, cmd == 'r')
                if exc:
                    type_, value, traceback = exc
                    newexc = True
                    continue
                break
            elif cmd == 'd':
                bpdb.post_mortem(traceback)
            elif cmd == 'e':
                raise SystemExit(1)
            elif cmd == 's':
                t = traceback
                while t.tb_next:
                    t = t.tb_next
                f = t.tb_frame
                lo = _LocalProxyDict(f.f_code.co_varnames, f.f_locals, f.f_globals)
                bpython.embed(lo, ['-i'])
            else:
                if _old_hook is not sys.__excepthook__:
                    _old_hook(type_, value, traceback)
                break
        except _recklessException as e:
            fancy_print(e.message)
