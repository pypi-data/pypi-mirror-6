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

import unittest
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable
from zikt.stackedbarchart import StackedBarChart
from zikt.cs import TikZCoordinateSystem

class TableTests(unittest.TestCase):
    
    def test_noFailureOnAbscissaLengthSpecified(self):
        table = FloatTable(getBasicTable())
        chart = StackedBarChart(
#                alongsideOrdinateLabelString = 'work left',
#                outerOrdinateLabelString = 'SP',
#                lowestLabelString = '{colHeader}',
                abscissaLength = 10,
#                additionalLowestLabelStyle = 'font=\\scriptsize, rotate=90, anchor=east'
        )
        _ = chart.render(table)