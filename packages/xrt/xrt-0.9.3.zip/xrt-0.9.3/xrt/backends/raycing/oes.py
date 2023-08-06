# -*- coding: utf-8 -*-
"""
Optical elements
----------------

Module :mod:`~xrt.backends.raycing.oes` defines a generic optical element in
class :class:`OE`. Its methods serve mainly for propagating the beam downstream
the beamline. This is done in the following sequence: for each ray transform
the beam from global to local coordinate system, find the intersection point
with the OE surface, define the corresponding state of the ray, calculate the
new direction, rotate the coherency matrix to the local s-p basis, calculate
reflectivity or transmittivity and apply it to the coherency matrix, rotate the
coherency matrix back and transform the beam from local to the global
coordinate system.

Module :mod:`~xrt.backends.raycing.oes` defines also several other optical
elements with various geometries.
"""
__author__ = "Konstantin Klementiev", "Roman Chernikov"
__date__ = "23 Apr 2014"

#import copy
#import gc
import numpy as np
import matplotlib as mpl
from .. import raycing
from . import sources as rs
from . import materials as rm
from . import stages as rst

_DEBUG = False


class OE(object):
    """The main base class for an optical element. It implements a generic flat
    mirror.
    """
    def __init__(
        self, bl, name, center=[0, 0, 0], pitch=0, roll=0, yaw=0,
        positionRoll=0., alarmLevel=None, surface=None, material=None,
        alpha=None,
        limPhysX=(-raycing.maxHalfSizeOfOE, raycing.maxHalfSizeOfOE),
        limOptX=None,
        limPhysY=(-raycing.maxHalfSizeOfOE, raycing.maxHalfSizeOfOE),
        limOptY=None,
        isParametric=False, shape='rect', order=None,
            shouldCheckCenter=False):
        """
        *bl*: instance of :class:`~xrt.backends.raycing.BeamLine`

        *name*: str

        *center*: 3-sequence of floats
            3D point in global system.

        *pitch, roll, yaw*: floats.
            Rotations Rx, Ry, Rz, correspondingly, defined in the local system.

        *positionRoll*: float
            A global roll used for putting the OE upside down (=math.pi) or
            at horizontal deflection (=[-]math.pi/2).

        *alarmLevel*: float or None
            Allowed fraction of incident rays to be absorbed by OE.

        *surface* None or sequence of str
            If there are several optical surfaces, like metalized stripes on
            a mirror, these are listed here as names; then also the optical
            limits *must* all be given by sequences of the same length if
            not None.

        *material* None or sequence of objects with :meth:`get_amplitude` or
            :meth:`get_refraction_index` method. If not None, must correspond
            to *surface*.

        *alpha* Asymmetry angle for a crystal OE (rad).

        *limPhysX* and *limPhysY*: (*min*, *max*) where *min*, *max* are
            floats or sequences of floats
            Physical dimension = local coordinate of the corresponding edge.
            Can be given by sequences of the length of *surface*. You do not
            have to provide the limits, although they may help in finding
            intersection points, especially for (strongly) curved surfaces.

        *limOptX* and *limOptY*: (*min*, *max*) where *min*, *max* are
            floats or sequences of floats
            Optical dimension = local coordinate of the corresponding edge.
            Useful when the optical surface is smaller than the whole
            surface, e.g. for metalized stripes on a mirror.

        *isParametric*: bool
            If True, the OE is defined by parametric equations rather than by
            z(*x*, *y*) function. For example, parametric representation is
            useful for description of closed surfaces, like capillaries.
            The user must supply the transformation functions
            :meth:`param_to_xyz` and :meth:`xyz_to_param` between local
            (*x*, *y*, *z*) and (*s*, *phi*, *r*) and the parametric surface
            *local_r* dependent on (*s*, *phi*). The exact meaning of these
            three new parameters is up to the user because this meaning is
            self-contained in the above mentioned user-supplied functions. For
            example, these can be viewed as cylindrical-like coordinates, where
            *s* is a running coordinate on a 3D axial curve, *phi* and *r* are
            polar coordinates in planes normal to the axial curve and crossing
            that curve at point *s*. Class :class:`SurfaceOfRevolution` gives
            an example of the transformation functions and represents a useful
            kind of parametric surface.

            The methods :meth:`local_n` (surface normal) and :meth:`local_g`
            (grating vector, if used for this OE) return 3D vectors in local
            xyz space but now the two input coordinate parameters are *s* and
            *phi*.

            The limits (*limPhysX*, *limOptX*) and (*limPhysY*, *limOptY*)
            still define, correspondingly, the limits in local *x* and *y*.

            The local beams (footprints) will additionally contain *s*, *phi*
            and *r* arrays.

        *shape*: str or list of [x, y] pairs
            The shape of OE. Supported: 'rect', 'round' or a list of [x, y]
            pairs for an arbitrary shape.

        *order*: int or sequence of int
            The order(s) of grating, FZP or Bragg-Fresnel diffraction.

        *shouldCheckCenter*: bool
            if True, invokes *checkCenter* method for checking whether the oe
            center lies on the original beam line. *checkCenter* implies
            vertical deflection and ignores any difference in height. You
            should override this method for OEs of horizontal deflection.
        """
        self.bl = bl
        bl.oes.append(self)
        self.ordinalNum = len(bl.oes)
        self.lostNum = -self.ordinalNum
        self.name = name
        self.center = center
        if shouldCheckCenter:
            self.checkCenter()

        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.positionRoll = positionRoll
        self.alarmLevel = alarmLevel

        self.surface = surface
        self.material = material
        self.set_alpha(alpha)
        self.curSurface = 0
        self.dx = 0
        self.limPhysX = limPhysX
        self.limPhysY = limPhysY
        self.limOptX = limOptX
        self.limOptY = limOptY
        self.isParametric = isParametric
        self.shape = shape
        self.order = 1 if order is None else order
        self.get_surface_limits()

    def set_alpha(self, alpha):
        """Sets the asymmetry angle *alpha* for a crystal OE. It calculates
        cos(alpha) and sin(alpha) which are then used for rotating the normal
        to the crystal planes."""
        self.alpha = alpha
        if alpha is None:
            return
        self.cosalpha = np.cos(alpha)
        self.sinalpha = np.sin(alpha)

    def checkCenter(self, misalignmentTolerated=raycing.misalignmentTolerated):
        """Checks whether the oe center lies on the original beam line. If the
        misalignment is bigger than *misalignmentTolerated*, a warning is
        issued. This implementation implies vertical deflection and ignores any
        difference in height. You should override this method for OEs of
        horizontal deflection."""
        a = self.bl.sinAzimuth
        b = self.bl.cosAzimuth
        d = b * (self.center[0]-self.bl.sources[0].center[0])\
            - a * (self.center[1]-self.bl.sources[0].center[1])
        if abs(d) > misalignmentTolerated:
            print "Warning: %s is off the beamline by %s" % (self.name, d)
            xc = a * b * (self.center[1]-self.bl.sources[0].center[1])\
                + self.bl.sources[0].center[0] * b**2 + self.center[0] * a**2
            yc = a * b * (self.center[0]-self.bl.sources[0].center[0])\
                + self.bl.sources[0].center[1] * a**2 + self.center[1] * b**2
            print "suggested xc, yc: ", xc, yc

    def get_orientation(self):
        """To be overridden. Should provide pitch, roll, yaw, height etc. given
        other, possibly newly added variables. Used in conjunction with the
        classes in :mod:`stages`."""
        pass

    def local_z(self, x, y):
        """Determines the surface of OE at (*x*, *y*) position. Typically is
        overridden in the derived classes. Must return either a scalar or an
        array of the length of *x* and *y*."""
        return 0  # just flat

    def local_z_distorted(self, x, y):
        return

    def local_g(self, x, y, rho=100.):
        """For a grating, gives the local reciprocal groove vector (without
        2pi!) in 1/mm at (*x*, *y*) position. The vector must lie on the
        surface, i.e. be orthogonal to the normal. Typically is overridden in
        the derived classes. Returns a 3-tuple of floats or of arrays of the
        length of *x* and *y*."""
        return 0, rho, 0  # constant line spacing along y

    def local_n(self, x, y):
        """Determines the normal vector of OE at (*x*, *y*) position. Typically
        is overridden in the derived classes. If OE is an asymmetric crystal,
        *local_n* must return 2 normals: the 1st one of the atomic planes and
        the 2nd one of the surface. Note the order!

        If *isParametric* in the constructor is True, :meth:`local_n` still
        returns 3D vector(s) in local xyz space but now the two input
        coordinate parameters are *s* and *phi*.

        The result is a 3-tuple or a 6-tuple. Each element is either a scalar
        or an array of the length of *x* and *y*."""
        # just flat:
        a = 0.  # -dz/dx
        b = 0.  # -dz/dy
        c = 1.
#        norm = (a**2 + b**2 + c**2)**0.5
#        a, b, c = a/norm, b/norm, c/norm
        if self.alpha:
            bAlpha, cAlpha = \
                raycing.rotate_x(b, c, self.cosalpha, -self.sinalpha)
            return [a, bAlpha, cAlpha, a, b, c]
        else:
            return [a, b, c]

    def local_n_distorted(self, x, y):
        """Angles d_pitch and d_roll."""
        return

    _h = 20.

    def xyz_to_param(self, x, y, z):  # for flat mirror as example
        r = np.sqrt(x**2 + (self._h-z)**2)
        return y, np.arcsin(x / r), r  # s, phi, r

    def param_to_xyz(self, s, phi, r):  # for flat mirror as example
        return r*np.sin(phi), s, self._h - r*np.cos(phi)  # x, y, z

    def local_r(self, s, phi):  # for flat mirror as example
        """Determines the surface of OE at (*s*, *phi*) position. Used when
        *isParametric* in the constructor is True. Typically is overridden in
        the derived classes. Must return either a scalar or an array of the
        length of *s* and *phi*."""
        return self._h / np.cos(phi)

    def local_r_distorted(self, x, y):
        return

    def find_dz(
            self, local_f, t, x0, y0, z0, a, b, c, invertNormal, derivOrder=0):
        """Returns the z or r difference (in the local system) between the ray
        and the surface. Used for finding the intersection point."""
        x = x0 + a*t
        y = y0 + b*t
        z = z0 + c*t
        if derivOrder == 0:
            if self.isParametric:
                if local_f is None:
                    local_f = self.local_r
                diffSign = -1
            else:
                if local_f is None:
                    local_f = self.local_z
                diffSign = 1
        else:
            if local_f is None:
                local_f = self.local_n

        if self.isParametric:  # s, phi, r =
            x, y, z = self.xyz_to_param(x, y, z)
        surf = local_f(x, y)  # z or r
        if derivOrder == 0:
            if surf is None:  # lost
                surf = np.zeros_like(z)
            ind = np.isnan(surf)
            if ind.sum() > 0:
                if _DEBUG:
                    print '{0} NaNs in the surface!!!'.format(ind.sum())
#                    print t[ind]
                surf[ind] = 0
            dz = (z - surf) * diffSign * invertNormal
        else:
            if surf is None:  # lost
                surf = 0, 0, 1
            dz = (a*surf[-3] + b*surf[-2] + c*surf[-1]) * invertNormal
        return dz, x, y, z

    def find_intersection(self, local_f, t1, t2, x, y, z, a, b, c,
                          invertNormal, derivOrder=0):
        """Finds the ray parameter *t* at the intersection point with the
        surface. Requires *t1* and *t2* as input bracketing. The ray is
        determined by its origin point (*x*, *y*, *z*) and its normalized
        direction (*a*, *b*, *c*). *t* is then the distance between the origin
        point and the intersection point. *derivOrder* tells if minimized is
        the z-difference (=0) or its derivative (=1)."""
