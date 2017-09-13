import logging
import pickle
import os
import numpy as np
from simulate import make_file_name, SimHandler

log = logging.getLogger(__name__)

def get_data(file_num, sim_handler, hf_only=False):
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

        times, forces, nodes = _parse_data(fd_data_file)
        radii, heights = _get_rh(nodes)
        disps = [_get_disp(i, amplitude, mid_time, end_disp) for i in times]

    if hf_only:
        return disps, forces

    return disps, forces, radii, heights

def _get_rh(nodes):
    node_pos = _get_node_pos()

    r = []
    h = []
    for i in range(len(nodes)):
        h.append(nodes[i][1])
        r.append(nodes[i][0] + node_pos[i])

    return r, h

def _get_surface_nodes():
    with open('surface.nam') as fp:
        nodes = []

        for i, line in enumerate(fp):
            if i == 0 or i == 1:
                continue
            temp = line.split(sep=',')
            nodes.append(int(temp[0]))

        nodes[1], nodes[0] = nodes[0], nodes[1]

    return nodes

def _get_node_pos():
    nodes = _get_surface_nodes()

    with open('all.msh') as fp:
        node_pos_dict = {}

        for i, line in enumerate(fp):
            if i == 0:
                continue
            temp = line.split(sep=',')

            if temp[0] == '*ELEMENT':
                break

            if int(temp[0]) in nodes:
                node_pos_dict[temp[0].strip()] = float(temp[1])

    node_pos = []
    for i in nodes:
        node_pos.append(node_pos_dict[str(i)])

    return node_pos

class DataHandler:
    """class to manage all data

    Attributes:
    list model_params,
    list disps,
    list forces,
    list radii,
    list heights"""

    def __init__(self, file_num, model_params, sim_handler):
        self.model_params = model_params
        self.disps, self.forces, self.radii, self.heights = get_data(file_num, sim_handler)

    def get_params(self):
        """Usage: no inputs

        Returns list params"""

        return self.model_params

    def get_fh(self):
        """Usage: no inputs

        Returns list h, list f"""

        return self.disps, self.forces

    def get_rh(self):
        """Usage: no inputs

        Returns list h, list f"""

        return self.radii, self.heights

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

    def get_pls_data(self, sim_handler, h_pnts, e_pnts):
        """Usage: SimHandler sim_handler, int N, list h_points, string curve

        curve should be "full", "loading", or "unloading"

        Number of points in full curve is 2*N

        h_pnts is [initial, max, end]

        Returns: f_interp, stresses"""
        split_data = _split_data(self.disps, self.forces)
        f_interp = []
        for i in h_pnts:
            f_interp.append(np.interp(i, split_data[0], split_data[1]))

        strains, stresses = sim_handler.get_es(self.model_params)
        s_interp = []
        for i in e_pnts:
            s_interp.append(np.interp(i, strains, stresses))

        return f_interp, s_interp

def _split_data(h, f):
    assert len(h) == len(f)

    max_ind = h.index(max(h))
    lo_h, lo_f = h[:max_ind+1], f[:max_ind+1]
    un_h, un_f = h[max_ind:], f[max_ind:]

    return [lo_h, lo_f, un_h, un_f]

def _parse_data(file):
    times = []
    forces = []
    nodes = []

    for row in file:
        temp = row.split()
        if len(temp) == 9:
            times.append(float(temp[-1]))
        if len(temp) == 3:
            forces.append(float(temp[1]) * -180)

    file.seek(0)
    for row in file:
        temp = row.split()
        if len(temp) == 8 and abs(float(temp[7]) - times[-1]) < 1e-6 and len(nodes) == 0:
            for row in file:
                temp = row.split()
                if len(temp) == 4:
                    nodes.append([float(temp[1]), float(temp[2])])
                if len(temp) == 8:
                    break

    #quirk as first and second nodes are switched
    if len(nodes) > 2:
        nodes[1], nodes[0] = nodes[0], nodes[1]
    return times, forces, nodes

def _get_disp(time, amplitude, mid_time, end_disp):
    if time <= mid_time:
        disp = time * (amplitude / mid_time)
    elif time > mid_time:
        disp = amplitude + (time - mid_time) * ((end_disp*amplitude - amplitude)/(1 - mid_time))

    return disp

class DataPickler:
    """class to read and write DataHandler files"""

    def __init__(self, filename, SimHandler=None, new_file=False):
        self.filename = filename
        self._fp = None

        if new_file:
            file = open(_get_pickle_name(filename), 'wb')
            file.close()
            if SimHandler is not None:
                self.write_data(SimHandler)
            else:
                raise NotImplementedError

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

    def __getitem__(self, key):
        return self.get_data()[key]

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
