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

import re

class TikZRenderer():
	# TODO: low : add comments to TikZ output everywhere
	def printComment(self, prefix,comment,outputlist):
		if self.printComments:
			s = re.sub(ur'^', prefix+u"% ", (u"-" * 80)+u"\n"+comment+u"\n"+(u"-" * 80), flags=re.M)
			outputlist.append(s)