import csv
import datetime
import logging
import sys
import os
from copy import copy
from os import system
from random import uniform, choice
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import optimiser as opt
from data_processor import get_smooth_data, get_smooth_surface
from post import DataHandler, DataPickler, get_data
from scipy.optimize import minimize
from scipy.interpolate import Rbf
from simulate import SimHandler
from sklearn.cross_decomposition import PLSRegression
from pyDOE import lhs

# unscaled: -1.547
# 1.0834 scale: -1.67

eval_counter = 0

def main():
    # delete_log('logfile') #<-------------------
    log = create_log('logfile')

    uni_pickle = DataPickler('db_3voce_even')
    lhs_pickle = DataPickler('db_3voce_lhs')
    sim_handler = uni_pickle.get_sim_handler()
    scale_v = np.array([500, 50, 1])
    error = []

    for data in lhs_pickle:
        if in_range(data.get_params(), [0.5, 5, 350], 0.2):
            h_v, f_v = data.get_fh()
            rbfi = build_rbf(uni_pickle, h_v, f_v, 85, scale_v)
            min_x = []
            min_fun = 100
            for i in range(100):
                s_p = [uniform(200, 300), uniform(200, 300), uniform(300, 400)]
                sol = minimize(rbf_eval, s_p, args=(rbfi), method='nelder-mead', options={'xtol':1e-4})
                if sol.success == True and in_range(sol.x, [0.5, 5, 350]*scale_v, 0.25):
                    if sol.fun < min_fun:
                        min_x = [sol.x[0]/500, sol.x[1]/50, sol.x[2]]
                        min_fun = sol.fun

            if min_x:
                e, s = sim_handler.get_es(min_x)
                e_t, s_t = data.get_es(sim_handler)
                error.append(opt.get_se_mse(s, s_t, e, 100, True))
    print(error)

    # plt.figure()
    # plt.rc('font', family='serif')
    # plt.hist(error)
    # # plt.hist(b, np.linspace(0.375, .625, 18))
    # # plt.axis([0.375, .625, 0, 400])
    # plt.ylabel(r'$\it{Number}$ $\it{of}$ $\it{occurances}$', fontsize = 12)
    # plt.xlabel(r'$\it{b}$', fontsize = 12)
    # plt.savefig("FIGURE1")
    # plt.show()

    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))
    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)

def in_range(par, centre, val):
    for i in range(len(par)):
        if abs(par[i] - centre[i]) >= (val*centre[i]):
            return False
    return True

def eval_function(cnst, log, sim_handler, data_pickler):
    global eval_counter
    ccx_params = {"mid_time": 0.7, "end_disp": 0.6, "amplitude": -1.67,
                  "spring_constant": 2.1e6, "press_stiffness": 880}
    es_params_true = {"final_strain": 1, "N": 30, "model": "voce-nonsat", "spacing": "log"}
    sim_handler_true = SimHandler(ccx_params, es_params_true)
    e_exp, s_exp = sim_handler_true.get_es([0.5, 10, 350, 50])

    if cnst[0] < 0.05:
        cnst[0] = 0.05

    sim_handler.run_sim(99, cnst)
    data = DataHandler(99, cnst, sim_handler)

    if data_pickler != 1:
        data_pickler.write_data(data)

    d, f = data.get_fh()
    r, h = data.get_rh()
    e, s = data.get_es(sim_handler)

    d_exp, f_exp, r_exp, h_exp = get_data(997, sim_handler_true)
    e_exp, s_exp = sim_handler_true.get_es([0.5, 10, 350, 50])
    f_exp = list(np.array(f_exp))

    ssum = []
    ssum_str = ['fh', 'rh', 'se']
    ssum.append(opt.get_fh_mse(d, f, d_exp, f_exp, 50))
    ssum.append(opt.get_rh_mse(r, h, r_exp, h_exp, 50))
    ssum.append(opt.get_se_mse(s, s_exp, e, 50))

    logstring = '> ' + str(eval_counter) + "\n"
    for i in range(len(cnst)):
        logstring += "{:c}: {:.5f},\t".format(97+i, cnst[i])
    log.info(logstring)

    logstring = ""
    for i in range(3):
        logstring += "{}: {:.5f},\t".format(ssum_str[i], ssum[i])
    log.info(logstring)

    log.info('Sum: ' + str((1e6)*(ssum[0])*(ssum[1]**0.5)*(1/(ssum[2]))))

    eval_counter += 1
    return (1e6)*(ssum[0])*(ssum[1]**0.5)*(1/(ssum[2]))


def rbf_eval(cnst, rbfi):
    return rbfi(*cnst)

