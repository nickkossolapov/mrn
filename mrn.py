import datetime
import logging
import sys
from copy import copy
from os import system
from random import uniform, choice
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
    # # delete_log() #<-------------------
    # log = create_log('log_db_lhs')
    # log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    # ccx_params = {"mid_time": 0.7, "end_disp": 0.6, "amplitude": -1.67,
    #               "spring_constant": 2.1e6, "press_stiffness": 880}
    # es_params_true = {"final_strain": 1, "N": 30, "model": "voce", "spacing": "log"}
    # sim_handler = SimHandler(ccx_params, es_params_true)
    # data_pickler = DataPickler('db_3voce_lhs', sim_handler, True)





    # log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    # for handler in log.handlers:
    #     handler.close()
    #     log.removeFilter(handler)


def eval_function(cnst, log, sim_handler, data_pickler):
    global eval_counter
    ccx_params = {"mid_time": 0.7, "end_disp": 0.6, "amplitude": -1.67,
                  "spring_constant": 2.1e6, "press_stiffness": 880}
    es_params_true = {"final_strain": 1, "N": 30, "model": "voce-nonsat", "spacing": "log"}
    sim_handler_true = SimHandler(ccx_params, es_params_true)
    e_exp, s_exp = sim_handler_true.get_es([0.5, 10, 350, 50])

    if cnst[0] < 0.05:
        cnst[0] = 0.05

    cnst_mod = [cnst[0], cnst[1] / 100, 400]

    sim_handler.run_sim(eval_counter, cnst_mod)
    data = DataHandler(eval_counter, cnst_mod, sim_handler)

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

    logstring = "\n"
    for i in range(len(cnst_mod)):
        logstring += "{:c}: {:.5f},\t".format(97+i, cnst_mod[i])
    log.info(logstring)

    logstring = ""
    for i in range(3):
        logstring += "{}: {:.5f},\t".format(ssum_str[i], ssum[i])
    log.info(logstring)

    log.info('Sum: ' + str(ssum[0]))

    eval_counter += 1
    return ssum[0]

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

def r_param(pars):
    r_pars = []
    for par in pars:
        r_pars.append(choice([-1, 1]) * uniform(0.3, 0.6) * par + par)
    return r_pars

def build_rbf(data_pickler, target_data_handler, eps=1.3):
    sim_handler = data_pickler.get_sim_handler()
    data = data_pickler.get_data()

    R = []
    X = [[] for i in range(len(data[i].get_params()))]

    h_v, f_v = target_data_handler.get_fh()
    x_v = target_data_handler.get_params()


    for data_point in data:
        h, f = data_point.get_fh()
        R.append(opt.get_fh_mse(h, f, h_v, f_v, 50))
        x = data_point.get_params()
        for j in range(len(X)):
            X[j].append(x[j])

    rbfi = Rbf(*X, R, function='gaussian', epsilon=eps)
    return rbfi


def epsilon_opt(eps, data_pickler):
    start_time = datetime.datetime.now()
    sim_handler = data_pickler.get_sim_handler()
    data = data_pickler.get_data()
    error = 0

    for i in range(len(data)):
        R = []
        X = [[] for i in range(len(data[i].get_params()))]

        t_data = copy(data)
        del t_data[i]

        h_v, f_v = data[i].get_fh()
        x_v = data[i].get_params()


        for data_point in t_data:
            h, f = data_point.get_fh()
            R.append(opt.get_fh_mse(h, f, h_v, f_v, 50))
            x = data_point.get_params()
            for j in range(len(X)):
                X[j].append(x[j])

        rbfi = Rbf(*X, R, function='gaussian', epsilon=eps[0])
        error += (rbfi(*x_v))**2

    print('ping!', ((datetime.datetime.now()-start_time).__str__())[:-7])

    return error

def do_pls(data_pickler, test_data, interp_args):
    test_f, test_s = test_data.get_pls_data(*interp_args)

    X, Y = [], []

    for handler in data_pickler:
        x, y = handler.get_pls_data(*interp_args)
        param = handler.model_params
        X.append(x)
        Y.append(param)

    pls = PLSRegression(3)
    pls.fit(X, Y)
    Y_pred = pls.predict([test_f])

    return Y_pred


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

if __name__ == "__main__":
    main()
