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

def main():
    ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.549}
    inputs = []

    for i in range(len(inputs)):
        name = _make_file_name(i)
        stresses, strains = get_plasticity(inputs[i])
        run_simulation(name, stresses, strains, ccx_params)
        disp, force = get_data(name, ccx_params)

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

def _delete_ccx_files(file_name):
    no_ext_name = file_name[:-4]
    files = glob.glob(no_ext_name + "*")

    for file in files:
        command = "del " + file
        system(command)

    return 0

if __name__ == "__main__":
    main()
