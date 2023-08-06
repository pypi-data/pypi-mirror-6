#!/usr/bin/env python
""" setup script for delocate package """
from os.path import join as pjoin
try:
    import setuptools
except ImportError:
    pass
from distutils.core import setup
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = pjoin('delocate', '_version.py')
versioneer.versionfile_build = pjoin('delocate', '_version.py')
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'delocate-'

setup(name='delocate',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Move OSX dynamic libraries into package',
      author='Matthew Brett',
      maintainer='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/delocate',
      packages=['delocate', 'delocate.tests'],
      package_data = {'delocate.tests':
                      [pjoin('data', '*.dylib'),
                       pjoin('data', 'liba.a'),
                       pjoin('data', 'a.o'),
                       pjoin('data', '*.whl'),
                       pjoin('data', 'test-lib'),
                       pjoin('data', 'make_libs.sh')]},
      scripts = [pjoin('scripts', f) for f in (
          'delocate-listdeps',
          'delocate-wheel',
          'delocate-path')],
      license='BSD license',
      classifiers = ['Intended Audience :: Developers',
                     "Environment :: Console",
                     'License :: OSI Approved :: BSD License',
                     'Programming Language :: Python',
                     'Operating System :: MacOS :: MacOS X',
                     'Development Status :: 3 - Alpha',
                     'Topic :: Software Development :: Libraries :: '
                     'Python Modules',
                     'Topic :: Software Development :: Build Tools'],
      long_description = open('README.rst', 'rt').read()
     )
