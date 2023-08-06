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
import pandas as pd

def distribution(resultat, var, x = np.NaN, t = np.NaN):
    """
    Distribution d'une variable sur la largeur de la paroi au temps t
    
    resultat : dictionnaire des resultats du calcul
    
    var : variable a tracer (type str)
    
    x : points de la distribution (par defaut les noeuds du maillage)
    
    t : temps (type float, par defaut le temps de fin de simul)
    
    Le resultat est un vecteur de meme format que x
    """
    
    """
    if np.isnan(x):
        x = resultat['x']
    
    if np.isnan(t):
        t = resultat['t'][-1]
    """
    
    try:
        f_t = interp1d(resultat['t'], resultat[var], axis=0)
        
    except KeyError:
        
        print "La cle %s n'est pas dans le dictionnaire resultat" % var
        return np.array([])
    
    # Distribution de 'var' au temps t sur tous les noeuds du maillage
    distr_nodes = f_t(t)
    
    # Fonction d'interpolation depuis les noeuds du maillage vers x
    f_x = interp1d(resultat['x'], distr_nodes, 'cubic', bounds_error=False)
    
    return f_x(x)


def evolution(resultat, var, x, t = np.NaN):
    """
    Evolution d'une variable au cours du temps sur un point de coordonnee x
    
    resultat : dictionnaire des resultats du calcul
    
    var : variable a tracer (type str)
    
    x : position (type float)
    """

    if np.any( np.isnan(t) ):
        t = resultat['t']
    
    try:
        f_x = interp1d(resultat['x'], resultat[var], 'cubic', axis=1)
        
    except KeyError:
        
        print "La cle %s n'est pas dans le dictionnaire resultat" % var
        return np.array([])
    
    # Evolution de 'var' au point x et aux temps du calcul
    evol_temps_simul = f_x(x)
    
    # Fonction d'interpolation depuis les temps de simul vers le temps voulu
    f_t = interp1d(resultat['t'], evol_temps_simul, bounds_error=False)
    
    return f_t(t)
    
def fitness(resultat):
    
    pass

if __name__ == "__main__":

    """ Exemples d'utilisation """    
    
    # Import des resultats des mesures
    mesures   = pd.read_csv('D:\MCF\Simulation\HAMpy\climats\PASSYS_01.txt', delimiter='\t')
    t_mesure  = np.array( mesures['temps (s)'] )
    T_mesure  = np.array( mesures['T_12']      )
    HR_mesure = np.array( mesures['HR_12']     )
    
    # Import des resultats du calcul
    calcul    = np.load('output_passys.npz')
    T_calcul  = evolution(calcul, 'T',  x = 0.12, t = t_mesure)
    HR_calcul = evolution(calcul, 'HR', x = 0.12, t = t_mesure)
    
    # Residus
    R_T  = np.sum( (T_mesure -  T_calcul) **2 ) / (max(T_mesure) - min(T_mesure))
    R_HR = np.sum( (HR_mesure - HR_calcul)**2 ) / (max(HR_mesure)- min(HR_mesure))

    """
    T_04 = evolution(resultat, 'T', 0.04, t_plot)
    T_08 = evolution(resultat, 'T', 0.08, t_plot)
    T_12 = evolution(resultat, 'T', 0.12, t_plot)
    a = np.array([T_04, T_08, T_12]).T
    
    HR_04 = evolution(resultat, 'HR', 0.04, t_plot)
    HR_08 = evolution(resultat, 'HR', 0.08, t_plot)
    HR_12 = evolution(resultat, 'HR', 0.12, t_plot)
    b = np.array([HR_04, HR_08, HR_12]).T
    
    np.savetxt('resultat_passys.txt', b, fmt='%.8e')
    """
    