#        if _DEBUG:
#            print 'find_intersection entered'
        dz1, x1, y1, z1 = self.find_dz(
            local_f, t1, x, y, z, a, b, c, invertNormal, derivOrder)
        dz2, x2, y2, z2 = self.find_dz(
            local_f, t2, x, y, z, a, b, c, invertNormal, derivOrder)
        tMin = max(t1.min(), 0)
        tMax = t2.max()
        ind1 = dz1 <= 0  # lost rays; for them the solution is t1
        ind2 = dz2 >= 0  # over rays; for them the solution is t2
        dz2[ind1 | ind2] = 0
        t2[ind1] = t1[ind1]
        x2[ind1] = x1[ind1]
        y2[ind1] = y1[ind1]
        z2[ind1] = z1[ind1]
        ind = ~(ind1 | ind2)  # good rays
        if abs(dz2).max() > abs(dz1).max()*20:
            t2, x2, y2, z2, numit = self._use_Brent_method(
                local_f, t1, t2, x, y, z, a, b, c, invertNormal, derivOrder,
                dz1, dz2, tMin, tMax, x2, y2, z2, ind)
        else:
            t2, x2, y2, z2, numit = self._use_my_method(
                local_f, t1, t2, x, y, z, a, b, c, invertNormal, derivOrder,
                dz1, dz2, tMin, tMax, x2, y2, z2, ind)
        if numit == raycing.maxIteration and _DEBUG:
            nn = ind.sum()
            print 'maxIteration is reached for {0} ray{1}!!!'.format(
                nn, 's' if nn > 1 else '')
#            print 'min deviation = {0}'.format(dz2[ind])
        if _DEBUG:
            print 'numit=', numit
        return t2, x2, y2, z2

    def _use_my_method(
        self, local_f, t1, t2, x, y, z, a, b, c, invertNormal, derivOrder,
            dz1, dz2, tMin, tMax, x2, y2, z2, ind):
        numit = 2
        while (ind.sum() > 0) and (numit < raycing.maxIteration):
            t = t1[ind]
            dz = dz1[ind]
            t1[ind] = t2[ind]
            dz1[ind] = dz2[ind]
            t2[ind] = t - (t1[ind]-t) * dz / (dz1[ind]-dz)
            swap = t2[ind] < tMin
            t2[np.where(ind)[0][swap]] = tMin
            swap = t2[ind] > tMax
            t2[np.where(ind)[0][swap]] = tMax
            dz2[ind], x2[ind], y2[ind], z2[ind] = self.find_dz(
                local_f, t2[ind], x[ind], y[ind], z[ind],
                a[ind], b[ind], c[ind], invertNormal, derivOrder)
            #swapping using duble slicing:
            swap = np.sign(dz2[ind]) == np.sign(dz1[ind])
            t1[np.where(ind)[0][swap]] = t[swap]
            dz1[np.where(ind)[0][swap]] = dz[swap]
            ind = ind & (abs(dz2) > raycing.zEps)
            numit += 1
#t2 holds the ray parameter at the intersection point
        return t2, x2, y2, z2, numit

    def _use_Brent_method(self, local_f, t1, t2, x, y, z, a, b, c,
                          invertNormal, derivOrder, dz1, dz2, tMin, tMax,
                          x2, y2, z2, ind):
        """Finds the ray parameter *t* at the intersection point with the
        surface. Requires *t1* and *t2* as input bracketing. The rays are
        determined by the origin points (*x*, *y*, *z*) and the normalized
        directions (*a*, *b*, *c*). *t* is then the distance between the origin
        point and the intersection point.

        Uses the classic Brent (1973) method to find a zero of the function
        `dz` on the sign changing interval [*t1*, *t2*]. It is a safe version
        of the secant method that uses inverse quadratic extrapolation. Brent's
        method combines root bracketing, interval bisection, and inverse
        quadratic interpolation.

        A description of the Brent's method can be found at
        http://en.wikipedia.org/wiki/Brent%27s_method.
        """
        swap = abs(dz1[ind]) < abs(dz2[ind])
        if swap.sum() > 0:
            t1[np.where(ind)[0][swap]], t2[np.where(ind)[0][swap]] =\
                t2[np.where(ind)[0][swap]], t1[np.where(ind)[0][swap]]
            dz1[np.where(ind)[0][swap]], dz2[np.where(ind)[0][swap]] =\
                dz2[np.where(ind)[0][swap]], dz1[np.where(ind)[0][swap]]
        t3 = np.copy(t1)  # c:=a
        dz3 = np.copy(dz1)  # f(c)
        t4 = np.zeros_like(t1)  # d
        mflag = np.ones_like(t1, dtype='bool')
        numit = 2
        ind = ind & (abs(dz2) > raycing.zEps)
        while (ind.sum() > 0) and (numit < raycing.maxIteration):
            xa, xb, xc, xd = t1[ind], t2[ind], t3[ind], t4[ind]
            fa, fb, fc = dz1[ind], dz2[ind], dz3[ind]
            mf = mflag[ind]
            xs = np.empty_like(xa)
            inq = (fa != fc) & (fb != fc)
            if inq.sum() > 0:
                xai = xa[inq]
                xbi = xb[inq]
                xci = xc[inq]
                fai = fa[inq]
                fbi = fb[inq]
                fci = fc[inq]
                xs[inq] = \
                    xai * fbi * fci / (fai-fbi) / (fai-fci) + \
                    fai * xbi * fci / (fbi-fai) / (fbi-fci) + \
                    fai * fbi * xci / (fci-fai) / (fci-fbi)
            inx = ~inq
            if inx.sum() > 0:
                xai = xa[inx]
                xbi = xb[inx]
                fai = fa[inx]
                fbi = fb[inx]
                xs[inx] = xbi - fbi * (xbi-xai) / (fbi-fai)

            cond1 = ((xs < (3*xa + xb) / 4.) & (xs < xb) |
                     (xs > (3*xa + xb) / 4.) & (xs > xb))
            cond2 = mf & (abs(xs - xb) >= (abs(xb - xc) / 2.))
            cond3 = (~mf) & (abs(xs - xb) >= (abs(xc - xd) / 2.))
            cond4 = mf & (abs(xb - xc) < raycing.zEps)
            cond5 = (~mf) & (abs(xc - xd) < raycing.zEps)
            conds = cond1 | cond2 | cond3 | cond4 | cond5
            xs[conds] = (xa[conds] + xb[conds]) / 2.
            mf = conds

            fs, x2[ind], y2[ind], z2[ind] = self.find_dz(
                local_f, xs, x[ind], y[ind], z[ind], a[ind], b[ind], c[ind],
                invertNormal, derivOrder)
            xd[:] = xc[:]
            xc[:] = xb[:]
            fc[:] = fb[:]
            fafsNeg = ((fa < 0) & (fs > 0)) | ((fa > 0) & (fs < 0))
            xb[fafsNeg] = xs[fafsNeg]
            fb[fafsNeg] = fs[fafsNeg]
            fafsPos = ~fafsNeg
            xa[fafsPos] = xs[fafsPos]
            fa[fafsPos] = fs[fafsPos]
            swap = abs(fa) < abs(fb)
            xa[swap], xb[swap] = xb[swap], xa[swap]
            fa[swap], fb[swap] = fb[swap], fa[swap]
            t1[ind], t2[ind], t3[ind], t4[ind] = xa, xb, xc, xd
            dz1[ind], dz2[ind], dz3[ind] = fa, fb, fc
            mflag[ind] = mf

            ind = ind & (abs(dz2) > raycing.zEps)
            numit += 1
#t2 holds the ray parameter at the intersection point
        return t2, x2, y2, z2, numit

    def get_surface_limits(self):
        """Returns surface_limits."""
        cs = self.curSurface
        self.surfPhysX = self.limPhysX
        if self.limPhysX is not None:
            try:
                if raycing.is_sequence(self.limPhysX[0]):
                    self.surfPhysX = (self.limPhysX[0][cs],
                                      self.limPhysX[1][cs])
            except IndexError:
                pass
        self.surfPhysY = self.limPhysY
        if self.limPhysY is not None:
            try:
                if raycing.is_sequence(self.limPhysY[0]):
                    self.surfPhysY = (self.limPhysY[0][cs],
                                      self.limPhysY[1][cs])
            except IndexError:
                pass
        self.surfOptX = self.limOptX
        if self.limOptX is not None:
            try:
                if raycing.is_sequence(self.limOptX[0]):
                    self.surfOptX = (self.limOptX[0][cs], self.limOptX[1][cs])
            except IndexError:
                pass
        self.surfOptY = self.limOptY
        if self.limOptY is not None:
            try:
                if raycing.is_sequence(self.limOptY[0]):
                    self.surfOptY = (self.limOptY[0][cs], self.limOptY[1][cs])
            except IndexError:
                pass

    def rays_good(self, x, y, is2ndXtal=False):
        """Returns *state* value for a ray with the given intersection point
        (*x*, *y*) with the surface of OE:
        1: good (intersected)
        2: reflected outside of working area ("out"),
        3: transmitted without intersection ("over"),
        -NN: lost (absorbed) at OE#NN - OE numbering starts from 1 !!!
        """
        if is2ndXtal:
            surfPhysX = self.surfPhysX2
            surfPhysY = self.surfPhysY2
            surfOptX = self.surfOptX2
            surfOptY = self.surfOptY2
        else:
            surfPhysX = self.surfPhysX
            surfPhysY = self.surfPhysY
            surfOptX = self.surfOptX
            surfOptY = self.surfOptY

        locState = np.ones(x.size, dtype=np.int)
        if isinstance(self.shape, str):
            if self.shape.startswith('re'):
                if surfOptX is not None:
                    locState[((surfPhysX[0] <= x) & (x < surfOptX[0])) |
                             ((surfOptX[1] <= x) & (x < surfPhysX[1]))] = 2
                if surfOptY is not None:
                    locState[((surfPhysY[0] <= y) & (y < surfOptY[0])) |
                             ((surfOptY[1] <= y) & (y < surfPhysY[1]))] = 2
                if not hasattr(self, 'overEdge'):
                    self.overEdge = 'yMax'
                ovE = self.overEdge.lower()
                if ovE.startswith('x') and ovE.endswith('in'):
                    locState[x < self.surfPhysX[0]] = 3
                    locState[(y < surfPhysY[0]) | (y > surfPhysY[1]) |
                             (x > surfPhysX[1])] = self.lostNum
                elif ovE.startswith('x') and ovE.endswith('ax'):
                    locState[x > self.surfPhysX[1]] = 3
                    locState[(y < surfPhysY[0]) | (y > surfPhysY[1]) |
                             (x < surfPhysX[0])] = self.lostNum
                elif ovE.startswith('y') and ovE.endswith('in'):
                    locState[y < self.surfPhysY[0]] = 3
                    locState[(x < surfPhysX[0]) | (x > surfPhysX[1]) |
                             (y > surfPhysY[1])] = self.lostNum
                elif ovE.startswith('y') and ovE.endswith('ax'):
                    locState[y > self.surfPhysY[1]] = 3
                    locState[(x < surfPhysX[0]) | (x > surfPhysX[1]) |
                             (y < surfPhysY[0])] = self.lostNum
            elif self.shape.startswith('ro'):
                centerX = (surfPhysX[0]+surfPhysX[1]) * 0.5
                if np.isnan(centerX):
                    centerX = 0
                radius = (surfPhysX[1]-surfPhysX[0]) * 0.5
                if surfOptY is not None:
                    centerY = (surfPhysY[0]+surfPhysY[1]) * 0.5
                else:
                    centerY = 0.
                if np.isnan(centerY):
                    centerY = 0
                if not np.isinf(radius):
                    locState[((x-centerX)**2 + (y-centerY)**2) > radius**2] =\
                        self.lostNum
        elif isinstance(self.shape, list):
            footprint = mpl.path.Path(self.shape)
            locState[:] = footprint.contains_points(np.array(zip(x, y)))
            locState[(locState == 0) & (y < surfPhysY[0])] = self.lostNum
            locState[locState == 0] = 3
        else:
            raise ValueError('Unknown shape of OE {0}!'.format(self.name))
        return locState

    def reflect(self, beam, needLocal=True):
        r"""Returns the reflected or transmitted beam in global and local
        (if *needLocal* is true) systems. The new direction is calculated as
        [wikiSnell]_:

        .. math::

            \vec{out}_{\rm reflect} &= \vec{in} + 2\cos{\theta_1}\vec{n}\\
            \vec{out}_{\rm refract} &= \frac{n_1}{n_2}\vec{in} +
            \left(\frac{n_1}{n_2}\cos{\theta_1} - \cos{\theta_2}\right)\vec{n},

        where

        .. math::

            \cos{\theta_1} &= -\vec{n}\cdot\vec{in}\\
            \cos{\theta_2} &= sign(\cos{\theta_1})\sqrt{1 -
            \left(\frac{n_1}{n_2}\right)^2\left(1-\cos^2{\theta_1}\right)}.

        For a grating or an FZP with the reciprocal vector :math:`g` in
        :math:`m` th order:

        .. math::

            \vec{out} &= \vec{in} - dn\vec{n} + \vec{g}m\lambda

        where

        .. math::

            dn &= -\cos{\theta_1} \pm \sqrt{\cos^2{\theta_1} -
            2\sin{\alpha}m\lambda - \vec{g}^2 m^2\lambda^2}

            \sin{\alpha} &= \vec{g}\cdot\vec{in}\\

        .. [wikiSnell] http://en.wikipedia.org/wiki/Snell%27s_law .
        """
        self.get_orientation()
