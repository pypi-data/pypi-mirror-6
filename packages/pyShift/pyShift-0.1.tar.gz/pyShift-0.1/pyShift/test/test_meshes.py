# ----------------------------------------------------------------------------
# pyShift - Cartesian Mesh Rigid Motion
#         - see file license.txt
#
import pyShift.gengrid_stub as GGN
import pyShift.motion as MTN
import math
import numpy
import copy

def test_gen():
  """Test mesh generation"""
  g1=GGN.parallelepiped(3,5,7)
  g2=GGN.cube(7)
  g3=GGN.rectangle(3,5)
  g4=GGN.square(5)

def test_gen_ex():
  """Test mesh exceptions"""
  try:
    g1=GGN.parallelepiped(30,50,70)
    assert False
  except Exception, v:
    if (v.args[0]==GGN.E_MAX_EXCEEDED): assert True
    else: assert False
  

