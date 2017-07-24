import logging
import numpy as np
from data_processor import get_smooth_data
from scipy.integrate import odeint

log = logging.getLogger(__name__)

def get_plasticity(par, N, model = "voce", spacing = "log"):
    """Usage: list par, int N, string method, string spacing

    Current models:

    2 param - a x E^b + Sy OR (Sy/(1-a)) x (1-a x exp(-b x E))

    4 param - Sp' = b x (1-exp(E/c))^d, a is initial yield stress

    2 param can be either "power" or "voce", and Sy may be included to make a 3 param model as c

    Spacing is either "log" or "lin"

    Returns: list stresses, list strains"""
    if spacing == "lin":
        strains = np.linspace(0, 1.5, N)

    elif spacing == "log":
        strains = np.geomspace(1, 2.5, N)-1

    if len(par) == 2 or len(par) == 3:
        if len(par) == 2:
            Sy = 255
        else:
            Sy = par[2]

        if model == "power":
            stresses = par[0]*(strains**par[1]) + Sy

        if model == "voce":
            stresses = (Sy/(1-par[0]))*(1-par[0]*np.exp(-par[1]*strains))

    if len(par) == 4:
        voce = lambda stress, strain: par[1]*(1-stress/par[2])**par[3]
        temp_stresses = odeint(voce, 0, strains)
        stresses = []
        for i in temp_stresses:
            stresses.append(i[0] + par[0])

    return list(stresses), list(strains)

def get_sum_squares(h, f, N, curve = "loading", scale = 1, limits = (0.05, 0.05, 0.05, 0.05) , weighting = 1, log_sum = False):
    """Usage: list h, list f, int N, float weighting, float scale, tuple limits

    limits is [loading upper, loading lower, unloading upper, unloading lower], where bounds are definied by min and max of data set.

    curve is either "full", "loading", or "unloading"

    Returns: float sum"""
    h_exp, f_exp = get_smooth_data(scale)
    fh_exp = _split_data(h_exp, f_exp)
    fh_fem = _split_data(h, f)

    ssum1 = _get_piecewise_ss(fh_exp[0], fh_exp[1], fh_fem[0], fh_fem[1], N//2+N%2, limits[0], limits[1])
    ssum2 = None
    if curve != "loading":
        ssum2 = weighting*_get_piecewise_ss(fh_exp[2], fh_exp[3], fh_fem[2], fh_fem[3], N//2, limits[2], limits[3])

    if log_sum and (ssum2 != None):
            log.info("Sum of squares: %.4f,\t %.4f", ssum1, ssum2)


    if curve == "full":
        ssum = ssum1+ssum2
    elif curve == "loading":
        ssum = ssum1
    elif curve == "unloading":
        ssum = ssum2

    return ssum

def _get_piecewise_ss(h_exp, f_exp, h_fem, f_fem, N, up_limit, lo_limit):
    p_ssum = 0
    if h_exp[0] > h_exp[-1]:
        for h in np.linspace(min(h_exp)+lo_limit, max(h_exp)-up_limit, N):
            f1 = np.interp(h, h_exp[::-1], f_exp[::-1])
            f2 = np.interp(h, h_fem[::-1], f_fem[::-1])
            p_ssum += ((f2-f1)/1000)**2

    else:
        for h in np.linspace(min(h_exp)+lo_limit, max(h_exp)-up_limit, N):
            f1 = np.interp(h, h_exp, f_exp)
            f2 = np.interp(h, h_fem, f_fem)
            p_ssum += ((f2-f1)/1000)**2

    return p_ssum/N

def _split_data(h, f):
    assert len(h) == len(f)

    max_ind = h.index(max(h))
    lo_h, lo_f = h[:max_ind+1], f[:max_ind+1]
    un_h, un_f = h[max_ind:], f[max_ind:]

    return [lo_h, lo_f, un_h, un_f]
