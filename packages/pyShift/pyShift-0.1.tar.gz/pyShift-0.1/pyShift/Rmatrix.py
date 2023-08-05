# ----------------------------------------------------------------------------
# pyShift - Cartesian Mesh Rigid Motion
#         - see file license.txt
#
from math import sqrt,cos,sin
import numpy

def rotationMatrix(p0,p1,alpha):
  """Rotation using arbitrary axis (Rodrigues formula).
  see: http://mathworld.wolfram.com/RodriguesRotationFormula.html
  see: http://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula

  args: p0,p1 two (x,y,z) points that defines the rotation axis
  args: alpha rotatino angle (radian)

  returns the rotation matrix as a 3x3 ndarray
  """
  zvct=[0.0,0.0,0.0]

  p0x=p0[0]
  p0y=p0[1]
  p0z=p0[2]
  p1x=p1[0]
  p1y=p1[1]
  p1z=p1[2]

  # Formule de Rodrigue rotation autour d'un axe quelconque
  norm=sqrt( ((p1x-p0x)*(p1x-p0x))
            +((p1y-p0y)*(p1y-p0y))
            +((p1z-p0z)*(p1z-p0z)))
  x=(p1x-p0x)/norm
  y=(p1y-p0y)/norm
  z=(p1z-p0z)/norm
  cp=cos(alpha)
  sp=sin(alpha)
  cm  = 1-cp
  xs  = x*sp
  ys  = y*sp
  zs  = z*sp
  xC  = x*cm
  yC  = y*cm
  zC  = z*cm
  xyC = x*yC
  yzC = y*zC
  zxC = z*xC

  rot=numpy.array([[x*xC+cp,xyC-zs,zxC+ys],
                   [xyC+zs,y*yC+cp,yzC-xs],
                   [zxC-ys,yzC+xs,z*zC+cp]])

  return rot

