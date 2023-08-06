# -*- coding: utf-8 -*-
r"""
ALBA CLÆSS beamline
-------------------

Files in `\\examples\\withRaycing\\08_CLAESS_BL`

See the optical scheme of the beamline
`here <http://www.cells.es/Beamlines/CLAESS/optics_layout.html>`_.

This script produces images at various positions along the beamline.

The following 13 images are:

1) FSM image after the front end with the projected absorbed rays (red) at

  a) the fixed front end mask,
  b) upstream half and
  c) downstream half of the movable front end mask

2) footprint on VCM,
3) footprint on the 1st crystal of DCM,
4) footprint on the 2nd crystal of DCM,
5) beam at the Bremsstrahlung block,
6) image at the foil holder of 4-diode XBPM,
7) footprint on VFM,
8) front collimator of the photon shutter,
9) image at the reducer flange 100CF-to-40CF,
10) image at the EH 4-blade slit,
11) image at the focal (sample) point.

.. image:: _images/ClaessBL-Rh-01DiamondFSM1+FixedMask_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-02DiamondFSM1+FEMaskLT_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-03DiamondFSM1+FEmaskRB_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-05VCM_footprintE_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-09Xtal1_footprintE_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-11Xtal2_footprintE_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-12BSBlock_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-13XBPM4foils_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-16VFM_footprint_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-18OH-PS-FrontCollimator_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-19eh100To40Flange_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-20slitEH_shrunk.*
   :scale: 50 %
.. image:: _images/ClaessBL-Rh-22FocusAtSampleE_shrunk.*
   :scale: 50 %

The script also exemplifies:

1) the usage of :func:`~xrt.backends.raycing.sources.shrink_source` for
   matching the front end slit to the size of the collimating mirror;
2) how to shrink the energy band before DCM in order to have simultanious
   images in the white *and* the monochromatic beam parts of the beamline;
3) the usage of
   :func:`~xrt.backends.raycing.apertures.RectangularAperture.touch_beam` for
   finding the optimal size of the EH slit.
"""
__author__ = "Konstantin Klementiev"
__date__ = "1 Mar 2012"

import sys
#sys.path.append(r"/home/klmnShared/Alba/Ray-tracing/with Python")
sys.path.append(r"c:\Ray-tracing")
#import math
import ClaessBL
import xrt.plotter as xrtp
import xrt.runner as xrtr


def add_plot(plots, plot, prefix, suffix):
    plots.append(plot)
    fileName = '{0}{1:02d}{2}{3}'.format(prefix, len(plots), plot.title,
                                         suffix)
    plot.saveName = [fileName + '.png', ]
#    plot.persistentName = fileName + '.pickle'


def main():
    prefix = 'ClaessBL-'
    beamLine = ClaessBL.build_beamline()
    stripe = 'Rh'
    ClaessBL.align_beamline(
        beamLine, hDiv=1.5e-3, vDiv=2.5e-4, nameVCMstripe=stripe,
        nameDCMcrystal='Si111', energy=9000., fixedExit=25.,
        nameDiagnFoil=u'Cu5µm', nameVFMcylinder=stripe)
    beamLine.dcm.energyMin = 9000.
    beamLine.dcm.energyMax = 9002.5
    prefix += stripe + '-'

    suffix = ''
#= uncomment for shrinking the source (front-end slit) ========================
    import xrt.backends.raycing.sources as rs
    hDiv, vDiv = 2e-3, 3.5e-4
#    hDiv, vDiv = 1.48e-3, 2.7e-4
    beamLine.feMovableMaskLT.set_divergence(
        beamLine.sources[0], [-hDiv/2, vDiv/2])
    beamLine.feMovableMaskRB.set_divergence(
        beamLine.sources[0], [hDiv/2, -vDiv/2])
