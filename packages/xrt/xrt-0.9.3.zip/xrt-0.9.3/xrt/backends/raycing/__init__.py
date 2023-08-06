# -*- coding: utf-8 -*-
"""
Package :mod:`~xrt.backends.raycing` provides the internal backend of xrt. It
defines beam sources in the module :mod:`~xrt.backends.raycing.sources`,
rectangular and round apertures in :mod:`~xrt.backends.raycing.apertures`,
optical elements in :mod:`~xrt.backends.raycing.oes`, material properties
(essentially reflectivity, transmittivity and absorption coefficient) for
interfaces and crystals in :mod:`~xrt.backends.raycing.materials` and screens
in :mod:`~xrt.backends.raycing.screens`.

.. _scriptingRaycing:

Coordinate systems
------------------

The following coordinate systems are considered (always right-handed):

1) *The global coordinate system*. It is arbitrary (user-defined) with one
   requirement driven by code simplification: Z-axis is vertical. For example,
   the system origin of Alba synchrotron is in the center of the ring at the
   ground level with Y-axis northward, Z upright and the units in mm. The
   positions of all optical elements, sources, screens etc. are given in the
   global coordinate system. This feature simplifies the beamline alignment
   when 3D CAD models are available.

2) *The local systems*.

   a) *of the beamline*. The local Y direction (the direction of the source)
      is determined by *azimuth* parameter of
      :class:`~xrt.backends.raycing.BeamLine` -- the angle measured cw from the
      global Y axis. The local beamline Z is also vertical and upward. The
      local beamline X is to the right. At *azimuth* = 0 the global system and
      the local beamline system are parallel to each other.

   b) *of an optical element*. The origin is on the optical surface. Z is
      out-of-surface. At pitch, roll and yaw all zeros the local oe system
      and the local beamline system are parallel to each other. Pitch, roll
      and yaw rotations (correspondingly: Rx, Ry and Rz) are defined relative
      to the beamline local axes. The user-supplied functions for the surface
      height (z) and the normal as functions of (x, y) are defined in the local
      oe system.

   c) *of other beamline elements: sources, apertures, screens*. Z is upward
      and Y is along the beam line. The origin is given by the user and
      normally is on the original beam line.

Units
-----

For the internal calculations, lengths are assumed to be in mm, although for
reflection geometries and simple Bragg cases (thick crystals) this convention
is not used. Angles are unitless (radians). Energy is in eV.

For plotting, the user may select units and conversion factors.

Beam categories
---------------

xrt discriminates rays by several categories:

a) ``good``: reflected within the working optical surface;
b) ``out``: reflected outside of the working optical surface, i.e. outside of
   a metal stripe on a mirror;
c) ``over``: propagated over the surface without intersection;
d) ``dead``: arrived below the optical surface and thus absorbed by the OE.

This distinction simplifies the adjustment of entrance and exit slits. The
user supplies `physical` and `optical` limits, where the latter is used to
define the ``out`` category (for rays between `physical` and `optical` limits).
An alarm is triggered if the fraction of dead rays exceeds a specified level.

Scripting in python
-------------------

The user of :mod:`~xrt.backends.raycing` must do the following:

1) Instantiate class :class:`~xrt.backends.raycing.BeamLine` and fill it with
   optical elements -- descendants of class
   :class:`~xrt.backends.raycing.oes.OE`).
2) Create a module-level function that returns a dictionary of beams -- the
   instances of :class:`~xrt.backends.raycing.sources.Beam`. Assign this
   function to the variable xrt.backends.raycing.run.run_process. The beams
   should be obtained by the methods shine() of a source, expose() of a
   screen, reflect() or multiple_reflect() of an optical element, propagate()
   of an aperture.
3) Use the keys in this dictionary for creating the plots (instances of
   :class:`~xrt.plotter.XYCPlot`). Note that at the time of instantiation the
   plots are just empty placeholders for the future 2D and 1D histograms.
4) Run :func:`~xrt.runner.run_ray_tracing()` function for the created plots.

Additionally, the user may define a generator that will run a loop of ray
tracing for changing geometry (mimics a real scan) or for different material
properties etc. The generator should modify the beamline elements and output
file names of the plots before *yield*. After the *yield* the plots are ready
and the generator may use their fields, e.g. *intensity* or *dE* to prepare a
scan plot. Typically, this sequence is within a loop; after the loop the user
may prepare the final scan plot using matplotlib functionality. The generator
is given to :func:`~xrt.runner.run_ray_tracing()` as a parameter.

See the supplied examples, with the simplest one in `demo.py`."""

__module__ = "raycing"
__author__ = "Konstantin Klementiev"
__date__ = "22 Apr 2014"

#import copy
import types
import numpy as np

#import psyco  #!!!psyco speeds it up!!!
#psyco.full()
#psyco.full(memory=200)
#psyco.profile(0.05, memory=200)

