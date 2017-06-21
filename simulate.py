import logging
import glob
import datetime
from os import system
from pre import make_inp

log = logging.getLogger(__name__)

def run_simulation(file_number, stresses, strains, params):
    """Usage: int file_number, list stresses, list strains, dict params

    Returns: no returns"""
    file_name = make_file_name(file_number)
    make_inp(file_name, stresses, strains, params)
    _run_ccx(file_name)
    _move_data(file_name)
    _delete_ccx_files(file_name)

    return 1

def make_file_name(num):
    """Usage: int num

    Returns string file_name"""
    preceding_zeros = 3
    string_num = str(num)

    return 'mrn{}.inp'.format('0'*(preceding_zeros-len(string_num)) + string_num)

def _run_ccx(file_name):
    no_ext_name = file_name[:-4]
    command = "ccx {} >nul".format(no_ext_name)

    start_time = datetime.datetime.now()
    log.info("\nStarted execution of %s at %s", file_name, start_time.strftime("%H:%M:%S"))
    system(command)
    run_time = ((datetime.datetime.now()-start_time).__str__())[:-7]
    log.info("Execution of %s finished with runtime of %s", file_name, run_time)

    return 1

def _move_data(file_name):
    name = file_name[:-4] + ".dat"
    command = 'move {} ./data/{}'.format(name, name)

    system(command)

    return 1

def _delete_ccx_files(file_name):
    no_ext_name = file_name[:-4]
    files = glob.glob(no_ext_name + "*")

    for file in files:
        command = "del " + file
        system(command)

    return 1
