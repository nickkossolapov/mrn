from copy import copy
import numpy as np
from post import DataHandler
from data_processor import get_smooth_data

def build_db(domain, data_pickler, sim_handler, delete = True, reconstruct = False):
    for i in domain:
        index = sim_handler.get_index()
        if not reconstruct:
            sim_handler.run_sim(index, i)
        data = DataHandler(index, i, sim_handler)
        if delete:
            data_pickler.write_data(data, index)
        else:
            data_pickler.write_data(data)

    return 1

def build_ncube(edges):
    domain = []
    _recursive_build(edges, domain, [])
    return domain

def _recursive_build(edges, domain, current):
    if len(edges[0]) == 0:
        domain.append(current)
    else:
        for i in edges:
            cut_edges = []
            for j in edges:
                cut_edges.append(j[1:])

            temp = copy(current)
            temp.append(i[0])
            _recursive_build(cut_edges, domain, temp)

def get_fh_mse(h, f, h_exp, f_exp, N, curve="loading", limits=(0.05, 0.05, 0.05, 0.05)):
    fh_exp = _split_data(h_exp, f_exp)
    fh_fem = _split_data(h, f)

    ssum1 = _get_piecewise_ss(fh_exp[0], fh_exp[1], fh_fem[0], fh_fem[1], N//2+N%2, limits[0], limits[1])
    ssum2 = None
    if curve in ("full", "unloading"):
        ssum2 = _get_piecewise_ss(fh_exp[2], fh_exp[3], fh_fem[2], fh_fem[3], N//2, limits[2], limits[3])

    if curve == "full":
        ssum = ssum1+ssum2
    elif curve == "unloading":
        ssum = ssum2
    else:
        ssum = ssum1

    return ssum

def get_rh_mse(r1, h1, r2, h2, N):
    ssum = 0
    for r in np.linspace(0, max(r1), N):
        p1 = np.interp(r, r1, h1)
        p2 = np.interp(r, r2, h2)
        ssum += ((p2-p1)*100)**2
    return ssum/N

def get_se_mse(s1, s2, e, N):
    ssum = 0
    for i in np.linspace(0, max(e), N):
        p1 = np.interp(i, e, s1)
        p2 = np.interp(i, e, s2)
        ssum += ((p2-p1)/100)**2
    return ssum/N

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
