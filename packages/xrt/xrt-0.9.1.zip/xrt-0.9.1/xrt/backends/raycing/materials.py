# -*- coding: utf-8 -*-
"""
Materials
---------

Module :mod:`~xrt.backends.raycing.materials` defines atomic and material
properties related to x-ray scattering, diffraction and propagation:
reflectivity, transmittivity, refraction index, absorption coefficient etc. It
also compares them with those calculated by XOP.
"""
__author__ = "Konstantin Klementiev"
__date__ = "2 Sep 2014"
import os
import math
#import cmath
import struct
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

ch = 12398.4186  # {5}   {c*h[eV*A]}
twoPi = math.pi * 2.
chbar = ch / twoPi  # {c*hbar[eV*A]}
r0 = 2.817940285e-5  # A
avogadro = 6.02214199e23  # atoms/mol

elementsList = (
    'none', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V',
    'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
    'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',
    'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr',
    'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
    'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi',
    'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U')


class Element(object):
    """This class serves for accessing the scattering factors f0, f1 and f2 of
    a chemical element. It can also report other atomic data listed in
    ``AtomicData.dat`` file adopted from XOP [XOP]_.
    """
    def __init__(self, elem, table='Chantler'):
        """
        The element can be specified by its name (case sensitive) or its
        ordinal number. At the time of instantiation the tabulated scattering
        factors are read which are then interpolated at the requested **q**
        value and energy. *table* can be 'Henke' (10 eV < *E* < 30 keV)
        [Henke]_, 'Chantler' (11 eV < *E* < 405 keV) [Chantler]_ or 'BrCo'
        (30 eV < *E* < 509 keV) [BrCo]_.

        .. [Henke] http://www-cxro.lbl.gov/optical_constants/
           B.L. Henke, E.M. Gullikson, and J.C. Davis, *X-ray interactions:
           photoabsorption, scattering, transmission, and reflection at
           E=50-30000 eV, Z=1-92*, Atomic Data and Nuclear Data Tables
           **54** (no.2) (1993) 181-342.

        .. [Chantler] http://physics.nist.gov/PhysRefData/FFast/Text/cover.html
           http://physics.nist.gov/PhysRefData/FFast/html/form.html
           C. T. Chantler, *Theoretical Form Factor, Attenuation, and
           Scattering Tabulation for Z = 1 - 92 from E = 1 - 10 eV to E = 0.4 -
           1.0 MeV*, J. Phys. Chem. Ref. Data **24** (1995) 71-643.

        .. [BrCo] http://www.bmsc.washington.edu/scatter/periodic-table.html
           ftp://ftpa.aps.anl.gov/pub/cross-section_codes/
           S. Brennan and P.L. Cowan, *A suite of programs for calculating
           x-ray absorption, reflection and diffraction performance for a
           variety of materials at arbitrary wavelengths*, Rev. Sci. Instrum.
           **63** (1992) 850-853.
           """
        if isinstance(elem, basestring):
            self.name = elem
            self.Z = elementsList.index(elem)
        elif isinstance(elem, int):
            self.name = elementsList[elem]
            self.Z = elem
        else:
            raise NameError('Wrong element')
        self.f0coeffs = self.read_f0_Kissel()
        self.E, self.f1, self.f2 = self.read_f1f2_vs_E(table=table)
        self.mass = self.read_atomic_data()

    def read_atomic_data(self):
        """
        Reads atomic data from ``AtomicData.dat`` file adopted from XOP [XOP]_.
        It has the following data:
        0  AtomicRadius[A]  CovalentRadius[A]  AtomicMass  BoilingPoint[K]
        MeltingPoint[K]  Density[g/ccm]  AtomicVolume
        CoherentScatteringLength[1E-12cm]  IncoherentX-section[barn]
        Absorption@1.8A[barn]  DebyeTemperature[K]  ThermalConductivity[W/cmK]

        In :meth:`read_atomic_data` only the mass is inquired. The user may
        extend the method to get the other values by simply adding the
        corresponding array elements to the returned value."""
        dataDir = os.path.dirname(__file__)
        with open(os.path.join(dataDir, 'data', 'AtomicData.dat')) as f:
            for li in f:
                fields = li.split()
                if int(fields[0]) == self.Z:
                    self.atomicData = [float(x) for x in fields]
                    break
        return self.atomicData[3]

    def read_f0_Kissel(self):
        r"""
        Reads f0 scattering factors from the tabulation of XOP [XOP]_. These
        were calculated by [Kissel]_ and then parameterized as [Waasmaier]_:

        .. math::

            f_0\left(\frac{q}{4\pi}\right) = c + \sum_{i=1}^5{a_i\exp\left(-b_i
            \left(q/(4\pi)\right)^2\right)}

        where :math:`q/(4\pi) = \sin{\theta} / \lambda` and :math:`a_i`,
        :math:`b_i` and :math:`c` are the coefficients tabulated in the file
        ``f0_xop.dat``.

        .. [Kissel] L. Kissel, Radiation physics and chemistry **59** (2000)
           185-200, http://www-phys.llnl.gov/Research/scattering/RTAB.html

        .. [Waasmaier] D. Waasmaier & A. Kirfel, Acta Cryst. **A51** (1995)
           416-413
        """
        dataDir = os.path.dirname(__file__)
        with open(os.path.join(dataDir, 'data', 'f0_xop.dat')) as f:
            for li in f:
                if li.startswith("#S"):
                    fields = li.split()
                    if int(fields[1]) == self.Z:
                        break
            else:
                raise 'cannot find the element {0}'.format(self.Z)
                return
            for li in f:
                if li.startswith("#UP"):
                    li = f.next()
                    break
            else:
                raise 'wrong file format!'
                return 0
        return [float(x) for x in li.split()]
#              = [a1  a2  a3  a4  a5  c  b1  b2  b3  b4  b5 ]

    def get_f0(self, qOver4pi=0):  # qOver4pi = sin(theta) / lambda
        """Calculates f0 for the given *qOver4pi*."""
        return self.f0coeffs[5] + sum(
            a * np.exp(-b * qOver4pi**2)
            for a, b in zip(self.f0coeffs[:5], self.f0coeffs[6:]))

    def read_f1f2_vs_E(self, table):
        """Reads f1 and f2 scattering factors from the given *table* at the
        instantiation time."""
        table += '.Ef'
        E, f1, f2 = [], [], []
        startFound = False
        dataDir = os.path.dirname(__file__)
        with open(os.path.join(dataDir, 'data', table), "rb") as f:
            while True:
                structEf1f2 = f.read(12)
                if not structEf1f2:
                    break
                ELoc, f1Loc, f2Loc = struct.unpack_from("<3f", structEf1f2)
                if startFound and ELoc == -1:
                    break
                if ELoc == -1 and f2Loc == self.Z:
                    startFound = True
                    continue
                if startFound:
                    E.append(ELoc)
                    f1.append(f1Loc - self.Z)
                    f2.append(f2Loc)
    #    pylab.plot(E, f1, '.', label=table+'f1')
    #    pylab.plot(E, f2, '.', label=table+'f2')
        return np.array(E), np.array(f1), np.array(f2)

    def get_f1f2(self, E):
        """Calculates (interpolates) f1 and f2 for the given array *E*."""
        if np.any(E < self.E[0]) or np.any(E > self.E[-1]):
            raise ValueError(
                ('E={0} is out of the data table range ' +
                 '[{1}, {2}]!!! Use another table.').format(
                    E[np.where((E < self.E[0]) | (E > self.E[-1]))], self.E[0],
                    self.E[-1]))
        f1 = np.interp(E, self.E, self.f1)
        f2 = np.interp(E, self.E, self.f2)
        return f1 + 1j * f2


