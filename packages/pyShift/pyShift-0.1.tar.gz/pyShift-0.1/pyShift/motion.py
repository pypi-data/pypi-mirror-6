# ----------------------------------------------------------------------------
# pyShift - Cartesian Mesh Rigid Motion
#         - see file license.txt
#
import pyShift.Rmatrix as RM

def shift(g1,p0,p1,alpha,trans):
    """Mesh rotation and translation on arbitrary axis.
    g1: the mesh (numpy array)
    p0,p1: two points for the rotation axis definition
    alpha: rotation angle (radian)
    trans: translation (x,y,z) tuple or list or ndarray
    returns g2 a new grid result of motion on g1 (g1 is unchanged)
    rotation is performed first, then translation

    example:

    >>> import pyShift.gengrid_stub
    >>> import pyShift.motion
    >>> g0=pyShift.gengrid_stub.square(3)
    >>> g1=pyShift.motion.shift(g0,(0,0,0),(1,1,1),45.,(0,0,0))
    >>> g1.tolist()[0][0]
    [[0.0], [-0.3330433752167512], [-0.6660867504335024]]

    """
    rmx=RM.rotationMatrix(p0,p1,alpha)
    shp=g1.shape
    g1.shape=(3,shp[1]*shp[2]*shp[3])
    g2=rmx.dot(g1)
    g2[0]+=trans[0]
    g2[1]+=trans[1]
    g2[2]+=trans[2]
    g1.shape=shp
    g2.shape=shp
    return g2

