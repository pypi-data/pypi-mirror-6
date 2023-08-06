# Copyright (C) 2014  Simon Rouchier
# 
# This file is part of Hamopy.
#
# Hamopy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hamopy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hamopy.  If not, see <http://www.gnu.org/licenses/>.
# 
# To contact the author : s.rouchier@gmail.com

from pylab import exp, log

# Proprietes relatives a la temperature
R       = 8.314     # constante des gaz parfaits
T_0     = 273.15    # zero Celsius
T_ref   = 293.15    # temperature de reference [K]

# Proprietes de l'air
p_atm       = 101325.       # pression atmospherique [Pa]
lambda_air  = 0.0262        # conductivite thermique de l'air [W.m-1.K-1]
alpha_air   = 2.216e-5      # diffusivite thermique de l'air [m2.s-1]
rho_air     = 1.2           # masse volumique de l'air [kg.m-3]
mu_air      = 1.8e-5        # viscosite denamique de l'air [Pa.s]
cp_air      = 1004.         # chaleur specifique de l'air [J.kg-1.K-1]

# Proprietes de l'eau
rho_liq     = 998.          # masse volumique de l'eau [kg.m-3]
eta_liq     = 1e-3          # viscosite dynamique de l'eau [Pa.s]
cp_liq      = 4180.         # chaleur specifique eau liquide [J.kg-1.K-1]
lambda_liq  = 0.6           # conductivite thermique de l'eau [W.m-1.K-1]
Rv          = R/18 * 1e3    # constante specifique de l'eau [J.kg-1.K-1]
tension     = 72.7e-3       # tension de surface eau/air [N.m-1]

# Proprietes de la vapeur
cp_vap = 1850.      # chaleur specifique vapeur [J.kg-1]
l_lv = 2.454e6      # chaleur latente de vaporisation de l'eau a 20 C [J.kg-1]

# FONCTIONS

def p_sat(T):
    """
    Pression de saturation de la vapeur d'eau dans l'air [Pa]
    
    input : temperature T [K]
    """
    
    return p_atm * exp( l_lv / Rv * (1/373.15 - 1./T) )
    
    
def D_va(T):
    """
    Diffusivite de l'eau dans l'air [m2/s]
    
    input : temperature T [K]
    """
    return 2.306e-5 * (T/273.15)**1.81;

def p_v(p_c, T):
    """
    Expression de la pression de vapeur p_v en fonction de la pression
    capillaire p_c et de la temperature T, avec la loi de Clausius-Clapeyron
    
    input : pression capillaire p_c [Pa], temperature T [K]
    """
    return p_sat(T) * exp( p_c / (rho_liq*Rv*T) )
    
def HR(p_c, T):
    """
    Expression de l'humidite relative HR en fonction de la pression
    capillaire p_c et de la temperature T, avec la loi de Clausius-Clapeyron
    
    input : pression capillaire p_c [Pa], temperature T [K]
    """
    return exp( p_c / (rho_liq*Rv*T) )

def p_c(HR, T):
    """
    Formule de Clausius-Clapeyron pour calculer la pression capillaire en
    fonction de l'humidite relative et de la temperature
    
    input : humidite relative HR [-], temperature T [K]
    """
    return rho_liq * Rv * T * log(HR)