# output beam in global coordinates
        gb = rs.Beam(copyFrom=beam)
        if needLocal:
# output beam in local coordinates
            lb = rs.Beam(copyFrom=beam)
        else:
            lb = gb
        good = beam.state > 0
        if good.sum() == 0:
            return gb, lb
#coordinates in local virgin system:
        raycing.global_to_virgin_local(self.bl, beam, lb, self.center, good)
        self._reflect_local(good, lb, gb, self.pitch,
                            self.roll+self.positionRoll, self.yaw,
                            self.dx, material=self.material)
        goodAfter = (gb.state == 1) | (gb.state == 2)
#in global coordinate system:
        if goodAfter.sum() > 0:
            raycing.virgin_local_to_global(self.bl, gb, self.center, goodAfter)
#not intersected rays remain unchanged except their state:
        notGood = ~goodAfter
        if notGood.sum() > 0:
            rs.copy_beam(gb, beam, notGood)
        return gb, lb  # in global(gb) and local(lb) coordinates

    def multiple_reflect(
            self, beam, maxReflections=1000, needElevationMap=False):
        """Does the same as :meth:`reflect` but with up to *maxReflections*
        reflection on the same surface. The returned beam has additional
        fields: *nRefl* for the number of reflections, *elevationD* for the
        maximum elevation distance between the rays and the surface as the ray
        travels between the impact points, *elevationX*, *elevationY*,
        *elevationZ* for the coordinates of the maximum elevation points."""
        self.get_orientation()
# output beam in global coordinates
        gb = rs.Beam(copyFrom=beam)
        lb = gb
        good = beam.state > 0
        if good.sum() == 0:
            return gb, lb
# coordinates in local virgin system:
        raycing.global_to_virgin_local(self.bl, beam, lb, self.center, good)
        iRefl = 0
        isMulti = False
        while iRefl <= maxReflections:
            tmpX, tmpY, tmpZ =\
                np.copy(lb.x[good]), np.copy(lb.y[good]), np.copy(lb.z[good])
            if _DEBUG:
                print 'reflection No {0}'.format(iRefl + 1)
            if iRefl == 0:
                if needElevationMap:
                    lb.elevationD = -np.ones_like(lb.x)
                    lb.elevationX = -np.ones_like(lb.x)*raycing.maxHalfSizeOfOE
                    lb.elevationY = -np.ones_like(lb.x)*raycing.maxHalfSizeOfOE
                    lb.elevationZ = -np.ones_like(lb.x)*raycing.maxHalfSizeOfOE
            self._reflect_local(good, lb, gb, self.pitch,
                                self.roll+self.positionRoll, self.yaw,
                                self.dx, material=self.material,
                                needElevationMap=needElevationMap,
                                isMulti=isMulti)
            if iRefl == 0:
                isMulti = True
                lb.nRefl = np.zeros_like(lb.state)
            ov = lb.state[good] == 3
            lb.x[np.where(good)[0][ov]] = tmpX[ov]
            lb.y[np.where(good)[0][ov]] = tmpY[ov]
            lb.z[np.where(good)[0][ov]] = tmpZ[ov]
            good = (lb.state == 1) | (lb.state == 2)
            lb.nRefl[good] += 1
            if iRefl == 0:
#all local footprints:
                lbN = rs.Beam(copyFrom=lb, withNumberOfReflections=True)
            else:
                lbN.concatenate(lb)
            iRefl += 1
            if _DEBUG:
                print 'iRefl=', iRefl, 'remains=', good.sum()
#                if good.sum() > 0:
#                    print 'y min max ', lb.y[good].min(), lb.y[good].max()
            if good.sum() == 0:
                break
#            gc.collect()
#in global coordinate system:
        goodAfter = gb.nRefl > 0
        gb.state[goodAfter] = 1
        if goodAfter.sum() > 0:
            raycing.virgin_local_to_global(self.bl, gb, self.center, goodAfter)
#not intersected rays remain unchanged except their state:
        notGood = ~goodAfter
        if notGood.sum() > 0:
            rs.copy_beam(gb, beam, notGood)
#in global(gb) and local(lbN) coordinates. lbN holds all the reflection spots.
        return gb, lbN

    def _set_t(self, xyz=None, abc=None, surfPhys=None,
               defSize=raycing.maxHalfSizeOfOE):
        if surfPhys is None:
            limMin = -defSize
            limMax = defSize
        else:
            limMin = surfPhys[0] if surfPhys[0] > -np.inf else -defSize
            limMax = surfPhys[1] if surfPhys[1] < np.inf else defSize
        if abc[0] > 0:
            tMin = (limMin-xyz)/abc - raycing.dt
            tMax = (limMax-xyz)/abc + raycing.dt
        else:
            tMin = (limMax-xyz)/abc - raycing.dt
            tMax = (limMin-xyz)/abc + raycing.dt
        return tMin, tMax

    def _bracketing(self, local_n, x, y, z, a, b, c, invertNormal,
                    is2ndXtal=False, isMulti=False, needElevationMap=False):
        if is2ndXtal:
            surfPhysX = self.surfPhysX2
            surfPhysY = self.surfPhysY2
        else:
            surfPhysX = self.surfPhysX
            surfPhysY = self.surfPhysY
        maxa = np.max(abs(a))
        maxb = np.max(abs(b))
        maxc = np.max(abs(c))
        maxMax = max(maxa, maxb, maxc)
        if maxMax == maxa:
            tMin, tMax = self._set_t(x, a, surfPhysX)
        elif maxMax == maxb:
            tMin, tMax = self._set_t(y, b, surfPhysY)
        else:
            tMin, tMax = self._set_t(z, c, defSize=raycing.maxDepthOfOE)
        tMin[tMin < 0] = 0
        elevation = None
        if isMulti:
            tMin[:] = 0
            tMaxTmp = np.copy(tMax)
            tMax, dummy, dummy, dummy = self.find_intersection(
                local_n, tMin, tMax, x, y, z, a, b, c, invertNormal,
                derivOrder=1)
            if needElevationMap:
                elevation = \
                    self.find_dz(None, tMax, x, y, z, a, b, c, invertNormal)
            tMin = tMax + raycing.ds
            tMax = tMaxTmp
        else:
            pass
#            if needElevationMap:
#                elevation = \
#                    self.find_dz(None, tMin, x, y, z, a, b, c, invertNormal)
        return tMin, tMax, elevation

    def _grating_deflection(
        self, goodN, lb, gNormal, oeNormal, beamInDotNormal, order=1,
            isTransmitting=False):
        beamInDotG = lb.a[goodN]*gNormal[0] +\
            lb.b[goodN]*gNormal[1] + lb.c[goodN]*gNormal[2]
        G2 = gNormal[0]**2 + gNormal[1]**2 + gNormal[2]**2
        if isinstance(order, int):
            locOrder = order
        else:
            locOrder = np.array(order)[np.random.randint(len(order),
                                       size=goodN.sum())]
            lb.order = locOrder
        orderLambda = locOrder * rm.ch / lb.E[goodN] * 1e-7

        if isTransmitting:  # transmitting grating, like FZP
            sig = 1.
        else:  # reflecting grating
            sig = -1.
        dn = beamInDotNormal + sig * np.sqrt(np.abs(
            beamInDotNormal**2 - 2*beamInDotG*orderLambda - G2*orderLambda**2))
        a_out = lb.a[goodN] - oeNormal[0]*dn + gNormal[0]*orderLambda
        b_out = lb.b[goodN] - oeNormal[1]*dn + gNormal[1]*orderLambda
        c_out = lb.c[goodN] - oeNormal[2]*dn + gNormal[2]*orderLambda
        return a_out, b_out, c_out

#    def _reportNaN(self, x, strName):
#        nanSum = np.isnan(x).sum()
#        if nanSum > 0:
#            print "{0} NaN rays in {1} in {2}!".format(
#                nanSum, strName, self.name)

    def _reflect_local(
        self, good, lb, vlb, pitch, roll, yaw, dx, local_z=None, local_n=None,
        local_g=None, fromVacuum=True, material=None, is2ndXtal=False,
            needElevationMap=False, isMulti=False):
        """Finds the intersection points of rays in the beam *lb* indexed by
        *good* array. *vlb* is the same beam in virgin local system.
        *pitch, roll, yaw* determine the transformation between true local and
        virgin local coordinates.
        *local_n* gives the normal (two normals (h, surface) if for crystal).
        *local_g* for a grating gives the local reciprocal groove vector in
        1/mm. *fromVacuum* tells the beam direction for the vacuum-OE
        interface. *material* is an instance of :class:`Material` or
        :class:`Crystal` or its derivatives. Depending on the geometry used, it
        must have either the method :meth:`get_refraction_index` or the
        :meth:`get_amplitude`."""
# rotate the world around the mirror.
# lb is truly local coordinates whereas vlb is in virgin local coordinates:
        if local_n is None:
            local_n = self.local_n
        raycing.rotate_beam(
            lb, good, way=1, pitch=-pitch, roll=-roll, yaw=-yaw)
        if dx:
            lb.x[good] -= dx
# x, y, z:
        if fromVacuum:
            invertNormal = 1
        else:
            invertNormal = -1
        tMin = np.zeros_like(lb.x)
        tMax = np.zeros_like(lb.x)
        tMin[good], tMax[good], elev = self._bracketing(
            local_n, lb.x[good], lb.y[good], lb.z[good], lb.a[good],
            lb.b[good], lb.c[good], invertNormal, is2ndXtal, isMulti=isMulti,
            needElevationMap=needElevationMap)
        if needElevationMap and elev:
            lb.elevationD[good] = elev[0]
            if self.isParametric:
                tX, tY, tZ = self.param_to_xyz(elev[1], elev[2], elev[3])
            else:
                tX, tY, tZ = elev[1], elev[2], elev[3]
            lb.elevationX[good] = tX
            lb.elevationY[good] = tY
            lb.elevationZ[good] = tZ
