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

import sys
import csv

class CSV:
	def __init__(self,delimiter=None,quotechar=None):
		self.delimiter = delimiter
		self.quotechar = quotechar
			
	def render(self,table):
		array = table.getTableArray()
		writer = csv.writer(sys.stdout)
		for item in array:
			writer.writerow(item)
		