elec_e = 1.602176462e-19
zEps = 1e-12  # mm: target accuracy in z while searching for intersection
misalignmentTolerated = 0.1  # for automatic checking of oe center position
accuracyInPosition = 0.1  # accuracy for positioning of oe
dt = zEps  # mm: margin around OE within which the intersection is searched
ds = 0.  # mm: margin used in multiple reflections
nrays = 100000
maxIteration = 100  # max number of iterations while searching for intersection
maxHalfSizeOfOE = 1000.
maxDepthOfOE = 100.
#maxZDeviationAtOE = 100.

#colors of the rays in a 0-10 range (red-violet)
hueGood = 3.
hueOut = 8.
hueOver = 1.6
hueDead = 0.2
hueMin = 0.
hueMax = 10.


def is_sequence(arg):
    """Checks whether *arg* is a sequence."""
    result = (not hasattr(arg, "strip") and hasattr(arg, "__getitem__") or
              hasattr(arg, "__iter__"))
    if result:
        try:
            arg[0]
        except IndexError:
            result = False
    return result


def distance_xy(p1, p2):
    """Calculates 2D distance between p1 and p2. p1 and p2 are vectors of
    length >= 2."""
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5


def distance_xyz(p1, p2):
    """Calculates 2D distance between p1 and p2. p1 and p2 are vectors of
    length >= 3."""
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)**0.5


def rotate_x(y, z, cosangle, sinangle):
    """3D rotaion around *x* (pitch). *y* and *z* are values or arrays.
    Positive rotation is for positive *sinangle*. Returns *yNew, zNew*."""
    return cosangle*y - sinangle*z, sinangle*y + cosangle*z


def rotate_y(x, z, cosangle, sinangle):
    """3D rotaion around *y* (roll). *x* and *z* are values or arrays.
    Positive rotation is for positive *sinangle*. Returns *xNew, zNew*."""
    return cosangle*x + sinangle*z, -sinangle*x + cosangle*z


def rotate_z(x, y, cosangle, sinangle):
    """3D rotaion around *z*. *x* and *y* are values or arrays.
    Positive rotation is for positive *sinangle*. Returns *xNew, yNew*."""
    return cosangle*x - sinangle*y, sinangle*x + cosangle*y


def rotate_beam(beam, indarr=None, way=1, pitch=0, roll=0, yaw=0,
                skip_xyz=False, skip_abc=False):
    """Rotates the *beam* indexed by *indarr* by the angles *yaw, roll, pitch*
    in the direct transform (when *way* = 1) and in the reverse sequence of the
    angles in the back transform (when *way* != 1).
    """
#the sequence pitch-roll-yaw cannot give a desired pitch at horizontal
#deflection (roll=pi/2). Therefore the direct sequence is yaw-roll-pitch.
    if way == 1:  # direct
        angles = (yaw, roll, pitch)
        rotates = (rotate_z, rotate_y, rotate_x)
        coords1 = (beam.x, beam.x, beam.y)
        coords2 = (beam.y, beam.z, beam.z)
        vcomps1 = (beam.a, beam.a, beam.b)
        vcomps2 = (beam.b, beam.c, beam.c)
    else:  # back
        angles = (pitch, roll, yaw)
        rotates = (rotate_x, rotate_y, rotate_z)
        coords1 = (beam.y, beam.x, beam.x)
        coords2 = (beam.z, beam.z, beam.y)
        vcomps1 = (beam.b, beam.a, beam.a)
        vcomps2 = (beam.c, beam.c, beam.b)
    for angle, rotate, coord1, coord2, vcomp1, vcomp2 in\
            zip(angles, rotates, coords1, coords2, vcomps1, vcomps2):
        if angle != 0:
            cosAngle = np.cos(angle)
            sinAngle = np.sin(angle)
            if indarr is None:
                indarr = slice(None)
            if not skip_xyz:
                coord1[indarr], coord2[indarr] =\
                    rotate(coord1[indarr], coord2[indarr], cosAngle, sinAngle)
            if not skip_abc:
                vcomp1[indarr], vcomp2[indarr] =\
                    rotate(vcomp1[indarr], vcomp2[indarr], cosAngle, sinAngle)