#        print 'tMin ', tMin[good].min(), tMin[good].max()
#        print 'tMax ', tMax[good].min(), tMax[good].max()

        tMax[good], lb.x[good], lb.y[good], lb.z[good] = \
            self.find_intersection(
                local_z, tMin[good], tMax[good], lb.x[good], lb.y[good],
                lb.z[good], lb.a[good], lb.b[good], lb.c[good], invertNormal)
#        print 'tMax ', tMax[good].min(), tMax[good].max()
#        print 's ', lb.x[good].min(), lb.x[good].max()
#state:
        if self.isParametric:
            z_distorted = self.local_r_distorted(lb.x[good], lb.y[good])
            tX, tY, tZ = self.param_to_xyz(lb.x[good], lb.y[good], lb.z[good])
        else:
            z_distorted = self.local_z_distorted(lb.x[good], lb.y[good])
            tX, tY = lb.x[good], lb.y[good]
        if z_distorted is not None:
            lb.z[good] += z_distorted
#        print 'tY ', tY[good].min(), tY[good].max()

        res = self.rays_good(tX, tY, is2ndXtal)
        gNormal = None
        if isinstance(res, tuple):
            lb.state[good], gNormal = res
        else:
            lb.state[good] = res
        goodN = (lb.state == 1) | (lb.state == 2)
#normal at x, y, z:
        if goodN.sum() > 0:
            lb.path[goodN] += tMax[goodN]
            oeNormal = np.asarray(local_n(lb.x[goodN], lb.y[goodN]), order='F')
            n_distorted = self.local_n_distorted(lb.x[goodN], lb.y[goodN])
            if n_distorted is not None:
                cosX, sinX = np.cos(n_distorted[0]), np.sin(n_distorted[0])
                lb.b[goodN], lb.c[goodN] = raycing.rotate_x(
                    lb.b[goodN], lb.c[goodN], cosX, sinX)
                cosY, sinY = np.cos(n_distorted[1]), np.sin(n_distorted[1])
                lb.a[goodN], lb.c[goodN] = raycing.rotate_y(
                    lb.a[goodN], lb.c[goodN], cosY, sinY)
            beamInDotNormal = lb.a[goodN]*oeNormal[0] +\
                lb.b[goodN]*oeNormal[1] + lb.c[goodN]*oeNormal[2]
            lb.theta = np.zeros_like(lb.x)
            lb.theta[goodN] = np.arccos(beamInDotNormal) - np.pi/2
#            if elevation is not None:
#                print 'max elevation = {0} mm'.format(elevation[goodN].max())
            toWhere = 0  # 0: reflect, 1: refract, 2: pass straight
            if material is not None:
                if raycing.is_sequence(material):
                    matSur = material[self.curSurface]
                else:
                    matSur = material
                if matSur.kind in ('plate', 'lens'):
                    toWhere = 1
                elif matSur.kind == 'crystal':
                    beamInDotSurfaceNormal = lb.a[goodN]*oeNormal[-3] +\
                        lb.b[goodN]*oeNormal[-2] + lb.c[goodN]*oeNormal[-1]
                    if matSur.geom.endswith('transmitted'):
                        toWhere = 2
                elif matSur.kind == 'grating':
                    toWhere = 3
                elif matSur.kind == 'FZP':
                    toWhere = 4
#direction:
            if local_g is None:
                local_g = self.local_g
            if toWhere in [3, 4]:  # grating, FZP
                if gNormal is None:
                    gNormal = np.asarray(local_g(lb.x[goodN], lb.y[goodN]),
                                         order='F')
                lb.a[goodN], lb.b[goodN], lb.c[goodN] =\
                    self._grating_deflection(goodN, lb, gNormal, oeNormal,
                                             beamInDotNormal, self.order,
                                             toWhere == 4)
            if toWhere in [0, 2]:  # reflect, straight
                useAsymmetricNormal = False
                if material is not None:
                    if matSur.kind == 'crystal' and toWhere == 0:
                        useAsymmetricNormal = True
                if useAsymmetricNormal:
                    normalDotSurfNormal = oeNormal[0]*oeNormal[-3] +\
                        oeNormal[1]*oeNormal[-2] + oeNormal[2]*oeNormal[-1]
                    dt = matSur.get_dtheta_symmetric_Bragg(lb.E[goodN])
                    gNormalCryst = np.asarray((
                        (oeNormal[0]-normalDotSurfNormal*oeNormal[-3]) * dt,
                        (oeNormal[1]-normalDotSurfNormal*oeNormal[-2]) * dt,
                        (oeNormal[2]-normalDotSurfNormal*oeNormal[-1]) * dt),
                        order='F') / (matSur.d * 1e-7) *\
                        np.sqrt(abs(1 - normalDotSurfNormal**2))
                    if matSur.geom.endswith('Fresnel'):
                        if isinstance(self.order, int):
                            locOrder = self.order
                        else:
                            locOrder = np.array(self.order)[np.random.randint(
                                len(self.order), size=goodN.sum())]
                        if gNormal is None:
                            gNormal = local_g(lb.x[goodN], lb.y[goodN])
                        gNormal = np.asarray(gNormal, order='F') * locOrder
                        gNormal[0] += gNormalCryst[0]
                        gNormal[1] += gNormalCryst[1]
                        gNormal[2] += gNormalCryst[2]
                    else:
                        gNormal = gNormalCryst
                    a_out, b_out, c_out =\
                        self._grating_deflection(
                            goodN, lb, gNormal, oeNormal, beamInDotNormal, 1,
                            matSur.geom.startswith('Laue'))
                else:
                    a_out = lb.a[goodN] - oeNormal[0]*2*beamInDotNormal
                    b_out = lb.b[goodN] - oeNormal[1]*2*beamInDotNormal
                    c_out = lb.c[goodN] - oeNormal[2]*2*beamInDotNormal
                if toWhere == 0:  # reflect
                    lb.a[goodN] = a_out
                    lb.b[goodN] = b_out
                    lb.c[goodN] = c_out
            elif toWhere == 1:  # refract
                refraction_index = \
                    matSur.get_refraction_index(lb.E[goodN]).real
                if fromVacuum:
                    n1overn2 = 1. / refraction_index
                else:
                    n1overn2 = refraction_index
                signN = np.sign(-beamInDotNormal)
                n1overn2cosTheta1 = -n1overn2 * beamInDotNormal
                cosTheta2 = signN * \
                    np.sqrt(1 - n1overn2**2 + n1overn2cosTheta1**2)
                dn = (n1overn2cosTheta1 - cosTheta2)
                lb.a[goodN] = lb.a[goodN] * n1overn2 + oeNormal[0]*dn
                lb.b[goodN] = lb.b[goodN] * n1overn2 + oeNormal[1]*dn
                lb.c[goodN] = lb.c[goodN] * n1overn2 + oeNormal[2]*dn
            else:  # pass straight, do nothing
                pass
#flux:
            if material is not None:
#rotate coherency matrix: {np.arctan2: 0./0.: =0, 1./0.: =pi/2}
                rollAngle = roll + np.arctan2(oeNormal[0], oeNormal[2])
                localJ = rs.rotate_coherency_matrix(lb, goodN, -rollAngle)
#get reflectivity
                if matSur.kind == 'crystal':
                    beamOutDotSurfaceNormal = a_out * oeNormal[-3] + \
                        b_out * oeNormal[-2] + c_out * oeNormal[-1]
                    refl = matSur.get_amplitude(
                        lb.E[goodN], beamInDotSurfaceNormal,
                        beamOutDotSurfaceNormal, beamInDotNormal)
                else:  # 'mirror', 'thin mirror', 'plate', 'lens', 'grating'
                    refl = matSur.get_amplitude(lb.E[goodN], beamInDotNormal,
                                                fromVacuum)
                ras, rap = refl[0], refl[1]
#                self._reportNaN(ras, 'ras')
#                self._reportNaN(rap, 'rap')
                nanSum = np.isnan(ras).sum()
                if nanSum > 0:
                    ras[np.isnan(ras)] = 0.
#                    raise ValueError("s-reflectivity contains {0} of nan's!".\
#                      format(nanSum))
                nanSum = np.isnan(rap).sum()
                if nanSum > 0:
                    rap[np.isnan(rap)] = 0.
#                    raise ValueError("p-reflectivity contains {0} of nan's!".\
#                      format(nanSum))

                lb.Jss[goodN] = (localJ[0] * ras * np.conjugate(ras)).real
                lb.Jpp[goodN] = (localJ[1] * rap * np.conjugate(rap)).real
                lb.Jsp[goodN] = localJ[2] * ras * np.conjugate(rap)
                if (not fromVacuum) and (matSur.kind != 'crystal'):
                    #tMax in mm, refl[2]=mu0 in 1/cm
                    att = np.exp(-refl[2] * tMax[goodN] * 0.1)
                    lb.Jss[goodN] *= att
                    lb.Jpp[goodN] *= att
                    lb.Jsp[goodN] *= att
#rotate coherency matrix back:
                lb.Jss[goodN], lb.Jpp[goodN], lb.Jsp[goodN] =\
                    rs.rotate_coherency_matrix(lb, goodN, rollAngle)
        if self.isParametric:
            lb.s = np.copy(lb.x)
            lb.phi = np.copy(lb.y)
            lb.r = np.copy(lb.z)
            lb.x[good], lb.y[good], lb.z[good] = self.param_to_xyz(
                lb.x[good], lb.y[good], lb.z[good])
        if vlb is not lb:
            rs.copy_beam(vlb, lb, good, includeState=True)
#rotate the world back for the virgin local beam:
        if dx:
            vlb.x[good] += dx
        raycing.rotate_beam(vlb, good, way=-1, pitch=pitch,
                            roll=roll, yaw=yaw)

        if self.alarmLevel is not None:
            raycing.check_alarm(self, good, vlb)

    def get_Kirchhoff_integral(self, beamIn, lb, theta, beta):
        n = self.local_n(lb.x, lb.y)
        cosGamma = (lb.a*n[-3] + lb.b*n[-2] + lb.c*n[-1])
        jk = 1j * lb.E / rm.chbar * 1e7
#        vec = np.asarray(outVectorLoc)
#        vecA = vec[:, 0][:, np.newaxis]
#        vecB = vec[:, 1][:, np.newaxis]
#        vecC = vec[:, 2][:, np.newaxis]
#        cosAlpha = vecA*n[-3] + vecB*n[-2] + vecC*n[-1]
#        path = -(vecA*lb.x + vecB*lb.y + vecC*lb.z) + lb.path
#        c = jk / 4. / np.pi * (cosGamma+cosAlpha) * np.exp(jk*path) /\
#            (beamIn.Jss+beamIn.Jpp)
        vecB = np.sin(beta)[:, np.newaxis]
        vecC = np.cos(beta)[:, np.newaxis]
        cosAlpha = vecB*n[-2] + vecC*n[-1]
        path = -(np.cos(theta)*lb.y + np.sin(theta)*lb.z) + lb.path
        c = (cosGamma+cosAlpha) * np.exp(jk*path) / (beamIn.Jss+beamIn.Jpp)
        lb.fieldKirchhoffS = np.sum(c * lb.Jss**0.5, axis=1)
        lb.fieldKirchhoffP = np.sum(c * lb.Jpp**0.5, axis=1)
        lb.fieldKirchhoffN = np.sum(c, axis=1)