def r_param(pars):
    r_pars = []
    for par in pars:
        r_pars.append(choice([-1, 1]) * uniform(0.3, 0.6) * par + par)
    return r_pars

def build_rbf(data_pickler, h_v, f_v, eps, scale_v):
    data = data_pickler.get_data()

    R = []
    X = [[] for i in range(len(scale_v))]

    for data_point in data:
        h, f = data_point.get_fh()
        R.append(opt.get_fh_mse(h, f, h_v, f_v, 50))
        x = copy(data_point.get_params())
        assert len(x) == len(scale_v)
        x *= np.array(scale_v)
        for j in range(len(X)):
            X[j].append(x[j])
    
    if eps == 0:
        rbfi = Rbf(*X, R, function='gaussian')
    else:
        rbfi = Rbf(*X, R, function='gaussian', epsilon=eps)
    return rbfi

def build_mixed_rbf(data_pickles, h_v, f_v, scale_v):
    for data_pickle in data_pickles:
        data = data_pickle.get_data()

        R = []
        X = [[] for i in range(len(scale_v))]

        for data_point in data:
            h, f = data_point.get_fh()
            R.append(opt.get_fh_mse(h, f, h_v, f_v, 50))
            x = copy(data_point.get_params())
            assert len(x) == len(scale_v)
            x *= np.array(scale_v)
            for j in range(len(X)):
                X[j].append(x[j])

    rbfi = Rbf(*X, R, function='gaussian')
    return rbfi
def epsilon_opt(eps, data_pickler, h_v, f_v, scale_v):
    data = data_pickler.get_data()
    error = 0
    sys.stdout = open(os.devnull, 'w')
    for i in range(len(data)):
        R = []
        X = [[] for i in range(len(data[i].get_params()))]

        mse_true = opt.get_fh_mse(*data[i].get_fh(), h_v, f_v, 50)
        x_v = copy(data[i].get_params())
        if scale_v != 1:
            x_v *= np.array(scale_v)

        t_data = copy(data)
        del t_data[i]

        for data_point in t_data:
            h, f = data_point.get_fh()
            R.append(opt.get_fh_mse(h, f, h_v, f_v, 50))
            x = copy(data_point.get_params())
            if scale_v != 1:
                x *= np.array(scale_v)
            for j in range(len(X)):
                X[j].append(x[j])

        rbfi = Rbf(*X, R, function='gaussian', epsilon=eps)
        error += (rbfi(*x_v)-mse_true)**2
    sys.stdout = sys.__stdout__
    return error

def build_pls(data_pickler, sim_handler, components, h_pnts, e_pnts, params=False):
    X, Y = [], []

    for handle in data_pickler:
        x, y = handle.get_pls_data(sim_handler, h_pnts, e_pnts)
        X.append(x)
        if params:
            Y.append(handle.get_params())
        else:
            Y.append(y)

    pls = PLSRegression(components)
    pls.fit(X, Y)

    return pls

def build_even_db(log, sim_handler, data_pickler):
    centre = np.array([0.5, 5, 350])
    for i in np.linspace(0.75, 1.25, 6):
        for j in np.linspace(0.75, 1.25, 6):
            for k in np.linspace(0.75, 1.25, 6):
                params = centre*[i, j, k]

                logstring = "\n"
                for l in range(len(params)):
                    logstring += "{:c}: {:.5f},\t".format(97+l, params[l])
                log.info(logstring)

                sim_handler.run_sim(901, params)
                data = DataHandler(901, params, sim_handler)
                data_pickler.write_data(data, 901)

    return 0


def build_lhs_db(log, sim_handler, data_pickler):
    centre = np.array([0.5, 5, 350])
    hypercube = 0.75 + 0.5 * (np.array(lhs(3, 256)))

    for i in range(len(hypercube)):
        params = centre*hypercube[i]

        logstring = "\n" + str(i) + ": "
        for l in range(len(params)):
            logstring += "{:c}: {:.5f},\t".format(97+l, params[l])
        log.info(logstring)

        sim_handler.run_sim(901, params)
        data = DataHandler(901, params, sim_handler)
        data_pickler.write_data(data, 901)

    return 0

def create_log(logname='logfile'):
    t_log = logging.getLogger()
    t_log.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logname+'.log')
    fh.setLevel(logging.DEBUG)
    t_log.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    t_log.addHandler(ch)

    return t_log

def delete_log(logname='logfile'):
    command = "del " + logname + ".log"
    system(command)

    return 0

def get_loading(h, f):
    assert len(h) == len(f)

    max_ind = h.index(max(h))
    lo_h, lo_f = h[:max_ind+1], f[:max_ind+1]
    un_h, un_f = h[max_ind:], f[max_ind:]

    return lo_h, lo_f

if __name__ == "__main__":
    main()
