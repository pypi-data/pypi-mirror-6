from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup


TOP_LEVEL_NAME = "whs"

setup(name=TOP_LEVEL_NAME+'.utils.pyman',
      version='0.9.0',
      description='Utility for easy creation of help POSIX man-like pages',
      long_description='''WHS Ltd provides collection of pure-python modules.

This is simple module created with intention of easier help system development
for your applications.

Standard usage should mimic POSIX man program, basing on builtin help()
implementation.

It was tested on python 3.3, but was written with any version in mind.
''',
      maintainer = "Filip Malczak",
      maintainer_email='filip(dot)malczak(at)gmail(dot)com',
      url='https://devzone.itadmin.pl',
      namespace_packages=[
          TOP_LEVEL_NAME,
      ],
      packages=[
          TOP_LEVEL_NAME+'.utils'
      ],
      py_modules=[
          "ez_setup",
          TOP_LEVEL_NAME+'.utils.pyman'
      ],
      license = "BSD license (http://opensource.org/licenses/bsd-license.php); "
      "owner: Web Harvesting Solutions Ltd; "
      "year: 2013",
      platforms =[ "Any"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Utilities"
      ],
     )
