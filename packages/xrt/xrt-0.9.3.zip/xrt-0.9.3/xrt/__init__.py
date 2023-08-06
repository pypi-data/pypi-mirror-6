# -*- coding: utf-8 -*-
"""Package xrt (XRayTracer) is a python software library for ray tracing in
x-ray regime. It is primarily meant for modeling synchrotron beamlines and
beamline elements.

+---------+-----------+--------------------+
| |IpPol| | |MontelM| | |vcmSi-FootprintP| |
+---------+-----------+--------------------+

.. |IpPol| image:: _images/IpPol.swf
   :alt: Undulator source vs. (x', z', E), vertical polarization
   :width: 321
   :height: 164
.. |MontelM| image:: _images/MontelP_n.png
   :alt: Reflection from Montel mirror
   :scale: 40 %
.. |vcmSi-FootprintP| image:: _images/vcmSi-FootprintP.swf
   :alt: Absorbed power and power density on a mirror at varying pitch angle
   :width: 248
   :height: 164

Why another ray tracing program?
--------------------------------

Indeed, there are several good programs for ray tracing, like `Shadow`, `Ray`,
`McXtrace`. These have been extremely useful in modeling synchrotron beamlines
and/or individual beamline components. However, they all have the following
drawbacks:

* Limited graphical output, where the images are composed of dots representing
  individual rays. A color map, if ever implemented, can encode a physical
  property *not* weighted with intensity (unless it is intensity itself).

* The choice of surface shapes is very limited. Closed shapes, like wave-guides
  or capillaries, are not possible.

* Multiple reflections at a single surface, as it happens in a multi-bounce
  capillary, are not possible.

* Non-sequential optical elements, as poly-capillaries or multi-mirror arrays,
  are not possible.

* There are many restrictive limitations on energy range and energy mesh
  points, spatial mesh size etc.

* The execution cannot be parallelized (except may be in `McXtrace`).

The above issues are resolved in xrt.

Features of xrt
---------------

* *Publication quality graphics*. 1D and 2D position histograms are
  *simultaneously* coded by hue and brightness. Typically, colors represent
  energy and brightness represents beam intensity. The user may select other
  quantities to be encoded by colors: angular and positional distributions,
  various polarization properties, beam categories, number of reflections,
  incidence angle etc. Brightness can also encode partial flux for a selected
  polarization and incident or absorbed power. Publication quality plots are
  provided by `matplotlib <http://matplotlib.org>`_ with image formats PNG,
  PostScript, PDF, SVG.

* *Unlimited number of rays*. The colored histograms are *cumulative*. The
  accumulation can be stopped and resumed.

* *Parallel execution*. xrt can be run :ref:`in parallel <tests>` in several
  threads or processes (can be opted), which accelerates the execution on
  multi-core computers. It can run on an external server (supercomputer), also
  without X window system (X11) support.

* *Scripting in Python*. xrt can be run within Python scripts to generate a
  series of images under changing geometrical or physical parameters. The image
  brightness and 1D histograms can be normalized to the global maximum
  throughout the series.

* *Sources*. xrt can have several light sources. For example, an ID beamline
  has 3 sources: one ID and two BM. This feature allows exploring the influence
  of out-of-focus sources.

* :ref:`Synchrotron sources <synchrotron-sources>`. Bending magnet, wiggler,
  undulator and elliptic undulator are calculated internally within xrt. There
  is also a legacy approach to sampling synchrotron sources using the codes
  `ws` and `urgent` which are parts of XOP package. Please look the section
  :ref:`comparison-synchrotron-sources` for the comparison between the
  implementations. If the photon source is one of the synchrotron sources, the
  total flux in the beam is reported not just in number of rays but in physical
  units of ph/s. The total power or absorbed power can be opted instead of flux
  and is reported in W. The power density can be visualized by isolines.
  Tapering of the magnetic gap has been added (0.9.2). Undulators can now be
  :ref:`calculated on GPU <calculations_on_GPU>`, with a high gain in
  computation speed (0.9.2).

* *Shapes*. There are several predefined shapes of optical elements implemented
  as python classes. The inheritance mechanism simplifies creation of other
  shapes. The user specifies methods for the surface and the surface normal.
  For asymmetric crystals, the normal to the atomic planes can be additionally
  given. The surface and the normals are defined either in local (x, y)
  coordinates or in user-defined parametric coordinates. Parametric
  representation enables closed shapes like capillaries. The methods of finding
  the intersections of rays with the surface are very robust and can cope with
  pathological cases like sharp surface kinks. Any surface can be combined with
  a (differently and variably oriented) crystal structure and/or (variable)
  grating vector. Surfaces can be faceted.

* *Energy dispersive elements*. Implemented are :meth:`crystals in dynamical
  diffraction <xrt.backends.raycing.materials.Crystal.get_amplitude>`,
  gratings (so far, without efficiency calculations), Fresnel zone plates and
  Bragg-Fresnel optics. Crystals can work in Bragg or Laue cases, in reflection
  or in transmission. The :meth:`two-field polarization phenomena
  <xrt.backends.raycing.sources.make_polarization>` are fully preserved, also
  within the Darwin diffraction plateau, thus enabling the ray tracing of
  crystal-based phase retarders. :func:`As compared to XOP/Shadow
  <tests.raycing.test_materials.run_tests>`, xrt works correctly for asymmetric
  crystals in transmission regime.

* *Materials*. The material properties are incorporated using :class:`three
  different tabulations <xrt.backends.raycing.materials.Element>` of the
  scattering factors, with differently wide and differently dense energy
  meshes. Refraction index and absorption coefficient are calculated from the
  scattering factors. Two-surface bodies, like plates or refractive lenses,
  are treated with both refraction and absorption.

* *Multiple reflections*. xrt can trace multiple reflections in a single
  optical element. This is useful, for example in 'whispering gallery' optics
  or in Montel or Wolter mirrors. Here, very handy is the histogramming over
  the number of reflections, incidence angle and elevation over the surface.

* *Non-sequential optics*. xrt can trace non-sequential optics where different
  parts of the incoming beam meet different surfaces. Examples of such optics
  are poly-capillaries and Wolter mirrors.

* *Global coordinate system*. The optical elements are positioned in a global
  coordinate system. This is convenient for modeling a real synchrotron
  beamline. The coordinates in this system can be directly taken from a CAD
  library. The optical surfaces are defined in local systems for the user's
  convenience.

* *Beam categories*. xrt discriminates rays by several categories: `good`,
  `out`, `over` and `dead`. This distinction simplifies the adjustment of
  entrance and exit slits. An alarm is triggered if the fraction of dead rays
  exceeds a specified level.

* *Portability*. xrt runs on Windows and Unix-like platforms, wherever you can
  run python.

* *Examples*. xrt comes with many examples; see the :ref:`gallery`.

Dependencies
------------
The histogramming is done by means of :mod:`numpy`; :mod:`matplotlib` is used
for plotting. If you use calculations on GPU (so far, only for calculating
undulators), you need AMD/NVIDIA drivers, Intel SDK for OpenCL, a CPU only
OpenCL runtime, pytools and pyopencl.

Python 3
--------
The code can be fully automatically converted to Python 3 with ``2to3`` at its
default options.

Get xrt
-------
xrt is available as source distribution from `here
<https://pypi.python.org/pypi/xrt>`_. The distribution archive also includes
tests and examples.

Installation
------------
Unzip the .zip file into a suitable directory, chdir to that directory and run
``python setup.py install``. Alternatively and probably more convenient: use
`sys.path.append()` in your
scripts to specify the path to xrt wherever you put it. Note that python-64-bit
is by ~20% faster than the 32-bit version (tested with WinPython).

Acknowledgments
---------------
Josep Nicolás and Jordi Juanhuix (synchrotron Alba) are acknowledged for
discussion and for their Matlab codes used as examples at early stages of the
project. Summer students of DESY Andrew Geondzhian and Victoria Kabanova are
acknowledged for their help in coding the classes of synchrotron sources.
"""

#========Convention============================================================
# Naming:
#   * classes MixedUpperCase
#   * varables lowerUpper _or_ lower
#   * functions underscore_separated _or_ lower
#==============================================================================
__module__ = "xrt"
__author__ = \
    "Konstantin Klementiev (MAX IV)", "Roman Chernikov (DESY Photon Science)"
__email__ = "first dot last at gmail dot com"
__versioninfo__ = (0, 9, 2)
__version__ = '.'.join(map(str, __versioninfo__))
__date__ = "4 Mar 2014"
__license__ = "MIT license"

#__all__ = ['plotter', 'runner', 'multipro']
