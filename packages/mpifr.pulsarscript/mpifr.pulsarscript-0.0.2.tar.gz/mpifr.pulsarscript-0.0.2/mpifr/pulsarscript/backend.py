# -*- coding: utf-8 -*-
"""
Module for wrapping around external programs, in order to eliminate the need
in frequent :func:`subprocess.call` (not nentioning world's biggest evil
function :func:`os.system`, which is a huge security hole). This module loads
its configuration from files names :file:`backend.conf.py`, which by default
are the following:

 * :file:`/etc/pulsar-script/backend.conf.py`
 * :file:`~/.config/pulsar-script/backend.conf.py`
 * :file:`./backend.conf.py`

:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import six
import subprocess
import mpifr.pulsarscript.config

config = mpifr.pulsarscript.config.getbunch("backend.config.py",
    CmdFilterbankPFFTS = "FilterBankPFFTS",
    CmdDownsample421   = "421.exe",
    CmdGzip            = "gzip")

def filterbankPFFTS(inputFile, outputFile):
    """
    Runs :program:`filterbank` program on a file. The exact command to use
    can be specified in configuration file entry `CmdFileterbankPFFTS`.

    :param inputFile:  Input PFFTS file, unchanged.
    :param outputFile: Output FIL file, overwritten.
    :returns: Exit code of underlying program.
    """
    assert(isinstance(inputFile, six.string_types))
    assert(isinstance(outputFile, six.string_types))

    # The 'subprocess.call' runs command "filterbank FILE.pffts > FILE.fil"
    # in a much neater and safer way than deprecated function 'os.system'.
    with open(outputFile, "wb") as output:
        return subprocess.call([
            config.CmdFilterbankPFFTS,
            inputFile],
            stdout = output)


def downsample421(inputFile,
    filFile      = None,
    maskFile     = None,
    maxminFile   = None,
    badchansFile = None,
    nbit         = 8,
    var          = 3,
    chanthresh   = 1.2):
    """
    Runs downsampling program (strangely named :program:`421.exe`, even
    in Linux). The exact path to that program can be specified in configuration
    file entry `CmdDownsample421`.

    :param inputFile:    Input FIL file, unchanged.
    :param filFile:      Output FIL file, overwritten.
    :param maskFile:     Output MASK file, overwritten.
    :param minmaxFile:   Output MINMAX file, overwritten.
    :param badchansFile: Output BADCHANS file, overwritten.
    :param nbit:         Number of bits in output files.
    :param var:          Unknown.
    :param chanthresh:   Unknown.
    :returns: Exit code of underlying program.
    """
    assert(inputFile is not None)
    assert(isinstance(inputFile,    six.string_types))
    assert(isinstance(maskFile,     six.string_types) or maskFile     is None)
    assert(isinstance(maxminFile,   six.string_types) or maxminFile   is None)
    assert(isinstance(badchansFile, six.string_types) or badchansFile is None)
    assert(isinstance(nbit,         six.integer_types))
    assert(isinstance(var,          six.integer_types + (float,)))

    cmdargs = []
    if filFile      is not None: cmdargs += ["-o",       filFile ]
    if maskFile     is not None: cmdargs += ["-omask",   maskFile ]
    if maxminFile   is not None: cmdargs += ["-maxmin",  maxminFile ]
    if badchansFile is not None: cmdargs += ["-rfichan", badchansFile ]

    if cmdargs == []:
        raise RuntimeError("Wrong parameters given.")

    return subprocess.call([
        config.CmdDownsample421,
        "-nbit",        str(nbit),
        "-var",         str(var),
        "-chanthresh",  str(chanthresh),
        "-f",           inputFile] + cmdargs)


def gzip(fileName):
    """
    Runs gzip archiver. This function wraps :program:`gzip` command called with
    exactly one argument. The exact path to that program can be specified in
    configuration file entry `CmdGzip`.

    :param fileName: Filename which is argument to :command:`gzip`.
    :return: Exit code of underlying program.
    """
    assert(isinstance(fileName, six.string_types))
    return subprocess.call([config.CmdGzip, fileName])
