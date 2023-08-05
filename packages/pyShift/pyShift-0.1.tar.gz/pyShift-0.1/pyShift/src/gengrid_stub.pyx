"""Cython interface to fortran ```gen3d```

.. py:data:: E_ZERO_DIM

   If one dim is 0 or 1 it fails, ZERO_DIM is returned.
"""

import  numpy as PNPY
cimport numpy as CNPY

cdef extern from "gengrid.h":

   long ZERO_DIM
   long MAX_EXCEEDED
   long STATUS_OK
   long BAD_POINTER
   long MAX_SIZE

   int generate(int i,int j,int k,float *x,float *y,float *z)

E_ZERO_DIM=43
E_MAX_EXCEEDED=91
E_STATUS_OK=0
E_BAD_POINTER=8
E_MAX_SIZE=65535

def square(int i):
  """Creates ```(3,i,i,1)``` mesh

  see :py:func:`parallelepiped`
  """
  cdef int j,k
  k=1
  j=i
  return parallelepiped(i,j,k)

def rectangle(int i, int j):
  """Creates ```(3,i,j,1)``` mesh

  see :py:func:`parallelepiped`
  """
  cdef int k
  k=1
  return parallelepiped(i,j,k)

def cube(int i):
  """Creates ```(3,i,i,i)``` mesh

  see :py:func:`parallelepiped`
  """
  cdef int j,k
  k=i
  j=i
  return parallelepiped(i,j,k)

def parallelepiped(int i,int j,int k):
  """Main function for mesh generation.

  Functions :py:func:`square`, :py:func:`rectangle`, :py:func:`cube`
  use this function with specific ```(i,j,k)```.

  * Args

    - imax: max points in ```i``` plane
    - jmax: max points in ```j``` plane
    - kmax: max points in ```k``` plane

  * Return

    - a ```numpy``` array of size ```(3,i,j,k)``` with first dim for
      ```(x,y,z)``` of each point.

  * Exceptions

    - the return :py:const:`E_STATUS_OK` comes from the fortran
      function :py:func:`generate` and indicates no error.
    - :py:const:`E_ZERO_DIM` is the returned exception if one dim is 
      zero or 1.
    - :py:const:`MAX_EXCEEDED` is raised if the number of points is
      greater than 65535
  """   
  cdef CNPY.ndarray x,y,z
  cdef int gridsize,status
  gridsize=i*j*k
  x=PNPY.ones((gridsize,),dtype='f',order='F')
  y=PNPY.ones((gridsize,),dtype='f',order='F')
  z=PNPY.ones((gridsize,),dtype='f',order='F')
  status=generate(i,j,k,<float*>x.data,<float*>y.data,<float*>z.data)
  if (status!=E_STATUS_OK): raise Exception, status
  r=PNPY.array((x,y,z))
  r.shape=(3,i,j,k)
  return r


