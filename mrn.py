<<<<<<< HEAD
from os import system
import glob
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pre import make_inp
from post import get_data
from plasticity import get_plasticity

# n = [0.142] is solution!
=======
import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares
>>>>>>> experimental

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.547}

def main():
    solution = minimize(optimise_function, (532, 0.142), method='Nelder-Mead', tol = 1e-6)
    print(solution)
    h_exp, f_exp = get_smooth_data()
    disp, force = get_data(eval_counter-1, ccx_params)

    plt.plot(h_exp, f_exp)
    plt.plot(disp, force)
    plt.show()


def optimise_function(fh):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(fh[0], fh[1])
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50)
    print("K: {},\tn: {},\tSum: {}".format(fh[0],fh[1], ssum))
<<<<<<< HEAD
=======
def main():
    ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.549}
    inputs = []

    for i in range(len(inputs)):
        name = _make_file_name(i)
        stresses, strains = get_plasticity(inputs[i])
        run_simulation(name, stresses, strains, ccx_params)
        disp, force = get_data(name, ccx_params)
<<<<<<< HEAD
=======

>>>>>>> experimental

def run_simulation(file_name, stresses, strains, params):
    make_inp(file_name, stresses, strains, params)
    _run_ccx(file_name)
    _move_data(file_name)
    _delete_ccx_files(file_name)

    return 0


def get_average_data():
    datafile = open('data.csv', 'r')
    reader = csv.reader(datafile, delimiter=',')
    _av_h = []
    _av_f = []

    first_row = True
    for row in reader:
        if first_row:
            first_row = False
            continue

        _av_h.append(float(row[-1])+0.1)
        _av_f.append(float(row[-2])*1000)

    return _av_h, _av_f


def _run_ccx(file_name):
    no_ext_name = file_name[:-4]
    command = "ccx {} >nul".format(no_ext_name)

    start_time = datetime.datetime.now()
    print("\nStarted execution of {} at {}".format(file_name, start_time.strftime("%H:%M:%S")))
    system(command)
    run_time = (datetime.datetime.now()-start_time).__str__()
    print("Execution of {} finished with runtime of {}.".format(file_name, run_time))

    return 0


def _make_file_name(num):
    preceding_zeros = 3
    string_num = str(num)

    return 'mrn{}.inp'.format('0'*(preceding_zeros-len(string_num)) + string_num)


def _move_data(file_name):
    name = file_name[:-4] + ".dat"
    command = 'move {} ./data/{}'.format(name, name)
    system(command)

    return 0
<<<<<<< HEAD
=======
>>>>>>> b9ea71c4b3feac3dd9935e71544c125aeeba4a81
>>>>>>> experimental
=======
>>>>>>> experimental

    eval_counter += 1

    return ssum
<<<<<<< HEAD
=======
    for file in files:
        command = "del " + file
        system(command)

    return 0
<<<<<<< HEAD
=======
>>>>>>> b9ea71c4b3feac3dd9935e71544c125aeeba4a81
>>>>>>> experimental
=======
>>>>>>> experimental

if __name__ == "__main__":
    main()