class DicedOE(OE):
    """Base class for a diced optical element. It implements a flat diced
    mirror. """
    def __init__(self, *args, **kwargs):
        """
        *dxFacet*, *dyFacet* size of the facets.

        *dxGap*, *dyGat* width of the gap between facets.
        """
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.dxFacet = kwargs.pop('dxFacet', 2.1)
        self.dyFacet = kwargs.pop('dyFacet', 1.4)
        self.dxGap = kwargs.pop('dxGap', 0.05)
        self.dyGap = kwargs.pop('dyGap', 0.05)
        self.xStep = self.dxFacet + self.dxGap
        self.yStep = self.dyFacet + self.dyGap
        return kwargs

    def facet_center_z(self, x, y):
        """Z of the facet centers at (*x*, *y*)."""
        return 0  # just flat

    def facet_center_n(self, x, y):
        """Surface normal or (Bragg normal and surface normal)."""
        return 0, 0, 1  # just flat

    def facet_delta_z(self, u, v):
        """Local Z in the facet coordinates."""
        return 0

    def facet_delta_n(self, u, v):
        """Local surface normal (always without Bragg normal!) in the facet
        coordinates. In the asymmetry case the lattice normal is taken as
        constant over the facet and is given by :meth:`facet_center_n`.
        """
        return 0, 0, 1

    def local_z(self, x, y, skipReturnZ=False):
        """Determines the surface of OE at (*x*, *y*) position."""
        cx = (x / self.xStep).round() * self.xStep  # center of the facet
        cy = (y / self.yStep).round() * self.yStep  # center of the facet
        cz = self.facet_center_z(cx, cy)
        cn = self.facet_center_n(cx, cy)
        fx = x - cx  # local coordinate in the facet
        fy = y - cy
        if skipReturnZ:
            return fx, fy, cn
        z = cz + (self.facet_delta_z(fx, fy) - cn[-3]*fx - cn[-2]*fy) / cn[-1]
#        inGaps = (abs(fx)>self.dxFacet/2) | (abs(fy)>self.dyFacet/2)
        return z

    def local_n(self, x, y):
        """Determines the normal vector of OE at (*x*, *y*) position. For an
        asymmetric crystal, *local_n* returns 2 normals: the 1st one of the
        atomic planes and the 2nd one of the surface. Note the order!"""
        fx, fy, cn = self.local_z(x, y, skipReturnZ=True)
        deltaNormals = self.facet_delta_n(fx, fy)
        if isinstance(deltaNormals[2], np.ndarray):
            useDeltaNormals = True
        else:
            useDeltaNormals = (deltaNormals[2] != 1)
        if useDeltaNormals:
            cn[-1] += deltaNormals[-1]
            cn[-2] += deltaNormals[-2]
            norm = (cn[-1]**2 + cn[-2]**2 + cn[-3]**2)**0.5
            cn[-1] /= norm
            cn[-2] /= norm
            cn[-3] /= norm
        if self.alpha:
            bAlpha, cAlpha = raycing.rotate_x(cn[1], cn[2],
                                              self.cosalpha, -self.sinalpha)
            return cn[0], bAlpha, cAlpha, cn[-3], cn[-2], cn[-1]
        else:
            return cn

    def rays_good(self, x, y, is2ndXtal=False):
        """Returns *state* value as inherited from :class:`OE`. The rays that
        fall inside the gaps are additionally considered as lost."""
#=1: good (intersected)
#=2: reflected outside of working area, =3: transmitted without intersection,
#=-NN: lost (absorbed) at OE#NN - OE numbering starts from 1 !!!
        locState = OE.rays_good(self, x, y, is2ndXtal)
        fx, fy, cn = self.local_z(x, y, skipReturnZ=True)
        inGaps = (abs(fx) > self.dxFacet/2) | (abs(fy) > self.dyFacet/2)
        locState[inGaps] = self.lostNum
        return locState


class JohannCylinder(OE):
    """Simply bent reflective optical element."""
    def __init__(self, *args, **kwargs):
        """
        *Rm* is meridional radius.

        *crossSection* determines the bending shape: either 'circular' or
        'parabolic'.
        """
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.Rm = kwargs.pop('Rm', 1000.)  # R meridional
        self.crossSection = kwargs.pop('crossSection', 'circular')
        if not (self.crossSection.startswith('circ') or
                self.crossSection.startswith('parab')):
            raise ValueError('unknown crossSection!')
        return kwargs

    def local_z(self, x, y):
        """Determines the surface of OE at (*x*, *y*) position."""
        if self.crossSection.startswith('circ'):  # 'circular'
            sq = self.Rm**2 - y**2
#            sq[sq<0] = 0
            return self.Rm - np.sqrt(sq)
        else:  # 'parabolic'
            return y**2 / 2.0 / self.Rm

    def local_n_cylinder(self, x, y, R, alpha):
        """The main part of :meth:`local_n`. It introduces two new arguments
        to simplify the implementation of :meth:`local_n` in the derived class
        :class:`JohanssonCylinder`."""
        a = np.zeros_like(x)  # -dz/dx
        b = -y / R  # -dz/dy
        if self.crossSection.startswith('circ'):  # 'circular'
            c = (R**2 - y**2)**0.5 / R
        else:  # 'parabolic'
            norm = (b**2 + 1)**0.5
            b /= norm
            c = 1. / norm
        if alpha:
            bAlpha, cAlpha = \
                raycing.rotate_x(b, c, self.cosalpha, -self.sinalpha)
            return [a, bAlpha, cAlpha, a, b, c]
        else:
            return [a, b, c]

    def local_n(self, x, y):
        """Determines the normal vector of OE at (*x*, *y*) position. For an
        asymmetric crystal, *local_n* returns 2 normals."""
        return self.local_n_cylinder(x, y, self.Rm, self.alpha)


class JohanssonCylinder(JohannCylinder):
    """Ground-bent reflective optical element."""
    def local_n(self, x, y):
        """Determines the normal vectors of OE at (*x*, *y*) position: of the
        atomic planes and of the surface."""
        nSurf = self.local_n_cylinder(x, y, self.Rm, None)
#approximate expressions:
#        nBragg = self.local_n_cylinder(x, y, self.Rm*2, self.alpha)
#        return [nBragg[0], nBragg[1], nBragg[2],
#           nSurf[-3], nSurf[-2], nSurf[-1]]
#exact expressions:
        a = np.zeros_like(x)
        b = -y
        c = (self.Rm**2 - y**2)**0.5 + self.Rm
        if self.alpha:
            b, c = raycing.rotate_x(b, c, self.cosalpha, -self.sinalpha)
        norm = np.sqrt(b**2 + c**2)
        return [a/norm, b/norm, c/norm, nSurf[-3], nSurf[-2], nSurf[-1]]


class JohannToroid(OE):
    """2D bent reflective optical element."""
    def __init__(self, *args, **kwargs):
        """
        *Rm* and *Rs* are meridional and sagittal radii.
        """
        kwargs = self.pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def pop_kwargs(self, **kwargs):
        self.Rm = kwargs.pop('Rm', 1000.)  # R meridional
        self.Rs = kwargs.pop('Rs', None)  # R sagittal
        if self.Rs is None:
            self.Rs = self.Rm
        return kwargs

    def local_z(self, x, y):
        """Determines the surface of OE at (*x*, *y*) position."""
        z = self.Rm - self.Rs - (self.Rm**2 - y**2)**0.5
        cosangle, sinangle = (z**2 - x**2)**0.5 / abs(z), -x/abs(z)
        bla, z = raycing.rotate_y(0, z, cosangle, sinangle)
        return z + self.Rs

    def local_n(self, x, y):
        """Determines the normal vectors of OE at (*x*, *y*) position: of the
        atomic planes and of the surface."""
        return self.local_n_toroid(x, y, self.Rm, self.Rs, self.alpha)

    def local_n_toroid(self, x, y, Rm, Rs, alpha):
        """The main part of :meth:`local_n`. It introduces three new arguments
        to simplify the implementation of :meth:`local_n` in the derived class
        :class:`JohanssonToroid`."""
        a = np.zeros_like(x)
        b = -y / Rm
        c = (Rm**2 - y**2)**0.5 / Rm
        if alpha:
            aAlpha = np.zeros_like(x)
            bAlpha, cAlpha = \
                raycing.rotate_x(b, c, self.cosalpha, -self.sinalpha)
        r = Rs - (Rm - (Rm**2 - y**2)**0.5)
        cosangle, sinangle = (r**2 - x**2)**0.5 / r, -x/r
        a, c = raycing.rotate_y(a, c, cosangle, sinangle)
        if alpha:
            aAlpha, cAlpha = \
                raycing.rotate_y(aAlpha, cAlpha, cosangle, sinangle)
            return [aAlpha, bAlpha, cAlpha, a, b, c]
        else:
            return [a, b, c]


class JohanssonToroid(JohannToroid):
    """Ground-2D-bent reflective optical element."""
    def local_n(self, x, y):
        """Determines the normal vectors of OE at (*x*, *y*) position: of the
        atomic planes and of the surface."""
        nSurf = self.local_n_toroid(x, y, self.Rm, self.Rs, None)
#approximate expressions:
#        nBragg = self.local_n_cylinder(x, y, self.Rm*2, self.alpha)
#        return [nBragg[0], nBragg[1], nBragg[2],
#            nSurf[-3], nSurf[-2], nSurf[-1]]
#exact expressions:
        a = np.zeros_like(x)
        b = -y
        c = (self.Rm**2 - y**2)**0.5 + self.Rm
        norm = np.sqrt(b**2 + c**2)
        b, c = b/norm, c/norm
        if self.alpha:
            b, c = raycing.rotate_x(b, c, self.cosalpha, -self.sinalpha)
        r = self.Rs - (self.Rm - (self.Rm**2 - y**2)**0.5)
        cosangle, sinangle = (r**2 - x**2)**0.5 / r, -x/r
        a, c = raycing.rotate_y(a, c, cosangle, sinangle)
        if self.alpha:
            a, c = raycing.rotate_y(a, c, cosangle, sinangle)
        return [a, b, c, nSurf[-3], nSurf[-2], nSurf[-1]]


class DicedJohannToroid(DicedOE, JohannToroid):
    """A diced version of :class:`JohannToroid`."""
    def __init__(self, *args, **kwargs):
        kwargs = self.pop_kwargs(**kwargs)
        DicedOE.__init__(self, *args, **kwargs)

    def pop_kwargs(self, **kwargs):
        return JohannToroid.pop_kwargs(self, **kwargs)

    def facet_center_z(self, x, y):
        return JohannToroid.local_z(self, x, y)

    def facet_center_n(self, x, y):
        return JohannToroid.local_n(self, x, y)


class DicedJohanssonToroid(DicedJohannToroid, JohanssonToroid):
    """A diced version of :class:`JohanssonToroid`."""
    def facet_center_n(self, x, y):
        return JohanssonToroid.local_n(self, x, y)

    def facet_delta_z(self, u, v):
        return v**2 / 2.0 / self.Rm

    def facet_delta_n(self, u, v):
        a = 0.  # -dz/dx
        b = -v / self.Rm  # -dz/dy
        c = 1.
        norm = (b**2 + 1)**0.5
        return a/norm, b/norm, c/norm


class LauePlate(OE):
    """A flat Laue plate. The thickness is defined in its *material* part."""
    def local_n(self, x, y):
        a, b, c = 0, 0, 1
        if self.alpha:
            bB, cB = raycing.rotate_x(b, c, -self.sinalpha, -self.cosalpha)
        else:
            bB, cB = c, -b
        return a, bB, cB, a, b, c


