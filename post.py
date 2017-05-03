import sys
import matplotlib.pyplot as plt

def get_data(file_name):
    """Usage: string file_name
    
    Returns: list displacements, list forces"""
    name = file_name[:-4] + ".dat"

    try:
        fd_data_file = open("./data/" + name, "r")
    except Exception:
        print("Cannot open {}.".format(file_name)) 
        quit()

    times, forces = _parse_data(fd_data_file)
    disps = [_get_disp(i, 1.8, 0.7, 0.9) for i in times]
    
    if len(forces) != len(disps):
        print("Forces and displacements don't have the same length in {}.".format(file_name))
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