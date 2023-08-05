# -*- coding: utf-8 -*-
"""
Screens
-------

Module :mod:`~xrt.backends.raycing.screens` defines a flat screen in the class
:class:`Screen` that intercepts a beam and gives its image.
"""
__author__ = "Konstantin Klementiev"
__date__ = "2 Jan 2014"
import numpy as np
import sources as rs


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
        blo.y[:] /= blo.b
        blo.x[:] -= blo.a * blo.y
        blo.z[:] -= blo.c * blo.y
        blo.y[:] = 0

        if self.compressX:
            blo.x[:] *= self.compressX
        if self.compressZ:
            blo.z[:] *= self.compressZ
        return blo
