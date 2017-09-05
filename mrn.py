import datetime
import logging
import sys
from os import system
import matplotlib.pyplot as plt
import numpy as np
import optimiser as opt
from data_processor import get_smooth_data, get_smooth_surface
from post import DataHandler, DataPickler, get_data
from random import uniform, choice
from scipy.optimize import minimize
from simulate import SimHandler
from sklearn.cross_decomposition import PLSRegression

# unscaled: -1.547
# 1.0834 scale: -1.67

eval_counter = 0
mse_data = []

def main():
    # delete_log() #<-------------------
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    ccx_params = {"mid_time": 0.7, "end_disp": 0.6, "amplitude": -1.67,
                  "spring_constant": 2.1e6, "press_stiffness": 880}
    es_params = {"final_strain": 1, "N": 30, "model": "power", "spacing": "log"}

    sim_handler = SimHandler(ccx_params, es_params)

    s_p = [[200, 0.2*100], [600, 0.6*100], [500, 0.6*100], [250, 0.3*100]]

    mse_overall = []
    global mse_data

    for i in range(4):
        pickle_name = 'opt_2power_to_nonsatvoce_nosurface' + str(i+1)
        data_pickler = DataPickler(pickle_name, sim_handler)
        solution = minimize(eval_function, s_p[i], args=(log, sim_handler, data_pickler), method='nelder-mead', options={'maxfev': 50})
        log.info(solution)
        log.info('\nMSE without surface' + str(i+1))
        log.info(mse_data)
        mse_overall.append(mse_data)
        mse_data = []

    log.info('\nOverall MSE without surface:')
    log.info(mse_overall)

    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)

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

    global mse_data
    mse_data.append(ssum)

    eval_counter += 1
    return ssum[0]


def r_param(pars):
    r_pars = []
    for par in pars:
        r_pars.append(choice([-1, 1]) * uniform(0.3, 0.6) * par + par)
    return r_pars


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


def create_log():
    t_log = logging.getLogger()
    t_log.setLevel(logging.DEBUG)

    fh = logging.FileHandler('logfile.log')
    fh.setLevel(logging.DEBUG)
    t_log.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    t_log.addHandler(ch)

    return t_log

def delete_log():
    command = "del logfile.log"
    system(command)

    return 1

if __name__ == "__main__":
    main()
