import logging
from simulate import make_file_name

log = logging.getLogger(__name__)

def get_data(file_name, params):
    """Usage: int file_name, dict params

    params requires a dictionary containing:
    "mid_time": float, "end_disp": float, "amplitude": float

    Returns: list displacements, list forces"""
    file_name = make_file_name(file_name)
    name = file_name[:-4] + ".dat"
    fd_data_file = open("./data/" + name, "r")

    amplitude = -params["amplitude"]
    mid_time = params["mid_time"]
    end_disp = params["end_disp"]

    times, forces = _parse_data(fd_data_file)
    disps = [_get_disp(i, amplitude, mid_time, end_disp) for i in times]

    if len(forces) != len(disps):
        log.info("Forces and displacements don't have the same length in %s.", file_name)
        quit()

    return disps, forces

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
        disp = time * amplitude / mid_time
    elif time > mid_time:
        disp = amplitude + (time - mid_time) * ((end_disp - amplitude)/(1 - mid_time))

    return disp
    