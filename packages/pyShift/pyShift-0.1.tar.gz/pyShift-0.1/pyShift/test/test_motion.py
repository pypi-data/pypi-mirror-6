# ----------------------------------------------------------------------------
# pyShift - Cartesian Mesh Rigid Motion
#         - see file license.txt
#
import pyShift.gengrid_stub as GGN
import pyShift.motion as MTN
import pyShift.display as DSP
import math
import numpy
import copy

import unittest

class MotionTestCase(unittest.TestCase):
  def setUp(self):
    self.mesh=GGN.parallelepiped(3,5,7)
  def test_00Module(self):
    import pyShift.motion
  def test_01Rotate(self):
    alpha=45*(math.pi/180.)
    p0=(0.0,0.0,0.0)
    p1=(0.0,1.0,0.0)
    trans=(0.0,0.0,0.0)
    g1=MTN.shift(self.mesh,p0,p1,alpha,trans)
    self.assertFalse((g1[0][0]==self.mesh[0][0]).all())
    self.assertTrue((g1[1][0]==self.mesh[1][0]).all())
    self.assertFalse((g1[2][0]==self.mesh[2][0]).all())
  def test_02Translate(self):
    alpha=0.0
    p0=(0.0,0.0,0.0)
    p1=(1.0,0.0,0.0)
    trans=(1.0,0.0,0.0)
    g1=MTN.shift(self.mesh,p0,p1,alpha,trans)
    self.assertTrue((g1[0][0]==(self.mesh[0][0]+1)).all())
    self.assertTrue((g1[1][0]==self.mesh[1][0]).all())
    self.assertTrue((g1[2][0]==self.mesh[2][0]).all())

