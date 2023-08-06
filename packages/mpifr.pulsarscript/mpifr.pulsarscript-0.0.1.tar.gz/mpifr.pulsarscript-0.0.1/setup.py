#!/usr/bin/env python
from setuptools import setup
import os
import sys


# Utility function to read whole file contents.
def filecontents(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name         = "mpifr.pulsarscript",
    packages     = ["mpifr.pulsarscript"],
    scripts      = ["pulsar-script"],
    version      = "0.0.1",
    description  = "Radioastronomic workflow service scripts",
    author       = "Pavel Kretov",
    author_email = "firegurafiku@gmail.com",
    license      = "MIT",
    url          = "https://bitbucket.org/mpifr/mpifr-pulsar-scripts",
    keywords     = ["command line" ],
    classifiers  = [
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Libraries :: Python Modules" ],
    long_description = filecontents("DESCRIPTION.rst"))
