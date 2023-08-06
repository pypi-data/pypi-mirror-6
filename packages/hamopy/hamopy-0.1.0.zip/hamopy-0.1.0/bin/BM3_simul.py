# -*- coding: utf-8 -*-
"""
Created on Wed Mar 05 11:44:45 2014

@author: Rouchier
"""

import numpy  as np
import pandas as pd

from hamopy.classes import Mesh, Boundary, Time

# Choix des matériaux et de la géométrie
from hamopy.materials.hamstad import BM3

mesh = Mesh(**{"materials"    : [BM3],
               "sizes"        : [0.2],
               "nbr_elements" : [40] })

# Conditions aux limites
fichier_climat = 'D:\MCF\Simulation\Python\Hamstad/BM3 climat.txt'
data0 = pd.read_csv(fichier_climat, delimiter='\t')

clim1 = Boundary('Neumann',**{"file"      : fichier_climat,
                              "delimiter" : "\t",
                              "time"      : "Temps (s)",
                              "T"         : 293.15,
                              "HR"        : 0.7,
                              "h_t"       : 10,
                              "h_m"       : 2e-7,
                              "P_air"     : "DeltaP"})

clim2 = Boundary('Neumann',**{"file"      : fichier_climat,
                              "delimiter" : "\t",
                              "time"      : "Temps (s)",
                              "T"         : 275.15,
                              "HR"        : 0.8,
                              "h_t"       : 10,
                              "h_m"       : 7.38e-12 })
clim = [clim1, clim2]

# Conditions initiales
init = {'T'  : 293.15,
        'HR' : 0.95}

# Discrétisation temporelle
temps = Time(method = 'variable',**{"delta_t"  : 900,
                                    "t_max"    : max(data0['Temps (s)']),
                                    "iter_max" : 12,
                                    "delta_min": 1e-3,
                                    "delta_max": 900 } )

if __name__ == "__main__":
    
    # Calcul
    from hamopy.algorithm import calcul
    resultat = calcul(mesh, clim, init, temps)
    
    # Post process
    from hamopy.postpro import evolution
    
    t_plot = np.array( data0['Temps (s)'] )
    x_plot = [0.05, 0.1, 0.15, 0.17, 0.19]
    
    from hamopy import ham_library as ham
    
    Temperature = np.column_stack([evolution(resultat, 'T', _, t_plot) for _ in x_plot]) - 273.15
    Humidite    = np.column_stack([evolution(resultat, 'HR', _, t_plot) for _ in x_plot])
    Eau = BM3.w(ham.p_c(Humidite, Temperature+273.15), Temperature+273.15)
