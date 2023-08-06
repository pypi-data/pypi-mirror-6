# -*- coding: utf-8 -*-
"""
Module which contains various utility functions. They can have nothing in
common, but to be useful in some (maybe quite rare) cases.

:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import contextlib
import fnmatch
import logging
import os
import sys
import tempfile


def getlogger(name, loglevel):
    """
    Returns logger for all informational and debug printing in script.
    See standard module :mod:`logging` for more information.
    :param name: Logger name.
    :param loglevel: Logging level.
    """
    logging.basicConfig(
        stream=sys.stderr,
        format="%(threadName)-10s %(levelname)-7s | %(module)s: %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    return logger


def listdir(dirname, pattern="*"):
    """
    """
    assert(isinstance(dirname, str))
    assert(isinstance(pattern, str))
    return fnmatch.filter(os.listdir(dirname), pattern)


def mkstemp1(**kwargs):
    """
    Wrapper for :func:`tempfile.mkstemp` function, which closes returnes file
    handle and return only the filename.
    :param kwargs: Keyword parameters to be passed to :func:`mkstemp`.
    :returns:      File name of the temporary file created.
    """
    (fd, fileName) = tempfile.mkstemp(**kwargs)
    os.close(fd)
    return fileName
	

@contextlib.contextmanager
def temporaryFile(**kwargs):
    """
    Creates temporary file and automatically removes it on exit
    of ``with`` statement. This may be very helpful when calling
    external commands from Python scripts.

    :param kwargs: Keyword parameters to be passed to :func:`tempfile.mkstemp`.
    :returns: Name of the temporary file created.
    """
    result = None
    try:
        result = mkstemp1(**kwargs)
        yield result
    finally:
        try: os.remove(result)
        except OSError: pass


@contextlib.contextmanager
def temporaryFiles(count=1, **kwargs):
    """
    Creates temporary files and automatically removes them all on exit
    of ``with`` statement. This may be very helpful when calling
    external commands from Python scripts.

    :param count:  Number of files to create.
    :param kwargs: Keyword parameters to be passed to :func:`tempfile.mkstemp`.
    :returns: List of names of temporary file created.
    """
    result = []
    try:
        result = [mkstemp1(**kwargs) for _ in range(count)]
        yield result
    finally:
        for f in result:
            try: os.remove(f)
            except OSError: pass
