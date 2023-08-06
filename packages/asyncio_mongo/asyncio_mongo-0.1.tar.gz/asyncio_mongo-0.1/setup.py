#!/usr/bin/env python

import sys
import os
import shutil

from setuptools import setup
from setuptools import Feature
from distutils.cmd import Command
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
from distutils.errors import DistutilsPlatformError, DistutilsExecError
from distutils.core import Extension


requirements = []
try:
    import xml.etree.ElementTree
except ImportError:
    requirements.append("elementtree")
try:
    import asyncio
except ImportError:
    requirements.append("asyncio")


if sys.platform == 'win32' and sys.version_info > (2, 6):
   # 2.6's distutils.msvc9compiler can raise an IOError when failing to
   # find the compiler
   build_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError,
                 IOError)
else:
   build_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class custom_build_ext(build_ext):
    """Allow C extension building to fail.

    The C extension speeds up BSON encoding, but is not essential.
    """

    warning_message = """
**************************************************************
WARNING: %s could not
be compiled. No C extensions are essential for PyMongo to run,
although they do result in significant speed improvements.

%s
**************************************************************
"""

    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError as e:
            print(e)
            print(self.warning_message % ("Extension modules",
                                          "There was an issue with your platform configuration - see above."))

    def build_extension(self, ext):
        if sys.version_info[:3] >= (2, 4, 0):
            try:
                build_ext.build_extension(self, ext)
            except build_errors as e:
                print(e)
                print(self.warning_message % ("The %s extension module" % ext.name,
                                              "Above is the ouput showing how "
                                              "the compilation failed."))
        else:
            print(self.warning_message % ("The %s extension module" % ext.name,
                                          "Please use Python >= 2.4 to take "
                                          "advantage of the extension."))

c_ext = Feature(
    "optional C extension",
    standard=True,
    ext_modules=[Extension('asyncio_mongo._bson._cbson',
                            include_dirs=['asyncio_mongo/_bson'],
                            sources=['asyncio_mongo/_bson/_cbsonmodule.c',
                                     'asyncio_mongo/_bson/time64.c',
                                     'asyncio_mongo/_bson/buffer.c',
                                     'asyncio_mongo/_bson/encoding_helpers.c']),
                 Extension('asyncio_mongo._pymongo._cmessage',
                           include_dirs=['bson'],
                           sources=['asyncio_mongo._pymongo/_cmessagemodule.c',
                                    'asyncio_mongo/_bson/buffer.c'])])

if "--no_ext" in sys.argv:
    sys.argv = [x for x in sys.argv if x != "--no_ext"]
    features = {}
else:
    features = {"c-ext": c_ext}

setup(
    name="asyncio_mongo",
    version="0.1",
    description="Asynchronous Python 3.3+ driver for MongoDB <http://www.mongodb.org>",
    author="Alexandre Fiori, Don Brown",
    author_email="mrdon@twdata.org",
    url="https://bitbucket.org/mrdon/asyncio-mongo",
    keywords=["mongo", "mongodb", "pymongo", "gridfs", "asyncio_mongo", "asyncio"],
    packages=["asyncio_mongo", "asyncio_mongo._pymongo", "asyncio_mongo._bson"],
    install_requires=requirements,
    features=features,
    license="Apache License, Version 2.0",
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Database"],
    cmdclass={"build_ext": custom_build_ext,
              "doc": ""})
