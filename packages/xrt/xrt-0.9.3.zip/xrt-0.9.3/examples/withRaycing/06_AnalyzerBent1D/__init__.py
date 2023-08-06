# -*- coding: utf-8 -*-
r"""
Comparison of 1D-bent crystal analyzers
---------------------------------------

Files in `\\examples\\withRaycing\\06_AnalyzerBent1D`

This study compares simply bent and ground-bent spectrometers utilizing Bragg
and Laue crystals. The bending is cylindrical (one-dimensional).

.. image:: _images/BraggLaue.*
   :scale: 50 %

:Conditions: Rowland circle radius = 1 m, 70v × 200h µm\ :sup:`2` unpolarized
   fluorescence source, crystal size = 100meridional × 20saggittal
   mm\ :sup:`2`.

The energy resolution was calculated as described in `the CDR of a diced
Johansson-like spectrometer at Alba/CLÆSS beamline
<http://www.cells.es/Beamlines/CLAESS/EXD-BL22-FA-0001v4.0.pdf>`_. This
requires two images: 1) of a flat energy distribution source and 2) of a
monochromatic source. The image is energy dispersive in the diffraction plane,
which can be used in practice with a position sensitive detector or with a slit
scan in front of a bulk detector. From these two images the energy resolution
*dE* was calculated and then 3) a verifying image was ray-traced for a source
of 7 energy lines evenly spaced with the found step *dE*. Such images are shown
for the four crystal geometries at a particular Bragg angle:

+-------------------+-------------+-------------+-----------+
|      geometry     | flat source | line source |  7 lines  |
+===================+=============+=============+===========+
| Bragg simply bent |  |bb_flat|  |  |bb_line|  | |bb_7lin| |
+-------------------+-------------+-------------+-----------+
| Bragg ground-bent |  |bg_flat|  |  |bg_line|  | |bg_7lin| |
+-------------------+-------------+-------------+-----------+
| Laue simply bent  |  |lb_flat|  |  |lb_line|  | |lb_7lin| |
+-------------------+-------------+-------------+-----------+
| Laue ground-bent  |  |lg_flat|  |  |lg_line|  | |lg_7lin| |
+-------------------+-------------+-------------+-----------+

.. |bb_flat| image:: _images/1D-01b-Si444-60-det_E-flat.*
   :scale: 50 %
.. |bb_line| image:: _images/1D-01b-Si444-60-det_E-line.*
   :scale: 50 %
.. |bb_7lin| image:: _images/1D-01b-Si444-60-det_E-7lin.*
   :scale: 50 %
.. |bg_flat| image:: _images/1D-02gb-Si444-60-det_E-flat.*
   :scale: 50 %
.. |bg_line| image:: _images/1D-02gb-Si444-60-det_E-line.*
   :scale: 50 %
.. |bg_7lin| image:: _images/1D-02gb-Si444-60-det_E-7lin.*
   :scale: 50 %
.. |lb_flat| image:: _images/1D-03lb-Si444-60-det_E-flat.*
   :scale: 50 %
.. |lb_line| image:: _images/1D-03lb-Si444-60-det_E-line.*
   :scale: 50 %
.. |lb_7lin| image:: _images/1D-03lb-Si444-60-det_E-7lin.*
   :scale: 50 %
.. |lg_flat| image:: _images/1D-04lgb-Si444-60-det_E-flat.*
   :scale: 50 %
.. |lg_line| image:: _images/1D-04lgb-Si444-60-det_E-line.*
   :scale: 50 %
.. |lg_7lin| image:: _images/1D-04lgb-Si444-60-det_E-7lin.*
   :scale: 50 %

The energy distribution over the crystal surface is hyperbolic for Bragg and
ellipsoidal for Laue crystals. Therefore, Laue crystals have limited acceptance
in the sagittal direction whereas Bragg crystals have the hyperbola branches
even for large sagittal sizes. Notice the full crystal coverage in the
meridional direction for the two ground-bent cases.

+-------------------+--------------+--------------+------------+
|      geometry     |  flat source |  mono source |  7 lines   |
+===================+==============+==============+============+
| Bragg simply bent |  |xbb_flat|  |  |xbb_line|  | |xbb_7lin| |
+-------------------+--------------+--------------+------------+
| Bragg ground-bent |  |xbg_flat|  |  |xbg_line|  | |xbg_7lin| |
+-------------------+--------------+--------------+------------+
| Laue simply bent  |  |xlb_flat|  |  |xlb_line|  | |xlb_7lin| |
+-------------------+--------------+--------------+------------+
| Laue ground-bent  |  |xlg_flat|  |  |xlg_line|  | |xlg_7lin| |
+-------------------+--------------+--------------+------------+

.. |xbb_flat| image:: _images/1D-01b-Si444-60-xtal_E-flat.*
   :scale: 40 %
.. |xbb_line| image:: _images/1D-01b-Si444-60-xtal_E-line.*
   :scale: 40 %
.. |xbb_7lin| image:: _images/1D-01b-Si444-60-xtal_E-7lin.*
   :scale: 40 %
.. |xbg_flat| image:: _images/1D-02gb-Si444-60-xtal_E-flat.*
   :scale: 40 %
.. |xbg_line| image:: _images/1D-02gb-Si444-60-xtal_E-line.*
   :scale: 40 %
.. |xbg_7lin| image:: _images/1D-02gb-Si444-60-xtal_E-7lin.*
   :scale: 40 %
.. |xlb_flat| image:: _images/1D-03lb-Si444-60-xtal_E-flat.*
   :scale: 40 %
.. |xlb_line| image:: _images/1D-03lb-Si444-60-xtal_E-line.*
   :scale: 40 %
.. |xlb_7lin| image:: _images/1D-03lb-Si444-60-xtal_E-7lin.*
   :scale: 40 %
.. |xlg_flat| image:: _images/1D-04lgb-Si444-60-xtal_E-flat.*
   :scale: 40 %
.. |xlg_line| image:: _images/1D-04lgb-Si444-60-xtal_E-line.*
   :scale: 40 %
.. |xlg_7lin| image:: _images/1D-04lgb-Si444-60-xtal_E-7lin.*
   :scale: 40 %

As a matter of principles checking, let us consider how the initially
unpolarized beam becomes partially polarized after being diffracted by the
crystal analyzer. As expected, the beam is fully polarized at 45° Bragg angle
(Brewster angle in x-ray regime). CAxis here is degree of polarization:

+----------------------------+--------------------------+
|         Bragg              |           Laue           |
+=============+==============+============+=============+
|  |DPBragg|  |  |DPBraggZ|  |  |DPLaue|  |  |DPLaueZ|  |
+-------------+--------------+------------+-------------+

.. |DPBragg| image:: _images/1D-DegOfPol_Bragg.swf
   :width: 322
   :height: 205
.. |DPBraggZ| image:: _images/zoomIcon.png
   :width: 20
   :target: _images/1D-DegOfPol_Bragg.swf
.. |DPLaue| image:: _images/1D-DegOfPol_Laue.swf
   :width: 315
   :height: 205
.. |DPLaueZ| image:: _images/zoomIcon.png
   :width: 20
   :target: _images/1D-DegOfPol_Laue.swf

.. rubric:: Comments

1) The ground-bent crystals are more efficient as the whole their surface works
   for a single energy, as opposed to simply bent crystals which have different
   parts reflecting the rays of different energies.
2) When the crystal is close to the source (small θ for Bragg and large θ for
   Laue), the images are distorted, even for the ground-bent crystals.
3) The Bragg case requires small pixel size in the meridional direction (~10 µm
   for 1-m-diameter Rowland circle) for a good spatial resolution but can
   profit from its compactness. The Laue case requires a big detector of a size
   comparable to that of the crystal but the pixel size is not required to be
   small.
4) The comparison of energy resolution in Bragg and Laue cases is not strictly
   correct here. While the former case can use the small beam size at the
   detector for utilizing energy dispersive property of the spectrometer, the
   latter one has a big image at the detector which is restricted by the size
   of the crystal. The size of the 'white' beam image is therefore correct only
   for the crystal size selected here. The Laue case can still be used in
   energy dispersive regime if 2D image analysis is utilized. At the present
   conditions, the energy resolution of Bragg crystals is better than that of
   Laue crystals except at small Bragg angles and low diffraction orders.
5) The energy resolution in ground-bent cases is not always better than that
   in simply bent cases because of strongly curved images. If the sagittal size
   of the crystal is smaller or :ref:`sagittal bending is used
   <dicedBentAnalyzers>`, the advantage of ground-bent crystals is clearly
   visible not only in terms of efficiency but also in terms of energy
   resolution.
"""
pass
