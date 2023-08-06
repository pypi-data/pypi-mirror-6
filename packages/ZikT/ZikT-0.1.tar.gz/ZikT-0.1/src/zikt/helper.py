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
import operator
from math import ceil, log10
import copy

class Coord(tuple):
	def __add__(self, other):
		return self.__class__(map(operator.add, self, other))

class Attributes:
	def __init__(self,parent=None,**kwargs):
		self.__content = {}
		if parent != None:
			self.extend(**(parent.getDict()))
		self.extend(**kwargs)
	def extend(self,**attributes):
		self.__content.update(attributes)
		for (k, v) in attributes.iteritems():
			setattr(self, k, v)
	def update(self,**attributes):
		for (k, v) in attributes.iteritems():
			if not k in self.__content.keys():
				raise "Attribute “%s” unknown."%k
			self.__content.update({k:v})
			setattr(self, k, v)
	def getDict(self):
		return self.__content.copy()
	def copy(self):
		return Attributes(**(copy.deepcopy(self.__content)))

class ziktRenderException(BaseException):
	def __init__(self,msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)
class ziktTableException(BaseException):
	def __init__(self,msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

def normalizeAngle(angle):
	return (360 + (angle % 360)) % 360

def angleIsNorthernHemisphere(angle):
	return (normalizeAngle(angle) <= 180)

def angleIsSouthernHemisphere(angle):
	return (normalizeAngle(angle) >= 180)

def angleIsWesternHemisphere(angle):
	return angleIsSouthernHemisphere(angle+90)

def angleIsEasternHemisphere(angle):
	return angleIsNorthernHemisphere(angle+90)

def decimalCeil(v):
	if v >= 1:
		v = ceil(float(v))
		digits=ceil(log10(v+0.1))
		return ceil(v*pow(10,-digits+1))*pow(10,digits-1)
	if v > 0 and v < 1:
		k = 1/v
		zeros=ceil(log10(k+0.1))
		return decimalCeil(v*pow(10,zeros))/pow(10,zeros)
	if v == 0:
		return 0
	else:
		return -decimalCeil(-v)
	
