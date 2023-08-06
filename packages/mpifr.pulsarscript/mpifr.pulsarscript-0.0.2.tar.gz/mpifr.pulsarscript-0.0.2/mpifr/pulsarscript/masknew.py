# -*- coding: utf-8 -*-
"""
:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import os
import threading
import rvlm.entrypoint
import mpifr.pulsarscript.mask as mask
import mpifr.pulsarscript.utils as utils


@rvlm.entrypoint.mainfunction()
def convertNewPfftsFiles(
        srcdir,
        outdir,
        tmpdir     = "",
        loglevel   = "WARNING",
        numthreads = 1,
        nbit       = 8,
        var        = 3,
        chanthresh = 1.2):
    """
    Matches files in input and output directories and converts only PFFTS files
    for which there no matching FIL, MASK, MINMAX and BADCHANS files. Conversion
    is done in multiple threads to speed up work.

    :param srcdir:     Source directory to look for PFFTS files.
    :param outdir:     Target directory to place generated files.
    :param tmpdir:     Directory for intermediate files.
    :param loglevel:   Verbosity level ("DEBUG", "INFO", "ERROR" and so on).
    :param nimthreads: Maximul number files processed in parallel.
    :param nbit:       Downsampling program parameter.
    :param var:        Downsampling program parameter.
    :param chanthresh: Downsampling program parameter.
    :returns:          Exit code (zero un success).
    """
    assert(isinstance(srcdir,     str))
    assert(isinstance(outdir,     str))
    assert(isinstance(tmpdir,     str))
    assert(isinstance(loglevel,   str))
    assert(isinstance(numthreads, int))
    assert(isinstance(nbit,       int))
    assert(isinstance(var,        int))
    assert(isinstance(chanthresh, float))

    logger = utils.getlogger(__file__, loglevel)
    logger.info("Comparing directories")
    logger.info(" ... source directory: %s", srcdir)
    logger.info(" ... target directory: %s", outdir)

    srcFiles = set(utils.listdir(srcdir, "*.pffts"))
    outFiles = set(utils.listdir(outdir, "*%dbit.*" % nbit))

    # Extensions for target files.
    extensions = [ ".fil", ".mask", ".minmax", ".badchans" ]

    # It is not safe to modify collection while iteration, hence, 'copy()'.
    # Functional magic inside, be careful.
    for f in srcFiles.copy():
        (base, _) = os.path.splitext(f)
        hereall = all(
            map(lambda t: t in outFiles,
            map(lambda e: "%s_%dbit%s" % (base,nbit,e),
            extensions)))

        if hereall:
            srcFiles.remove(f)

    logger.info(" ... unique files found: %d", len(srcFiles))
    files = sorted(srcFiles, reverse=True)

    logger.debug("Creating lock object")
    lock = threading.Lock()


    def threadFunc():
        logger = utils.getlogger(__file__, loglevel)
        logger.debug("Entering thread")
        fileName = None
        while True:
            with lock:
                try:
                    fileName = files.pop()
                except IndexError:
                    break

            logger.info("Processing file: %s", fileName)
            exitcode = mask.convertPfftsFiles(outdir, *[fileName],
                tmpdir     = tmpdir,
                loglevel   = loglevel,
                skiperrors = True,
                nbit       = nbit,
                var        = var,
                chanthresh = chanthresh)

            if exitcode != 0:
                logger.error("Cannot convert file: %s", f)

        logger.debug("Leaving thread")

    # Note the usage of 'min()' in order not to create more threads then
    # total files found.
    threads = [threading.Thread(target=threadFunc)
        for thr in range(min(numthreads, len(files)))]

    for thr in threads:
        thr.start()

    for thr in threads:
        thr.join()

    # Always return success for now.
    return 0
