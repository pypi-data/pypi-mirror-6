# ----------------------------------------------------------------------------
# pyShift - Cartesian Mesh Rigid Motion
#         - see file license.txt
#
import pyShift.gengrid_stub as GGN
import pyShift.motion as MTN
import math
import numpy
import copy

def asWireSurf(g):
  """Takes a Mesh as arg and returns the boundary surfaces.
  return is a tuple (l,x,y,z) with **l** the number of points
  and **x**,**y**,**z** lists of x,y and z for each point.
  """
  shp=g.shape
  lx=[]
  ly=[]
  lz=[]
  (c,i,j,k)=shp
  for ix in xrange(i):
    lx+=[(g[0,ix, 0,  0],  g[0,ix, 0,  k-1])]
    ly+=[(g[1,ix, 0,  0],  g[1,ix, 0,  k-1])]
    lz+=[(g[2,ix, 0,  0],  g[2,ix, 0,  k-1])]
    lx+=[(g[0,ix, 0,  0],  g[0,ix, j-1,0  ])]
    ly+=[(g[1,ix, 0,  0],  g[1,ix, j-1,0  ])]
    lz+=[(g[2,ix, 0,  0],  g[2,ix, j-1,0  ])]
    lx+=[(g[0,ix, j-1,0],  g[0,ix, j-1,k-1])]
    ly+=[(g[1,ix, j-1,0],  g[1,ix, j-1,k-1])]
    lz+=[(g[2,ix, j-1,0],  g[2,ix, j-1,k-1])]
    lx+=[(g[0,ix, 0,  k-1],g[0,ix, j-1,k-1])]
    ly+=[(g[1,ix, 0,  k-1],g[1,ix, j-1,k-1])]
    lz+=[(g[2,ix, 0,  k-1],g[2,ix, j-1,k-1])]
  for jx in xrange(j):
    lx+=[(g[0,0,  jx, 0],  g[0,0,  jx, k-1])]
    ly+=[(g[1,0,  jx, 0],  g[1,0,  jx, k-1])]
    lz+=[(g[2,0,  jx, 0],  g[2,0,  jx, k-1])]
    lx+=[(g[0,0,  jx, 0],  g[0,i-1,jx, 0  ])]
    ly+=[(g[1,0,  jx, 0],  g[1,i-1,jx, 0  ])]
    lz+=[(g[2,0,  jx, 0],  g[2,i-1,jx, 0  ])]
    lx+=[(g[0,0,  jx, k-1],g[0,i-1,jx, k-1])]
    ly+=[(g[1,0,  jx, k-1],g[1,i-1,jx, k-1])]
    lz+=[(g[2,0,  jx, k-1],g[2,i-1,jx, k-1])]
    lx+=[(g[0,i-1,jx, 0],  g[0,i-1,jx, k-1])]
    ly+=[(g[1,i-1,jx, 0],  g[1,i-1,jx, k-1])]
    lz+=[(g[2,i-1,jx, 0],  g[2,i-1,jx, k-1])]
  for kx in xrange(k):
    lx+=[(g[0,0,  0,  kx], g[0,i-1,0,  kx])]
    ly+=[(g[1,0,  0,  kx], g[1,i-1,0,  kx])]
    lz+=[(g[2,0,  0,  kx], g[2,i-1,0,  kx])]
    lx+=[(g[0,0,  0,  kx], g[0,0,  j-1,kx])]
    ly+=[(g[1,0,  0,  kx], g[1,0,  j-1,kx])]
    lz+=[(g[2,0,  0,  kx], g[2,0,  j-1,kx])]
    lx+=[(g[0,0,  j-1,kx], g[0,i-1,j-1,kx])]
    ly+=[(g[1,0,  j-1,kx], g[1,i-1,j-1,kx])]
    lz+=[(g[2,0,  j-1,kx], g[2,i-1,j-1,kx])]
    lx+=[(g[0,i-1,0,  kx], g[0,i-1,j-1,kx])]
    ly+=[(g[1,i-1,0,  kx], g[1,i-1,j-1,kx])]
    lz+=[(g[2,i-1,0,  kx], g[2,i-1,j-1,kx])]
  return (len(lx),lx,ly,lz)

def show(grids):
  """Calls matplotlib and displays the grids.
  Arg is a list of grids, each is pre-processed to get boundary surfaces"""
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.axis('equal')
  for g in grids:
    gc=numpy.random.rand(3,1)
    (n,lx,ly,lz)=asWireSurf(g)
    for ln in xrange(n):
      plt.plot(lx[ln],ly[ln],lz[ln],color=gc,marker='None',linestyle='-')
  plt.show()