class BentLaueCylinder(OE):
    """Simply bent reflective optical element in Laue geometry."""
    def __init__(self, *args, **kwargs):
        """
        *R* is meridional radius.
        *crossSection* determines the bending shape: either 'circular' or
        'parabolic'.
        """
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.R = kwargs.pop('R', 1.0e4)
        self.crossSection = kwargs.pop('crossSection', 'parabolic')
        if not (self.crossSection.startswith('circ') or
                self.crossSection.startswith('parab')):
            raise ValueError('unknown crossSection!')
        return kwargs

    def local_z(self, x, y):
        """Determines the surface of OE at (*x*, *y*) position."""
        if self.crossSection.startswith('circ'):  # 'circular'
            return self.R - np.sqrt(self.R**2 - y**2)
        else:  # 'parabolic'
            return y**2 / 2.0 / self.R

    def local_n_cylinder(self, x, y, R, alpha):
        """The main part of :meth:`local_n`. It introduces two new arguments
        to simplify the implementation of :meth:`local_n` in the derived class
        :class:`GroundBentLaueCylinder`."""
        a = np.zeros_like(x)  # -dz/dx
        b = -y / R  # -dz/dy
        if self.crossSection.startswith('circ'):  # 'circular'
            c = (R**2 - y**2)**0.5 / R
        elif self.crossSection.startswith('parab'):  # 'parabolic'
            norm = (b**2 + 1)**0.5
            b /= norm
            c = 1. / norm
        else:
            raise ValueError('unknown crossSection!')
        if alpha:
            bB, cB = raycing.rotate_x(b, c, -self.sinalpha, -self.cosalpha)
        else:
            bB, cB = c, -b
        return a, bB, cB, a, b, c

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        return self.local_n_cylinder(x, y, self.R, self.alpha)


class GroundBentLaueCylinder(BentLaueCylinder):
    """Ground-bent reflective optical element in Laue geometry, aka DuMond
    spectrometer."""
    def local_n(self, x, y):
        """Determines the normal vectors of OE at (*x*, *y*) position: of the
        atomic planes and of the surface."""
        nSurf = self.local_n_cylinder(x, y, self.R, None)
#approximate expressions:
#        nBragg = self.local_n_cylinder(x, y, self.R*2, self.alpha)
#        return [nBragg[0], nBragg[1], nBragg[2],
#            nSurf[-3], nSurf[-2], nSurf[-1]]
#exact expressions:
        a = np.zeros_like(x)
        b = -y
        c = (self.R**2 - y**2)**0.5 + self.R
        if self.alpha:
            b, c = raycing.rotate_x(b, c, -self.sinalpha, -self.cosalpha)
        else:
            b, c = c, -b
        norm = np.sqrt(b**2 + c**2)
        return [a/norm, b/norm, c/norm, nSurf[-3], nSurf[-2], nSurf[-1]]


class BentLaueSphere(BentLaueCylinder):
    """Spherically bent reflective optical element in Laue geometry."""
    def local_z(self, x, y):
        if self.crossSection.startswith('circ'):  # 'circular'
            return self.R - np.sqrt(self.R**2 - x**2 - y**2)
        else:  # 'parabolic'
            return (x**2+y**2) / 2.0 / self.R

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        if self.crossSection.startswith('circ'):  # 'circular'
            a = -x * (self.R**2 - x**2 - y**2)**(-0.5)  # -dx/dy
            b = -y * (self.R**2 - x**2 - y**2)**(-0.5)  # -dz/dy
        else:  # 'parabolic'
            a = -x / self.R  # -dz/dx
            b = -y / self.R  # -dz/dy
        c = 1.
        norm = (a**2 + b**2 + 1)**0.5
        aB = 0.
        bB = c
        cB = -b
        normB = (b**2 + c**2)**0.5
        return aB/normB, bB/normB, cB/normB, a/norm, b/norm, c/norm


class MirrorOnTripodWithTwoXStages(OE, rst.Tripod, rst.TwoXStages):
    """Combines a simple mirror with a tripod support + two X-stages."""
    def __init__(self, *args, **kwargs):
        """jack1, jack2, jack3 [lists!] are 3d points in the global coordinate
        system at the horizontal state of OE.
        tx1, tx2 [lists!] are [x, y] points in local system.
        dx is the nominal x shift of the center in local system.
        """
        kwargs, argsT = rst.Tripod.pop_kwargs(self, **kwargs)
        kwargs, argsX = rst.TwoXStages.pop_kwargs(self, **kwargs)
        OE.__init__(self, *args, **kwargs)
        rst.Tripod.__init__(self, *argsT)
        rst.TwoXStages.__init__(self, *argsX)

    def get_orientation(self):
        """Finds orientation (x, z, and 3 rotations) given two x stages and
        three jacks."""
        rst.TwoXStages.get_orientation(self)
        rst.Tripod.get_orientation(self)


class BentFlatMirror(OE):
    """Implements Vertically Collimating Mirror. Exemplifies inclusion of a new
    parameter (here, *R*) without the need of explicit repetition of all the
    parameters of the parent class."""
    def __init__(self, *args, **kwargs):
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.R = kwargs.pop('R', 5.0e6)
        return kwargs

    def local_z(self, x, y):
        """Determines the surface of OE at (x, y) position. Here: a
        meridionally bent parabolic cylinder with fixed ends and a sag at the
        center."""
        return (y**2 - self.limPhysY[0]**2) / 2.0 / self.R

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        a = 0.  # -dz/dx
        b = -y / self.R  # -dz/dy
        c = 1.
#        norm = (a**2 + b**2 + c**2)**0.5
#        return a/norm, b/norm, c/norm
        norm = (b**2 + 1)**0.5
        return a/norm, b/norm, c/norm

SimpleVCM = BentFlatMirror


class VCM(SimpleVCM, MirrorOnTripodWithTwoXStages):
    """Implements Vertically Collimating Mirror on support."""
    def __init__(self, *args, **kwargs):
        kwargs, argsT = rst.Tripod.pop_kwargs(self, **kwargs)
        kwargs, argsX = rst.TwoXStages.pop_kwargs(self, **kwargs)
        SimpleVCM.__init__(self, *args, **kwargs)
        rst.Tripod.__init__(self, *argsT)
        rst.TwoXStages.__init__(self, *argsX)


class ToroidMirror(OE):
    """Implements Vertically Focusing Mirror. Exemplifies inclusion of new
    parameters (here, *R* and *r*) without the need of explicit repetition
    of all the parameters of the parent class."""
    def __init__(self, *args, **kwargs):
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.R = kwargs.pop('R', 5.0e6)
        self.r = kwargs.pop('r', 50.)
        return kwargs

    def local_z(self, x, y):
        return y**2/2.0/self.R + self.r - (self.r**2-x**2)**0.5

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        a = -x * (self.r**2-x**2)**(-0.5)  # -dz/dx
        b = -y / self.R  # -dz/dy
        c = 1.
        norm = (a**2 + b**2 + 1)**0.5
        return a/norm, b/norm, c/norm

SimpleVFM = ToroidMirror


class VFM(SimpleVFM, MirrorOnTripodWithTwoXStages):
    """Implements Vertically Focusing Mirror with the fixed ends."""
    def __init__(self, *args, **kwargs):
        limPhysY = kwargs.get('limPhysY', None)
        if limPhysY is None:
            raise AttributeError('limPhysY must be given')
        kwargs, argsT = rst.Tripod.pop_kwargs(self, **kwargs)
        kwargs, argsX = rst.TwoXStages.pop_kwargs(self, **kwargs)
        SimpleVFM.__init__(self, *args, **kwargs)
        rst.Tripod.__init__(self, *argsT)
        rst.TwoXStages.__init__(self, *argsX)

    def local_z(self, x, y):
        """Determines the surface of OE at (x, y) position. Here: a circular
        sagittal cylinder, meridionally parabolically bent with fixed ends and
        a sag at the center."""
        z = self.r - (self.r**2 - x**2)**0.5
        if self.limOptX is not None:
            zMax = self.r - (self.r**2 - self.limOptX[1]**2)**0.5
            z[z > zMax] = zMax
        z += (y**2 - self.limPhysY[0]**2) / 2.0 / self.R
        return z

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        a = -x * (self.r**2 - x**2)**(-0.5)  # -dz/dx
        if self.limOptX is not None:
            a[(x < self.limOptX[0]) | (x > self.limOptX[1])] = 0.0  # -dz/dx
        b = -y / self.R  # -dz/dy
        c = 1.
        norm = (a**2 + b**2 + 1)**0.5
        return a/norm, b/norm, c/norm


class DualVFM(MirrorOnTripodWithTwoXStages):
    """Implements Vertically Focusing Mirror with two toroids."""
    def __init__(self, *args, **kwargs):
        """
        *r1*, *r2*: float. Sagittal radii of the cylinders.

        *xCylinder1*, *xCylinder2*: float. Local x coordinates of the cylinder
        axes.

        *hCylinder1*, *hCylinder2*: float.
        z depth of the cylinder at x = xCylinder1 and x = xCylinder2. Positive
        depth is under the nominal flat surface (local z = 0).
        """
        kwargs = self.__pop_kwargs(**kwargs)
        MirrorOnTripodWithTwoXStages.__init__(self, *args, **kwargs)
        self.hCylinder = 0

    def __pop_kwargs(self, **kwargs):
        self.R = kwargs.pop('R', 5.0e6)
        self.r1 = kwargs.pop('r1', 70.0)
        self.xCylinder1 = kwargs.pop('xCylinder1', 23.5)
        self.hCylinder1 = kwargs.pop('hCylinder1', 3.7035)
        self.r2 = kwargs.pop('r2', 35.98)
        self.xCylinder2 = kwargs.pop('xCylinder2', -25.0)
        self.hCylinder2 = kwargs.pop('hCylinder2', 6.9504)
        return kwargs

    def local_z(self, x, y):
        """Determines the surface of OE at (x, y) position. Here: two circular
        sagittal cylinders, meridionally parabolically bent with fixed ends and
        a sag at the center."""
        z = np.empty_like(x)
        ind = x < 0
        z[ind] = self.r2 - self.hCylinder2 -\
            (self.r2**2 - (x[ind] - self.xCylinder2)**2)**0.5
        z[~ind] = self.r1 - self.hCylinder1 -\
            (self.r1**2 - (x[~ind] - self.xCylinder1)**2)**0.5
        z[z > 0] = 0.
        z += (y**2 - self.limPhysY[0]**2) / 2.0 / self.R
        return z

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        ind = x < 0
        a = np.empty_like(x)
        a[ind] = -(x[ind] - self.xCylinder2) * \
            (self.r2**2 - (x[ind] - self.xCylinder2)**2)**(-0.5)  # -dz/dx
        a[~ind] = -(x[~ind] - self.xCylinder1) * \
            (self.r1**2 - (x[~ind] - self.xCylinder1)**2)**(-0.5)  # -dz/dx
        z = self.local_z(x, y)
        a[z > 0] = 0.  # -dz/dx
        b = -y / self.R  # -dz/dy
        c = 1.
        norm = (a**2 + b**2 + 1)**0.5
        return a/norm, b/norm, c/norm

    def select_surface(self, surfaceName):
        """Updates self.curSurface index and finds dx offset corresponding to
        the requested cylinder(toroid)."""
        self.curSurface = self.surface.index(surfaceName)
        if self.curSurface == 0:
            self.dx = -self.xCylinder1
            self.hCylinder = self.hCylinder1
            self.r = self.r1
        elif self.curSurface == 1:
            self.dx = -self.xCylinder2
            self.hCylinder = self.hCylinder2
            self.r = self.r2
        self.get_surface_limits()
        self.set_x_stages()


