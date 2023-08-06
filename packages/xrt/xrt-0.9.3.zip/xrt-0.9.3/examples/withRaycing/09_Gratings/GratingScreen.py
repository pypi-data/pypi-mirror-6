# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "20 Jan 2014"
import sys
sys.path.append(r"c:\Ray-tracing")
import numpy as np
#import matplotlib as mpl
#import matplotlib.pyplot as plt

import xrt.plotter as xrtp
import xrt.runner as xrtr
import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.screens as rsc

#coating = rm.Material('Au', rho=19.3)
coating = rm.Material('Ni', rho=8.902)
#coating = None

scanEnergies = 100, 500, 1000
scanZlim = [[0.8, 0.8, 0.8], [3, 1.5, 1], [4, 2, 1.5], [5, 2, 2]]
scanZ0 = np.linspace(-0.8, 0.8, 256)
pitch = np.radians(2.)
blaze = np.radians(1.48)
rho = 1200.  # lines/mm
rho_1 = 1./rho
p = 10000.
q = 10000.

sinBlaze, cosBlaze, tanBlaze = np.sin(blaze), np.cos(blaze), np.tan(blaze)
cosTheta = np.cos(pitch)
sinTheta = np.sin(pitch)
#print 'max height = {0} nm'.format(rho_1 * tanBlaze * 1e6)


def report_order_pos(orders=range(11)):
    z0 = q * np.tan(2*pitch)
    for energy in scanEnergies:
        l_d = rm.ch / energy * 1e-7 * rho
        beta = np.arcsin(cosTheta - np.asarray(orders)*l_d)
        z = q * np.tan(pitch + np.pi/2 - beta)
        print 'E={0}: z={1}'.format(energy, z-z0)


class BlazedGrating(roe.OE):
    def local_z(self, x, y):
        return (y % rho_1) * tanBlaze

    def local_n(self, x, y):
        return [np.zeros_like(x), -sinBlaze*np.ones_like(x),
                cosBlaze*np.ones_like(x)]

    def find_intersection(self, local_f, t1, t2, x, y, z, a, b, c,
                          invertNormal, derivOrder=0):
        b_c = b / c
        y_z = (y - z*b/c)
        i = np.floor(b_c*tanBlaze + y_z/rho_1)
        z2 = (y_z - i*rho_1) / (1./tanBlaze - b_c)
        if (z2 > tanBlaze * rho_1).any():
            raise
        if (z2 < 0).any():
            raise
        y2 = b_c * (z2-z) + y
        x2 = x
        t2 = (y2-y) / b
        return t2, x2, y2, z2


def build_beamline(nrays=raycing.nrays):
    beamLine = raycing.BeamLine(azimuth=0, height=0)
    rs.GeometricSource(
        beamLine, 'MAX-IV', nrays=nrays,
        distz='flat', dz=1, distx=None, distxprime=None, distzprime=None,
        distE='lines', polarization='horizontal')
    beamLine.pg = BlazedGrating(
        beamLine, 'PlaneGrating', (0, p, 0), pitch=pitch, material=coating)
    beamLine.fsm = rsc.Screen(beamLine, 'FSM', (0, p+q, q*np.tan(2*pitch)))
    return beamLine


def run_process(beamLine, shineOnly1stSource=False):
    beamSource = beamLine.sources[0].shine()
    beamPGglobal, beamPGlocal = beamLine.pg.reflect(beamSource)
    beamKirchhoff0 = beamLine.fsm.expose_Kirchhoff(
        beamSource, beamLine.pg, beamPGglobal, beamPGlocal, 0.*scanZ0,
        beamLine.scanZ0)
    beamKirchhoff1 = beamLine.fsm.expose_Kirchhoff(
        beamSource, beamLine.pg, beamPGglobal, beamPGlocal, 0.*scanZ0,
        beamLine.scanZ1)
    beamKirchhoff2 = beamLine.fsm.expose_Kirchhoff(
        beamSource, beamLine.pg, beamPGglobal, beamPGlocal, 0.*scanZ0,
        beamLine.scanZ2)
    beamKirchhoff3 = beamLine.fsm.expose_Kirchhoff(
        beamSource, beamLine.pg, beamPGglobal, beamPGlocal, 0.*scanZ0,
        beamLine.scanZ3)
    outDict = {'beamSource': beamSource,
               'beamPGglobal': beamPGglobal, 'beamPGlocal': beamPGlocal,
               'beamKirchhoff0': beamKirchhoff0,
               'beamKirchhoff1': beamKirchhoff1,
               'beamKirchhoff2': beamKirchhoff2,
               'beamKirchhoff3': beamKirchhoff3}
    return outDict
rr.run_process = run_process


def main():
    beamLine = build_beamline(nrays=1e5)

    plots = []

