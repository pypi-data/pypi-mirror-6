#!/usr/bin/env python
"""
 python-ups
 Copyright (C) 2009 Pablo Hernandez

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from distutils.core import setup, Command
from zipfile import ZipFile, ZIP_STORED
import os
import ups

LONG_DESCRIPTION = \
"""A light wrapper around UPS's Web Services SOAP API using suds."""

CLASSIFIERS = [
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules'
              ]

KEYWORDS = 'ups soap suds wrapper'

class zip_docs(Command):
    description = "Zip the docs directory in preparation for uploading to PyPi."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        filename = "python-ups-docs-%s.zip" % ups.VERSION
        file = open(filename, 'w')
        zfile = ZipFile(file, 'w', ZIP_STORED)

        for file in os.listdir('docs'):
            if file != '.svn':
                zfile.write(os.path.join('docs', file),
                            arcname=file)
        zfile.close()


setup(name='liteview-ups',
      version=ups.VERSION,
      description='UPS Web Services API wrapper.',
      long_description=LONG_DESCRIPTION,
      author='Pablo Hernandez',
      author_email='pabloh007@gmail.com',
      url='http://code.google.com/p/python-ups/',
      download_url='http://pypi.python.org/pypi/ups/',
      packages=['ups', 'ups.services'],
      package_dir={'ups': 'ups'},
      #package_data={'fedex': ['wsdl/*.wsdl', 'wsdl/test_server_wsdl/*.wsdl']},
      platforms=['Platform Independent'],
      license='GPLv3',
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      requires=['suds'],
      install_requires=['suds'],
      cmdclass={'zip_docs': zip_docs},
     )
