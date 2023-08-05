#!/usr/bin/env python

#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@lpsc.in2p3.fr
#
# Version : 1.0.0 beta (2013)
#
#############################################################################

VERSION = '1.0.0'

#############################################################################

try:
	from setuptools import setup

except ImportError:
	from distutils.core import setup

#############################################################################

setup(
	name = 'jsonv',
	version = VERSION,
	author = 'Jerome Odier',
	author_email = 'jerome.odier@lpsc.in2p3.fr',
	description = 'JSON validator with EBNF grammar',
	url = 'https://bitbucket.org/jodier/jsonv/',
	download_url = 'https://bitbucket.org/jodier/jsonv/get/master.tar.gz',
	license = 'CeCILL-C',
	packages = ['jsonv'],
	package_data = {'jsonv': ['*.txt']}
)

#############################################################################
