# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "23 Apr 2014"
import sys
sys.path.append(r"c:\Ray-tracing")
import numpy as np
import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
#import xrt.backends.raycing.apertures as ra
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
#import xrt.backends.raycing.materials as rm
import xrt.plotter as xrtp
import xrt.runner as xrtr
import xrt.backends.raycing.screens as rsc

mGold = None  # rm.Material('Au', rho=19.3)
sqrt2 = np.sqrt(2)


class MontelMirror(roe.BentFlatMirror):
    def local_z(self, x, y):
        dz = abs(x)
        return roe.BentFlatMirror.local_z(self, x, y) * sqrt2 + dz

    def local_n(self, x, y):
        a = -np.sign(x) / sqrt2  # -dz/dx
        b = -y / self.R  # -dz/dy
        c = 1. / sqrt2
        norm = (a**2 + b**2 + c**2)**0.5
        return a/norm, b/norm, c/norm


class MontelMirrorP(roe.BentFlatMirror, roe.SurfaceOfRevolution):
    _h = 100

    def local_r(self, s, phi):
        z = -roe.BentFlatMirror.local_z(self, 0, s) + self._h
        r = np.empty_like(phi)
        left = (phi > -0.75*np.pi) & (phi < 0)
        bottom = (phi < -0.75*np.pi) | (phi > np.pi/2)
        denS = np.maximum(abs(np.sin(phi[left])), 1e-5)
        denC = np.maximum(abs(np.cos(phi[bottom])), 1e-5)
        r[left] = z[left]/denS
        r[bottom] = z[bottom]/denC
        r[~(left | bottom)] = 1e5
        return r

    def local_n(self, s, phi):
        a, b, c = roe.BentFlatMirror.local_n(self, 0, s)
        aOut = np.zeros_like(phi)
        bOut = np.ones_like(phi)
        cOut = np.zeros_like(phi)
        left = (phi > -0.75*np.pi) & (phi < 0)
        bottom = (phi < -0.75*np.pi) | (phi > np.pi/2)
        aOut[left] = c[left]
        bOut[left] = b[left]
        bOut[bottom] = b[bottom]
        cOut[bottom] = c[bottom]
        return aOut, bOut, cOut

E0 = 9000.
L = 1200.
pitch = 4e-3
p = 20000.
q = 2000.
R = 2 * p / np.sin(pitch)
#R = 2 * p * q / (p + q) / np.sin(pitch)

#Thera are two implementations of Montel mirror: in XYZ coordinates and in
#parametric coordinates.
isParametric = True


def build_beamline(nrays=raycing.nrays):
    beamLine = raycing.BeamLine(height=0)
    rs.GeometricSource(
        beamLine, 'GeometricSource', (0, 0, 0),
        nrays=nrays, dx=0., dz=0., dxprime=2e-4, dzprime=1e-4,
        distE='lines', energies=(E0,), polarization='horizontal')
    beamLine.fsm1 = rsc.Screen(beamLine, 'FSM1', (0., p-1000, 0.))
    if isParametric:
        beamLine.montel = MontelMirrorP(
            beamLine, 'MontelMirrorP', [0, p, 0],
            pitch=pitch, yaw=-pitch, material=mGold, limPhysY=[-L/2, L/2], R=R)
        beamLine.montel.center[0] = beamLine.montel._h
        beamLine.montel.center[2] = beamLine.montel._h
    else:
        beamLine.montel = MontelMirror(
            beamLine, 'MontelMirror', [0, p, 0],
            positionRoll=np.pi/4, pitch=pitch*sqrt2,
            material=mGold, limPhysY=[-L/2, L/2], R=R)
    beamLine.fsm2 = rsc.Screen(beamLine, 'FSM2', (0, p+q, 0))
    return beamLine


def run_process(beamLine, shineOnly1stSource=False):
    beamSource = beamLine.sources[0].shine()
    beamFSM1 = beamLine.fsm1.expose(beamSource)
    beamMontelGlobal, beamMontelLocalN = \
        beamLine.montel.multiple_reflect(beamSource, maxReflections=20)
    beamFSM2 = beamLine.fsm2.expose(beamMontelGlobal)
    outDict = {'beamSource': beamSource, 'beamFSM1': beamFSM1,
               'beamMontelGlobal': beamMontelGlobal,
               'beamMontelLocalN': beamMontelLocalN,
               'beamFSM2': beamFSM2}
    return outDict
rr.run_process = run_process


def main():
    beamLine = build_beamline()
#    fwhmFormatStrE = '%.2f'
    plots = []
    pAdd = 'P' if isParametric else ''

    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xrtp.XYCAxis(r'$x$', 'mm'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm'), title='FSM1_E')
    plot.caxis.fwhmFormatStr = None
#    plot.caxis.limits = [70, 140]
    plots.append(plot)

    plot = xrtp.XYCPlotWithNumerOfReflections(
        'beamFSM2', (1, 3, -1),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=128, limits=[-10, 20]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=128, limits=[-10, 20]),
        caxis='category', title='FSM2_Es')
    plot.xaxis.fwhmFormatStr = None
    plot.yaxis.fwhmFormatStr = None
    plot.saveName = ['Montel{0}_cat.png'.format(pAdd), ]
    plots.append(plot)

    plot = xrtp.XYCPlotWithNumerOfReflections(
        'beamFSM2', (1, 3, -1),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=128, limits=[-10, 20]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', bins=128, limits=[-10, 20]),
        caxis=xrtp.XYCAxis('number of reflections', '', bins=32, ppb=8,
                           data=raycing.get_reflection_number),
        title='FSM2_Es')
    plot.caxis.limits = [-0.1, 2.1]
    plot.xaxis.fwhmFormatStr = None
    plot.yaxis.fwhmFormatStr = None
    plot.caxis.fwhmFormatStr = None
    plot.saveName = ['Montel{0}_n.png'.format(pAdd), ]
    plots.append(plot)

    xrtr.run_ray_tracing(plots, repeats=40, beamLine=beamLine, processes='all')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