#    meshSource = rs.shrink_source(beamLine, ('beamVCMlocal','beamVFMlocal'),
#      -hDiv/2, hDiv/2, -vDiv/2, vDiv/2, 64, 64)
    meshSource = rs.shrink_source(beamLine, ('beamVCMlocal',),
                                  -hDiv/2, hDiv/2, -vDiv/2, vDiv/2, 64, 64)
    beamLine.feMovableMaskLT.set_divergence(
        beamLine.sources[0], [meshSource.minxprime, meshSource.maxzprime])
    beamLine.feMovableMaskRB.set_divergence(
        beamLine.sources[0], [meshSource.maxxprime, meshSource.minzprime])
    print 'when the beam matches VCM:'
    print 'beam divergence = {0:.2f}h x {1:.2f}v mrad^2'.format(
        (-meshSource.minxprime + meshSource.maxxprime) * 1e3,
        (-meshSource.minzprime + meshSource.maxzprime) * 1e3)
    print 'full feMovableMaskLT.opening = [{0[0]:.3f}, {0[1]:.3f}]'.format(
        beamLine.feMovableMaskLT.opening)
    print 'full feMovableMaskRB.opening = [{0[0]:.3f}, {0[1]:.3f}]'.format(
        beamLine.feMovableMaskRB.opening)
    print 'half feMovableMaskLT.opening = [{0[0]:.3f}, {0[1]:.3f}]'.format(
        [op/2 for op in beamLine.feMovableMaskLT.opening])
    print 'half feMovableMaskRB.opening = [{0[0]:.3f}, {0[1]:.3f}]'.format(
        [op/2 for op in beamLine.feMovableMaskRB.opening])
    suffix = '_shrunk'
#= touch the beam with the EH slit: ===========================================
# note that for using `touch_beam` the beams must exist, therefore you should
# run the source shrinkage above or `run_process` below this line.
#    ClaessBL.run_process(beamLine)
    beamLine.slitEH.touch_beam(beamLine.beams['beamVFMglobal'])
#= make narrow energy band before DCM =========================================
    ClaessBL.shouldShrinkEnergy = True
#==============================================================================
    dE = beamLine.sources[0].energies[-1] - beamLine.sources[0].energies[0]
    midE = \
        (beamLine.sources[0].energies[-1] + beamLine.sources[0].energies[0])/2
    if dE < midE / 20.:
        fwhmFormatStrE = '%.2f'
        offsetE = round(midE)
    else:
        fwhmFormatStrE = None
        offsetE = 0
    fwhmFormatStrEMono = fwhmFormatStrE
    offsetEMono = offsetE
    if ClaessBL.shouldShrinkEnergy:
        fwhmFormatStrEMono = '%.2f'
        offsetEMono = beamLine.dcm.energyMin
    plots = []

