# -*- coding: utf-8 -*-
"""
Apertures
---------

Module :mod:`apertures` defines rectangular and round apertures and a set of
coplanar rectangular apertures. Rectangular apertures may have one or more
defining edges. For example, a simple obstacle, like a beam stop block would
have one edge, a block of front-end slits would have two edges at 90 degrees to
each other, and a collimator would have all four edges.

The classes have useful methods for getting divergence from the aperture size,
for setting divergence (calculating the aperture size given the divergence) and
for touching the beam with the aperture, i.e. calculating the minimum aperture
size that lets the whole beam through.
"""
__author__ = "Konstantin Klementiev"
__date__ = "8 Jan 2014"
#import copy
#import math
import numpy as np
from .. import raycing
from . import sources as rs


class RectangularAperture(object):
    """Implements an aperture or an obstacle with a combination of horizontal
    and/or vertical edge(s)."""
    def __init__(self, bl, name, x, y, kind, opening, alarmLevel=None):
        """
        *bl*: instance of BeamLine.

        *name*: str.

        *x* and *y*: float. The aperture is assumed to be a vertical plane
        perpendicular to the beam line. *x* and *y* in the general system give
        the intersection point of this plane with the nominal beam line.

        *kind* is any combination (tuple) of 'top', 'bottom', 'left', 'right'.

        *opening* is a list of distances (with sign according to the local
        coordinate system) from the blade edges to the initial beam line
        with the length corresponding to *kind*.

        *alarmLevel*: float or None. Allowed fraction of number of rays
        absorbed at the aperture relative to the number of incident rays.
        """
        self.bl = bl
        bl.slits.append(self)
        self.ordinalNum = len(bl.slits)
        self.lostNum = -self.ordinalNum - 1000
        self.name = name
        self.x = x
        self.y = y
        if isinstance(kind, str):
            self.kind = (kind,)
            self.opening = [opening, ]
        else:
            self.kind = kind
            self.opening = opening
        self.alarmLevel = alarmLevel
#For plotting footprint images with the envelope aperture:
        self.surface = name,
        self.limOptX = [-500, 500]
        self.limOptY = [-500, 500]
        self.limPhysX = self.limOptX
        self.limPhysY = self.limOptY
        self.set_optical_limits()
        self.shape = 'rect'

    def set_optical_limits(self):
        """For plotting footprint images with the envelope aperture."""
        for akind, d in zip(self.kind, self.opening):
            td = float(d)  # otherwise is of type 'numpy.float64' and is
#raycing.is_sequence(d) returns True which is not expected.
            if akind.startswith('l'):
                self.limOptX[0] = td
            elif akind.startswith('r'):
                self.limOptX[1] = td
            elif akind.startswith('b'):
                self.limOptY[0] = td
            elif akind.startswith('t'):
                self.limOptY[1] = td

    def get_divergence(self, source):
        """Gets divergences given the blade openings."""
        sourceToAperture = ((self.x-source.center[0])**2 +
                            (self.y-source.center[1])**2)**0.5
        divergence = []
        for d in self.opening:
            divergence.append(d / sourceToAperture)
        return divergence

    def set_divergence(self, source, divergence):
        """Gets the blade openings given divergences.
        *divergence* is a sequence corresponding to *kind*"""
        sourceToAperture = ((self.x-source.center[0])**2 +
                            (self.y-source.center[1])**2)**0.5
        d = []
        for div in divergence:
            if div > 0:
                sgn = 1
            else:
                sgn = -1
            d.append(div*sourceToAperture + sgn*raycing.accuracyInPosition)
        self.opening = d

    def propagate(self, beam):
        """Assigns the "lost" value to *beam.state* array for the rays
        intercepted by the aperture. The "lost" value is
        ``-self.ordinalNum - 1000.``"""
        good = beam.state > 0
