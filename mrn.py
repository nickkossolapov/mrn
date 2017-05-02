import pre, post
import os
import matplotlib.pyplot as plt

def main():
    stresses = [250, 300, 350, 400, 450, 500]
    strains = [0.0, 0.1, 0.2, 0.4, 0.1, 2.5]
    ccx_props = {"mid_time": 0.7, "end_disp": 0.9, "amplitude": -1.8}

    name = make_file_name(9)
    pre.make_inp(name, stresses, strains, ccx_props)
    run_ccx(name)
    move_data(name)
    disp, force = post.get_data(name)
    plt.plot(disp, force)
    plt.show()


def run_ccx(file_name):
    owd = os.getcwd()
    os.chdir("C:/Program Files (x86)/bConverged/CalculiX/ccx/")

    if not(os.path.isfile("ccx.exe")):
        print("Cannot find CalculiX executable")
        quit()

    _file_dir = owd + "\\" + file_name[:-4]
    print(_file_dir)

    _command = "./ccx.exe {}".format(_file_dir)
    #ccx won't actually execute???
    os.system(_command)
    print("Execution of {} finished.".format(file_name))

    os.system("cd {}".format(owd))
    return 1


def make_file_name(num):
    _preceding_zeros = 3
    _string_num = str(num)
    return 'mrn{}.inp'.format('0'*(_preceding_zeros-len(_string_num)) + _string_num)

def move_data(file_name):
    _name = file_name[:-4] + ".dat"
    command = 'move {} ./data/{}'.format(_name, _name)
    os.system(command)
    return 1

if __name__ == "__main__":
    main()