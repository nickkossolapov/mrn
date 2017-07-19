import datetime
import logging
import sys
import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares

# unscaled "amplitude": -1.547
# 1.0834 scale: -1.669
# 3 param voce: [0.744, 2.55, 237], end disp of 0.7

eval_counter = 0
ccx_params = {"mid_time": 0.85, "end_disp": 0.9, "amplitude": -1.669, "spring_constant": 2.1e6, "press_stiffness": 780}

def main():
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    solution = minimize(eval_function, [0.7, 2.5, 250], args=(log), method='nelder-mead')
    log.info(solution)

    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)


def eval_function(cnst, log):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(cnst, 30, "voce")
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50, "loading", 1.0834)

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

if __name__ == "__main__":
    main()
