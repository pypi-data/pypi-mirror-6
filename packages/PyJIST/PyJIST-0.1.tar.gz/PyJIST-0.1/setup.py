#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyJIST -- The simplified JIST Command Line Interface

PyJIST is Python-based wrapper for accessing the JIST command line interface
(CLI) without the hassle of constructing complicated classpaths and memorizing
long module definitions.

Created by Andrew Asman on 2014-02-17
Copyright 2014 MASI, Vanderbilt University. All rights reserved..

--- Prerequisites ---
Install mipav
Install JIST (the newer the better)
Install Python (tested on 2.7)
"""

__author__ = 'Andrew Asman <andrew.j.asman@vanderbilt.edu>'
__license__ = 'GPL'
__copyright__ = '2014, Vanderbilt University'

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License (GPL)
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
Programming Language :: Python
Programming Language :: Python :: 2.7
"""

from distutils.core import setup
import os

doclines = __doc__.split("\n")

if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

setup(name='PyJIST',
      version='0.1',
      packages=['PyJIST'],
      scripts=['bin/JIST-run'],
      author='Andrew J. Asman',
      author_email='andrew.j.asman@vanderbilt.edu',
      maintainer='MASI lab, Vanderbilt University',
      maintainer_email='andrew.j.asman@vanderbilt.edu',
      url='https://www.nitrc.org/plugins/mwiki/index.php/jist:PyJIST',
      download_url='http://masi.vuse.vanderbilt.edu/jenkins/job/Build%20PyJIST/',
      license='GPL',
      platforms = ["any"],
      description=doclines[1],
      long_description = "\n".join(doclines[3:]),
      classifiers=filter(None,classifiers.split("\n")),
     )
