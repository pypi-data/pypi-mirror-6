#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Dec  2 12:38:08 CET 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring adminstrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all parameters that define our package.
setup(

    # Basic information about the project
    name='xfacereclib.paper.IET2014',
    version='1.0.0',
    description='Running the experiments as given in paper: "Score Calibration in Face Recognition".',

    # Additional information of the package
    url='http://gitlab.idiap.ch/manuel.guenther/xfacereclib-paper-iet2014',
    license='LICENSE.txt',
    author='Manuel Guenther',
    author_email='manuel.guenther@idiap.ch',

    # The description that is shown on the PyPI page
    long_description=open('README.rst').read(),

    # The definition of what is provided by this package
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install" this package.
    # All packages that are mentioned here, but are not installed on the current system will be installed locally and only visible to the scripts of this package.
    # Don't worry - You won't need adminstrative privileges when using buildout.
    install_requires=[
      'setuptools',                   # the tool to install dependent packages
      'bob >= 1.2.0, <= 1.3.0',       # the base signal processing/machine learning library containing most of the face recognition algorithms
      'facereclib == 1.2.1',          # the tool to actually run all experiments
      'xbob.db.scface',               # the interface to the SCface database
      'xbob.db.mobio',                # the interface to the MOBIO database
      'matplotlib'                    # plotting utility
    ],

    # This defines a namespace package so that other projects can share this namespace.
    namespace_packages = [
      'xfacereclib',
      'xfacereclib.paper'
    ],

    # Here, the entry points (resources) are registered.
    entry_points = {
      # Register four console scripts, one for executing the experiments, one for evaluating the results, one for categorical calibration and one for generating the plots
      'console_scripts': [
        'iet2014_face_recog.py  = xfacereclib.paper.IET2014.execute:main',
        'iet2014_evaluate.py  = xfacereclib.paper.IET2014.evaluate:main',
        'iet2014_categorical.py  = xfacereclib.paper.IET2014.categorical:main',
        'iet2014_plot.py  = xfacereclib.paper.IET2014.plot:main',
      ],

      # register the particular databases as resources of the FaceRecLib
      # so that they can be used on command line
      'facereclib.database': [
        'c-scface-combined     = xfacereclib.paper.IET2014.database_scface:combined',
        'c-scface-close        = xfacereclib.paper.IET2014.database_scface:close',
        'c-scface-medium       = xfacereclib.paper.IET2014.database_scface:medium',
        'c-scface-far          = xfacereclib.paper.IET2014.database_scface:far',
        'c-mobio               = xfacereclib.paper.IET2014.database_mobio:database',
      ],
    },

    # Classifiers for PyPI
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python :: 2.7',
      'Environment :: Console',
      'Framework :: Buildout',
      'Topic :: Scientific/Engineering',
    ],
)
