#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Python library ZikT.
# 
# ZikT is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License,
# version 3, as published by the Free Software Foundation.
# 
# ZikT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with ZikT. If not, see <http://www.gnu.org/licenses/>.
'''
@author: Daniel Llin Ferrero
'''


from distutils.core import setup

try:
	with open ("about", "r") as aboutfile:
		about = aboutfile.read()
except:
	about = ""

setup(
	name='ZikT',
	version='0.1',
	description='Python lib for generating TikZ charts from table data',
	author='Daniel Llin Ferrero',
	author_email='texnh@llin.info',
	url='https://pypi.python.org/pypi/zikt/',
	package_dir={'': 'src'},
	packages=['zikt'],
	package_data={'zikt': ['doc/zikt.pdf','latex/zikt.sty']},
	scripts=['scripts/zikt'],
	requires=['unicodecsv'],
	license='LGPL 3  (http://www.gnu.org/licenses/lgpl-3.0)',
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Environment :: Console',
		'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
	],
	long_description = about
)