class Material(object):
    """
    :class:`Material` serves for getting reflectivity, transmittivity,
    refraction index and absorption coefficient of a material specified by its
    chemical formula and density."""
    def __init__(self, elements, quantities=None, kind='mirror', rho=0, t=None,
                 table='Chantler'):
        """
        *elements*: str or sequence of str, contains all the constituent
        elements (symbols).

        *quantities*: None or sequence of floats of length of *elements*.
        Coefficients in the chemical formula. If None, the coefficients = 1.

        *kind*: one of 'mirror', 'thin mirror', 'plate', 'lens', 'grating',
        'FZP'

        *rho*: density in g/cm\ :sup:`3`.

        *t*: thickness in mm, required only for 'thin mirror'.

        *table*: tabulation of f1 and f2 of the material's elements.
        """
        if isinstance(elements, basestring):
            elements = elements,
        if quantities is None:
            self.quantities = [1. for elem in elements]
        else:
            self.quantities = quantities
        self.elements = []
        self.mass = 0.
        self.name = r''
        for elem, xi in zip(elements, self.quantities):
            newElement = Element(elem, table)
            self.elements.append(newElement)
            self.mass += xi * newElement.mass
            self.name += elem
            if xi != 1:
                self.name += '$_{' + '{0}'.format(xi) + '}$'
        self.kind = kind  # 'mirror', 'thin mirror', 'plate', 'lens'
        if self.kind == 'thin mirror':
            if t is None:
                raise ValueError('Give the thin mirror a thickness!')
            self.t = t  # t in mm
        self.rho = rho  # density g/cm^3
        self.geom = ''

    def get_refraction_index(self, E):
        r"""
        Calculates refraction index at given *E*. *E* can be an array.

        .. math::

            n = 1 - \frac{r_0\lambda^2 N_A \rho}{2\pi M}\sum_i{x_i f_i(0)}

        where :math:`r_0` is the classical electron radius, :math:`\lambda` is
        the wavelength, :math:`N_A` is Avogadro’s number, :math:`\rho` is the
        material density, *M* is molar mass, :math:`x_i` are atomic
        concentrations (coefficients in the chemical formula) and
        :math:`f_i(0)` are the complex atomic scattering factor for the forward
        scattering.
        """
        xf = np.zeros_like(E) * 0j
        for elem, xi in zip(self.elements, self.quantities):
            xf += (elem.Z + elem.get_f1f2(E)) * xi
        return 1 - 1e-24 * avogadro * r0 / twoPi * (ch / E)**2 * self.rho * \
            xf / self.mass  # 1e-24 = A^3/cm^3

    def get_absorption_coefficient(self, E):  # mu0
        r"""
        Calculates the linear absorption coefficient from the imaginary part of
        refraction index. *E* can be an array. The result is in cm\ :sup:`-1`.

        .. math::

            \mu = \Im(n)/\lambda.
        """
        return abs((self.get_refraction_index(E)).imag) * E / chbar * 2e8

    def get_amplitude(self, E, beamInDotNormal, fromVacuum=True):
        r"""
        Calculates amplitude of reflectivity (for 'mirror' and 'thin mirror')
        or transmittivity (for 'plate' and 'lens') [wikiFresnelEq]_,
        [Als-Nielsen]_. *E* is energy, *beamInDotNormal* is cosine of the angle
        between the incoming beam and the normal (:math:`\theta_1` below), both
        can be scalars or arrays. The interface of the material is assumed to
        be with vacuum; the direction is given by boolean *fromVacuum*. Returns
        a tuple of the amplitudes of s and p polarizations and the absorption
        coefficient in cm\ :sup:`-1`.

        .. math::

            r_s^{\rm mirror} &= \frac{n_1\cos{\theta_1} - n_2\cos{\theta_2}}
            {n_1\cos{\theta_1} + n_2\cos{\theta_2}}\\
            r_p^{\rm mirror} &= \frac{n_2\cos{\theta_1} - n_1\cos{\theta_2}}
            {n_2\cos{\theta_1} + n_1\cos{\theta_2}}\\

            r_{s,p}^{\rm thin\ mirror} &= r_{s,p}^{\rm mirror}\frac{1 - p^2}
            {1 - (r_{s,p}^{\rm mirror})^2p^2},

        where the phase factor
        :math:`p^2 = \exp(2iEtn_2\cos{\theta_2}/c\hbar)`.

        .. math::

            t_s^{\rm plate,\ lens} &= 2\frac{n_1\cos{\theta_1}}
            {n_1\cos{\theta_1} + n_2\cos{\theta_2}}t_f\\
            t_p^{\rm plate,\ lens} &= 2\frac{n_1\cos{\theta_1}}
            {n_2\cos{\theta_1} + n_1\cos{\theta_2}}t_f\\

        where :math:`t_f = \sqrt{\frac{\Re(n_2n_1)\cos{\theta_2}}
        {cos{\theta_1}}}/|n_1|`.

        .. [wikiFresnelEq] http://en.wikipedia.org/wiki/Fresnel_equations .
        .. [Als-Nielsen] Jens Als-Nielsen, Des McMorrow, *Elements of Modern
           X-ray Physics*, John Wiley and Sons, 2001.
        """
        if self.kind in ('grating', 'FZP'):
            return 1, 1, 0
        n = self.get_refraction_index(E)
#        print 1-n
        if fromVacuum:
            n1 = 1.
            n2 = n
        else:
            n1 = n
            n2 = 1.
        cosAlpha = abs(beamInDotNormal)
        sinAlpha = np.sqrt(1 - beamInDotNormal**2)
        if isinstance(sinAlpha, np.ndarray):
            sinAlpha[np.isnan(sinAlpha)] = 0.
        n1cosAlpha = n1 * cosAlpha
#        cosBeta = np.sqrt(1 - (n1.real/n2.real*sinAlpha)**2)
        cosBeta = np.sqrt(1 - (n1/n2*sinAlpha)**2)
        n2cosBeta = n2 * cosBeta
        if self.kind in ('mirror', 'thin mirror', 'grating'):  # reflectivity
            rs = (n1cosAlpha-n2cosBeta) / (n1cosAlpha+n2cosBeta)
            rp = (n2*cosAlpha - n1*cosBeta) / (n2*cosAlpha + n1*cosBeta)
            if self.kind == 'thin mirror':
                p2 = np.exp(2j * E / chbar * n2cosBeta * self.t * 1e7)
                rs *= (1-p2) / (1 - rs**2*p2)
                rp *= (1-p2) / (1 - rp**2*p2)
        elif self.kind in ('plate', 'lens', 'FZP'):  # transmittivity
            tf = np.sqrt(
                (n2cosBeta * n1.conjugate()).real / cosAlpha) / abs(n1)
            rs = 2 * n1cosAlpha / (n1cosAlpha+n2cosBeta) * tf
            rp = 2 * n1cosAlpha / (n2*cosAlpha + n1*cosBeta) * tf
        return rs, rp, abs(n.imag) * E / chbar * 2e8  # 1/cm


class Crystal(Material):
    """The parent class for crystals. The descendants must define
    :meth:`get_structure_factor`. :class:`Material` gives reflectivity and
    transmittivity of a crystal in Bragg and Laue cases."""
    def __init__(self, hkl, d, V=None, elements='Si', quantities=None, rho=0,
                 t=None, factDW=1., geom='Bragg reflected', table='Chantler'):
#      table='Henke'):
        u"""
        *hkl* a sequence of hkl indices.

        *d* interatomic spacing in Å.

        *V* unit cell volume in Å\ :sup:`3`. If not given, is calculated from
        *d* assuming a cubic symmetry.

        *elements*, *quantities*, *rho*, *t*, *table* are used by the parent
        :class:`Material`.

        *factDW*: Debye-Waller factor applied to the structure factor.

        *geom*: the 1st word is either 'Bragg' or 'Laue', the 2nd word is
        either 'transmitted' or 'reflected' or 'Fresnel' (the optical element
        must then provide `local_g` method that gives the grating vector).
        """
        super(Crystal, self).__init__(elements, quantities, rho, table)
        self.hkl = hkl
        self.sqrthkl2 = math.sqrt(sum(i**2 for i in hkl))
        self.d = d
        if V is None:
            V = (d * self.sqrthkl2)**3
        self.V = V
        self.chiToF = - r0 / math.pi / self.V  # minus!
        self.geom = geom
        self.factDW = factDW
        self.kind = 'crystal'
        self.t = t  # in mm

