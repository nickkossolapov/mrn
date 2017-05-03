import pre, post, plasticity
from os import system
import glob
import matplotlib.pyplot as plt
import csv
import numpy as np
import datetime

def main():
    ccx_params = {"mid_time": 0.7, "end_disp": 0.9, "amplitude": -1.8}
    n = np.linspace(0.00005, 0.005, 50)

    for i in range(len(n)):
        name = make_file_name(i)
        stresses, strains = plasticity.get_plasticity(n[i])
        run_simulation(name, stresses, strains, ccx_params)
        disp, force = post.get_data(name)
        plt.plot(disp, force)

    av_h, av_f = get_average_data()
    plt.plot(av_h, av_f)
    plt.show()

def run_simulation(file_name, stresses, strains, params):
    pre.make_inp(name, stresses, strains, params)
    _run_ccx(file_name) 
    _move_data(file_name)
    _delete_ccx_files(file_name)


def get_average_data():
    datafile = open('data.csv', 'r')
    reader = csv.reader(_datafile, delimiter=',')
    _av_h = []
    _av_f = []

    first_row = True
    for row in _reader:
        if first_row:
            first_row = False
            continue

        _av_h.append(float(row[-1])+0.1)
        _av_f.append(float(row[-2])*1000)
    return _av_h, _av_f

def _run_ccx(file_name):
    no_ext_name = file_name[:-4]
    command = "ccx {} >nul".format(no_ext_name)
    try:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        print("Started execution of {} at \t{}".format(file_name, time))
        system(command)
        time = datetime.datetime.now().strftime("%H:%M:%S")
        print("Execution of {} finished at \t{}.".format(file_name, time)))
        return 1
    except Exception:
        print("Something went wrong executing {}.".format(file_name))
        return -1

def _make_file_name(num):
    preceding_zeros = 3
    string_num = str(num)
    return 'mrn{}.inp'.format('0'*(preceding_zeros-len(string_num)) + string_num)

def _move_data(file_name):
    name = file_name[:-4] + ".dat"
    command = 'move {} ./data/{}'.format(name, name)

    system command)
    return 1

def _delete_ccx_files(file_name):
    no_ext_name = file_name[:-4]
    files = glob.glob(no_ext_name + "*")

    for file in files:
        command = "del /F " + file
        system(command)
    return 1

if __name__ == "__main__":
    main()