def global_to_virgin_local(bl, beam, lo, center=None, part=None):
    """Transforms *beam* from the global to the virgin (i.e. with pitch, roll
    and yaw all zeros) local system. The resulting local beam is *lo*. If
    *center* is provided, the rotation Rz is about it, otherwise is about the
    origin of *beam*. The beam arrays can be sliced by *part* indexing array.
    *bl* is an instance of :class:`BeamLine`"""
    if part is None:
        part = np.ones(beam.x.shape, dtype=np.bool)
    a0, b0 = bl.sinAzimuth, bl.cosAzimuth
    if center is not None:
        lo.x[part] = beam.x[part] - center[0]
        lo.y[part] = beam.y[part] - center[1]
        lo.z[part] = beam.z[part] - center[2]
    else:
        lo.x[part] = beam.x[part]
        lo.y[part] = beam.y[part]
        lo.z[part] = beam.z[part]
    if a0 == 0:
        lo.a[part] = beam.a[part]
        lo.b[part] = beam.b[part]
    else:
        lo.x[part], lo.y[part] = rotate_z(lo.x[part], lo.y[part], b0, a0)
        lo.a[part], lo.b[part] = rotate_z(beam.a[part], beam.b[part], b0, a0)
    lo.c[part] = beam.c[part]  # unchanged


def virgin_local_to_global(bl, vlb, center=None, part=None):
    """Transforms *vlb* from the virgin (i.e. with pitch, roll and yaw all
    zeros) local to the global system and overwrites the result to *vlb*. If
    *center* is provided, the rotation Rz is about it, otherwise is about the
    origin of *beam*. The beam arrays can be sliced by *part* indexing array.
    *bl* is an instance of :class:`BeamLine`"""
    if part is None:
        part = np.ones(vlb.x.shape, dtype=np.bool)
    a0, b0 = bl.sinAzimuth, bl.cosAzimuth
    if a0 != 0:
        vlb.a[part], vlb.b[part] = rotate_z(vlb.a[part], vlb.b[part], b0, -a0)
        vlb.x[part], vlb.y[part] = rotate_z(vlb.x[part], vlb.y[part], b0, -a0)
    if center is not None:
        vlb.x[part] += center[0]
        vlb.y[part] += center[1]
        vlb.z[part] += center[2]


def check_alarm(self, incoming, beam):
    """Appends an alarm string to the list of beamline alarms if the alarm
    condition is fulfilled."""
    incomingSum = incoming.sum()
    if incomingSum > 0:
        badSum = (beam.state == self.lostNum).sum()
        ratio = float(badSum)/incomingSum
        if ratio > self.alarmLevel:
            alarmStr = ('{0}{1} absorbes {2:.2%} of rays ' +
                        'at {3:.0%} alarm level!').format(
                'Alarm! ', self.name, ratio, self.alarmLevel)
            self.bl.alarms.append(alarmStr)
    else:
        self.bl.alarms.append('no incident rays to {0}!'.format(self.name))
#        print self.name
#        raise