#    def get_amplitude_Authie(self, E, gamma0, gammah, beamInDotHNormal):
#        """A. Authier, Dynamical Theory of X-ray Diffraction -1. Perfect
#        Crystals, in X-ray and Neutron Dynamical Diffraction: Theory and
#        Applications, ed. A. Authier, S. Lagomarsino & B. K. Tanner, NATO ASI
#        Ser., Ser. B: Physics 357 (1996) 1–32, Plenum Press: New York and
#        London."""
#        def _dynamical_theory_Bragg():
#            rx = np.sqrt(eta**2 - 1)
#            if self.t is not None:
#                arg = self.t * 1e7 * rx * math.pi/ lambdaExt
#                if self.geom.endswith('transmitted'):
#                    mu0 = -twoPi / waveLength * chi0.imag
#                    att = np.exp(-mu0 / 4 * (-1. / gamma0 - 1. / gammah) *
#                                 self.t)
#                    ta = att / (np.cos(arg) + 1j * eta * np.sin(arg) / rx)
#                    return ta
#                eps = 1.0j / np.tan (arg)
#            else:
#                eps = 1.
#            ra = 1. / (eta - rx * eps)
#            rb = 1. / (eta + rx * eps)
#            indB = np.where(abs(rb) < abs(ra))
#            ra[indB] = rb[indB]
#            return ra
#        def _dynamical_theory_Laue():
#            rx = np.sqrt(eta**2 + 1)
#            mu0 = -twoPi / waveLength * chi0.imag
#            t = self.t * 1e7
#            att = np.exp(-mu0 / 4 * (-1. / gamma0 - 1. / gammah) * t)
#            arg = t * rx * math.pi / lambdaExt
#            if self.geom.endswith('transmitted'):
#                ta = att * (np.cos(arg) + 1j * eta * np.sin(arg) / rx)
#                return ta
#            ra = abs(chih / chih_) * att * np.sin(arg) / rx
#            return ra
#        if self.geom.startswith('Bragg'):
#            _dynamical_theory = _dynamical_theory_Bragg
#        else:
#            _dynamical_theory = _dynamical_theory_Laue
#        waveLength = ch / E#the word "lambda" is reserved
#        sinThetaOverLambda = abs(beamInDotHNormal / waveLength)
#        F0, Fhkl, Fhkl_ = self.get_structure_factor(E, sinThetaOverLambda)
#        lambdaSquare = waveLength ** 2
#        chiToFlambdaSquare = self.chiToF * lambdaSquare
#        chi0 = F0 * chiToFlambdaSquare
#        chih = Fhkl * chiToFlambdaSquare
#        chih_ = Fhkl_ * chiToFlambdaSquare
#        gamma = gammah / gamma0# asymmetry parameter = 1/b
#        theta = np.arcsin(abs(beamInDotHNormal))
#        sin2theta = np.sin(2. * theta)
#        cos2theta = np.cos(2. * theta)
#        theta0 = np.arcsin(ch / (2 * self.d * E))
#        dtheta0 = - chi0 * (1 - gamma) / 2 / sin2theta
#        delta = np.sqrt(abs(gamma) * chih * chih_)/ sin2theta
#        if self.t is not None:
#            lambdaExt = waveLength * abs(gammah) / (delta * sin2theta)
#        else:
#            lambdaExt = None
#        eta = (theta - theta0 - dtheta0) / delta
##s polarization:
#        resS = _dynamical_theory()
##p polarization:
#        eta /= cos2theta
#        if self.t is not None:
#            lambdaExt /= cos2theta
#        resP = _dynamical_theory()
#        return resS, resP

    def get_Darwin_width(self, E, b=1., polarization='s'):
        r"""Calculates the Darwin width as

        .. math::

            2\delta = |C|\sqrt{\chi_h\chi_{\overline{h}} / b}/\sin{2\theta}
        """
        theta0 = self.get_Bragg_angle(E)
        sin2theta = np.sin(2. * theta0)
        waveLength = ch / E  # the word "lambda" is reserved
        sinThetaOverLambda = np.sin(theta0) / waveLength
        F0, Fhkl, Fhkl_ = self.get_structure_factor(E, sinThetaOverLambda)
        lambdaSquare = waveLength**2
        chiToFlambdaSquare = self.chiToF * lambdaSquare
        chih = Fhkl * chiToFlambdaSquare
        chih_ = Fhkl_ * chiToFlambdaSquare
        if polarization == 's':
            polFactor = 1.
        else:
            polFactor = np.cos(2. * theta0)
        return 2 * (np.sqrt((polFactor**2 * chih*chih_ / b)) / sin2theta).real

    def get_extinction_depth(self, E, polarization='s'):  # in microns
        theta0 = self.get_Bragg_angle(E)
        dw = self.get_Darwin_width(E, 1., polarization)
        return self.d / 2. / dw * np.tan(theta0) * 1e-4   # in microns

    def get_amplitude(self, E, beamInDotNormal, beamOutDotNormal,
                      beamInDotHNormal):
        r"""
        Calculates complex amplitude reflectivity and transmittivity for s- and
        p-polarizations (:math:`\gamma = s, p`) in Bragg and Laue cases for the
        crystal of thickness *L*, based upon Belyakov & Dmitrienko [BD]_:

        .. math::

            R_{\gamma}^{\rm Bragg} &= \chi_{\vec{H}}C_{\gamma}(\alpha +
            i\Delta_{\gamma}\cot{l_{\gamma}})^{-1}|b|^{-\frac{1}{2}}\\
            T_{\gamma}^{\rm Bragg} &= (\cos{l{_\gamma}} - i\alpha\Delta
            {_\gamma}^{-1}\sin{l_{\gamma}})^{-1}\exp{(i\vec{\kappa}_0^2 L
            (\chi_0 - \alpha b) (2\vec{\kappa}_0\vec{s})^{-1})}\\
            R_{\gamma}^{\rm Laue} &= \chi_{\vec{H}}C_{\gamma}
            \Delta_{\gamma}^{-1}\sin{l_{\gamma}}\exp{(i\vec{\kappa}_0^2 L
            (\chi_0 - \alpha b) (2\vec{\kappa}_0\vec{s})^{-1})}
            |b|^{-\frac{1}{2}}\\
            T_{\gamma}^{\rm Laue} &= (\cos{l_{\gamma}} + i\alpha
            \Delta_{\gamma}^{-1}\sin{l_{\gamma}})\exp{(i\vec{\kappa}_0^2 L
            (\chi_0 - \alpha b) (2\vec{\kappa}_0\vec{s})^{-1})}

        where

        .. math::

            \alpha &= \frac{\vec{H}^2 + 2\vec{\kappa}_0\vec{H}}
            {2\vec{\kappa}_0^2}+\frac{\chi_0(1-b)}{2b}\\
            \Delta_{\gamma} &= \left(\alpha^2 +\frac{C_{\gamma}^2\chi_{\vec{H}}
            \chi_{\overline{\vec{H}}}}{b}\right)^{\frac{1}{2}}\\
            l_{\gamma} &= \frac{\Delta_{\gamma}\vec{\kappa}_0^2L}
            {2\vec{\kappa}_{\vec{H}}\vec{s}}\\
            b &= \frac{\vec{\kappa}_0\vec{s}}{\vec{\kappa}_{\vec{H}}\vec{s}}\\
            C_s &= 1, \quad C_p = \cos{2\theta_B}

        In the case of thick crystal in Bragg geometry:

        .. math::

            R_{\gamma}^{\rm Bragg} = \frac{\chi_{\vec{H}} C_{\gamma}}
            {\alpha\pm\Delta_{\gamma}}|b|^{-\frac{1}{2}}

        with the sign in the denominator that gives the smaller modulus of
        :math:`R_\gamma`.

        :math:`\chi_{\vec{H}}` is the Fourier harmonic of the x-ray
        susceptibility, and :math:`\vec{H}` is the reciprocal lattice vector of
        the crystal. :math:`\vec{\kappa}_0` and :math:`\vec{\kappa}_{\vec{H}}`
        are the wave vectors of the direct and diffracted waves.
        :math:`\chi_{\vec{H}}` is calculated as:

        .. math::

            \chi_{\vec{H}} = - \frac{r_0\lambda^2}{\pi V}F_{\vec{H}},

        where :math:`r_e = e^2 / mc^2` is the classical radius of the electron,
        :math:`\lambda` is the wavelength, *V* is the volume of the unit cell.

        notice :math:`|b|^{-\frac{1}{2}}` added to the formulas of Belyakov &
        Dmitrienko in the cases of Bragg and Laue reflections. This is needed
        because ray tracing deals not with wave fields but with rays and
        therefore not with intensities (i.e. per cross-section) but with flux.

        .. [BD] V. A. Belyakov and V. E. Dmitrienko, *Polarization phenomena in
           x-ray optics*, Uspekhi Fiz. Nauk. **158** (1989) 679–721, Sov. Phys.
           Usp. **32** (1989) 697–719.
        """
        def for_one_polarization(polFactor):
            delta = np.sqrt((alpha**2 + polFactor**2 * chih * chih_ / b))
            if self.t is None:  # thick Bragg