#    plotSource = xrtp.XYCPlot(
#        'beamSource', (1,),
#        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-1.2, 1.2]),
#        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-1.2, 1.2]))
#    plots.append(plotSource)
#
#    plot = xrtp.XYCPlot(
#        'beamPGlocal', (1,), aspect='auto',
#        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-1.2, 1.2]),
#        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-30, 30]),
#        title='PG_local')
#    plots.append(plot)
#
#    plot = xrtp.XYCPlot(
#        'beamPGglobal', (1,), aspect='auto',
#        xaxis=xrtp.XYCAxis(r'$y$', u'µm', limits=[-2+p*1000, 2+p*1000]),
#        yaxis=xrtp.XYCAxis(r'$z$', 'nm', limits=[0, 30]),
#        title='PG_local_zoom')
#    plot.xaxis.offset = p*1000
#    plots.append(plot)

    plotK0 = xrtp.XYCPlot(
        'beamKirchhoff0', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=4, ppb=32, limits=[-0.1, 0.1]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=256, ppb=2),
        caxis=xrtp.XYCAxis(r'averaged path', 'mm', bins=256, ppb=2),
        title='beamKirchhoff0')
    plotK0.caxis.offset = p + q
    plots.append(plotK0)

    plotK1 = xrtp.XYCPlot(
        'beamKirchhoff1', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=4, ppb=32, limits=[-0.1, 0.1]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=256, ppb=2),
        caxis=xrtp.XYCAxis(r'averaged path', 'mm', bins=256, ppb=2),
        title='beamKirchhoff1')
    plotK1.caxis.offset = p + q
    plots.append(plotK1)

    plotK2 = xrtp.XYCPlot(
        'beamKirchhoff2', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=4, ppb=32, limits=[-0.1, 0.1]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=256, ppb=2),
        caxis=xrtp.XYCAxis(r'averaged path', 'mm', bins=256, ppb=2),
        title='beamKirchhoff2')
    plotK2.caxis.offset = p + q
    plots.append(plotK2)

    plotK3 = xrtp.XYCPlot(
        'beamKirchhoff3', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=4, ppb=32, limits=[-0.1, 0.1]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=256, ppb=2),
        caxis=xrtp.XYCAxis(r'averaged path', 'mm', bins=256, ppb=2),
        title='beamKirchhoff3')
    plotK3.caxis.offset = p + q
    plots.append(plotK3)

#    def plot_z_profile(scan, efficiencyS, fName):
#        fig = plt.figure(figsize=(5, 8), dpi=72)
#        fig.subplots_adjust(hspace=0.4)
#        for ie, e in enumerate(scanEnergies):
#            ax = fig.add_subplot(len(scanEnergies), 1, ie+1)
#            ax.set_title('E = {0} eV'.format(e))
#            ax.plot(scan, efficiencyS[ie], 'b', lw=1, label='TE')
#            ax.set_xlabel(r'$z$ (mm)')
#            ax.set_ylabel(r'intensity')
#            ax.set_xlim(scan[0], scan[-1])
##            ax.legend()
#        fig.savefig(fName)

    def plot_generator():
#        efficiencyS = []
#        efficiencySNorm = []
        z0 = q * np.tan(2*pitch)
        for ie, energy in enumerate(scanEnergies):
            l_d = rm.ch / energy * 1e-7 * rho
            beta = np.arcsin(cosTheta-np.asarray([0, 1, 2, 3]) * l_d)
            z = q * np.tan(pitch + np.pi/2 - beta) - z0
            beamLine.scanZ0 = scanZ0
            plotK0.yaxis.limits = beamLine.scanZ0[0], beamLine.scanZ0[-1]
            scanZ1 = np.linspace(-scanZlim[1][ie], scanZlim[1][ie], 256)
            beamLine.scanZ1 = scanZ1 + z[1]
            plotK1.yaxis.limits = beamLine.scanZ1[0], beamLine.scanZ1[-1]
            scanZ2 = np.linspace(-scanZlim[2][ie], scanZlim[2][ie], 256)
            beamLine.scanZ2 = scanZ2 + z[2]
            plotK2.yaxis.limits = beamLine.scanZ2[0], beamLine.scanZ2[-1]
            scanZ3 = np.linspace(-scanZlim[3][ie], scanZlim[3][ie], 256)
            beamLine.scanZ3 = scanZ3 + z[3]
            plotK3.yaxis.limits = beamLine.scanZ3[0], beamLine.scanZ3[-1]
            plotK1.caxis.limits = None
            plotK2.caxis.limits = None
            plotK3.caxis.limits = None

            beamLine.sources[0].energies[0] = energy
            plotK0.saveName = 'order0,E={0:04d}.png'.format(energy)
            plotK1.saveName = 'order1,E={0:04d}.png'.format(energy)
            plotK2.saveName = 'order2,E={0:04d}.png'.format(energy)
            plotK3.saveName = 'order3,E={0:04d}.png'.format(energy)
            yield
#            norm = sum(abs(plotK.fieldKirchhoffN)**2)
#            eff = abs(plotK.fieldKirchhoffS)**2
#            efficiencyS.append(eff)
#            efficiencySNorm.append(eff / norm)
#        plot_z_profile(scanZ, efficiencyS, 'zProfile.png')
#        plot_z_profile(scanZ, efficiencySNorm, 'zProfileNorm.png')
#        plt.show()

    xrtr.run_ray_tracing(plots, repeats=6*40, beamLine=beamLine,
                         generator=plot_generator, processes='half')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
#    report_order_pos()
    main()