#beam in local coordinates
        lo = rs.Beam(nrays=len(beam.x))
        raycing.global_to_virgin_local(
            self.bl, beam, lo, (self.x, self.y, self.bl.height), good)
        lo.y[good] /= lo.b[good]
        lo.x[good] -= lo.a[good] * lo.y[good]
        lo.z[good] -= lo.c[good] * lo.y[good]
        badIndices = np.zeros(len(beam.x), dtype=np.bool)
        for akind, d in zip(self.kind, self.opening):
            if akind.startswith('l'):
                badIndices[good] = badIndices[good] | (lo.x[good] < d)
            elif akind.startswith('r'):
                badIndices[good] = badIndices[good] | (lo.x[good] > d)
            elif akind.startswith('b'):
                badIndices[good] = badIndices[good] | (lo.z[good] < d)
            elif akind.startswith('t'):
                badIndices[good] = badIndices[good] | (lo.z[good] > d)
        beam.state[badIndices] = self.lostNum

        lo.state[good] = beam.state[good]
        if self.alarmLevel is not None:
            raycing.check_alarm(self, good, beam)
        return lo

    def touch_beam(self, beam):
        """Adjusts the aperture (i.e. sets self.opening) so that it touches the
        *beam*."""
        good = (beam.state == 1) | (beam.state == 2)
#        good = beam.state > 0
#beam in local coordinates
        lo = rs.Beam(nrays=len(beam.x))
        raycing.global_to_virgin_local(
            self.bl, beam, lo, (self.x, self.y, self.bl.height), good)
        lo.y[good] /= lo.b[good]
        if ('left' in self.kind) or ('right' in self.kind):
            lo.x[good] -= lo.a[good] * lo.y[good]
        if ('top' in self.kind) or ('bottom' in self.kind):
            lo.z[good] -= lo.c[good] * lo.y[good]
        locOpening = []
        if good.sum() > 0:
            for akind, d in zip(self.kind, self.opening):
                if akind.startswith('l'):
                    locOpening.append(lo.x[good].min())
                elif akind.startswith('r'):
                    locOpening.append(lo.x[good].max())
                elif akind.startswith('t'):
                    locOpening.append(lo.z[good].max())
                elif akind.startswith('b'):
                    locOpening.append(lo.z[good].min())
                else:
                    continue
        self.opening = locOpening
        self.set_optical_limits()


class SetOfRectangularAperturesOnZActuator(RectangularAperture):
    """Implements a set of coplanar apertures with a Z actuator."""
    def __init__(self, bl, name, x, y, zActuator, apertures, centerZs, dXs,
                 dZs, alarmLevel=None):
        """
        *bl*: instance of BeamLine

        *name*: str.

        *x* and *y*: float.
            The apertures are assumed to be in a vertical plane perpendicular
            to the beam line. *x* and *y* in the general system give the
            intersection point of this plane with the nominal beam line.

        *zActuator*: float.
             The value of zActuator at which the *centerZs* are given.

        *apertures*: sequence of str.
            Names of apertures. The last one must be one of
            'bottom-edge' or 'top-edge'.

        *centerZs*: sequence of float.
            Z coordinates of the aperture centers in in the general system.
            The last one specifies the edge.

        *dXs* and *dZs*: sequence of float.
            Openings in x and z local axes which correspond to
            *apertures[:-1]*.

        *alarmLevel*: float or None.
            allowed fraction of number of rays absorbed at the aperture
            relative to the number of incident rays.
        """
        self.bl = bl
        bl.slits.append(self)
        self.ordinalNum = len(bl.slits)
        self.lostNum = -self.ordinalNum - 1000
        self.name = name
        self.x = x
        self.y = y
        self.zActuator = zActuator
        self.z0 = zActuator
        self.apertures = apertures
        self.centerZs = centerZs
        self.dXs = dXs
        self.dZs = dZs
        self.zlims = None
        self.alarmLevel = alarmLevel