#                if (alpha==np.nan).sum()>0: print '(alpha==np.nan).sum()>0!!!'
                ra = chih * polFactor / (alpha+delta)
                ad = alpha - delta
                ad[ad == 0] = 1e-100
                rb = chih * polFactor / ad
                indB = np.where(np.isnan(ra))
                ra[indB] = rb[indB]
                indB = np.where(abs(rb) < abs(ra))
                ra[indB] = rb[indB]
#                if np.isnan(ra).sum() > 0:
#                    if (alpha == -delta).sum() > 0:
#                        print 'alpha = -delta!', (alpha == -delta).sum()
#                        print 'alpha ',alpha[alpha == -delta]
#                        print 'delta ', delta[alpha == -delta]
#                        print 'chih ', chih[alpha == -delta]
#                        print 'b ', b[alpha == -delta]
#                    if (alpha == delta).sum() > 0:
#                        print 'alpha = delta!', (alpha == delta).sum()
#                    if np.isnan(alpha).sum() > 0:
#                        print 'alpha contains nan!'
#                    if np.isnan(delta).sum() > 0:
#                        print 'delta contains nan!'
#                    if np.isnan(chih).sum() > 0:
#                        print 'chih contains nan!'
#                    raise ValueError('reflectivity contains nan!')
                return ra / np.sqrt(abs(b))
            t = self.t * 1e7
            l = t * delta * k02 / 2 / kHs
            if self.geom.startswith('Bragg'):
                if self.geom.endswith('transmitted'):
                    ra = 1 / (np.cos(l) - 1j * alpha * np.sin(l) / delta) *\
                        np.exp(1j * k02 * t * (chi0 - alpha*b) / 2 / k0s)
                else:
                    ra = chih * polFactor / (alpha + 1j*delta / np.tan(l))
            else:  # Laue
                if self.geom.endswith('transmitted'):
                    ra = (np.cos(l) + 1j * alpha * np.sin(l) / delta) *\
                        np.exp(1j * k02 * t * (chi0 - alpha*b) / 2 / k0s)
                else:
                    ra = chih * polFactor * np.sin(l) / delta *\
                        np.exp(1j * k02 * t * (chi0 - alpha*b) / 2 / k0s)
            if not self.geom.endswith('transmitted'):
                ra /= np.sqrt(abs(b))
            return ra
        waveLength = ch / E  # the word "lambda" is reserved
        k = twoPi / waveLength
        k0s = -beamInDotNormal * k
        kHs = -beamOutDotNormal * k
        k0H = abs(beamInDotHNormal) * (twoPi/self.d) * k
        k02 = k**2
        H2 = (twoPi / self.d)**2
        b = k0s / kHs
        F0, Fhkl, Fhkl_ = \
            self.get_structure_factor(E, np.sqrt(H2) / 4 / math.pi)
        lambdaSquare = waveLength ** 2
#notice conjugate() needed for the formulas of Belyakov & Dmitrienko!!!
        chiToFlambdaSquare = self.chiToF * lambdaSquare
        chi0 = F0.conjugate() * chiToFlambdaSquare
        chih = Fhkl.conjugate() * chiToFlambdaSquare
        chih_ = Fhkl_.conjugate() * chiToFlambdaSquare

        thetaB = self.get_Bragg_angle(E)
        alpha = (H2/2 - k0H) / k02 + chi0/2 * (1/b - 1)
        curveS = for_one_polarization(1.)  # s polarization
        polFactor = np.cos(2. * thetaB)
        curveP = for_one_polarization(polFactor)  # p polarization
        return curveS, curveP  # , phi.real

    def get_Bragg_angle(self, E):
        return np.arcsin(ch / (2*self.d*E))

    def get_dtheta_symmetric_Bragg(self, E):
        r"""
        The angle correction for the symmetric Bragg case:

        .. math::

            \delta\theta = \chi_0 / \sin{2\theta_B}
        """
        F0, Fhkl, Fhkl_ = self.get_structure_factor(E, 0.5 / self.d)
        waveLength = ch / E  # the word "lambda" is reserved
        lambdaSquare = waveLength ** 2
#notice conjugate() needed for the formulas of Belyakov & Dmitrienko!!!
        chiToFlambdaSquare = self.chiToF * lambdaSquare
        chi0 = F0 * chiToFlambdaSquare
        thetaB = self.get_Bragg_angle(E)
        return (chi0 / np.sin(2*thetaB)).real


class CrystalFcc(Crystal):
    r"""
    A derivative class from :class:`Crystal` that defines the structure factor
    for an fcc crystal as:

    .. math::

        F_{hkl}^{fcc} = f \times \left\{ \begin{array}{rl}
        4 &\mbox{if $h,k,l$ are all even or all odd} \\ 0 &\mbox{ otherwise}
        \end{array} \right.
    """
    def get_structure_factor(self, E, sinThetaOverLambda):
        anomalousPart = self.elements[0].get_f1f2(E)
        F0 = 4 * (self.elements[0].Z+anomalousPart) * self.factDW
        residue = sum(i % 2 for i in self.hkl)
        if residue == 0 or residue == 3:
            f0 = self.elements[0].get_f0(sinThetaOverLambda)
            Fhkl = 4 * (f0+anomalousPart) * self.factDW
        else:
            Fhkl = 0.
        return F0, Fhkl, Fhkl


class CrystalDiamond(CrystalFcc):
    r"""
    A derivative class from :class:`Crystal` that defines the structure factor
    for a diamond-like crystal as:

    .. math::

        F_{hkl}^{\rm diamond} = F_{hkl}^{fcc}\left(1 + e^{i\frac{\pi}{2}
        (h + k + l)}\right).
    """
    def get_structure_factor(self, E, sinThetaOverLambda):
        diamondToFcc = 1 + np.exp(0.5j * math.pi * sum(self.hkl))
        F0, Fhkl, Fhkl_ = super(CrystalDiamond, self).get_structure_factor(
            E, sinThetaOverLambda)
        return F0 * 2, Fhkl * abs(diamondToFcc), Fhkl_ * abs(diamondToFcc)


class CrystalSi(CrystalDiamond):
    """
    A derivative class from :class:`CrystalDiamond` that defines the crystal
    d-spacing as a function of temperature.
    """
    def __init__(self, *args, **kwargs):
        """
        *tK* is the temperature in Kelvin.
        *hkl* are the hkl indices given as a tuple.
        """
        self.tK = kwargs.pop('tK', 297.15)
        self.hkl = kwargs.get('hkl', (1, 1, 1))
