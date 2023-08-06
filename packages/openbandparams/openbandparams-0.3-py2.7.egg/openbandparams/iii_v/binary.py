#
#   Copyright (c) 2013-2014, Scott J Maddox
#
#   This file is part of openbandparams.
#
#   openbandparams is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   openbandparams is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with openbandparams.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

# std lib imports
import logging; log = logging.getLogger(__name__)

# third party imports

# local imports
from openbandparams.base_material import Base
from openbandparams.equations import varshni

class Binary(Base):
    name = None
    
    # All methods should be class methods so that they can reference parameters
    # defined by the inheriting class.
    @classmethod
    def a_300K(cls, **kwargs):
        '''
        Returns the lattice parameter, a, in Angstroms at 300 K.
        '''
        return cls._a_300K
    
    @classmethod
    def da_dT(cls, **kwargs):
        '''
        Returns the thermal expansion coefficient, da_dT, of the lattice
        parameter, a, in Angstroms per Kelvin.
        '''
        return cls._da_dT
    
    @classmethod
    def a(cls, **kwargs):
        '''
        Returns the lattice parameter, a, in Angstroms at a given
        temperature, T, in Kelvin (default: 300 K).
        '''
        T = cls._get_T(kwargs)
        return cls.a_300K() + cls.da_dT() * (T - 300)
    
    @classmethod
    def Eg_Gamma_0(cls, **kwargs):
        '''
        Returns the Gamma-valley bandgap, Eg_Gamma, in electron Volts
        at 0 K.
        '''
        return cls._Eg_Gamma_0
    
    @classmethod
    def alpha_Gamma(cls, **kwargs):
        '''
        Returns the Gamma-valley alpha Varshni parameter, alpha_Gamma, in
        electron Volts per Kelvin.
        '''
        return cls._alpha_Gamma
    
    @classmethod
    def beta_Gamma(cls, **kwargs):
        '''
        Returns the Gamma-valley beta Varshni parameter, beta_Gamma, in
        Kelvin.
        '''
        return cls._beta_Gamma
    
    @classmethod
    def Eg_Gamma(cls, **kwargs):
        '''
        Returns the Gamma-valley bandgap, Eg_Gamma, in electron Volts at a
        given temperature, T, in Kelvin (default: 300 K).
        '''
        T = cls._get_T(kwargs)
        return varshni(cls.Eg_Gamma_0(), cls.alpha_Gamma(),
                       cls.beta_Gamma(), T)
    
    @classmethod
    def Eg_X_0(cls, **kwargs):
        '''
        Returns the X-valley bandgap, Eg_X, in electron Volts
        at 0 K.
        '''
        return cls._Eg_X_0
    
    @classmethod
    def alpha_X(cls, **kwargs):
        '''
        Returns the X-valley alpha Varshni parameter, alpha_X, in
        electron Volts per Kelvin.
        '''
        return cls._alpha_X
    
    @classmethod
    def beta_X(cls, **kwargs):
        '''
        Returns the X-valley beta Varshni parameter, beta_X, in
        Kelvin.
        '''
        return cls._beta_X
    
    @classmethod
    def Eg_X(cls, **kwargs):
        '''
        Returns the X-valley bandgap, Eg_X, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K).
        '''
        T = cls._get_T(kwargs)
        return varshni(cls.Eg_X_0(), cls.alpha_X(), cls.beta_X(), T)
    
    @classmethod
    def Eg_L_0(cls, **kwargs):
        '''
        Returns the L-valley bandgap, Eg_L, in electron Volts
        at 0 K.
        '''
        return cls._Eg_L_0
    
    @classmethod
    def alpha_L(cls, **kwargs):
        '''
        Returns the L-valley alpha Varshni parameter, alpha_L, in
        electron Volts per Kelvin.
        '''
        return cls._alpha_L
    
    @classmethod
    def beta_L(cls, **kwargs):
        '''
        Returns the L-valley beta Varshni parameter, beta_L, in
        Kelvin.
        '''
        return cls._beta_L
    
    @classmethod
    def Eg_L(cls, **kwargs):
        '''
        Returns the L-valley bandgap, Eg_L, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K).
        '''
        T = cls._get_T(kwargs)
        return varshni(cls.Eg_L_0(), cls.alpha_L(), cls.beta_L(), T)
    
    @classmethod
    def Eg(cls, **kwargs):
        '''
        Returns the bandgap, Eg, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K).
        '''
        T = cls._get_T(kwargs)
        return min(cls.Eg_Gamma(T=T), cls.Eg_X(T=T), cls.Eg_L(T=T))
    
    @classmethod
    def Delta_SO(cls, **kwargs):
        '''
        Returns the split-off energy, Delta_SO, in electron Volts.
        '''
        return cls._Delta_SO
    
    @classmethod
    def meff_e_Gamma(cls, **kwargs):
        '''
        Returns the Gamma-valley electron effective mass, meff_e_Gamma,
        in units of electron mass.
        '''
        return cls._meff_e_Gamma
    
    @classmethod
    def meff_e_L_long(cls, **kwargs):
        '''
        Returns the L-valley electron effective mass in the longitudinal
        direction, meff_e_L_long, in units of electron mass.
        '''
        return cls._meff_e_L_long
    
    @classmethod
    def meff_e_L_trans(cls, **kwargs):
        '''
        Returns the L-valley electron effective mass in the transverse
        direction, meff_e_L_trans, in units of electron mass.
        '''
        return cls._meff_e_L_trans
    
    @classmethod
    def meff_e_L_DOS(cls, **kwargs):
        '''
        Returns the L-valley electron density of states effective mass,
        meff_e_L_DOS, in units of electron mass.
        '''
        return cls._meff_e_L_DOS
    
    @classmethod
    def meff_e_X_long(cls, **kwargs):
        '''
        Returns the X-valley electron effective mass in the longitudinal
        direction, meff_e_X_long, in units of electron mass.
        '''
        return cls._meff_e_X_long
    
    @classmethod
    def meff_e_X_trans(cls, **kwargs):
        '''
        Returns the X-valley electron effective mass in the transverse
        direction, meff_e_X_trans, in units of electron mass.
        '''
        return cls._meff_e_X_trans
    
    @classmethod
    def meff_e_X_DOS(cls, **kwargs):
        '''
        Returns the X-valley electron density of states effective mass,
        meff_e_X_DOS, in units of electron mass.
        '''
        return cls._meff_e_X_DOS
    
    @classmethod
    def Luttinger1(cls, **kwargs):
        '''
        Returns the first Luttinger parameter (unitless).
        '''
        return cls._Luttinger1
    
    @classmethod
    def Luttinger2(cls, **kwargs):
        '''
        Returns the second Luttinger parameter (unitless).
        '''
        return cls._Luttinger2
    
    @classmethod
    def Luttinger3(cls, **kwargs):
        '''
        Returns the second Luttinger parameter (unitless).
        '''
        return cls._Luttinger3
    
    @classmethod
    def meff_SO(cls, **kwargs):
        '''
        Returns the split-off band hole effective mass, meff_SO, in units
        of electron mass.
        '''
        return cls._meff_SO
    
    @classmethod
    def Ep(cls, **kwargs):
        '''
        Returns the Ep matrix element, in electron Volts.
        '''
        return cls._Ep
    
    @classmethod
    def F(cls, **kwargs):
        '''
        Returns the F Kane parameter (unitless).
        '''
        return cls._F
    
    @classmethod
    def VBO(cls, **kwargs):
        '''
        Returns the valance band offset energy, VBO, in electron Volts
        relative to the InSb valance band maximum.
        '''
        return cls._VBO
    
    @classmethod
    def a_c(cls, **kwargs):
        '''
        Returns the conduction band deformation potential, a_c, in
        electron Volts.
        '''
        return cls._a_c
    
    @classmethod
    def a_v(cls, **kwargs):
        '''
        Returns the valance band deformation potential, a_v, in
        electron Volts.
        '''
        return cls._a_v
    
    @classmethod
    def b(cls, **kwargs):
        '''
        Returns the b shear deformation potential, in electron Volts.
        '''
        return cls._b
    
    @classmethod
    def d(cls, **kwargs):
        '''
        Returns the d shear deformation potential, in electron Volts.
        '''
        return cls._d
    
    @classmethod
    def c_11(cls, **kwargs):
        '''
        Returns the c_11 elastic constant, in gigapascals.
        '''
        return cls._c_11
    
    @classmethod
    def c_12(cls, **kwargs):
        '''
        Returns the c_12 elastic constant, in gigapascals.
        '''
        return cls._c_12
    
    @classmethod
    def c_44(cls, **kwargs):
        '''
        Returns the c_44 elastic constant, in gigapascals.
        '''
        return cls._c_44