import numpy as np
from data_processor import get_smooth_data

def get_plasticity(K, n):
    #using logarithmic strain data does funny things?
    # strains = np.geomspace(1, 2.5, 50)-1
    strains = np.linspace(0, 1.5, 50)
    stresses = K*(strains**n)
    stresses[0] = 255 #don't forgot to modify first data point

    return list(stresses), list(strains)

def test_plasticity(a, b):
    f = [0, 0, a, 0, 0]
    h = [0, 0.1, 1.545, b, 1]
    return h, f

def get_sum_squares(h, f, N):
    """Usage: list h, list f, int N

    Returns: float sum"""
    h_exp, f_exp = get_smooth_data()
    fh_exp = _split_data(h_exp, f_exp)
    fh_fem = _split_data(h, f)

    ssum = _get_piecewise_ss(fh_exp[0], fh_exp[1], fh_fem[0], fh_fem[1], N//2+N%2)
    # ssum += _get_piecewise_ss(fh_exp[2], fh_exp[3], fh_fem[2], fh_fem[3], N//2)

    return ssum

def _get_piecewise_ss(h_exp, f_exp, h_fem, f_fem, N):
    interval = len(h_exp)//N
    p_ssum = 0

    for i in range(1, N):
        h = h_exp[interval*i]
        f1 = f_exp[interval*i]
        f2 = np.interp(h, h_fem, f_fem)
        p_ssum += ((f2-f1)/1000)**2

    return p_ssum/(N-1)

def _split_data(h, f):
    assert len(h) == len(f)

    max_ind = h.index(max(h))
    lo_h, lo_f = h[:max_ind+1], f[:max_ind+1]
    un_h, un_f = h[max_ind:], f[max_ind:]

    return [lo_h, lo_f, un_h, un_f]