def get_x(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.x


def get_y(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.y


def get_z(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.z


def get_s(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.s


def get_phi(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.phi


def get_r(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.r


def get_xprime(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.a / beam.b


def get_zprime(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.c / beam.b


def get_path(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.path


def get_order(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.order if hasattr(beam, 'order') else np.ones_like(beam.state)


def get_energy(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.E


def get_reflection_number(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.nRefl  # if hasattr(beam, 'nRefl') else beam.state


def get_elevation_d(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.elevationD
# if hasattr(beam, 'elevationD') else np.zeros_like(beam.x)


def get_elevation_x(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.elevationX  # if hasattr(beam, 'elevationX') else beam.x


def get_elevation_y(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.elevationY  # if hasattr(beam, 'elevationY') else beam.y


def get_elevation_z(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.elevationZ  # if hasattr(beam, 'elevationZ') else beam.z


def get_polarization_degree(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    I = (beam.Jss + beam.Jpp)
    I[I <= 0] = 1.
    pd = np.sqrt((beam.Jss-beam.Jpp)**2 + 4.*abs(beam.Jsp)**2) / I
    pd[I <= 0] = 0.
    return pd


def get_ratio_ellipse_axes(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    dI2 = (beam.Jss - beam.Jpp)**2
    return 2. * beam.Jsp.imag /\
        (np.sqrt(dI2 + 4*abs(beam.Jsp)**2) + np.sqrt(dI2 + 4*beam.Jsp.real**2))


def get_circular_polarization_rate(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    I = (beam.Jss + beam.Jpp)
    I[I <= 0] = 1.
    cpr = 2. * beam.Jsp.imag / I
    cpr[I <= 0] = 0.
    return cpr


def get_polarization_psi(beam):
    """Angle between the semimajor axis of the polarization ellipse relative to
    the s polarization. Used for retrieving data for x-, y- or c-axis of a
    plot."""
#    return 0.5 * np.arctan2(2.*beam.Jsp.real, beam.Jss-beam.Jpp) * 180 / np.pi
    return 0.5 * np.arctan2(2.*beam.Jsp.real, beam.Jss-beam.Jpp)


def get_phase_shift(beam):  # in units of pi!
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return np.angle(beam.Jsp) / np.pi


def get_incidence_angle(beam):
    """Used for retrieving data for x-, y- or c-axis of a plot."""
    return beam.theta if hasattr(beam, 'theta') else np.zeros_like(beam.x)


def get_output(plot, beamsReturnedBy_run_process):
    """Used by :mod:`multipro` for creating images of *plot* - instance of
    :class:`XYCPlot`. *beamsReturnedBy_run_process* is a dictionary of
    :class:`Beam` instances returned by user-defined :func:`run_process`.

    :func:`get_output` creates an indexing array corresponding to the requested
    properties of rays in *plot*. It also calculates the number of rays with
    various properties defined in `raycing` backend.
     """
    beam = beamsReturnedBy_run_process[plot.beam]
    if plot.beamState is None:
        beamState = beam.state
    else:
        beamState = beamsReturnedBy_run_process[plot.beamState].state

    if hasattr(beam, 'displayAsAbsorbedPower'):
        plot.displayAsAbsorbedPower = True
    nrays = len(beam.x)
    if isinstance(plot.xaxis.data, types.FunctionType):
        x = plot.xaxis.data(beam) * plot.xaxis.factor
    elif isinstance(plot.xaxis.data, np.ndarray):
        x = plot.xaxis.data * plot.xaxis.factor
    else:
        raise ValueError('cannot find data for x!')
    if isinstance(plot.yaxis.data, types.FunctionType):
        y = plot.yaxis.data(beam) * plot.yaxis.factor
    elif isinstance(plot.yaxis.data, np.ndarray):
        y = plot.yaxis.data * plot.yaxis.factor
    else:
        raise ValueError('cannot find data for y!')
    if plot.caxis.useCategory:
        cData = np.zeros_like(beamState)
        cData[beamState == 1] = hueGood
        cData[beamState == 2] = hueOut
        cData[beamState == 3] = hueOver
        cData[beamState < 0] = hueDead
        flux = np.ones_like(x)
    else:
        if plot.beamC is None:
            beamC = beam
        else:
            beamC = beamsReturnedBy_run_process[plot.beamC]
        if isinstance(plot.caxis.data, types.FunctionType):
            cData = plot.caxis.data(beamC) * plot.caxis.factor
        elif isinstance(plot.caxis.data, np.ndarray):
            cData = plot.caxis.data * plot.caxis.factor
        else:
            raise ValueError('cannot find data for cData!')

        if plot.fluxKind.startswith('power'):
            flux = (beam.Jss + beam.Jpp) *\
                beam.E * beam.accepted / beam.seeded * elec_e
        elif plot.fluxKind.startswith('s'):
            flux = beam.Jss
        elif plot.fluxKind.startswith('p'):
            flux = beam.Jpp
        elif plot.fluxKind.startswith('+-45'):
            flux = 2*beam.Jpp.real
        elif plot.fluxKind.startswith('left-right'):
            flux = 2*beam.Jpp.imag
        else:
            flux = beam.Jss + beam.Jpp

    locAlive = (beamState > 0).sum()
    part = np.zeros(nrays, dtype=np.bool)
    locGood = 0
    locOut = 0
    locOver = 0
    locDead = 0
    for rayFlag in plot.rayFlag:
        locPart = beamState == rayFlag
        if rayFlag == 1:
            locGood = locPart.sum()
        if rayFlag == 2:
            locOut = locPart.sum()
        if rayFlag == 3:
            locOver = locPart.sum()
        if rayFlag < 0:
            locDead += locPart.sum()
        part = part | locPart
    if hasattr(beam, 'accepted'):
        locAccepted = beam.accepted
        locAcceptedE = beam.acceptedE
        locSeeded = beam.seeded
    else:
        locAccepted = 0
        locAcceptedE = 0
        locSeeded = 0
    if hasattr(beam, 'fieldKirchhoffS'):
        locFieldKirchhoffS = beam.fieldKirchhoffS
        locFieldKirchhoffP = beam.fieldKirchhoffP
        locFieldKirchhoffN = beam.fieldKirchhoffN
    else:
        locFieldKirchhoffS, locFieldKirchhoffP, locFieldKirchhoffN = 0., 0., 0.

    return x[part], y[part], flux[part], cData[part], nrays, locAlive,\
        locGood, locOut, locOver, locDead, locAccepted, locAcceptedE,\
        locSeeded, locFieldKirchhoffS, locFieldKirchhoffP, locFieldKirchhoffN


class BeamLine(object):
    """Container class for beamline components. It also defines the beam line
    direction and height"""
    def __init__(self, azimuth=0., height=1400.0):
        """
        *azimuth* is counted in cw direction from the global Y axis. At
        *azimuth* = 0 the local Y coincides with the global Y."""
        self.azimuth = azimuth
        self.sinAzimuth = np.sin(azimuth)  # a0
        self.cosAzimuth = np.cos(azimuth)  # b0
        self.height = height
        self.sources = []
        self.oes = []
        self.slits = []
        self.screens = []
        self.alarms = []
