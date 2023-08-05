#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed Apr 20 17:32:54 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Basic tests for the error measuring system of bob
"""

import os, sys
import unittest
import numpy
import scipy
import bob
from scipy.stats import norm
#import pkg_resources

from . import Bootstraps
def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

def count(array, value=True):
  """Counts occurrences of a certain value in an array"""
  return list(array == value).count(True)

def save(fname, data):
  """Saves a single array into a file in the 'data' directory."""
  bob.io.Array(data).save(os.path.join('data', fname))

class ErrorTest(unittest.TestCase):
  """Various measure package tests for error evaluation."""

  def test_ROC2DET(self):


    X=numpy.array([(100.0-float(x))/100 for x in range(0, 100)])
    Y=numpy.array([float(x)/100 for x in range(1, 101)])
    nX=numpy.array([norm.ppf(x) for x in X])
    nY=numpy.array([norm.ppf(x) for x in Y])

    firsts=(nX>2).nonzero()
    lasts=(nY>2).nonzero()
    first=firsts[0][-1]+1
    last=lasts[0][0]
    nX=nX[first:last]
    nY=nY[first:last]


    OOUT=Bootstraps.ROC2DETPolar(X,Y)
    OOUT1=Bootstraps.Polar2DET(OOUT)

    f=scipy.interpolate.interp1d(numpy.array(OOUT1[1]),numpy.array(OOUT1[0]),kind='linear',bounds_error=False)
    l_oY=f(nX)
    angle=scipy.spatial.distance.euclidean(nY,l_oY)
    self.assertTrue(angle<= 0.01, 'angle incorrect: expected value{0} actual value{1}'.format(0.01, angle))

