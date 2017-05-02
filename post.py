import sys
import matplotlib.pyplot as plt

def get_fd_data(file_name):
    """Usage: string file_name
    
    Output: list displacements, list forces"""

    fd_data_file = open(file_name, "r")
    times, forces = _get_data(fd_data_file)
    displacements = [_get_displacement(i, 1.8, 0.7, 0.9) for i in times]
    
    if len(forces) != len(displacements):
        print("Forces and displacements don't have the same length")
        quit()

    return displacements, forces

def _open_file():
    """Adapted from CalcluliX examples scripts by Martin Kraska github.com/mkraska/CalculiX-Examples/"""

    if len(sys.argv)==1:
        print("No jobname given.")
        files=glob.glob("*.dat")
        if len(files)==1:
            print("Found", files[0])
            job=files[0]
        else:
            print("Available data files:")
            for f in files:
                print("  ", f)
            quit()
    if len(sys.argv)>1:
        print("Jobname:",sys.argv[1])
        job = sys.argv[1]+".dat"

    return open(job,"r")

def _get_data(file):
    times = []
    forces = []

    for row in file:
        temp = row.split()
        if len(temp) == 9:
            times.append(float(temp[-1]))
        if len(temp) == 3:
            forces.append(float(temp[1]) * -180)
         
    return times, forces    

def _get_displacement(time, amplitude, mid_time, end_disp):
    if time <= mid_time:    
        displacement = time * amplitude / mid_time
    elif time > mid_time:
        displacement = amplitude + (time - mid_time) * ((end_disp - amplitude)/(1 - mid_time))

    return displacement