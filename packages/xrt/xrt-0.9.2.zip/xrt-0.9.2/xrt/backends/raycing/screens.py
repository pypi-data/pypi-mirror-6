# -*- coding: utf-8 -*-
"""
Screens
-------

Module :mod:`~xrt.backends.raycing.screens` defines a flat screen in the class
:class:`Screen` that intercepts a beam and gives its image.
"""
__author__ = "Konstantin Klementiev"
__date__ = "8 Jan 2014"
import numpy as np
from .. import raycing
from . import sources as rs
from . import materials as rm


class Screen(object):
    def __init__(self, bl, name, center=[0, 0, 0], x='auto', z='auto',
                 compressX=None, compressZ=None):
        """
        *bl*: instance of :class:`~xrt.backends.raycing.BeamLine`.

        *name*: str.

        *center*: tuple of 3 floats, is a 3D point in the global system.

        *x, z*: 3-tuples or 'auto'. Normalized 3D vectors in the global system
        which determine the local x and z axes lying in the screen plane. If
        *x* is 'auto', it is horizontal and perpendicular to the beam line.
        If *z* is 'auto', it is vertical.

        *compressX, compressZ* are multiplicative compression coefficients for
        the corresponding axes.
        """
        self.name = name
        self.bl = bl
        bl.screens.append(self)
        self.ordinalNum = len(bl.screens)
        self.center = center
        self.set_orientation(x, z)
        self.compressX = compressX
        self.compressZ = compressZ

    def set_orientation(self, x=None, z=None):
        """Determines the local x, y and z in the global system."""
        if x == 'auto':
            self.x = self.bl.cosAzimuth, -self.bl.sinAzimuth, 0.
        elif x is not None:
            self.x = x
        if z == 'auto':
            self.z = 0., 0., 1.
        elif z is not None:
            self.z = z
        assert np.dot(self.x, self.z) == 0, 'x and z must be orthogonal!'
        self.y = np.cross(self.z, self.x)

    def expose(self, beam):
        """Exposes the screen to the beam. *beam* is in global system, the
        returned beam is in local system of the screen and represents the
        desired image."""
        blo = rs.Beam(copyFrom=beam, withNumberOfReflections=True)  # local
        blo.x[:] = beam.x[:] - self.center[0]
        blo.y[:] = beam.y[:] - self.center[1]
        blo.z[:] = beam.z[:] - self.center[2]
        xyz = blo.x, blo.y, blo.z
        blo.x[:], blo.y[:], blo.z[:] = \
            sum(c*b for c, b in zip(self.x, xyz)),\
            sum(c*b for c, b in zip(self.y, xyz)),\
            sum(c*b for c, b in zip(self.z, xyz))
        abc = beam.a, beam.b, beam.c
        blo.a[:], blo.b[:], blo.c[:] = \
            sum(c*b for c, b in zip(self.x, abc)),\
            sum(c*b for c, b in zip(self.y, abc)),\
            sum(c*b for c, b in zip(self.z, abc))

#*** if path at the screen is needed *******
#        maxa = np.max(abs(blo.a))
#        maxb = np.max(abs(blo.b))
#        maxc = np.max(abs(blo.c))
#        maxMax = max(maxa, maxb, maxc)
#        if maxMax == maxa:
#            blo.path[:] = -blo.x / blo.a
#        elif maxMax == maxb:
#            blo.path[:] = -blo.y / blo.b
#        else:
#            blo.path[:] = -blo.z / blo.c
#end if path at the screen is needed *******

        blo.y[:] /= blo.b
        blo.x[:] -= blo.a * blo.y
        blo.z[:] -= blo.c * blo.y
        blo.y[:] = 0

        if self.compressX:
            blo.x[:] *= self.compressX
        if self.compressZ:
            blo.z[:] *= self.compressZ
        return blo

    def expose_Kirchhoff(self, beamOEin, oe, beamOEglo, beamOEloc, xloc, zloc):
        n = oe.local_n(beamOEloc.x, beamOEloc.y)
        cosGamma = (beamOEloc.a*n[-3] + beamOEloc.b*n[-2] + beamOEloc.c*n[-1])
