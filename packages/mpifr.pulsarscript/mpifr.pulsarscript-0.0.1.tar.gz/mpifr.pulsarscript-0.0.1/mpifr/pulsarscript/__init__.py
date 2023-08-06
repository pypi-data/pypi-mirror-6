# -*- coding: utf-8 -*-
"""
Module which assists using of other modules in project. Currently it contains
the list of available modules to be run as scripts and functions to run them
as separate processed, via forking or Popen. This module provides two major
functions: :func:`runmodule` and :func:`runfork`.

:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import os
import sys
import subprocess


def runmodule(name, *args, **kwargs):
    """
    Runs module as a script in a separate Python interpreter. Module name may
    be fully-qualified or relative to this module. Example usages:

      * Running standard module :mod:`runpy`, which call itself, which calls
        itself and so on... ::

            runmodule("runpy", "runpy", "runpy", "runpy")

      * Running submodule :mod:`mask` as object, still with getopt-style
        parameters. Module must be imported with ``import`` clause
        before it can be used like that::

            import mpifr.pulsarscript.mask
            runmodule(mpifr.pulsarscript.mask, "--help")

      * Running submodule :mod:`mask` by name with getopt-style parameters,
        as if invoked via :command:`pulsar-script`, with output redirection
        (handled by by :func:`subprocess.Popen`). Note that no import clause
        needed in this case::

            fd = open("test.log", "w+b")
            runmodule("mpifr.pulsarscript.mask", "--help", stderr=fd)

    :param name:   Module name or module object.
    :param args:   Extra command line parameters.
    :param kwargs: Extra parameters to :func:`subprocess.Popen`.
    :returns:      Result returned by :func:`subprocess.Popen`.
    """
    assert(isinstance(name, str) or type(name) == type(sys))
    if type(name) == type(sys):
        name = name.__name__

    # In order to let python find 'mpifr.puslasrscript.*' moduiles in case they
    # are not installed system-wide, there must be performed alteration
    # of 'PYTHONPATH' environment variable.
    env = os.environ.copy()
    path = ":".join(sys.path)
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = path
    else:
        env["PYTHONPATH"] += ":" + path

    # Note here the use of Python interpreter's command-line option '-m' which
    # loads module and runs it as a script.
    return subprocess.Popen(
        [sys.executable, "-m", name] + list(args), env = env, **kwargs)


def runfork(func, *args, **kwargs):
    """
    Runs function in parallel by forking Python interpreter process. This is
    not supported on Windows unless you use Cygwin. Child process gets
    terminated after the function returned while parent process get the PID
    of child and can thereby monitor the state of child. Example usages:

      * Simple hello-world lambda::

            import sys
            runfork(lambda: sys.stdout.write("Hello, world."))

      * More elaborated version::

            import sys
            runfork(lambda who: sys.stdout.write("Hello, %s."% who), "world")

      * Running a dozen of lambdas in separate process and wait until they
        all are done::

            import sys
            import os
            import time

            pids = []
            for i in range(0, 12):
                pid = runfork(lambda t: time.sleep(x*1000), t = i)
                pids.append(pid)

            for pid in pids:
                os.waitpid(pid)

    :param func: Callable object to run in separate process.
    :param args: Positional arguments to be passed to `func`.
    :param kwargs: Keyword arguments to be passed to `func`.
    :returns: Process ID (PID) of child process.
    """
    assert(callable(func))

    pid = os.fork()

    # If fork() returned something notzero (and haven't raise an exception)
    # then it is the parent process. Just return pid and leave.
    if pid != 0:
        return pid

    # If we are here then it is a child process. Now we should execute desired
    # function and then exit process.
    result = func(*args, **kwargs)
    if not isinstance(result, int):
        result = 0

    os._exit(result)
