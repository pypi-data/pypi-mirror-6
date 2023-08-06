#!/usr/bin/env python

#############################################################################
# Author  : Jerome ODIER, Jerome FULACHIER, Fabian LAMBERT, Solveig Albrand
#
# Email   : jerome.odier@lpsc.in2p3.fr
#           jerome.fulachier@lpsc.in2p3.fr
#           fabian.lambert@lpsc.in2p3.fr
#           solveig.albrand@lpsc.in2p3.fr
#
#############################################################################

try:
	from setuptools import setup

except ImportError:
	from distutils.core import setup

#############################################################################

setup(
	name = 'pyAMI_nedm',
	version = '5.0.0',
	author = 'Jerome Odier',
	author_email = 'jerome.odier@cern.ch',
	description = 'Python ATLAS Metadata Interface (pyAMI) for nEDM',
	url = 'https://bitbucket.org/jodier/pyami_nedm',
	license = 'CeCILL-C',
	packages = ['nedm'],
	package_data = {'': ['README.md', '*.txt'], 'nedm': ['*.txt']},
	scripts = ['ami_nedm'],
	install_requires = ['pyAMI_core']
)

#############################################################################
