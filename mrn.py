import datetime
import logging
import sys
import matplotlib.pyplot as plt
import numpy as np
import optimiser as opt
from data_processor import get_smooth_data
from post import DataHandler, DataPickler
from scipy.optimize import minimize
from simulate import run_simulation
from sklearn.cross_decomposition import PLSRegression


# unscaled "amplitude": -1.547
# 1.0834 scale: -1.669
# 3 param voce w/o f: [0.744, 2.55, 237], end disp 0.7, midtime 0.6
# 3 param voce w/ f: [0.611, 2.61, 256], end disp 0.9, midtime 0.85???

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.7, "amplitude": -1.669, "spring_constant": 2.1e6, "press_stiffness": 780}

def main():
    # delete_log() #<------

    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))
    global eval_counter

    a = [0.70, 0.73, 0.76, 0.79]
    b = [2.4, 2,5, 2.6, 2.7]
    Sy = [220, 230, 240, 250]

    data_pickler = DataPickler('pls_test', True)

    for i in range(4):
        for j in range(4):
            for k in range(4):
                stresses, strains = opt.get_plasticity([a[i], b[j], Sy[k]], 30, 1)
                run_simulation(eval_counter, stresses, strains, ccx_params)
                data = DataHandler(eval_counter, stresses, strains, ccx_params)
                data_pickler.write_data(data)
                eval_counter += 1

    stresses, strains = opt.get_plasticity([0.745, 2.55, 235], 30, 1)
    run_simulation(999, stresses, strains, ccx_params)
    # test_f, test_s = DataHandler(999, stresses, strains, ccx_params).get_psl_data()

    # X = []
    # Y = []
    # h_pnts = [0.11, 1.65, 1.]
    # for handler in data_pickler:
    #     handler.interpolate_data(50, h_pnts, "loading")
    #     x, y = handler.get_psl_data()
    #     X.append(x)
    #     Y.append(y)


    # pls = PLSRegression(3)
    # pls.fit(X, Y)
    # Y_pred = pls.predict([test_f])
    # plt.plot(strains, stresses)
    # plt.plot(test_f, Y_pred[0])
    # plt.show()


    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)

def eval_function(cnst, log):
    global eval_counter

    file_num = eval_counter
    stresses, strains = opt.get_plasticity(cnst, 30, 1)
    run_simulation(file_num, stresses, strains, ccx_params, 0.5)
    disp, force = DataHandler(999, stresses, strains, ccx_params).get_data()

    ssum = opt.get_sum_squares(disp, force, 50, "loading", 1.0834)

    logstring = ""
    for i in range(len(cnst)):
        logstring += "{:c}: {:.5f},\t".format(97+i, cnst[i])

    logstring += "Sum: {:.5f}".format(ssum)
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