# Batchelder and Simmons, J. Chem. Phys. 41, 2324 (1964):
        self.a0 = 5.419490
        self.dl_l0 = self.dl_l(273.15)
        self.sqrthkl2 = math.sqrt(sum(i**2 for i in self.hkl))
        kwargs['d'] = self.get_a() / self.sqrthkl2
        kwargs['elements'] = 'Si'
        kwargs['hkl'] = self.hkl
        super(CrystalSi, self).__init__(*args, **kwargs)

    def dl_l(self, t=None):
        """Calculates the crystal elongation at temperature *t*. Uses the
        parameterization from [Swenson]_. Less than 1% error; the reference
        temperature is 19.9C; data is in units of unitless; *t* must be in
        degrees Kelvin.

        .. [Swenson] C.A. Swenson, J. Phys. Chem. Ref. Data 12(2) (1983) 179
        """
        if t is None:
            t = self.tK
        if t >= 0.0 and t < 30.0:
            return -2.154537e-004
        elif t >= 30.0 and t < 130.0:
            return -2.303956e-014 * t**4 + 7.834799e-011 * t**3 - \
                1.724143e-008 * t**2 + 8.396104e-007 * t - 2.276144e-004
        elif t >= 130.0 and t < 293.0:
            return -1.223001e-011 * t**3 + 1.532991e-008 * t**2 - \
                3.263667e-006 * t - 5.217231e-005
        elif t >= 293.0 and t <= 1000.0:
            return -1.161022e-012 * t**3 + 3.311476e-009 * t**2 + \
                1.124129e-006 * t - 5.844535e-004
        else:
            return 1.0e+100

    def get_a(self):
        """Gives the lattice parameter."""
        return self.a0 * (self.dl_l()-self.dl_l0+1)

    def get_Bragg_offset(self, E, Eref):
        """Calculates the Bragg angle offset due to a mechanical (mounting)
        misalignment.

        *E* is the calculated energy of a spectrum feature, typically the edge
        position.

        *Eref* is the tabulated position of the same feature."""
        self.d = self.get_a() / self.sqrthkl2
        chOverTwod = ch / 2 / self.d
        return math.asin(chOverTwod/E) - math.asin(chOverTwod/Eref)


def compare_rocking_curves(hkl, t=None, geom='Bragg reflected', factDW=1.,
                           legendPos1=4, legendPos2=1):
    """A comparison subroutine used in the module test suit."""
    def for_one_alpha(crystal, alphaDeg, hkl):
        alpha = math.radians(alphaDeg)
        s0 = (np.zeros_like(theta), np.cos(theta+alpha), -np.sin(theta+alpha))
        sh = (np.zeros_like(theta), np.cos(theta-alpha), np.sin(theta-alpha))
        if geom.startswith('Bragg'):
            n = (0, 0, 1)  # outward surface normal
        else:
            n = (0, -1, 0)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))

        fig = plt.figure()
        fig.subplots_adjust(right=0.88)
        ax = fig.add_subplot(111)

#        curS, curP = crystal.get_amplitude_Authie(E, gamma0, gammah, hns0)
#        p5, = ax.plot((theta - thetaCenter) * convFactor, abs(curS)**2, '-g')
#        p6, = ax.plot((theta - thetaCenter) * convFactor, abs(curP)**2, '--g')
        curS, curP = crystal.get_amplitude(E, gamma0, gammah, hns0)
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(curS * curP.conj()))
        p9, = ax2.plot((theta-thetaCenter) * convFactor, phi, 'c', lw=1,
                       yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')

        if t is not None:
            tt = u', t={0:.0f}µm'.format(t * 1e3)
            tname = '{0:03d}mum'.format(int(t * 1e3))
        else:
            tt = ' thick'
            tname = 'thick'
        if geom.startswith('Bragg'):
            geomPrefix = 'b'
        else:
            geomPrefix = 'l'
        if geom.endswith('transmitted'):
            geomPrefix += 't'
        fig.suptitle(r'{0} Si{1}, $\alpha={2:.1f}^\circ${3}'.format(geom,
                     hkl, alphaDeg, tt), fontsize=16)

        path = os.path.join('data', 'XOP-RockingCurves') + os.sep
        x, R2s = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_s.xc.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s XCrystal')
        x, R2p = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_p.xc.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p2, = ax.plot(x, R2p, '--k', label='p XCrystal')

        x, R2s = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_s.xin.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p3, = ax.plot(x, R2s, '-b', label='s XInpro')
        x, R2p = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_p.xin.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p4, = ax.plot(x, R2p, '--b', label='p XInpro')

        p7, = ax.plot((theta - thetaCenter) * convFactor, abs(curS)**2, '-r')
        p8, = ax.plot((theta - thetaCenter) * convFactor, abs(curP)**2, '--r')
        ax.set_xlabel(r'$\theta-\theta_B$ (arcsec)')
        if geom.endswith('transmitted'):
            ax.set_ylabel('transmittivity')
        else:
            ax.set_ylabel('reflectivity')
        ax.set_xlim([dtheta[0] * convFactor, dtheta[-1] * convFactor])
#upper right	1
#upper left	2
#lower left	3
#lower right	4
#right   	5
#center left	6
#center right	7
#lower center	8
#upper center	9
#center         10
        l1 = ax2.legend([p1, p2], ['s', 'p'], loc=legendPos1)
#        ax.legend([p1, p3, p5, p7], ['XCrystal/XOP', 'XInpro/XOP',
#        'pxrt-Authier', 'pxrt-Bel&Dm'], loc=1)
        ax2.legend([p1, p3, p7], ['XCrystal/XOP', 'XInpro/XOP', 'xrt'],
                   loc=legendPos2)
        ax2.add_artist(l1)

        fname = '{0}Si{1}_{2}_{3:-.0f}'.format(
            geomPrefix, hkl, tname, alphaDeg)
        fig.savefig(fname + '.png')

    E0 = 10000.
    convFactor = 180 / math.pi * 3600.  # arcsec
    if hkl == '111':  # Si111
        if geom.startswith('Bragg'):
            dtheta = np.linspace(0, 100, 400) * 1e-6
        else:
            dtheta = np.linspace(-50, 50, 400) * 1e-6
        dSpacing = 3.13562
        hklInd = 1, 1, 1
    elif hkl == '333':  # Si333
        if geom.startswith('Bragg'):
            dtheta = np.linspace(0, 30, 400) * 1e-6
        else:
            dtheta = np.linspace(-15, 15, 400) * 1e-6
        dSpacing = 3.13562 / 3
        hklInd = 3, 3, 3

    siCrystal = CrystalDiamond(hklInd, dSpacing, t=t, geom=geom, factDW=factDW)
    thetaCenter = math.asin(ch / (2*siCrystal.d*E0))

    E = np.ones_like(dtheta) * E0
    theta = dtheta + thetaCenter
    for_one_alpha(siCrystal, 0., hkl)
    for_one_alpha(siCrystal, -5., hkl)
    for_one_alpha(siCrystal, 5., hkl)


def compare_Bragg_Laue(hkl, beamPath, factDW=1.):
    """A comparison subroutine used in the module test suit."""
    def for_one_alpha(alphaDeg, hkl):
        alpha = math.radians(alphaDeg)
        s0 = (np.zeros_like(theta), np.cos(theta+alpha), -np.sin(theta+alpha))
        sh = (np.zeros_like(theta), np.cos(theta-alpha), np.sin(theta-alpha))

#'Bragg':
        n = (0, 0, 1)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))
        braggS, braggP = siBraggCrystal.get_amplitude(E, gamma0, gammah, hns0)
#'Laue':
        n = (0, -1, 0)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))
        laueS, laueP = siLaueCrystal.get_amplitude(E, gamma0, gammah, hns0)

        fig = plt.figure()
        ax = fig.add_subplot(111)

# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(braggS * braggP.conj()))
        p5, = ax2.plot((theta-thetaCenter) * convFactor, phi, '-c', lw=1,
                       yunits=math.pi, zorder=0)
        phi = np.unwrap(np.angle(laueS * laueP.conj()))
        p6, = ax2.plot((theta-thetaCenter) * convFactor, phi, '-c.', lw=1,
                       yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')

        fig.suptitle(r'Comparison of Bragg and Laue transmittivity for Si{0}'.
                     format(hkl), fontsize=16)
        p1, = ax.plot((theta-thetaCenter) * convFactor, abs(braggS)**2, '-r')
        p2, = ax.plot((theta-thetaCenter) * convFactor, abs(braggP)**2, '-b')
        p3, = ax.plot((theta-thetaCenter) * convFactor, abs(laueS)**2, '-r.')
        p4, = ax.plot((theta-thetaCenter) * convFactor, abs(laueP)**2, '-b.')
        ax.set_xlabel(r'$\theta-\theta_B$ (arcsec)')
        ax.set_ylabel('transmittivity')

#upper right	1
#upper left	2
#lower left	3
#lower right	4
#right   	5
#center left	6
#center right	7
#lower center	8
#upper center	9
#center         10
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], [u'Bragg t={0:.1f} µm'.format(
            siBraggCrystal.t * 1e3), u'Laue t={0:.1f} µm'.format(
            siLaueCrystal.t * 1e3)], loc=2)
        ax.add_artist(l1)
        ax.set_xlim([dtheta[0] * convFactor, dtheta[-1] * convFactor])

        fname = r'BraggLaueTrSi{0}'.format(hkl)
        fig.savefig(fname + '.png')

    E0 = 10000.
    convFactor = 180 / math.pi * 3600.  # arcsec
    if hkl == '111':  # Si111
        dtheta = np.linspace(-100, 100, 400) * 1e-6
        dSpacing = 3.13562
        hklInd = 1, 1, 1
    elif hkl == '333':  # Si333
        dtheta = np.linspace(-30, 30, 400) * 1e-6
        dSpacing = 3.13562 / 3
        hklInd = 3, 3, 3

    thetaCenter = math.asin(ch / (2*dSpacing*E0))
    t = beamPath * math.sin(thetaCenter)
    siBraggCrystal = CrystalDiamond(hklInd, dSpacing, t=t,
                                    geom='Bragg transmitted', factDW=factDW)
    t = beamPath * math.cos(thetaCenter)
    siLaueCrystal = CrystalDiamond(hklInd, dSpacing, t=t,
                                   geom='Laue transmitted', factDW=factDW)

    E = np.ones_like(dtheta) * E0
    theta = dtheta + thetaCenter
    for_one_alpha(0., hkl)
#    for_one_alpha(siCrystal, -5., hkl)
#    for_one_alpha(siCrystal, 5., hkl)