#    plot = xrtp.XYCPlot('beamFilter1local1', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-18., 18.]),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
#      ePos=1, title='Filter1 footprint1E')
#    plot.caxis.fwhmFormatStr = fwhmFormatStrE
#    plot.caxis.offset = offsetE
#    add_plot(plots, plot, prefix, suffix)
#
#    plot = xrtp.XYCPlot('beamFilter1local2', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-18., 18.]),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
#      ePos=1, title='Filter1 footprint2E')
#    plot.caxis.fwhmFormatStr = fwhmFormatStrE
#    plot.caxis.offset = offsetE
#    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM1', (1, beamLine.feFixedMask.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-18., 18.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm1.name+'+FixedMask')
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM1', (1, beamLine.feMovableMaskLT.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-18., 18.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm1.name+'+FEMaskLT')
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM1', (1, beamLine.feMovableMaskRB.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-18., 18.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm1.name+'+FEmaskRB')
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamVCMlocal', (1, 2, 4), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-53., 53.]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-655., 655.]),
        caxis='category', title='VCM_footprint', oe=beamLine.vcm)
    plot.xaxis.fwhmFormatStr = '%.1f'
    plot.yaxis.fwhmFormatStr = '%.0f'
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamVCMlocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-53., 53.]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-655., 655.]),
        ePos=1, title='VCM_footprintE', oe=beamLine.vcm)
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.caxis.offset = offsetE
    plot.xaxis.fwhmFormatStr = '%.1f'
    plot.yaxis.fwhmFormatStr = '%.0f'
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1, 2, 3, 4, beamLine.vcm.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm2.name)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-8., 8.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[4., 20.]), ePos=1,
        title=beamLine.fsm2.name+'E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.caxis.offset = offsetE
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamDCMlocal1', (1, 2, 4), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-51.1, 51.1]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-30., 30.]),
        caxis='category', title='Xtal1_footprint', oe=beamLine.dcm)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamDCMlocal1', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-51.1, 51.1]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-30., 30.]),
        ePos=1, title='Xtal1_footprintE', oe=beamLine.dcm)
    plot.caxis.fwhmFormatStr = fwhmFormatStrEMono
    plot.caxis.offset = offsetEMono
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamDCMlocal2', (1, 2, 4, -2), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-48.6, 48.6]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-90., 90.]),
        caxis='category', title='Xtal2_footprint', oe=beamLine.dcm,
        raycingParam=2)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamDCMlocal2', (1, 4), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-48.6, 48.6]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-90., 90.]),
        ePos=1, title='Xtal2_footprintE', oe=beamLine.dcm, raycingParam=2)
    plot.caxis.fwhmFormatStr = fwhmFormatStrEMono
    plot.caxis.offset = offsetEMono
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamBSBlocklocal', (1, 2, beamLine.BSBlock.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-30., 30.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[10., 70.]),
        caxis='category', title=beamLine.BSBlock.name, oe=beamLine.BSBlock)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamXBPMlocal', (1, 2, 4, beamLine.xbpm4foils.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-30., 30.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=beamLine.xbpm4foils.zlims),
        caxis='category', title=beamLine.xbpm4foils.name,
        oe=beamLine.xbpm4foils)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM3', (1, 2, 3, 4, beamLine.dcm.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm3.name)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM3', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-8., 8.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[57., 73.]), ePos=1,
        title=beamLine.fsm3.name+'E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrEMono
    plot.caxis.offset = offsetEMono
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamVFMlocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-56., 56.]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-714., 714.]),
        caxis='category', title='VFM_footprint', oe=beamLine.vfm)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSM4', (1, 2, 3, 4, beamLine.vfm.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis='category', title=beamLine.fsm4.name)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamPSFrontLocal', (1, 2, 4, beamLine.ohPSFront.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-30., 30.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[30., 90.]),
        caxis='category', title=beamLine.ohPSFront.name, oe=beamLine.ohPSFront)
    add_plot(plots, plot, prefix, suffix)

    cz = beamLine.heightVFM - beamLine.height
    plot = xrtp.XYCPlot(
        'beam100To40FlangeLocal', (1, 2, 4, beamLine.eh100To40Flange.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-20., 20.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[cz-20., cz+20.]),
        caxis='category', title=beamLine.eh100To40Flange.name,
        oe=beamLine.eh100To40Flange)
    add_plot(plots, plot, prefix, suffix)

    cz = beamLine.heightVFM - beamLine.height
    plot = xrtp.XYCPlot(
        'beamSlitEHLocal', (1, 2, 4, beamLine.slitEH.lostNum),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-5., 5.]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[cz-5., cz+5.]),
        caxis='category', title=beamLine.slitEH.name, oe=beamLine.slitEH)
    add_plot(plots, plot, prefix, suffix)

    cz = beamLine.heightVFM - beamLine.height
    dz = 0.5
    plot = xrtp.XYCPlot(
        'beamFSMSample', (1, 2, 4),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-dz, dz],
                           fwhmFormatStr='%1.3f'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[cz-dz, cz+dz],
                           fwhmFormatStr='%1.3f'),
        caxis='category', title=beamLine.fsmAtSample.name)
    add_plot(plots, plot, prefix, suffix)

    plot = xrtp.XYCPlot(
        'beamFSMSample', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-dz, dz],
                           fwhmFormatStr='%1.3f'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[cz-dz, cz+dz],
                           fwhmFormatStr='%1.3f'),
        ePos=1, title=beamLine.fsmAtSample.name+'E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrEMono
    plot.caxis.offset = offsetEMono
    add_plot(plots, plot, prefix, suffix)

    def close_all():
        pass
#        import matplotlib.pyplot as plt
#        plt.close('all')

    xrtr.run_ray_tracing(plots, repeats=160, beamLine=beamLine,
                         afterScript=close_all, processes='auto')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
#    import cProfile
#    cProfile.run('main()', 'stats')
#    import pstats
#    p = pstats.Stats('stats')
#    p.sort_stats('cumulative').print_stats(40)

    main()
