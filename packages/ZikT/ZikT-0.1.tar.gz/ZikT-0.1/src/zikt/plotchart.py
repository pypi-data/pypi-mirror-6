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

from zikt.cschart import MultipleValueCoordinateChart
from zikt.helper import Attributes
from zikt.painter import PlotPainter
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable

class PlotChart(MultipleValueCoordinateChart):
	base = Attributes(
		parent=MultipleValueCoordinateChart.base,
		painter=[PlotPainter],
		#
		valuePointLabelAboveString=u"{value}",
		valuePointLabelAboveStyle=u"",
		valuePointLabelBelowString=u"",
		valuePointLabelBelowStyle=u"",
		#
		plotMarks = ["square*"],
		plotMarkStyle = "ziktPlotChartMark",
		additionalPlotMarkStyle = u"mark={mark},mark options={{color={outlineColor}}}",
		#
		lineStyle = u"ziktPlotChartLine",
		additionalLineStyle = u"color={drawColor}"
	)
	presettings =  {
		'base': base,
	}
	
	def __init__(self,preset="base", printComments=True, **kwargs):
		MultipleValueCoordinateChart.__init__(self)
		self.attributes = PlotChart.presettings[preset]
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		

if __name__ == "__main__":
	c =  PlotChart(ordinateLength=6,stackmode = True)
	print c.render(table = FloatTable(getBasicTable()))