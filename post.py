import logging
import pickle
from simulate import make_file_name

log = logging.getLogger(__name__)

def get_data(file_name, params):
    """Usage: int file_name, dict params

    params requires a dictionary containing:
    "mid_time": float, "end_disp": float, "amplitude": float

    Returns: list displacements, list forces"""
    file_name = make_file_name(file_name)
    name = file_name[:-4] + ".dat"

    with open("./data/" + name, "r") as fd_data_file:
        amplitude = -params["amplitude"]
        mid_time = params["mid_time"]
        end_disp = params["end_disp"]

        times, forces = _parse_data(fd_data_file)
        disps = [_get_disp(i, amplitude, mid_time, end_disp) for i in times]

    return disps, forces

def write_psl_data(filename, data, new_file = False):
    """Usage: string filename

    data should be list of lists, i.e. [list s, list e, list h, list f]

    Returns: no returns"""
    if not new_file:
        with open('./psl_data/' + filename, 'ab') as fp:
            pickle.dump(data, fp)
    else:
        with open('./psl_data/' + filename, 'wb') as fp:
            pickle.dump(data, fp)

    return 1

def read_psl_data(filename):
    """Usage: string filename

    Returns: list s, list e, list h, list f"""
    s = []
    e = []
    f = []
    h = []

    with open('./psl_data/' + filename, 'rb') as fp:
        while True:
            try:
                x = pickle.load(fp)
                s.append(x[0])
                e.append(x[1])
                h.append(x[2])
                f.append(x[3])
            except EOFError:
                break

    return s, e, h, f

def get_loading(h, f):
    """Usage: list h, list f, bool loading_only

    Returns: list split_h, list split_f"""
    max_ind = h.index(max(h))
    split_h = h[:max_ind+1]
    split_f = f[:max_ind+1]

    return split_h, split_f

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
