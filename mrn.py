import datetime
import logging
import sys
import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares, test_plasticity

#K: 892.836650801792,    n: 0.40923596690313946

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.547}

def main():
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    solution = minimize(optimise_function, (45000, 1.15), method='Nelder-Mead', tol = 1, args=(log))
    log.info(solution)

    disp, force = get_data(eval_counter-1, ccx_params)
    h_exp, f_exp = get_smooth_data()
    plt.plot(h_exp, f_exp)
    plt.plot(disp, force)
    plt.show()

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)


def optimise_function(fh, log):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(fh[0], fh[1])
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50, 1e-1)
    log.info("K: %.4f,\tn: %.4f,\tSum: %.5f", fh[0], fh[1], ssum)

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
