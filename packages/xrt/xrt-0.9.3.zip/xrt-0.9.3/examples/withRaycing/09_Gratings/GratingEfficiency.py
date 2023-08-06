# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "20 Jan 2014"
import sys
sys.path.append(r"c:\Ray-tracing")
import numpy as np
#import matplotlib as mpl
import matplotlib.pyplot as plt

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.plotter as xrtp
import xrt.runner as xrtr

#coating = rm.Material('Au', rho=19.3)
coating = rm.Material('Ni', rho=8.902)
#coating = None

#whatToScan = 'energy'
whatToScan = 'angle'
if whatToScan == 'energy':
    scanEnergies = np.linspace(100, 1100, 101)
else:
    scanEnergies = 100, 500, 1000
    scanAngles = np.linspace(0, np.pi/2, 10000)
    degAngles = np.degrees(scanAngles)
    bunch = 20
    bunchAngles = np.array(
        [scanAngles[i:i+bunch].sum()/bunch
            for i in range(0, len(scanAngles), bunch)])
    bunchAnglesDeg = np.degrees(bunchAngles)
pitch = np.radians(2.)
blaze = np.radians(1.48)
rho = 1200.  # lines/mm
rho_1 = 1./rho
orders = 0, 1, 2

sinBlaze, cosBlaze, tanBlaze = np.sin(blaze), np.cos(blaze), np.tan(blaze)
cosTheta = np.cos(pitch)
sinTheta = np.sin(pitch)
#print 'max height = {0} nm'.format(rho_1 * tanBlaze * 1e6)


class BlazedGrating(roe.OE):
    def local_z(self, x, y):
        return (y % rho_1) * tanBlaze

    def local_n(self, x, y):
        return 0, -sinBlaze, cosBlaze

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
        distz='flat', dz=2, distx=None, distxprime=None, distzprime=None,
        distE='lines', polarization='horizontal')
    beamLine.pg = BlazedGrating(
        beamLine, 'PlaneGrating', (0, 1e4, 0), pitch=pitch, material=coating)
    return beamLine


def run_process(beamLine, shineOnly1stSource=False):
    beamSource = beamLine.sources[0].shine()
    beamPGglobal, beamPGlocal = beamLine.pg.reflect(beamSource)
    if whatToScan == 'energy':
        l_d = rm.ch / beamLine.sources[0].energies[0] * 1e-7 * rho
        beta = np.arcsin(cosTheta - np.asarray(beamLine.pg.orders)*l_d)
    else:
        beta = scanAngles
    beamLine.pg.get_Kirchhoff_integral(beamSource, beamPGlocal, pitch, beta)
    outDict = {'beamSource': beamSource,
               'beamPGglobal': beamPGglobal, 'beamPGlocal': beamPGlocal}
    return outDict
rr.run_process = run_process


def main():
    beamLine = build_beamline(nrays=1e3)

    plots = []

    plotSource = xrtp.XYCPlot(
        'beamSource', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-1.2, 1.2]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-1.2, 1.2]))
    plots.append(plotSource)

    plotPG = xrtp.XYCPlot(
        'beamPGlocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-1.2, 1.2]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-30, 30]),
        title='PG_local')
    plots.append(plotPG)

    plot = xrtp.XYCPlot(
        'beamPGlocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$y$', u'µm', limits=[-2, 2]),
        yaxis=xrtp.XYCAxis(r'$z$', 'nm', limits=[0, 30]),
        title='PG_local_zoom')
    plots.append(plot)

    def plot_energy_scans(efficiencyS, fName):
        fig = plt.figure(figsize=(5, 8), dpi=72)
        fig.subplots_adjust(hspace=0.4)
        for im, m in enumerate(orders):
            ax = fig.add_subplot(len(orders), 1, im+1)
            ax.set_title('Order {0}'.format(m))
            y = np.array([eff[im] for eff in efficiencyS])
            ax.plot(scanEnergies, y, 'b', lw=1, label='TE')
            ax.set_xlabel(u'energy (eV)')
            ax.set_ylabel(r'absolute efficiency')
            ax.set_xlim(scanEnergies[0], scanEnergies[-1])
#            ax.legend()
        fig.savefig(fName)

    def plot_angle_scans(angles, efficiencyS, fName):
        fig = plt.figure(figsize=(5, 8), dpi=72)
        fig.subplots_adjust(hspace=0.4)
        for ie, e in enumerate(scanEnergies):
            ax = fig.add_subplot(len(orders), 1, ie+1)
            ax.set_title('E = {0} eV'.format(e))
            ax.plot(angles, efficiencyS[ie], 'b', lw=1, label='TE')
            ax.set_xlabel(r'$\beta$ (degree)')
            ax.set_ylabel(r'absolute efficiency')
            ax.set_xlim(angles[0], angles[-1])
#            ax.legend()
        fig.savefig(fName)

    def plot_generator():
        efficiencyS = []
        efficiencySNorm = []
        for ie, energy in enumerate(scanEnergies):
            if whatToScan == 'energy':
                l_d = rm.ch / energy * 1e-7 * rho
                beamLine.pg.mMin = int(np.trunc((cosTheta-1) / l_d))
                beamLine.pg.mMax = int(np.trunc((cosTheta+1) / l_d))
                beamLine.pg.orders = range(
                    beamLine.pg.mMin, beamLine.pg.mMax+1)
                print 'grating orders available at E={0} eV: {1} to {2}'.\
                    format(energy, beamLine.pg.mMin, beamLine.pg.mMax)
            beamLine.sources[0].energies[0] = energy
            for plot in plots:
                plot.caxis.limits = [energy-0.1, energy+0.1]
                plot.caxis.offset = energy
            yield
#            fieldKirchhoffN = plotPG.fieldKirchhoffN
#            fieldKirchhoffS = plotPG.fieldKirchhoffS
            fieldKirchhoffN = np.array(
                [plotPG.fieldKirchhoffN[i:i+bunch].sum()
                 for i in range(0, len(plotPG.fieldKirchhoffN), bunch)])
            fieldKirchhoffS = np.array(
                [plotPG.fieldKirchhoffS[i:i+bunch].sum()
                 for i in range(0, len(plotPG.fieldKirchhoffS), bunch)])
            norm = sum(abs(fieldKirchhoffN)**2)
            eff = abs(fieldKirchhoffS)**2
            efficiencyS.append(eff)
            efficiencySNorm.append(eff / norm)
            if whatToScan == 'energy':
                axis = beamLine.pg.orders
                axisName = 'orders'
                axisUnit = ''
            else:
                axis = degAngles
                axisName = 'angles'
                axisUnit = 'deg'
            print "sum of efficiency over {0} from {1} to {2} {3} = {4}".\
                format(axisName, min(axis), max(axis), axisUnit,
                       (eff/norm).sum())

        if whatToScan == 'energy':
            plot_energy_scans(efficiencySNorm, 'efficiencyNormVsEnergy.png')
        else:
            plot_angle_scans(
                bunchAnglesDeg, efficiencyS, 'efficiencyVsAngle.png')
            plot_angle_scans(
                bunchAnglesDeg, efficiencySNorm, 'efficiencyNormVsAngle.png')
        plt.show()

#    xrtr.run_ray_tracing(plots, repeats=24*1000, beamLine=beamLine,
    xrtr.run_ray_tracing(plots, repeats=1, beamLine=beamLine,
                         generator=plot_generator, processes='all')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