class EllipticalMirror(OE):
    """Implements elliptical mirror. The user supplies the two focal distances
    *p* and *q*. If *isCylindrical* is True, the figure is an elliptical
    cylinder, otherwise it is an ellipsoid of revolution along the major axis.
    """
    def __init__(self, *args, **kwargs):
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)
        self.get_orientation()

    def __pop_kwargs(self, **kwargs):
        self.p = kwargs.pop('p', 5000.)
        self.q = kwargs.pop('q', 5000.)
        self.isCylindrical = kwargs.pop('isCylindrical', False)
        self.pcorrected = 0
        return kwargs

    def get_orientation(self):
        if self.pcorrected and self.pitch0 != self.pitch:
            self.pcorrected = 0
        if not self.pcorrected:
            self.gamma = np.pi - 2*self.pitch
            self.ce = 0.5 * np.sqrt(self.p**2 + self.q**2
                                    - 2 * self.p * self.q * np.cos(self.gamma))
            self.ae = 0.5 * (self.p+self.q)
            self.be = np.sqrt(self.ae*self.ae - self.ce*self.ce)
            self.alpha = np.arccos((4 * self.ce**2 - self.q**2 + self.p**2) /
                                   (4*self.ce*self.p))
            self.delta = 0.5*np.pi - self.alpha - 0.5*self.gamma
            self.pitch = self.pitch - self.delta
            self.pitch0 = self.pitch
            self.pcorrected = 1

    def local_z(self, x, y):
        delta_y = self.p * np.cos(self.alpha) - self.ce
        delta_z = -self.p * np.sin(self.alpha)
        return -self.be * np.sqrt(1 - ((y+delta_y)/self.ae)**2) - delta_z

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        delta_y = self.p * np.cos(self.alpha) - self.ce
#        delta_z = -self.p*np.sin(self.alpha)
        a = 0  # -dz/dx
        b = -self.be * (y+delta_y) /\
            (np.sqrt(1 - ((y+delta_y)/self.ae)**2) * self.ae**2)  # -dz/dy
        c = 1.
        norm = (a**2 + b**2 + 1)**0.5
        return a/norm, b/norm, c/norm


class ParabolicMirror(OE):
    """Implements parabolic mirror. The user supplies the focal distance *p*.
    if *p*>0, the mirror is collimating, otherwise focusing. If *isCylindrical*
    is True, the figure is a parabolic cylinder, otherwise it is a paraboloid
    of revolution."""
    def __init__(self, *args, **kwargs):
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)
        self.get_orientation()

    def __pop_kwargs(self, **kwargs):
        """ Here 'p' means the distance between the focus and the mirror
        surface, not the parabola parameter"""
        self.p = kwargs.pop('p', 5000.)
        self.isCylindrical = kwargs.pop('isCylindrical', False)
        self.pcorrected = 0
        return kwargs

    def get_orientation(self):
        if self.pcorrected and self.pitch0 != self.pitch:
            self.pcorrected = 0
        if not self.pcorrected:
            self.alpha = np.abs(2 * self.pitch)
            self.pp = self.p * (1-np.cos(self.alpha))
            print "Parabola paremeter: " + str(self.pp)
            self.delta_y = 0.5 * self.p * (1+np.cos(self.alpha))
            self.delta_z = -np.abs(self.p) * np.sin(self.alpha)
            self.pitch = 2 * self.pitch
            self.pitch0 = self.pitch
            self.pcorrected = 1

    def local_z(self, x, y):
        return -np.sqrt(2 * self.pp * (y+self.delta_y)) - self.delta_z

    def local_n(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        #delta_y = 0.5*self.p*(1+np.cos(self.alpha))
        a = 0
        b = np.sign(self.p) * np.sqrt(0.5 * self.pp / (y+self.delta_y))
        c = 1.
        norm = np.sqrt(b**2 + 1)
        return a/norm, b/norm, c/norm


class EllipticalMirrorParam(OE):
    """The elliptical mirror is implemented as a parametric surface. The
    parameterization is the following: *s* - is local coordinate along the
    major axis with origin at the ellipse center. *phi* and *r* are local polar
    coordinates in planes normal to the major axis at every point *s*. The
    polar axis is upwards.

    The user supplies the two focal distances *p* and *q* and the *pitch*
    angle. If *isCylindrical* is True, the figure is an elliptical cylinder,
    otherwise it is an ellipsoid of revolution along the major axis.
    """
    def __init__(self, *args, **kwargs):
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)
        gamma = np.arctan2((self.p-self.q) * np.sin(self.pitch),
                           (self.p+self.q) * np.cos(self.pitch))
        self.cosGamma = np.cos(gamma)
        self.sinGamma = np.sin(gamma)
        self.y0 = (self.q-self.p) / 2. * np.cos(self.pitch)
        self.z0 = (self.q+self.p) / 2. * np.sin(self.pitch)
        self.ellipseA = (self.q+self.p) / 2.
        self.ellipseB = np.sqrt(self.q * self.p) * np.sin(self.pitch)
        self.isParametric = True

    def __pop_kwargs(self, **kwargs):
        self.p = kwargs.pop('p')  # source-to-mirror
        self.q = kwargs.pop('q')  # mirror-to-focus
        self.isCylindrical = kwargs.pop('isCylindrical', False)
        return kwargs

    def xyz_to_param(self, x, y, z):
        yNew, zNew = raycing.rotate_x(y - self.y0, z - self.z0, self.cosGamma,
                                      self.sinGamma)
        return yNew, np.arctan2(x, zNew), np.sqrt(x**2 + zNew**2)  # s, phi, r

    def param_to_xyz(self, s, phi, r):
        x = r * np.sin(phi)
        y = s
        z = r * np.cos(phi)
        yNew, zNew = raycing.rotate_x(y, z, self.cosGamma, -self.sinGamma)
        return x, yNew + self.y0, zNew + self.z0

    def local_r(self, s, phi):
        r = self.ellipseB * np.sqrt(1 - s**2 / self.ellipseA**2)
        if self.isCylindrical:
            r /= abs(np.cos(phi))
        return np.where(abs(phi) > np.pi/2, r, np.ones_like(phi)*1e20)

    def local_n(self, s, phi):
        nr = -self.ellipseB / self.ellipseA * s / \
            np.sqrt(self.ellipseA**2 - s**2)
        norm = np.sqrt(nr**2 + 1)
        b = nr / norm
        if self.isCylindrical:
            a = np.zeros_like(phi)
            c = 1. / norm
        else:
            a = -np.sin(phi) / norm
            c = -np.cos(phi) / norm
        bNew, cNew = raycing.rotate_x(b, c, self.cosGamma, -self.sinGamma)
        return a, bNew, cNew


