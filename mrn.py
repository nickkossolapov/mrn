import datetime
import logging
import sys
import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares

# K: 297.45,  n: 0.519,

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.547, "spring_constant": 2.1e6}

def main():
    log = create_log()
    log.info("--- Program started at %s ---", datetime.datetime.now().strftime("%H:%M:%S"))

    simplex = [[245, 900, 2500, 12], [250, 950, 1750, 12.5], [255, 1000, 2000, 13], [260, 1050, 2250, 13.5], [265, 1100, 2500, 14]]

    solution = minimize(eval_function, [255, 1000, 2000, 13], args = (log))
    log.info(solution)
    log.info("\n--- Program completed at %s ---\n", datetime.datetime.now().strftime("%H:%M:%S"))

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)


def eval_function(cnst, log):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(cnst, 50, "log")
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50, 1)

    logstring = ""
    for i in range(len(cnst)):
        logstring += "\t{:c}: {:.5f},".format(97+i, cnst[i])

    logstring += "\tSum: {:.5f}".format(ssum)
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
