from __future__ import print_function, unicode_literals

import blessings
import bpdb
import bpython
import sys

from execute import advance_frame, execute


term = blessings.Terminal()


class _recklessException(Exception):
    pass


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
 s : shell (bpython){t.normal}
'''.format(hook_name, t=term))
    cmd = False
    while cmd not in set('cdens'):
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


def continue_(traceback):
    first = True
    t = traceback
    while t.tb_next:
        t = t.tb_next
    f = t.tb_frame
    try:
        advance_frame(f)
    except ValueError as e:
        raise _recklessException("couldn't advance to next line: " + e.message)
    fancy_print('resuming execution')
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
            if isinteractive():
                return _old_hook(type_, value, traceback)
            if newexc:
                fancy_print('intercepting an exception:')
                sys.__excepthook__(type_, value, traceback)
                newexc = False
            cmd = prompt()
            if cmd == 'c':
                exc = continue_(traceback)
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
                bpython.embed(t.tb_frame.f_locals, ['-i'])
            else:
                if _old_hook is not sys.__excepthook__:
                    _old_hook(type_, value, traceback)
                break
        except _recklessException as e:
            fancy_print(e.message)
            break
