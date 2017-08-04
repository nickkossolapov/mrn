import datetime
import logging
import sys
from os import system
import matplotlib.pyplot as plt
import numpy as np
import optimiser as opt
from data_processor import get_smooth_data
from post import DataHandler, DataPickler, get_data
from scipy.optimize import minimize
from simulate import SimHandler
from sklearn.cross_decomposition import PLSRegression


# unscaled "amplitude": -1.547
# 1.0834 scale: -1.669
# 3 param voce w/o f: [0.744, 2.55, 237], end disp 0.7, midtime 0.6
# 3 param voce w/ f: [0.611, 2.61, 256], end disp 0.9, midtime 0.85???

eval_counter = 0

def main():
    # delete_log() #<-------------------
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    ccx_params = {"mid_time": 0.8, "end_disp": 0.9, "amplitude": -1.67,
                  "spring_constant": 2.1e6, "press_stiffness": 860}
    es_params = {"final_strain": 0.6, "N": 15, "model": "voce", "spacing": "log"}
    sim_handler = SimHandler(ccx_params, es_params)

    sim_handler.run_sim(0, [0.62, 2.7, 255])
    data = DataHandler(0, [0.62, 2.7, 255], sim_handler)
    plt.plot(*data.get_data())
    plt.plot(*get_smooth_data())
    plt.show()

    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)

def optimise(log, sim_handler):
    data_pickler = DataPickler('opt_3param_f', True)
    solution = minimize(eval_function, [0.62, 2.7, 250], args=(log, data_pickler, sim_handler), method='nelder-mead')
    log.info(solution)


def do_pls(data_pickler, test_data, interp_args):
    test_f, test_s = test_data.get_pls_data(*interp_args)

    X, Y = [], []

    for handler in data_pickler:
        x, y = handler.get_pls_data(*interp_args)
        param = handler.model_params
        X.append(x)
        Y.append(param)

    pls = PLSRegression(components)
    pls.fit(X, Y)
    Y_pred = pls.predict([test_f])

    return Y_pred

def eval_function(cnst, log, data_pickler, sim_handler):
    global eval_counter

    sim_handler.run_sim(eval_counter, cnst)
    data = DataHandler(eval_counter, cnst, sim_handler)
    data_pickler.write_data(data)
    disp, force = data.get_data()

    ssum = opt.get_sum_squares(disp, force, 50, 1.0834)

    logstring = ""
    for i in range(len(cnst)):
        logstring += "{:c}: {:.5f},\t".format(97+i, cnst[i])

    logstring += "Sum: {:.7f}".format(ssum)
    log.info(logstring)

    eval_counter += 1
    return ssum

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
