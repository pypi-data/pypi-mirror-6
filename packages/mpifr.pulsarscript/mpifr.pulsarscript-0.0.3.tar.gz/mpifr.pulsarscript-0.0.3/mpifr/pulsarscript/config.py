# -*- coding: utf-8 -*-
"""
Module for gavering data from variously located configuration files written
in Python. It tries to find out configuration files in various locations, and,
if found, runs their code to get values from them. Note that despite their code
is executed in protected environment, it still may contain **any** Python code,
even mallicious. It is your responsibility to check your configs before using
this module.

It is recommented to give you configuration files extension ".py" to clearly
indicate the fact that they'll get executed, not just parsed.

For example if you want to read configuration file named :file:`test.conf.py`
and default locations list is used, the following files will be checked,
in that order:

 * :file:`/etc/pulsar-script/test.conf`
 * :file:`~/.config/pulsar-script/test.conf`
 * :file:`./test.conf`

Note that latest files can (and, in most cases, will) override settings made
in the former ones.

:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import sys
import os
import mpifr.pulsarscript.bunch as bunch


locations = ["/etc/pulsar-script", "~/.config/pulsar-script", "."]
"""
Paths where to look for configuration files. You may use tilde ("~") to denote
user home directory, as it gets expanded by :func:`os.path.expanduser`.
"""


def getdict(filename, defaults = {}):
    """
    Reads configuration files with given `filename` and returns
    dictionary with their data. Value of `default` parameter is used
    as initial for for protected environment. It is also returned when no
    configuration files were found at all. To prevent code in configuration
    file from modifying variables in main script, default environment gets
    copied before configuration files execution.

    :param filename: Configuration files relative name (with extension).
    :param defaults: Default values for configuration files' entries.
    :returns:        Dictionary with extries collected from configuration files.
    """
    assert(isinstance(filename, str))
    assert(isinstance(defaults, dict))
    result = defaults.copy()
    for loc in locations:
        # It is quite safe to completely ignore all possible errors raised
        # by underlying configuration file's script [1]. But on the level
        # of the caller script we must not ignore anything but I/O errors [2],
        # in order not to miss errors in own code.
        # Also see http://stackoverflow.com/a/436267/1447225 for more
        # information about execfile() workaround in Python-3.
        try:
            configFile = os.path.join(os.path.expanduser(loc), filename)
            with open(configFile, "r") as cfg:
                contents = cfg.read()
                try:
                    exec(contents, None, result)
                except:
                    pass # [1]
        except IOError:
            pass # [2]

    return result


def getbunch(filename, **defaults):
    """
    Convenience function for :func:`getdict` which eliminates the need for
    verbose `hash["param"]` syntax. Call it simply::

        cfg = config.getbunch("test.conf.py",
            verbose = False,
            archiver = "gzip")

        print(cfg.verbose)
        print(cfg.archiver)
    """
    return bunch.Bunch(**getdict(filename, defaults))
