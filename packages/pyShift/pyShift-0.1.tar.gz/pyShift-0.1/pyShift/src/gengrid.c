
#include <stdio.h>
#include "gengrid.h"

int generate(int i,int j,int k,float *x,float *y,float *z)
{
  if (i*j*k==0)
  {
    return ZERO_DIM;
  }
  if ((x==NULL)||(y==NULL)||(z==NULL))
  {
    return BAD_POINTER;
  }
  if (i*j*k>MAX_SIZE)
  {
    return MAX_EXCEEDED;
  }
  gen3d_(&i,&j,&k,x,y,z);
  return STATUS_OK;
}
