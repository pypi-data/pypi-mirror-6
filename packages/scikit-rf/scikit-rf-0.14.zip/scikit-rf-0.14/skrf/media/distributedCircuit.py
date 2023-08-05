

'''
.. module:: skrf.media.distributedCircuit
============================================================
distributedCircuit (:mod:`skrf.media.distributedCircuit`)
============================================================

A transmission line defined in terms of distributed circuit components
'''

from copy import deepcopy
from scipy.constants import  epsilon_0, mu_0, c,pi, mil
import numpy as npy
from numpy import sqrt, exp, array,tan,sin,cos,inf, log, real,imag,\
         interp, linspace, shape,zeros, reshape

from ..tlineFunctions import electrical_length
from .media import Media
# used as substitutes to handle mathematical singularities.
INF = 1e99
ONE = 1.0 + 1/1e14


class DistributedCircuit(Media):
    '''
    Generic, distributed circuit TEM transmission line

    A TEM transmission line, defined in terms of  distributed impedance
    and admittance values. A Distributed Circuit may be defined in terms
    of the following attributes,

    ================================  ================  ================
    Quantity                          Symbol            Property
    ================================  ================  ================
    Distributed Capacitance           :math:`C^{'}`     :attr:`C`
    Distributed Inductance            :math:`I^{'}`     :attr:`I`
    Distributed Resistance            :math:`R^{'}`     :attr:`R`
    Distributed Conductance           :math:`G^{'}`     :attr:`G`
    ================================  ================  ================


    From these, the following quantities may be calculated, which
    are functions of angular frequency (:math:`\omega`):
    
    ===================================  ==================================================  ==============================
    Quantity                             Symbol                                              Property
    ===================================  ==================================================  ==============================
    Distributed Impedance                :math:`Z^{'} = R^{'} + j \\omega I^{'}`              :attr:`Z`
    Distributed Admittance               :math:`Y^{'} = G^{'} + j \\omega C^{'}`              :attr:`Y`
    ===================================  ==================================================  ==============================


    From these we can calculate properties which define their wave
    behavior:

    ===================================  ============================================  ==============================
    Quantity                             Symbol                                        Method
    ===================================  ============================================  ==============================
    Characteristic Impedance             :math:`Z_0 = \\sqrt{ \\frac{Z^{'}}{Y^{'}}}`     :func:`Z0`
    Propagation Constant                 :math:`\\gamma = \\sqrt{ Z^{'}  Y^{'}}`         :func:`gamma`
    ===================================  ============================================  ==============================

    Given the following definitions, the components of propagation
    constant are interpreted as follows:

    .. math::
        +\\Re e\\{\\gamma\\} = \\text{attenuation}
    
        -\\Im m\\{\\gamma\\} = \\text{forward propagation}



    '''
    ## CONSTRUCTOR
    def __init__(self, frequency,  C, I, R, G,*args, **kwargs):
        '''
        Distributed Circuit constructor.

        Parameters
        ------------
        frequency : :class:`~skrf.frequency.Frequency` object
        C : number, or array-like
                distributed capacitance, in F/m
        I : number, or array-like
                distributed inductance, in  H/m
        R : number, or array-like
                distributed resistance, in Ohm/m
        G : number, or array-like
                distributed conductance, in S/m


        Notes
        ----------
        C,I,R,G can all be vectors as long as they are the same
        length

        This object can be constructed from a Media instance too, see
        the classmethod :func:`from_Media`
        '''

        self.frequency = frequency.copy()
        self.C, self.I, self.R, self.G = C,I,R,G

        # for unambiguousness
        self.distributed_resistance = self.R
        self.distributed_capacitance = self.C
        self.distributed_inductance = self.I
        self.distributed_conductance = self.G

        Media.__init__(self,\
                frequency = frequency,\
                propagation_constant = self.gamma, \
                characteristic_impedance = self.Z0,\
                *args, **kwargs)

    def __str__(self):
        f=self.frequency
        try:
            output =  \
                'Distributed Circuit Media.  %i-%i %s.  %i points'%\
                (f.f_scaled[0],f.f_scaled[-1],f.unit, f.npoints) + \
                '\nI\'= %.2f, C\'= %.2f,R\'= %.2f, G\'= %.2f, '% \
                (self.I, self.C,self.R, self.G)
        except(TypeError):
            output =  \
                'Distributed Circuit Media.  %i-%i %s.  %i points'%\
                (f.f_scaled[0],f.f_scaled[-1],f.unit, f.npoints) + \
                '\nI\'= %.2f.., C\'= %.2f..,R\'= %.2f.., G\'= %.2f.., '% \
                (self.I[0], self.C[0],self.R[0], self.G[0])
        return output

    def __repr__(self):
        return self.__str__()

    def __getstate__(self):
        '''
        method needed to allow for pickling
        '''
        d = self.__dict__.copy()
        del d['delay'] # cant pickle instance methods
        return(d)
            
    @classmethod
    def from_Media(cls, my_media, *args, **kwargs):
        '''
        Initializes a DistributedCircuit from an existing
        :class:'~skrf.media.media.Media' instance.

        Parameters
        ------------
        '''

        w  =  my_media.frequency.w
        gamma = my_media.propagation_constant
        Z0 = my_media.characteristic_impedance

        Y = gamma/Z0
        Z = gamma*Z0
        G,C = real(Y), imag(Y)/w
        R,I = real(Z), imag(Z)/w
        return cls(my_media.frequency, C=C, I=I, R=R, G=G, *args, **kwargs)


    @property
    def Z(self):
        '''
        Distributed Impedance, :math:`Z^{'}`

        Defined as

        .. math::
                Z^{'} = R^{'} + j \\omega I^{'}


        Returns
        --------
        Z : numpy.ndarray
                Distributed impedance in units of ohm/m
        '''
        w  = 2*npy.pi * self.frequency.f
        return self.R + 1j*w*self.I

    @property
    def Y(self):
        '''
        Distributed Admittance, :math:`Y^{'}`
        
        Defined as
        
        .. math::
                Y^{'} = G^{'} + j \\omega C^{'}

        Returns
        --------
        Y : numpy.ndarray
                Distributed Admittance in units of S/m
        '''

        w = 2*npy.pi*self.frequency.f
        return self.G + 1j*w*self.C


    def Z0(self):
        '''
        Characteristic Impedance, :math:`Z0`

        .. math::
                Z_0 = \\sqrt{ \\frac{Z^{'}}{Y^{'}}}

        Returns
        --------
        Z0 : numpy.ndarray
                Characteristic Impedance in units of ohms
        '''

        return sqrt(self.Z/self.Y)


    def gamma(self):
        '''
        Propagation Constant, :math:`\\gamma`

        Defined as,

        .. math::
                \\gamma =  \\sqrt{ Z^{'}  Y^{'}}

        Returns
        --------
        gamma : numpy.ndarray
                Propagation Constant,

        Notes
        ---------
        The components of propagation constant are interpreted as follows:

        positive real(gamma) = attenuation
        positive imag(gamma) = forward propagation
        '''
        return sqrt(self.Z*self.Y)