def compare_reflectivity():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(stripe, refs, refp, theta, reprAngle):
        fig = plt.figure()
        fig.subplots_adjust(right=0.86)
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel('reflectivity')
        ax.set_xlim(30, 5e4)
        fig.suptitle(stripe.name + ' ' + reprAngle, fontsize=16)
        x, R2s = np.loadtxt(refs, unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s xf1f2')
        x, R2s = np.loadtxt(refp, unpack=True)
        p2, = ax.plot(x, R2s, '--k', label='p xf1f2')
        refl = stripe.get_amplitude(E, math.sin(theta))
        rs, rp = refl[0], refl[1]
        p3, = ax.semilogx(E, abs(rs)**2, '-r')
        p4, = ax.semilogx(E, abs(rp)**2, '--r')
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], ['Xf1f2/XOP', 'xrt'], loc=6)
        ax.add_artist(l1)
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(rs * rp.conj()))
        p9, = ax2.plot(x, phi, 'c', lw=2, yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')
        fname = 'MirrorRefl' + stripe.name + reprAngle
        fig.savefig(fname + '.png')

    dataDir = os.path.join('data', 'XOP-Reflectivities')
    E = np.logspace(1.+math.log10(3.), 4.+math.log10(5.), 500)
    stripeSi = Material('Si', rho=2.33)
    for_one_material(stripeSi,
                     os.path.join(dataDir, "Si05deg_s.xf1f2.gz"),
                     os.path.join(dataDir, "Si05deg_p.xf1f2.gz"),
                     math.radians(0.5), '@ 0.5 deg')
    stripePt = Material('Pt', rho=21.45)
    for_one_material(stripePt,
                     os.path.join(dataDir, "Pt4mrad_s.xf1f2.gz"),
                     os.path.join(dataDir, "Pt4mrad_p.xf1f2.gz"),
                     4e-3, '@ 4 mrad')
    stripeSiO2 = Material(('Si', 'O'), quantities=(1, 2), rho=2.2)
    for_one_material(stripeSiO2,
                     os.path.join(dataDir, "SiO205deg_s.xf1f2.gz"),
                     os.path.join(dataDir, "SiO205deg_p.xf1f2.gz"),
                     math.radians(0.5), '@ 0.5 deg')
    stripeRh = Material('Rh', rho=12.41)
    for_one_material(stripeRh,
                     os.path.join(dataDir, "Rh2mrad_s.xf1f2.gz"),
                     os.path.join(dataDir, "Rh2mrad_p.xf1f2.gz"),
                     2e-3, '@ 2 mrad')


def compare_reflectivity_slab():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(stripe, refs, refp, E, reprEnergy):
        fig = plt.figure()
        fig.subplots_adjust(right=0.86)
        ax = fig.add_subplot(111)
        ax.set_xlabel('grazing angle (deg)')
        ax.set_ylabel('reflectivity')
        ax.set_xlim(0, 10)
        fig.suptitle(stripe.name + ' ' + reprEnergy, fontsize=16)
        x, R2s = np.loadtxt(refs, unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s Mlayer')
        x, R2s = np.loadtxt(refp, unpack=True)
        p2, = ax.plot(x, R2s, '--k', label='p Mlayer')
        refl = stripe.get_amplitude(E, np.sin(np.deg2rad(theta)))
        rs, rp = refl[0], refl[1]
        p3, = ax.semilogy(theta, abs(rs)**2, '-r')
        p4, = ax.semilogy(theta, abs(rp)**2, '--r')
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], ['Mlayer/XOP', 'xrt'], loc=1)
        ax.add_artist(l1)
        ylim = ax.get_ylim()
        ax.set_ylim([ylim[0], 1])
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(rs * rp.conj()))
        p9, = ax2.plot(x, phi, 'c', lw=2, yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')
        fname = 'SlabRefl' + stripe.name + ' ' + reprEnergy
        fig.savefig(fname + '.png')

    dataDir = os.path.join('data', 'XOP-Reflectivities')
    theta = np.linspace(0, 10, 500)  # degrees
    layerW = Material('W', kind='thin mirror', rho=19.3, t=2.5e-6)
    for_one_material(layerW,
                     os.path.join(dataDir, "W25A_10kev_s.mlayer.gz"),
                     os.path.join(dataDir, "W25A_10kev_p.mlayer.gz"), 1e4,
                     u'slab, t = 25 Å, @ 10 keV')


def compare_absorption_coeff():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(mat, ref1, title):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel(r'$\mu_0$ (cm$^{-1}$)')
        fig.suptitle(title, fontsize=16)
        x, mu0 = np.loadtxt(ref1, unpack=True)
        p1, = ax.loglog(x, mu0, '-k', lw=2, label='XCrossSec')
        calcmu0 = mat.get_absorption_coefficient(E)
        p3, = ax.loglog(E, calcmu0, '-r', label='xrt')
        ax.legend(loc=1)
        ax.set_xlim(E[0], E[-1])
        fname = title
        fig.savefig(fname + '.png')

    dataDir = os.path.join('data', 'XOP-Reflectivities')
    E = np.logspace(1, 4.+math.log10(3.), 500)
    mat = Material('Be', rho=1.848)
    for_one_material(mat, os.path.join(dataDir, "Be_absCoeff.xcrosssec.gz"),
                     u'Absorption in Be')


def compare_transmittivity():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(mat, thickness, ref1, title, sname):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel('transmittivity')
        fig.suptitle(title, fontsize=16)
        x, tr = np.loadtxt(ref1, unpack=True)
        p1, = ax.semilogx(x, tr, '-k', lw=2, label='XPower/XOP')
        calcmu0 = mat.get_absorption_coefficient(E)
        transm = np.exp(-calcmu0 * thickness)
        p3, = ax.semilogx(E, transm, '-r', label='xrt')
        ax.legend(loc=2)
        ax.set_xlim(E[0], E[-1])
        fname = 'Transm' + sname
        fig.savefig(fname + '.png')

    dataDir = os.path.join('data', 'XOP-Reflectivities')
    E = np.logspace(2.+math.log10(3.), 4.+math.log10(3.), 500)
    matDiamond = Material('C', rho=3.52)
    for_one_material(matDiamond, 60*1e-4,
                     os.path.join(dataDir, "Diamond60mum.xpower.gz"),
                     r'Transmittivity of 60-$\mu$m-thick diamond', 'Diamond')


def run_tests():
    """The body of the module test suit. Uncomment the tests you want. Various
    material properties are compared with those calculated by XCrystal/XOP
    (also used by shadow for modeling crystal optics), XInpro/XOP and others.

    .. rubric:: Reflectivity of Bragg crystals

    All the curves are basically equal. The small amplitude differences are due
    to slight differences in Debye-Waller factor and/or tabulated values of the
    atomic scattering factors. The phase difference between s- and p-polarized
    rays (calculated by xrt, cyan line, right Y axis) is not calculated by the
    XOP programs and therefore is given without comparison.

    +-------+--------------------+------------------+-------------------+
    |       |      α = -5°       |    symmetric     |       α = 5°      |
    +=======+====================+==================+===================+
    | thick | |bSi111_thick_-5|  | |bSi111_thick_0| | |bSi111_thick_5|  |
    |       | |bSi333_thick_-5|  | |bSi333_thick_0| | |bSi333_thick_5|  |
    +-------+--------------------+------------------+-------------------+
    | 100 µm|   |bSi111_100_-5|  |  |bSi111_100_0|  |  |bSi111_100_5|   |
    |       |   |bSi333_100_-5|  |  |bSi333_100_0|  |  |bSi333_100_5|   |
    +-------+--------------------+------------------+-------------------+
    | 7 µm  |   |bSi111_007_-5|  |  |bSi111_007_0|  |  |bSi111_007_5|   |
    |       |   |bSi333_007_-5|  |  |bSi333_007_0|  |  |bSi333_007_5|   |
    +-------+--------------------+------------------+-------------------+

    .. |bSi111_thick_-5| image:: _images/bSi111_thick_-5.*
       :scale: 35 %
    .. |bSi111_thick_0| image:: _images/bSi111_thick_0.*
       :scale: 35 %
    .. |bSi111_thick_5| image:: _images/bSi111_thick_5.*
       :scale: 35 %
    .. |bSi111_100_-5| image:: _images/bSi111_100mum_-5.*
       :scale: 35 %
    .. |bSi111_100_0| image:: _images/bSi111_100mum_0.*
       :scale: 35 %
    .. |bSi111_100_5| image:: _images/bSi111_100mum_5.*
       :scale: 35 %
    .. |bSi111_007_-5| image:: _images/bSi111_007mum_-5.*
       :scale: 35 %
    .. |bSi111_007_0| image:: _images/bSi111_007mum_0.*
       :scale: 35 %
    .. |bSi111_007_5| image:: _images/bSi111_007mum_5.*
       :scale: 35 %

    .. |bSi333_thick_-5| image:: _images/bSi333_thick_-5.*
       :scale: 35 %
    .. |bSi333_thick_0| image:: _images/bSi333_thick_0.*
       :scale: 35 %
    .. |bSi333_thick_5| image:: _images/bSi333_thick_5.*
       :scale: 35 %
    .. |bSi333_100_-5| image:: _images/bSi333_100mum_-5.*
       :scale: 35 %
    .. |bSi333_100_0| image:: _images/bSi333_100mum_0.*
       :scale: 35 %
    .. |bSi333_100_5| image:: _images/bSi333_100mum_5.*
       :scale: 35 %
    .. |bSi333_007_-5| image:: _images/bSi333_007mum_-5.*
       :scale: 35 %
    .. |bSi333_007_0| image:: _images/bSi333_007mum_0.*
       :scale: 35 %
    .. |bSi333_007_5| image:: _images/bSi333_007mum_5.*
       :scale: 35 %

    .. rubric:: Reflectivity of Laue crystals

    All the curves are basically equal. The small amplitude differences are due
    to slight differences in Debye-Waller factor and/or tabulated values of the
    atomic scattering factors. The phase difference between s- and p-polarized
    rays (calculated by xrt, cyan line, right Y axis) is not calculated by the
    XOP programs and therefore is given without comparison.

    +-------+--------------------+------------------+-------------------+
    |       |      α = -5°       |    symmetric     |       α = 5°      |
    +=======+====================+==================+===================+
    | 100 µm|   |lSi111_100_-5|  |  |lSi111_100_0|  |  |lSi111_100_5|   |
    |       |   |lSi333_100_-5|  |  |lSi333_100_0|  |  |lSi333_100_5|   |
    +-------+--------------------+------------------+-------------------+
    | 7 µm  |   |lSi111_007_-5|  |  |lSi111_007_0|  |  |lSi111_007_5|   |
    |       |   |lSi333_007_-5|  |  |lSi333_007_0|  |  |lSi333_007_5|   |
    +-------+--------------------+------------------+-------------------+

    .. |lSi111_100_-5| image:: _images/lSi111_100mum_-5.*
       :scale: 35 %
    .. |lSi111_100_0| image:: _images/lSi111_100mum_0.*
       :scale: 35 %
    .. |lSi111_100_5| image:: _images/lSi111_100mum_5.*
       :scale: 35 %
    .. |lSi111_007_-5| image:: _images/lSi111_007mum_-5.*
       :scale: 35 %
    .. |lSi111_007_0| image:: _images/lSi111_007mum_0.*
       :scale: 35 %
    .. |lSi111_007_5| image:: _images/lSi111_007mum_5.*
       :scale: 35 %

    .. |lSi333_100_-5| image:: _images/lSi333_100mum_-5.*
       :scale: 35 %
    .. |lSi333_100_0| image:: _images/lSi333_100mum_0.*
       :scale: 35 %
    .. |lSi333_100_5| image:: _images/lSi333_100mum_5.*
       :scale: 35 %
    .. |lSi333_007_-5| image:: _images/lSi333_007mum_-5.*
       :scale: 35 %
    .. |lSi333_007_0| image:: _images/lSi333_007mum_0.*
       :scale: 35 %
    .. |lSi333_007_5| image:: _images/lSi333_007mum_5.*
       :scale: 35 %

    .. rubric:: Transmittivity of Bragg crystals

    The curves are basically equal only for the symmetric case. Both
    XCrystal/XOP and XInpro/XOP are wrong for asymmetric crystals, when they
    give too low or too high (>1) transmittivity.

    +-------+--------------------+-------------------+--------------------+
    |       |      α = -5°       |     symmetric     |        α = 5°      |
    +=======+====================+===================+====================+
    | 100 µm|  |btSi111_100_-5|  |  |btSi111_100_0|  |  |btSi111_100_5|   |
    |       |  |btSi333_100_-5|  |  |btSi333_100_0|  |  |btSi333_100_5|   |
    +-------+--------------------+-------------------+--------------------+
    | 7 µm  |  |btSi111_007_-5|  |  |btSi111_007_0|  |  |btSi111_007_5|   |
    |       |  |btSi333_007_-5|  |  |btSi333_007_0|  |  |btSi333_007_5|   |
    +-------+--------------------+-------------------+--------------------+

    .. |btSi111_100_-5| image:: _images/btSi111_100mum_-5.*
       :scale: 35 %
    .. |btSi111_100_0| image:: _images/btSi111_100mum_0.*
       :scale: 35 %
    .. |btSi111_100_5| image:: _images/btSi111_100mum_5.*
       :scale: 35 %
    .. |btSi111_007_-5| image:: _images/btSi111_007mum_-5.*
       :scale: 35 %
    .. |btSi111_007_0| image:: _images/btSi111_007mum_0.*
       :scale: 35 %
    .. |btSi111_007_5| image:: _images/btSi111_007mum_5.*
       :scale: 35 %

    .. |btSi333_100_-5| image:: _images/btSi333_100mum_-5.*
       :scale: 35 %
    .. |btSi333_100_0| image:: _images/btSi333_100mum_0.*
       :scale: 35 %
    .. |btSi333_100_5| image:: _images/btSi333_100mum_5.*
       :scale: 35 %
    .. |btSi333_007_-5| image:: _images/btSi333_007mum_-5.*
       :scale: 35 %
    .. |btSi333_007_0| image:: _images/btSi333_007mum_0.*
       :scale: 35 %
    .. |btSi333_007_5| image:: _images/btSi333_007mum_5.*
       :scale: 35 %

    .. rubric:: Transmittivity of Laue crystals

    The curves are basically equal only for the symmetric case and only with
    XInpro/XOP results. XInpro/XOP is wrong for asymmetric crystals, when it
    gives too low or too high (>1) transmittivity. As seen, XCrystal/XOP is
    essentially different and wrong with Laue transmittivity.

    +-------+--------------------+-------------------+--------------------+
    |       |      α = -5°       |    symmetric      |        α = 5°      |
    +=======+====================+===================+====================+
    | 100 µm|  |ltSi111_100_-5|  |  |ltSi111_100_0|  |  |ltSi111_100_5|   |
    |       |  |ltSi333_100_-5|  |  |ltSi333_100_0|  |  |ltSi333_100_5|   |
    +-------+--------------------+-------------------+--------------------+
    | 7 µm  |  |ltSi111_007_-5|  |  |ltSi111_007_0|  |  |ltSi111_007_5|   |
    |       |  |ltSi333_007_-5|  |  |ltSi333_007_0|  |  |ltSi333_007_5|   |
    +-------+--------------------+-------------------+--------------------+

    .. |ltSi111_100_-5| image:: _images/ltSi111_100mum_-5.*
       :scale: 35 %
    .. |ltSi111_100_0| image:: _images/ltSi111_100mum_0.*
       :scale: 35 %
    .. |ltSi111_100_5| image:: _images/ltSi111_100mum_5.*
       :scale: 35 %
    .. |ltSi111_007_-5| image:: _images/ltSi111_007mum_-5.*
       :scale: 35 %
    .. |ltSi111_007_0| image:: _images/ltSi111_007mum_0.*
       :scale: 35 %
    .. |ltSi111_007_5| image:: _images/ltSi111_007mum_5.*
       :scale: 35 %

    .. |ltSi333_100_-5| image:: _images/ltSi333_100mum_-5.*
       :scale: 35 %
    .. |ltSi333_100_0| image:: _images/ltSi333_100mum_0.*
       :scale: 35 %
    .. |ltSi333_100_5| image:: _images/ltSi333_100mum_5.*
       :scale: 35 %
    .. |ltSi333_007_-5| image:: _images/ltSi333_007mum_-5.*
       :scale: 35 %
    .. |ltSi333_007_0| image:: _images/ltSi333_007mum_0.*
       :scale: 35 %
    .. |ltSi333_007_5| image:: _images/ltSi333_007mum_5.*
       :scale: 35 %

    .. rubric:: Mirror reflectivity

    The curves are basically equal. The small amplitude differences are due
    to slight differences in tabulated values of the atomic scattering factors.
    The phase difference between s- and p-polarized rays (calculated by xrt,
    cyan line, right Y axis) is not calculated by the XOP programs and
    therefore is given without comparison.

    .. image:: _images/MirrorReflSi@0.5deg.*
       :scale: 35 %
    .. image:: _images/MirrorReflSiO2@0.5deg.*
       :scale: 35 %
    .. image:: _images/MirrorReflRh@2mrad.*
       :scale: 35 %
    .. image:: _images/MirrorReflPt@4mrad.*
       :scale: 35 %

    .. rubric:: Slab reflectivity

    The curves are basically equal. The small amplitude differences are due
    to slight differences in tabulated values of the atomic scattering factors.
    The phase difference between s- and p-polarized rays (calculated by xrt,
    cyan line, right Y axis) is not calculated by the XOP programs and
    therefore is given without comparison.

    .. image:: _images/SlabReflW.*
       :scale: 35 %

    .. rubric:: Transmittivity of materials

    The curves are basically equal. The small amplitude differences are due
    to slight differences in tabulated values of the atomic scattering factors.

    .. image:: _images/TransmDiamond.*
       :scale: 35 %

    .. rubric:: Absorption of materials

    The curves are basically equal. The small amplitude differences are due
    to slight differences in tabulated values of the atomic scattering factors.

    .. image:: _images/AbsorptionBe.*
       :scale: 35 %
"""
#Compare the calculated rocking curves of Si crystals with those calculated by
#XCrystal and XInpro (parts of XOP):
#    compare_rocking_curves('111')
#    compare_rocking_curves('333')
#    compare_rocking_curves('111', t=0.007)#t is thickness in mm
#    compare_rocking_curves('333', t=0.007)
#    compare_rocking_curves('111', t=0.100)
#    compare_rocking_curves('333', t=0.100)
#    compare_rocking_curves('111', t=0.007, geom='Bragg transmitted')
#    compare_rocking_curves('333', t=0.007, geom='Bragg transmitted')
#    compare_rocking_curves('111', t=0.100, geom='Bragg transmitted')
#    compare_rocking_curves('333', t=0.100, geom='Bragg transmitted')
#    compare_rocking_curves('111', t=0.007, geom='Laue reflected')
#    compare_rocking_curves('333', t=0.007, geom='Laue reflected')
#    compare_rocking_curves('111', t=0.100, geom='Laue reflected')
#    compare_rocking_curves('333', t=0.100, geom='Laue reflected')
#    compare_rocking_curves('111', t=0.007, geom='Laue transmitted')
#    compare_rocking_curves('333', t=0.007, geom='Laue transmitted')
#    compare_rocking_curves('111', t=0.100, geom='Laue transmitted')
#    compare_rocking_curves('333', t=0.100, geom='Laue transmitted')

#check that Bragg transmitted and Laue transmitted give the same results if the
#beam path is equal:
#    beamPath = 0.1#mm
#    compare_Bragg_Laue('111', beamPath=beamPath)
#    compare_Bragg_Laue('333', beamPath=beamPath)

#Compare the calculated reflectivities of Si, Pt, SiO_2 with those by Xf1f2
#(part of XOP):
    compare_reflectivity()

#Compare the calculated reflectivities of W slab with those by Mlayer
#(part of XOP):
#    compare_reflectivity_slab()

#Compare the calculated absorption coefficient with that by XCrossSec
#(part of XOP):
#    compare_absorption_coeff()

#Compare the calculated transmittivity with that by XPower
#(part of XOP):
#    compare_transmittivity()

#Play with Si crystal:
#    crystalSi = CrystalSi(hkl=(1,1,1), tK=100.)
#    print 2 * crystalSi.get_a()/math.sqrt(3.)#2dSi111
#    print 'Si111 d-spacing = {0:.6f}'.format(crystalSi.d)
#    print crystalSi.get_Bragg_offset(8600, 8979)
#
#    crystalDiamond = CrystalDiamond((1,1,1), 2.0592872, elements='C')
#    E = 9000.
#    print u'Darwin width at E={0:.0f} eV is {1:.5f} µrad for s-polarization'.\
#      format(E, crystalDiamond.get_Darwin_width(E) * 1e6)
#    print u'Darwin width at E={0:.0f} eV is {1:.5f} µrad for p-polarization'.\
#      format(E, crystalDiamond.get_Darwin_width(E, polarization='p') * 1e6)

    plt.show()
    print "finished"


if __name__ == '__main__':
    run_tests()
