# -*- coding: utf-8 -*-
"""
Created on Wed Nov 06 09:18:55 2013

@author: Rouchier
"""

from hamopy.classes import Material

# Load material of benchmark #4

BM4_load = Material('BM4_load', rho = 2005., cp = 840.)

BM4_load.set_conduc(lambda_0 = 0.5,
                    lambda_m = 0.45)
                    
BM4_load.set_isotherm('vangenuchten',**{"w_sat" : 157.,
                                        "l"     : [0.3, 0.7],
                                        "alpha" : [1.25e-5, 1.8e-5],
                                        "m"     : [0.394, 0.833] })
                                         
BM4_load.set_perm_vapor('schirmer',**{"mu" : 30.,
                                      "p"  : 0.497 } )
                                       
# Lightweight material of benchmark #3

BM3 = Material('BM3', rho = 212, cp = 1000)

BM3.set_conduc(lambda_0 = 0.06,
               lambda_m = 0.56)

BM3.set_isotherm('vangenuchten', **{"w_sat"    : 871,
                                    "l"        : [0.41, 0.59],
                                    "alpha"    : [6.12e-7, 1.22e-6],
                                    "m"        : [0.5981, 0.5816]  })

BM3.set_perm_vapor('schirmer', **{"mu" : 5.6,
                                  "p"  : 0.2 })

BM3.set_perm_liquid('exp', **{"a" : [-46.245, 294.506, -1439, 3249, -3370, 1305] } )

BM3.set_perm_air(3e-5*1.8e-5*0.2)