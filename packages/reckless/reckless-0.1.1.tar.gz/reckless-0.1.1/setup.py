from setuptools import setup

import site

setup(
    name = 'reckless',
    version = '0.1.1',
    packages = ['reckless'],
    py_modules = ['sitecustomize'],
    install_requires = [
        'blessings>=1.1',
        'bpython>=0.12'
    ],
    zip_safe = False,

    author = 'Ed Kellett',
    author_email = 'edk141@gmail.com',
    description = 'An exception hook that can keep running code after a top-level exception occurs',
    license = 'MIT',

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Utilities'
    ],

    long_description = '''
If you encounter a top-level exception while running a python program in a
tty, this package will give you the option to continue execution anyway like a
deranged lunatic.

Once you are executing things in this mode, things get a bit weird. The stack
will have strange entries on it, unassigned local variables will take on the
value None, and if you yield from a generator something will go wrong (most
likely the program will disappear from the stack and you'll immediately exit).

Tested on CPython 2.7 only.
'''
)