#rotate the normal to virgin local system:
        ng = rs.Beam(0)
        ng.a, ng.b, ng.c = n[-3], n[-2], n[-1]
#        print 'ncos', np.degrees(np.arccos(ng.c))
        raycing.rotate_beam(ng, way=-1, pitch=oe.pitch, roll=oe.roll +
                            oe.positionRoll, yaw=oe.yaw, skip_xyz=True)
#        print 'ncos', np.degrees(np.arccos(ng.c))
#rotate the normal from virgin local to global system:
        a0, b0 = oe.bl.sinAzimuth, oe.bl.cosAzimuth
        if a0 != 0:
            ng.a, ng.b = raycing.rotate_z(ng.a, ng.b, b0, -a0)
        jk = 1j * beamOEglo.E[0] / rm.chbar * 1e7  # [mm^-1]

        blo = rs.Beam(nrays=len(zloc))  # local
        blo.x = np.asarray(xloc)
        blo.z = np.asarray(zloc)
        xglo = (self.center[0] + self.x[0]*blo.x +
                self.z[0]*blo.z)[:, np.newaxis]
        yglo = (self.center[1] + self.x[1]*blo.x +
                self.z[1]*blo.z)[:, np.newaxis]
        zglo = (self.center[2] + self.x[2]*blo.x +
                self.z[2]*blo.z)[:, np.newaxis]
        aglo = self.center[0]
        bglo = self.center[1] - oe.center[1]
        cglo = self.center[2]
#        print 'aglo ', aglo
#        print 'bglo ', bglo
#        print 'cglo ', cglo
#        print 'ncos', np.degrees(np.arccos(ng.c))
        pathAfter = (aglo**2 + bglo**2 + cglo**2)**0.5
        cosAlpha = (aglo*ng.a + bglo*ng.b + cglo*ng.c) / pathAfter
#        print 'pi/2-alpha ', np.degrees(np.arcsin(cosAlpha))

#        print 'beamOEglo.x ', beamOEglo.x.min(), beamOEglo.x.max()
#        print 'beamOEglo.y ', beamOEglo.y.min(), beamOEglo.y.max()
#        print 'beamOEglo.z ', beamOEglo.z.min(), beamOEglo.z.max()
        aglo = xglo - beamOEglo.x
        bglo = yglo - beamOEglo.y
        cglo = zglo - beamOEglo.z
#        print 'aglo ', aglo.min(), aglo.max()
#        print 'bglo ', bglo.min(), bglo.max()
#        print 'cglo ', cglo.min(), cglo.max()
        pathAfter = (aglo**2 + bglo**2 + cglo**2)**0.5
        cosAlpha = (aglo*ng.a + bglo*ng.b + cglo*ng.c) / pathAfter
#        print 'pi/2-alpha ', np.degrees(np.arcsin(cosAlpha.min())),\
#            np.degrees(np.arcsin(cosAlpha.max()))
        path = beamOEloc.path + pathAfter
# averaged path:
        blo.path = np.sum(path, axis=1) / path.shape[1]
        c = (cosGamma+cosAlpha) * np.exp(jk*path) / (beamOEin.Jss+beamOEin.Jpp)
        blo.fieldKirchhoffS = np.sum(c * beamOEloc.Jss**0.5, axis=1)
        blo.fieldKirchhoffP = np.sum(c * beamOEloc.Jpp**0.5, axis=1)
        blo.fieldKirchhoffN = np.sum(c, axis=1)
        blo.Jss[:] = abs(blo.fieldKirchhoffS)**2
        blo.Jpp[:] = abs(blo.fieldKirchhoffP)**2
        blo.E[:] = beamOEglo.E[0]
        blo.state[:] = 1
#        raise
        return blo
