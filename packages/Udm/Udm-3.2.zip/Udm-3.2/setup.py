#!/usr/bin/env python

import sys
import os
import os.path
import platform
#from distutils.core import setup, Extension
#from distutils.command.build_ext import build_ext
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

this_dir = os.path.dirname(os.path.abspath(__file__))

setup_args = dict(
    name='Udm',
    version='3.2',
    description='Universal Data Model',
    long_description='Universal Data Model',
    author='Kevin Smyth',
    author_email='ksmyth@isis.vanderbilt.edu',
    url='http://repo.isis.vanderbilt.edu/',
    license='Vanderbilt UDM License',
    packages=['udm'],
)

setup_args['ext_modules'] = [
  Extension('udm.udm',
    ['UdmPython.cpp'],
    libraries=['boost_python', 'udm'], # TODO: udm?
    library_dirs = [os.path.join(this_dir, '../../lib/.libs')],
    include_dirs=['/usr/include/udm/', os.path.join(this_dir, '../../include')])
]
if platform.system() == 'Windows':
    class my_build_ext(build_ext):
        def build_extension(self, ext):
            ''' Copies the already-compiled pyd
            '''
            import shutil
            import os.path
            try:
                os.makedirs(os.path.dirname(self.get_ext_fullpath(ext.name)))
            except WindowsError, e:
                if e.winerror != 183: # already exists
                    raise


            shutil.copyfile(os.path.join(this_dir, r'..\..\bin\Python%d%d\udm.pyd' % sys.version_info[0:2]), self.get_ext_fullpath(ext.name))

    setup_args['cmdclass'] = {'build_ext': my_build_ext }

setup(**setup_args)
