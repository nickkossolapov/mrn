import logging
import pickle
import os
import numpy as np
from simulate import make_file_name

log = logging.getLogger(__name__)

def get_data(file_num, sim_handler):
    """Usage: int file_name, SimHandler sim_handler

    params requires a dictionary containing:
    "mid_time": float, "end_disp": float, "amplitude": float

    Returns: list displacements, list forces"""
    params = sim_handler.get_params()
    file_name = make_file_name(file_num)
    name = file_name[:-4] + ".dat"

    with open("./data/" + name, "r") as fd_data_file:
        amplitude = -params["amplitude"]
        mid_time = params["mid_time"]
        end_disp = params["end_disp"]

        times, forces = _parse_data(fd_data_file)
        disps = [_get_disp(i, amplitude, mid_time, end_disp) for i in times]

    return disps, forces

class DataHandler:
    """class to manage all data

    Attributes:
    list model_params,
    list disps,
    list forces"""

    def __init__(self, file_num, model_params, sim_handler):
        self.model_params = model_params
        self.disps, self.forces = get_data(file_num, sim_handler)

    def get_data(self):
        """Usage: no inputs

        Returns list h, list f"""

        return self.disps, self.forces

    def get_loading_data(self):
        """Usage: no inputs

        Returns list h, list f"""

        split_data = _split_data(self.disps, self.forces)

        return split_data[0], split_data[1]

    def get_es(self, sim_handler):
        """Usage: SimHandler sim_handler

        Returns list stresses, list strains"""
        strains, stresses = sim_handler.get_es(self.model_params)
        return strains, stresses

    def get_pls_data(self, sim_handler, N, h_pnts, curve = "full"):
        """Usage: SimHandler sim_handler, int N, list h_points, string curve

        curve should be "full", "loading", or "unloading"

        Number of points in full curve is 2*N

        h_pnts is [initial, max, end]

        Returns: f_interp, stresses"""

        strains, stresses = sim_handler.get_es(self.model_params)

        split_data = _split_data(self.disps, self.forces)
        f_loading = []
        f_unloading = []
        h_loading = list(np.linspace(h_pnts[0], h_pnts[1], N))
        h_unloading = list(np.linspace(h_pnts[2], h_pnts[1], N))

        for i in h_loading:
            f_loading.append(np.interp(i, split_data[0], split_data[1]))

        for j in h_unloading:
            f_unloading.append(np.interp(j, split_data[2][::-1], split_data[3][::-1]))

        if curve == "loading":
            f_interp = f_loading

        elif curve == "unloading":
            f_interp = f_unloading

        else:
            f_interp = f_loading + f_unloading[::-1][1:]

        return f_interp, stresses

def _split_data(h, f):
    assert len(h) == len(f)

    max_ind = h.index(max(h))
    lo_h, lo_f = h[:max_ind+1], f[:max_ind+1]
    un_h, un_f = h[max_ind:], f[max_ind:]

    return [lo_h, lo_f, un_h, un_f]

def _parse_data(file):
    times = []
    forces = []

    for row in file:
        temp = row.split()
        if len(temp) == 9:
            times.append(float(temp[-1]))
        if len(temp) == 3:
            forces.append(float(temp[1]) * -180)

    return times, forces

def _get_disp(time, amplitude, mid_time, end_disp):
    if time <= mid_time:
        disp = time * (amplitude / mid_time)
    elif time > mid_time:
        disp = amplitude + (time - mid_time) * ((end_disp*amplitude - amplitude)/(1 - mid_time))

    return disp

class DataPickler:
    """class to read and write DataHandler files"""

    def __init__(self, filename, SimHandler, new_file = False):
        self.filename = filename
        self._fp = None

        if new_file:
            file = open(_get_pickle_name(filename), 'wb')
            file.close()
            #TODO: Manage sim handler better?
            self.write_data(SimHandler)

    def __iter__(self):
        self._fp = open(_get_pickle_name(self.filename), 'rb')
        return self

    def __next__(self):
        try:
            x = pickle.load(self._fp)
            if x.__class__.__name__ == "DataHandler":
                return x
            else:
                x = pickle.load(self._fp)
                return x
        except EOFError:
            self._fp.close()
            raise StopIteration

    def write_data(self, data_handler, dat_to_delete = None):
        """Usage: DataHandler data_handler, int dat_to_delete

        Returns: no returns"""

        with open(_get_pickle_name(self.filename), 'ab') as fp:
            pickle.dump(data_handler, fp)

        if isinstance(dat_to_delete, int):
            _delete_data(dat_to_delete)

    def get_data(self):
        """Usage: no inputs

        Returns: list DataHandlers"""

        data_handlers = []
        with open(_get_pickle_name(self.filename), 'rb') as fp:
            while True:
                try:
                    x = pickle.load(fp)
                    if x.__class__.__name__ == "DataHandler":
                        data_handlers.append(x)
                except EOFError:
                    break

        return data_handlers

    def get_sim_handler(self):
        """Usage: no inputs

        """
        with open(_get_pickle_name(self.filename), 'rb') as fp:
            x = pickle.load(fp)
            if x.__class__.__name__ == "SimHandler":
                return x
            else:
                raise IOError("SimHandler doesn't exist in file")

def _get_pickle_name(filename):
    return './data/' + filename + '.p'

def _delete_data(file_num):
    file_name = make_file_name(file_num)
    name = file_name[:-4] + ".dat"
    os.remove('./data/{}'.format(name))

    return 1
