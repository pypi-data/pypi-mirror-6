# -*- coding: utf-8 -*-
"""
:copyright: 2014, Marina Berezina
:copyright: 2014, Pavel Kretov
:license: MIT
"""
import os
import shutil
import tempfile
import rvlm.entrypoint
import mpifr.pulsarscript.backend as backend
import mpifr.pulsarscript.utils as utils


@rvlm.entrypoint.mainfunction()
def convertPfftsFiles(outdir, *files,
        tmpdir     = "",
        skiperrors = False,
        loglevel   = "WARNING",
        nbit       = 8,
        var        = 3,
        chanthresh = 1.2):
    """
    Converts PFFTS files. For each input file a bunch of data files is
    generated an places to output directory. For example, if input file base
    name is :file:`test.pffts` and `nbit` is :const:`8`, then the
    following files are generated in the output directory:

       * :file:`test_8bit.fil`
       * :file:`test_8bit.mask`
       * :file:`test_8bit.maxmin`
       * :file:`test_8bit.badchans`
    """
    # Assertions for 'nbit', 'var' and 'chanthresh' are skipped because they
    # are checked in underlying 'backend.filterbankPFFTS' function.
    assert(isinstance(outdir, str))
    assert(isinstance(tmpdir, str))
    assert(isinstance(skiperrors, bool))
    assert(isinstance(loglevel, str))
    for f in files:
        assert(isinstance(f, str))

    logger = utils.getlogger(__file__, loglevel)

    # First, check for output directory presence. If none, try to create one.
    if not os.path.isdir(outdir):
        raise RuntimeError("Unable to find output directory %s." % outdir)

    # Next, check for temp directory presence.
    if tmpdir == "":
        tmpdir = None
    if tmpdir is not None and not os.path.isdir(tmpdir):
        raise RuntimeError("Unable to find temporary directory %s." % tmpdir)

    extensions = [ ".fil", ".mask", ".minmax", ".badchans"]

    # Exit code (nice shorthand, isn't it?).
    xc = 0
    with utils.temporaryFile(dir=tmpdir) as tempFilFile:
        for f in files:
            # Get bare basename without extension.
            (base, _) = os.path.splitext(os.path.basename(f))
            
            targetFiles = [os.path.join(outdir, "%s_%dbit%s"
                            % (base, nbit, ext)) for ext in extensions]

            with utils.temporaryFiles(len(extensions), dir=tmpdir) as tempFiles:

                logger.info("Processing file: %s", f)
                logger.debug(" ... using temp file: %s (fil)", tempFilFile)
                for temp in tempFiles:
                    logger.debug(" ... using temp file: %s", temp)

                # This is a fake 'for' loop which runs only one iteration.
                for _ in range(1):
                    xc = backend.filterbankPFFTS(f, tempFilFile)
                    if xc != 0: break
                   
                    xc = backend.downsample421(tempFilFile,
                        nbit         = nbit,
                        var          = var,
                        chanthresh   = chanthresh,
                        filFile      = tempFiles[0],
                        maskFile     = tempFiles[1],
                        maxminFile   = tempFiles[2],
                        badchansFile = tempFiles[3])
                    if xc != 0: break
                
                    for (temp, target) in zip(tempFiles, targetFiles):
                        logger.debug(" ... moving: %s -> %s", temp, target)
                        try: shutil.move(temp, target)
                        except shutil.Error: xc = 1
                
            if xc != 0:
                logger.error("Cannot convert file: %s", f)
                if skiperrors: continue
                else: break

    return xc
