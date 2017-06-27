import datetime
import logging
import sys
import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares

# K: 870.81973,	n: 0.41040
# K: 878.72981, n: 0.44389

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.547}

def main():
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    solution = minimize(eval_function, (500, 0.4), method='Nelder-Mead', tol = 1e-6, args=(log))
    log.info(solution)

    disp, force = get_data(eval_counter-1, ccx_params)
    h_exp, f_exp = get_smooth_data()
    plt.plot(h_exp, f_exp)
    plt.plot(disp, force)
    plt.show()
    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)


def eval_function(cnst, log):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(cnst[0], cnst[1])
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50, 1)
    log.info("K: %.5f,\tn: %.5f,\tSum: %.5f", cnst[0], cnst[1], ssum)

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

if __name__ == "__main__":
    main()
