import pre, post, plasticity
from os import system
import glob
import matplotlib.pyplot as plt
import subprocess

def main():

    ccx_params = {"mid_time": 0.7, "end_disp": 0.9, "amplitude": -1.8}
    n = [0.01, 0.02, 0.03, 0.04, 0.05]
    for i in range(5):
        stresses, strains = plasticity.get_plasticity(n[i])
        name = make_file_name(i)
        pre.make_inp(name, stresses, strains, ccx_params)
        run_ccx(name) 
        move_data(name)
        delete_ccx_files(name)
        disp, force = post.get_data(name)
        plt.plot(disp, force)

    plt.legend(n)
    plt.show()



def run_ccx(file_name):
    _no_ext_name = file_name[:-4]
    _command = "ccx {} >nul".format(_no_ext_name)
    try:
        print("Started execution of {}".format(file_name))
        system(_command)
        print("Execution of {} finished.".format(file_name))
        return 1
    except Exception:
        print("Something went wrong executing {}.".format(file_name))
        return -1

def make_file_name(num):
    _preceding_zeros = 3
    _string_num = str(num)
    return 'mrn{}.inp'.format('0'*(_preceding_zeros-len(_string_num)) + _string_num)

def move_data(file_name):
    _name = file_name[:-4] + ".dat"
    _command = 'move {} ./data/{}'.format(_name, _name)

    system(_command)
    return 1

def delete_ccx_files(file_name):
    _no_ext_name = file_name[:-4]
    files = glob.glob(_no_ext_name + "*")

    for file in files:
        _command = "del /F " + file
        system(_command)
    return 1


if __name__ == "__main__":
    main()