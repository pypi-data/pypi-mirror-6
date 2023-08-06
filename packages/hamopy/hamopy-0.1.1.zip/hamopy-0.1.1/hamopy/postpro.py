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

from scipy.interpolate import interp1d
import numpy  as np

def distribution(result, var, x = None, t = None):
    """
    Distribution of a variable at a given time
    
    :result: dictionary of results provided by the simulation
    :var: string, which variable to extract from result
    :x: coordinates on which the distribution spans
    :t: float, time of the distribution
    """

    if x is None:
        x = result['x']
    
    if t is None:
        t = result['t'][-1]

    try:
        f_t = interp1d(result['t'], result[var], axis=0)
        
    except KeyError:
        
        print "The key %s is not in the dictionary of results" % var
        return np.array([])
    
    # Distribution of 'var' at the time 't' on all nodes of the mesh
    distr_nodes = f_t(t)
    
    # Interpolate from the node coordinates to the output discretisation
    f_x = interp1d(result['x'], distr_nodes, 'cubic', bounds_error=False)
    
    return f_x(x)


def evolution(result, var, x, t = None):
    """
    Temporal evolution of a variable at a specific location
    
    :result: dictionary of results provided by the simulation
    :var: string, which variable to extract from result
    :x: float, location of the point
    :t: time scale on which to extract the data (optional)
    """

    if t is None:
        t = result['t']
    
    try:
        f_x = interp1d(result['x'], result[var], 'cubic', axis=1)
        
    except KeyError:
        
        print "The key %s is not in the dictionary of results" % var
        return np.array([])
    
    # Evolution of 'var' at the location x at all time steps of the simulation
    evol_temps_simul = f_x(x)
    
    # Interpolate from the time of simulation to the output time
    f_t = interp1d(result['t'], evol_temps_simul, bounds_error=False)
    
    return f_t(t)

    