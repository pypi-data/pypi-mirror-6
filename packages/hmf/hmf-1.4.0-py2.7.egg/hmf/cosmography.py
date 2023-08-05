'''
Created on Jan 21, 2013

@author: Steven
'''
import numpy as np
import scipy.integrate as intg
import cosmolopy.distance as cdist

def d_plus(z, **cosmo):
    """
    Finds the factor D+(a), from Lukic et. al. 2007, eq. 8.
    
    Uses romberg integration with a suitable step-size. 
    
    Input: z: redshift.
    
    Output: dplus: the factor.
    """
    a_upper = 1.0 / (1.0 + z)
    lna = np.linspace(np.log(1e-8), np.log(a_upper), 1000)
    z_vec = 1.0 / np.exp(lna) - 1.0

    integrand = 1.0 / (np.exp(lna) * cdist.e_z(z_vec, **cosmo)) ** 3

    integral = intg.simps(np.exp(lna) * integrand, dx=lna[1] - lna[0])
    dplus = 5.0 * cosmo["omega_M_0"] * cdist.e_z(z, **cosmo) * integral / 2.0

    return dplus

def growth_factor(z, **cosmo):
    """
    Finds the factor d(a) = D+(a)/D+(a=1), from Lukic et. al. 2007, eq. 8.
    
    Input: z: redshift.
    
    Output: growth: the growth factor.
    """

    growth = d_plus(z, **cosmo) / d_plus(0.0, **cosmo)

    return growth
