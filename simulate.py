import logging
import glob
import datetime
from os import system
import numpy as np
from pre import make_inp
from scipy.integrate import odeint

log = logging.getLogger(__name__)

class SimHandler:
    """class to manage simulation parameter between multiple simulations

    Attributes:
    dict ccx_params
    float final_strain
    int N
    string model
    string spacing
    float friction
    int sim_no"""

    def __init__(self, ccx_params, es_params, friction = 0):
        self.ccx_params = ccx_params
        self.final_strain = es_params["final_strain"]
        self.N = es_params["N"]
        self.model = es_params["model"]
        self.spacing = es_params["spacing"]
        self.friction = friction
        self.sim_no = 0

    def get_es(self, par):
        """Usage: list parameters

        Returns: list strains, list stresses"""
        strains = _get_strains(self.N, self.final_strain, self.spacing)
        if len(par) == 1:
            stresses = (300**(1-par[0])) * (70000**par[0]) * ((strains - 300/70000)**par[0])

        if len(par) == 2 or len(par) == 3:
            if len(par) == 2:
                Sy = 300
            else:
                Sy = par[2]

            if self.model == "power":
                stresses = par[0]*(strains**par[1]) + Sy

            if self.model == "power-mod":
                stresses = par[0]*((strains - Sy/70000)**par[1]) + Sy

            if self.model == "voce":
                stresses = (Sy/(1-par[0]))*(1-par[0]*np.exp(-par[1]*strains))

        if len(par) == 4:
            if self.model == "voce-nonsat":
                stresses = (par[2]/(1-par[0]))*(1-par[0]*np.exp(-par[1]*strains)) + par[3]*strains
            else:
                voce = lambda stress, strain: par[1]*(1-stress/par[2])**par[3]
                temp_stresses = odeint(voce, 0, strains)
                stresses = []
                for i in temp_stresses:
                    stresses.append(i[0] + par[0])

        return list(strains), list(stresses)

    def run_sim(self, file_number, par, make_only = False):
        """Usage: int file_number, list stresses, list strains, dict params, friction float, make_only bool

        Enable make_only to prevent execution of files

        Returns: no returns"""
        strains, stresses = self.get_es(par)
        file_name = make_file_name(file_number)
        make_inp(file_name, stresses, strains, self.ccx_params, self.friction)

        if not make_only:
            _run_ccx(file_name)
            _move_data(file_name)
            _delete_ccx_files(file_name)
            self.sim_no += 1

        return 1

    def get_params(self):
        """Usage: no inputs

        returns dict params"""
        return self.ccx_params

    def get_index(self):
        """Usage: no inuts

        Returns: int next_index"""
        return self.sim_no + 1


def make_file_name(num):
    """Usage: int num

    Returns: string file_name"""
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

def _get_strains(N, final_strain, spacing = "log"):
    if spacing == "lin":
        strains = np.linspace(0, final_strain**0.5, N)
    elif spacing == "log":
        strains = np.geomspace(1, final_strain**0.5+1, N)-1

    return strains**2