# For plotting footprint images:
        self.surface = self.apertures
        self.limOptX = [0, 0]
        self.limOptY = [0, 0]
        self.limOptX[0] = [-dx*0.5 for dx in dXs]
        self.limOptX[1] = [dx*0.5 for dx in dXs]
        self.limOptX[0].append(-500)
        self.limOptX[1].append(500)
        self.limPhysX = self.limOptX
        self.limPhysY = self.limOptY
        self.shape = 'rect'

    def select_aperture(self, apertureName, targetZ):
        """Updates self.curAperture index and finds dz offset corresponding to
        the requested aperture."""
        ca = self.apertures.index(apertureName)
        self.curAperture = ca
        if ca < len(self.apertures) - 1:
            self.kind = 'left', 'right', 'bottom', 'top'
            dx = self.dXs[ca] * 0.5
            dz = self.dZs[ca] * 0.5
            cz = targetZ - self.bl.height
            self.opening = -dx, dx, cz-dz, cz+dz
            self.zActuator = self.z0 + targetZ - self.centerZs[ca]
        else:
            if self.apertures[-1] == 'top-edge':
                self.kind = 'bottom',
            elif self.apertures[-1] == 'bottom-edge':
                self.kind = 'top',
            else:
                raise ValueError('not "top-edge" nor "bottom-edge"!')
            self.opening = self.centerZs[-1] - self.bl.height,
            self.zActuator = self.z0
        maxHalfdZ = max(self.dZs) * 0.5
        minZ = min(self.centerZs) + self.zActuator - self.z0
        maxZ = max(self.centerZs) + self.zActuator - self.z0
        self.zlims = [min(minZ, targetZ) - self.bl.height - maxHalfdZ,
                      max(maxZ, targetZ) - self.bl.height + maxHalfdZ]
        self.set_optical_limits()

    def set_optical_limits(self):
        """For plotting footprint images with the envelope apertures."""
        addToCz = -self.bl.height + self.zActuator - self.z0
        self.limOptY[0] = \
            [cz + addToCz - dz*0.5 for cz, dz in zip(self.centerZs, self.dZs)]
        self.limOptY[1] = \
            [cz + addToCz + dz*0.5 for cz, dz in zip(self.centerZs, self.dZs)]
        self.limOptY[0].append(self.centerZs[-1] + addToCz)
        self.limOptY[1].append(200)


class RoundAperture(object):
    """Implements a round aperture meant to represent a pipe or a flange."""
    def __init__(self, bl, name, center, r, alarmLevel=None):
        """ The aperture is assumed to be a vertical plane perpendicular
        to the beam line. *center* is a 3D point in the general system.
        *r* is the radius.
        """
        self.bl = bl
        bl.slits.append(self)
        self.ordinalNum = len(bl.slits)
        self.lostNum = -self.ordinalNum - 1000
        self.name = name
        self.center = center
        self.r = r
        self.alarmLevel = alarmLevel
#For plotting footprint images with the envelope aperture:
        self.surface = name,
        self.limOptX = [-r, r]
        self.limPhysX = self.limOptX
        self.set_z(center[2])
        self.shape = 'round'

    def set_z(self, z):
        """For plotting footprint images with the envelope aperture."""
        self.center[2] = z
        cz = z - self.bl.height
        self.limOptY = [cz - self.r, cz + self.r]
        self.limPhysY = self.limOptY

    def get_divergence(self, source):
        """Gets the full divergence given the aperture radius."""
        ss = [a - b for a, b in zip(self.center - source.center)]
        return self.r * 2 * (np.dot(ss, ss) ** -0.5)

    def propagate(self, beam):
        """Assigns the "lost" value to *beam.state* array for the rays
        intercepted by the aperture. The "lost" value is
        ``-self.ordinalNum - 1000.``"""
        good = beam.state > 0
#beam in local coordinates
        lo = rs.Beam(nrays=len(beam.x))
        raycing.global_to_virgin_local(
            self.bl, beam, lo, (self.center[0], self.center[1],
                                self.bl.height), good)
        lo.y[good] /= lo.b[good]
        lo.x[good] -= lo.a[good] * lo.y[good]
        lo.z[good] -= lo.c[good] * lo.y[good]
        lo.y[good] = (lo.x[good]**2 +
                      (lo.z[good]-self.center[2] + self.bl.height)**2)**0.5

        badIndices = np.zeros(len(beam.x), dtype=np.bool)
        badIndices[good] = lo.y[good] > self.r
        beam.state[badIndices] = self.lostNum
        lo.state[good] = beam.state[good]
        if self.alarmLevel is not None:
            raycing.check_alarm(self, good, beam)
        return lo
