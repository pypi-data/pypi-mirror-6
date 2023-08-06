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

from __future__ import division
from zikt.cschart import MultipleValueCoordinateChart

#TODO:high: test painters with tables containing significant null value patterns

def getLabelNode(coord, name,attributeDict,renderer,orientation=None):
	style = renderer.attributeDict[name+"Style"]
	string = renderer.attributeDict[name+"String"]
	if style != None and string != None and string != "":
		string = string.format(**attributeDict)
		style = style.format(**attributeDict)
		if orientation  == None:
			orientationStyle = ""
		else:
			orientationStyle = renderer.getStyle('orientedLabelStyle' + orientation) + ","
		return "\\path ({c}) node[{orientationStyle}{style}] {{{label}}};".format(
			c=coord,
			orientationStyle=orientationStyle,
			style=style,
			label=string
		)
	else:
		return None
	##
##
		
class PlotPainter():
	@staticmethod
	def paint(renderer,table,labelTable,rowIndex):
		lineResult = []
		markResult = []
		labelResult = []
		lastCoord=None
		for colIndex in range(table.getColCount()):
			if table.getCell(colIndex,rowIndex) == None:
				continue
			coord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex)
			formatDict = renderer.getCellDict(colIndex,rowIndex,table,labelTable)
			formatDict.update({
				'mark' : renderer.getRowAttribute(rowIndex,'plotMarks'),
			})
			# the label above
			labelAbove = getLabelNode(coord, "valuePointLabelAbove", formatDict, renderer, orientation = 'Above')
			if labelAbove != None:
				labelResult.append(labelAbove)
			# the label below
			labelBelow = getLabelNode(coord, "valuePointLabelBelow", formatDict, renderer, orientation = 'Below')
			if labelBelow != None:
				labelResult.append(labelBelow)
			# the plot marks
			if renderer.attributes.plotMarkStyle != None:
				markStyle = (renderer.attributes.plotMarkStyle + ", " + renderer.attributes.additionalPlotMarkStyle).format(**dict(formatDict.items()))
				markResult.append("\\path[{style}] plot coordinates {{({c})}};".format(c=coord, style=markStyle))
			# the plot line
			if renderer.attributes.lineStyle != None:
				lineStyle = (renderer.attributes.lineStyle + ", " + renderer.attributes.additionalLineStyle).format(**dict(formatDict.items()))
				if lastCoord !=None:
					lineResult.append("\path[{style}] ({lastC}) -- ({c});".format(lastC=lastCoord, c=coord, style=lineStyle))
			# for the next iteration... :)			
			lastCoord = coord
			##
		return '\n'.join(['\n'.join(lineResult),'\n'.join(markResult),'\n'.join(labelResult)])
		##

class BarPainter:
	@staticmethod
	def paint(renderer,table,labelTable,rowIndex):
		if rowIndex == 0:
			return ""
		barResult = []
		labelResult = []
		for colIndex in range(table.getColCount()):
			if table.getCell(colIndex,rowIndex) == None:
				continue
			##
			coord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex)
			lowerCoord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex-1)
			formatDict = renderer.getCellDict(colIndex,rowIndex,table,labelTable,designOffset=-1)
			# the bar
			barStyle = (renderer.attributes.barStyle + "," + renderer.attributes.additionalBarStyle).format(**formatDict)
			offset = (renderer.attributes.abscissaTickDelta * renderer.attributes.barWidthRatio) / 2
			v1 = renderer.tcoord(renderer.transformTikZVector(-offset,0))
			v2 = renderer.tcoord(renderer.transformTikZVector(offset,0))
			
			barResult.append(
				"\\path[coordinate] ({c2}) ++{v2} coordinate(t);\\path[{style}] ({c1}) ++{v1} rectangle (t);".format(
					style=barStyle,
					c1=coord,
					c2=lowerCoord,
					v1=v1,
					v2=v2,
					offset=offset,
					unit=renderer.attributes.baseunit,
				)
			)
		return '\n'.join(['\n'.join(barResult),'\n'.join(labelResult)])