class DCM(OE):
    """Implements a Double Crystal Monochromator with flat crystals."""
    def __init__(self, *args, **kwargs):
        """
        *bragg*: Bragg angle in rad.

        *cryst1roll*, *cryst2roll*, *cryst2pitch*, *cryst2finePitch*:
            misalignment angles in rad.

        *cryst2perpTransl*, *cryst2longTransl*: perpendicular and longitudinal
            translations of the 2nd crystal in respect to the 1st one.

        *limPhysX2*, *limPhysY2*, *limOptX2*, *limOptY2*, *material2*:
            refer to the 2nd crystal and are similar to the same parameters
            of the parent class :class:`OE` without the trailing "2".
        """
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)
        self.energyMin = rs.defaultEnergy - 5.
        self.energyMax = rs.defaultEnergy + 5.

    def __pop_kwargs(self, **kwargs):
        self.bragg = kwargs.pop('bragg', 0)
        self.cryst1roll = kwargs.pop('cryst1roll', 0)
        self.cryst2roll = kwargs.pop('cryst2roll', 0)
        self.cryst2pitch = kwargs.pop('cryst2pitch', 0)
        self.cryst2finePitch = kwargs.pop('cryst2finePitch', 0)
        self.cryst2perpTransl = kwargs.pop('cryst2perpTransl', 0)
        self.cryst2longTransl = kwargs.pop('cryst2longTransl', 0)
        self.limPhysX2 = kwargs.pop('limPhysX2', (-np.inf, np.inf))
        self.limPhysY2 = kwargs.pop('limPhysY2', (-np.inf, np.inf))
        self.limOptX2 = kwargs.pop('limOptX2', None)
        self.limOptY2 = kwargs.pop('limOptY2', None)
        self.material = kwargs.get('material', None)
        self.material2 = kwargs.pop('material2', self.material)
        return kwargs

    def get_surface_limits(self):
        """Returns surface_limits."""
        OE.get_surface_limits(self)
        cs = self.curSurface
        self.surfPhysX2 = self.limPhysX2
        if self.limPhysX2 is not None:
            if raycing.is_sequence(self.limPhysX2[0]):
                self.surfPhysX2 = (self.limPhysX2[0][cs],
                                   self.limPhysX2[1][cs])
        self.surfPhysY2 = self.limPhysY2
        if self.limPhysY2 is not None:
            if raycing.is_sequence(self.limPhysY2[0]):
                self.surfPhysY = (self.limPhysY2[0][cs], self.limPhysY2[1][cs])
        self.surfOptX2 = self.limOptX2
        if self.limOptX2 is not None:
            if raycing.is_sequence(self.limOptX2[0]):
                self.surfOptX = (self.limOptX2[0][cs], self.limOptX2[1][cs])
        self.surfOptY2 = self.limOptY2
        if self.limOptY2 is not None:
            if raycing.is_sequence(self.limOptY2[0]):
                self.surfOptY = (self.limOptY2[0][cs], self.limOptY2[1][cs])

    def local_z1(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        # just flat:
        return self.local_z(x, y)

    def local_z2(self, x, y):
        return self.local_z1(x, y)

    def local_n1(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        # just flat:
        return self.local_n(x, y)

    def local_n2(self, x, y):
        return self.local_n1(x, y)

    def double_reflect(self, beam, needLocal=True,
                       fromVacuum1=True, fromVacuum2=True):
        """Returns the reflected beam in global and two local (if *needLocal*
        is true) systems."""
        self.get_orientation()
        gb = rs.Beam(copyFrom=beam)  # output beam in global coordinates
        if needLocal:
            lo1 = rs.Beam(copyFrom=beam)  # output beam in local coordinates
            lo2 = rs.Beam(copyFrom=beam)  # output beam in local coordinates
        else:
            lo1 = gb
            lo2 = gb

        good1 = beam.state > 0
        if good1.sum() == 0:
            return gb, lo1, lo2
        raycing.global_to_virgin_local(self.bl, beam, lo1, self.center, good1)
#bring to local system of 1st crystal:
        raycing.rotate_beam(lo1, good1, way=1,
                            pitch=-(self.pitch + self.bragg),
                            roll=-self.roll-self.positionRoll, yaw=-self.yaw)

        self._reflect_local(
            good1, lo1, gb, 0, self.cryst1roll, 0, self.dx,
            local_z=self.local_z1, local_n=self.local_n1,
            fromVacuum=fromVacuum1, material=self.material)
        goodAfter1 = (gb.state == 1) | (gb.state == 2)
#not intersected rays remain unchanged except their state:
        notGood = ~goodAfter1
        if notGood.sum() > 0:
            rs.copy_beam(gb, beam, notGood)

        good2 = gb.state > 0
        if good2.sum() == 0:
            return gb, lo1, lo2
        gb.y[good2] -= self.cryst2longTransl
        gb.z[good2] -= self.cryst2perpTransl
        if needLocal:
            rs.copy_beam(lo2, gb, good2, includeState=True)
        self._reflect_local(
            good2, lo2, gb, self.cryst2pitch + self.cryst2finePitch,
            self.cryst2roll + np.pi, 0, -self.dx, local_z=self.local_z2,
            local_n=self.local_n2, fromVacuum=fromVacuum2,
            material=self.material2, is2ndXtal=True)
        gb.y[good2] += self.cryst2longTransl
        gb.z[good2] += self.cryst2perpTransl
        goodAfter2 = (gb.state == 1) | (gb.state == 2)
        raycing.rotate_beam(
            gb, goodAfter2, way=-1, pitch=(self.pitch + self.bragg),
            roll=self.roll+self.positionRoll, yaw=self.yaw)
#in global coordinate system:
        raycing.virgin_local_to_global(self.bl, gb, self.center, goodAfter2)
#not intersected rays remain unchanged except their state:
        notGood = ~goodAfter2
        if notGood.sum() > 0:
            rs.copy_beam(gb, beam, notGood)
        return gb, lo1, lo2  # in global(gb) and local(lo1 and lo2) coordinates


class DCMOnTripodWithOneXStage(DCM, rst.Tripod, rst.OneXStage):
    """Combines a DCM with a tripod support + one X-stage."""
    def __init__(self, *args, **kwargs):
        """*jack1*, *jack2*, *jack3* [lists!] are 3d points in the *general*
        coordinate system at the horizontal state of OE.
        *dx* is the nominal *x* shift of the center in local system.
        """
        kwargs, argsT = rst.Tripod.pop_kwargs(self, **kwargs)
        kwargs, argsX = rst.OneXStage.pop_kwargs(self, **kwargs)
        DCM.__init__(self, *args, **kwargs)
        rst.Tripod.__init__(self, *argsT)
        rst.OneXStage.__init__(self, *argsX)

        for alim in (self.limOptX2, self.limOptY2):
            if alim is not None:
                if not (raycing.is_sequence(alim[0]) and
                        raycing.is_sequence(alim[1])):
                    raise ValueError('"limOptX" must be a tuple of sequences!')
                if not (len(alim[0]) == len(alim[1]) == len(self.surface)):
                    raise ValueError(
                        'len(self.limOptX[0,1]) != len(surface) !!!')

        for alim in (self.limPhysX2[0], self.limPhysX2[1],
                     self.limPhysY2[0], self.limPhysY2[1]):
            if raycing.is_sequence(alim):
                if len((self.surface)) != len(alim):
                    raise ValueError(
                        'length of "surface" and "limPhys..." must be equal!')

    def get_orientation(self):
        """Finds orientation (x, z and 3 rotations) given one x stage and
        three jacks."""
        rst.Tripod.get_orientation(self)


class Plate(DCM):
    """Implements a body with two surfaces. Is derived from :class:`DCM`
    because it also has two interfaces but the parameters referring to the 2nd
    crystal should be ignored."""
    def __init__(self, *args, **kwargs):
        """*t* is thickness in mm."""
        kwargs = self.__pop_kwargs(**kwargs)
        DCM.__init__(self, *args, **kwargs)
        self.cryst2perpTransl = -self.t
        self.material2 = self.material

    def __pop_kwargs(self, **kwargs):
        self.t = kwargs.pop('t', 0)  # difference of z zeros in mm
        return kwargs

    def double_refract(self, beam, needLocal=True):
        """Returns the refracted beam in global and two local (if *needLocal*
        is true) systems."""
        self.cryst2perpTransl = -self.t
        return self.double_reflect(beam, needLocal, fromVacuum1=True,
                                   fromVacuum2=False)


class ParaboloidFlatLens(Plate):
    """Implements a refractive lens with one side parabolic and the other one
    flat."""
    def __init__(self, *args, **kwargs):
        """*focus* the focal distance of the of paraboloid in mm. The
        paraboloid is then defined by the equation:

        .. math::
            z = (x^2 + y^2) / (4 * focus)

        *zmax*, if given, limits the *z* coordinate; the object becomes then a
        plate of the thickness :math:`zmax + t` with a paraboloid hole at the
        origin.
        """
        kwargs = self.__pop_kwargs(**kwargs)
        Plate.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.focus = kwargs.pop('focus', 1.)
        self.zmax = kwargs.pop('zmax', None)
        return kwargs

    def local_z1(self, x, y):
        """Determines the normal vector of OE at (x, y) position."""
        z = (x**2 + y**2) / (4 * self.focus)
        if self.zmax is not None:
            z[z > self.zmax] = self.zmax
        return z

    def local_z2(self, x, y):
        """Determines the surface of OE at (x, y) position."""
        return 0  # just flat

    def local_n1(self, x, y):
        """Determines the normal vector of OE at (x, y) position. If OE is an
        asymmetric crystal, *local_n* must return 2 normals: the 1st one of the
        atomic planes and the 2nd one of the surface."""
        # just flat:
        a = -x / (2*self.focus)  # -dz/dx
        b = -y / (2*self.focus)  # -dz/dy
        if self.zmax is not None:
            z = (x**2 + y**2) / (4*self.focus)
            if isinstance(a, np.ndarray):
                a[z > self.zmax] = 0
            if isinstance(b, np.ndarray):
                b[z > self.zmax] = 0
        c = np.ones_like(x)
        norm = (a**2 + b**2 + 1)**0.5
        return a/norm, b/norm, c/norm

    def local_n2(self, x, y):
        return self.local_n(x, y)


class ParabolicCylinderFlatLens(ParaboloidFlatLens):
    """Implements a refractive lens with one side as parabolic cylinder and
    the other one flat."""
    def local_z1(self, x, y):
        return ParaboloidFlatLens.local_z1(self, 0, y)

    def local_n1(self, x, y):
        return ParaboloidFlatLens.local_n1(self, 0, y)


class DoubleParaboloidLens(ParaboloidFlatLens):
    """Implements a refractive lens with two equal paraboloids from both
    sides."""
    def local_z2(self, x, y):
        return self.local_z1(x, y)

    def local_n2(self, x, y):
        return self.local_n1(x, y)

#class ConvConcParaboloidLens(ParaboloidFlatLens):
#    def local_z2(self, x, y):
#        return -self.local_z1(x, y)
#
#    def local_n2(self, x, y):
#        n1 = self.local_n1(x, y)
#        return -n1[0], -n1[1], n1[2]


class SurfaceOfRevolution(OE):
    """Base class for parametric surfaces of revolution. The parameterization
    implements cylindrical coordinates, where *s* is *y* (along the beamline),
    and *phi* and *r* are polar coordinates in planes normal to *s*."""
    def get_surface_limits(self):
        self.isParametric = True
        OE.get_surface_limits(self)

    def xyz_to_param(self, x, y, z):
        return y, np.arctan2(x, z), np.sqrt(x**2 + z**2)  # s, phi, r

    def param_to_xyz(self, s, phi, r):
        return r * np.sin(phi), s, r * np.cos(phi)  # x, y, z


class NormalFZP(OE):
    """Implements a circular Fresnel Zone Plate, as it is described in
    X-Ray Data Booklet, Section 4.4.
    """
    def __init__(self, *args, **kwargs):
        """*f* (mm) is the focal distance calculated for waves of energy *E*
        (eV). The number of zones is given either by *N* or calculated from
        *thinnestZone* (mm). If *isCentralZoneBlack* is False, the zones are
        inverted. The diffraction order (can be a sequence) is given by
        *order*."""
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        from scipy import interpolate
        f = kwargs.pop('f')
        E = kwargs.pop('E')
        N = kwargs.pop('N', 1000)
        self.isCentralZoneBlack = kwargs.pop('isCentralZoneBlack', True)
        thinnestZone = kwargs.pop('thinnestZone', None)
        lambdaE = rm.ch / E * 1e-7
        if thinnestZone is not None:
            N = lambdaE * f / 4. / thinnestZone**2
        self.zones = np.arange(N+1)
        self.rn = np.sqrt(self.zones*f*lambdaE + 0.25*(self.zones*lambdaE)**2)
        if _DEBUG:
            print self.rn
            print f, N
            print 'R(N)={0}, dR(N)={1}'.format(
                self.rn[-1], self.rn[-1]-self.rn[-2])
        self.r_to_i = interpolate.interp1d(self.rn, self.zones,
                                           bounds_error=False, fill_value=0)
        self.i_to_r = interpolate.interp1d(self.zones, self.rn,
                                           bounds_error=False, fill_value=0)
#        self.drn = self.rn[1:] - self.rn[:-1]
        return kwargs

    def rays_good(self, x, y, is2ndXtal=False):
        """Returns *state* value as inherited from :class:`OE`. The rays that
        fall inside the screening zones are additionally considered as lost."""
        locState = OE.rays_good(self, x, y, is2ndXtal)
        r = np.sqrt(x**2 + y**2)
        i = (self.r_to_i(r)).astype(int)
        good = (i % 2 == int(self.isCentralZoneBlack)) & (r < self.rn[-1])
        locState[~good] = self.lostNum
        gz = np.zeros_like(x[good])

        rho = 1./(self.i_to_r(i[good]+1) - self.i_to_r(i[good]-1))
        gx = -x[good] / r[good] * rho
        gy = -y[good] / r[good] * rho
        gn = gx, gy, gz
        return locState, gn


class GeneralFZPin0YZ(OE):
    """Implements a general Fresnel Zone Plate, where the zones are determined
    by two foci and the surface shape of the OE.
    """
    def __init__(self, *args, **kwargs):
        """*f1* and *f2* are the two foci given by 3-sequences representing 3D
        points in _local_ coordinates or 'inf' for infinite position. The zones
        are calculated for waves of energy *E* (eV). The number of zones is
        *N*. The zones can be phase shifted by 'phaseShift'; if it is 0, the
        central zone is at the constructive interference. The diffraction order
        (can be a sequence if several orders are needed) is given by *order*.
        """
        kwargs = self.__pop_kwargs(**kwargs)
        OE.__init__(self, *args, **kwargs)

    def __pop_kwargs(self, **kwargs):
        self.f1 = kwargs.pop('f1')  # in local coordinates!!!
        self.f2 = kwargs.pop('f2')  # in local coordinates!!!
        E = kwargs.pop('E')
        self.N = kwargs.pop('N', 1000)
        self.lambdaE = rm.ch / E * 1e-7
        phaseShift = kwargs.pop('phaseShift', 0)
        self.set_phase_shift(phaseShift)
        return kwargs

    def set_phase_shift(self, phaseShift):
        if phaseShift:
            phaseShift /= np.pi
        z = self.local_z(0, 0)
        d1 = 0 if isinstance(self.f1, str) else\
            raycing.distance_xyz([0, 0, z], self.f1)
        d2 = 0 if isinstance(self.f2, str) else\
            raycing.distance_xyz([0, 0, z], self.f2)
        self.poleHalfLambda = (d1+d2) / (self.lambdaE/2) - phaseShift

    def rays_good(self, x, y, is2ndXtal=False):
        locState = OE.rays_good(self, x, y, is2ndXtal)
        z = self.local_z(x, y)
        d1 = y * np.cos(self.pitch) if isinstance(self.f1, str) else\
            raycing.distance_xyz([x, y, z], self.f1)
        d2 = y * np.cos(self.pitch) if isinstance(self.f2, str) else\
            raycing.distance_xyz([x, y, z], self.f2)
        halfLambda = (d1+d2) / (self.lambdaE/2) - self.poleHalfLambda

        zone = np.floor(halfLambda).astype(np.int64)
        N = 0
        while N < self.N:
            if (zone == (N+1)).sum() == 0:
                break
            N += 1
        good = (zone % 2 == 0) & (zone < N)
        locState[~good] = self.lostNum

        a = np.zeros(N+1)
        b = np.zeros(N+1)
        for i in range(1, N+1, 2):
#            if (zone == i).sum() == 0: continue
            a[i] = max(abs(x[zone == i]))
            b[i] = max(abs(y[zone == i]))

        gz = np.zeros_like(x[good])
        r = np.sqrt(x[good]**2 + y[good]**2)
        l = (x[good]**2 / (a[zone[good]+1]-a[zone[good]-1]) +
             y[good]**2 / (b[zone[good]+1]-b[zone[good]-1])) / r**2
        gx = -x[good] * l / r
        gy = -y[good] * l / r

        gn = gx, gy, gz
        return locState, gn
