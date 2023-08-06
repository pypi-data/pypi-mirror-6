# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime
from setuptools import setup, find_packages

classifiers = """
Development Status :: 4 - Beta
Framework :: Django
Programming Language :: Python
Intended Audience :: Developers
Natural Language :: English
Operating System :: OS Independent
Topic :: Software Development :: Libraries
Topic :: Utilities
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Topic :: Software Development :: Libraries :: Application Frameworks
"""

version = '0.1.1'
url = 'https://github.com/AsymmetricVentures/asym-core'

setup(
	name = 'asymmetricbase.core',
	version = '{}-{}'.format(version, datetime.now().strftime('%Y%m%d%H%M')),
	url = url,
	download_url = '{}/archive/v{}.tar.gz'.format(url, version),
	author = 'Richard Eames',
	author_email = 'reames@asymmetricventures.com',
	packages = find_packages(),
	classifiers = list(filter(None, classifiers.split('\n'))),
	namespace_packages = ['asymmetricbase'],
	
	license = 'GPLv2',
	description = 'Core utilities for Asymmeric Base Framework',
	
	install_requires = (
		'django>=1.4.5',
		'jinja2>=2.7',
		'pytz',  # most recent
		'south<2.0',
		'hamlpy',  # most recent,
		'Pillow',
		'boto',
		
		'asymmetricbase.fields',
		'asymmetricbase.logging',
		'asymmetricbase.forms',
		'asymmetricbase.testing',
	),
	dependency_links = [
		'https://github.com/AsymmetricVentures/asym-fields.git#egg=asymmetricbase.fields-dev',
		'https://github.com/AsymmetricVentures/asym-logging.git#egg=asymmetricbase.logging-dev',
		'https://github.com/AsymmetricVentures/asym-testing.git#egg=asymmetricbase.testing-dev',
		'https://github.com/AsymmetricVentures/asym-forms.git#egg=asymmetricbase.forms-dev',
	],
	package_dir = {
		'asymmetricbase' : 	'asymmetricbase',
	},
	package_data = {'' : ['*.djhtml']}
)
