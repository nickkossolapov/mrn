import sys
import matplotlib.pyplot as plt

def main():
    fd_data = open("mrn.dat", "r")
    times, forces = get_data(fd_data)
    displacements = [get_displacement(i, 1.8, 0.7, 0.9) for i in times]
    plt.plot(displacements, forces)
    plt.show()

def open_file():
    """Reads system arguments and parses them appropriately. 
    
    Adapted from CalcluliX examples scripts by Martin Kraska github.com/mkraska/CalculiX-Examples/"""

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

def get_data(file):
    """Returns the force data and the displacement data in the input file.
    
    Multiplies forces in files by -180, as per CalculiX axisymmetric elements"""

    times = []
    forces = []

    for row in file:
        temp = row.split()
        if len(temp) == 9:
            times.append(float(temp[-1]))
        if len(temp) == 3:
            forces.append(float(temp[1]) * -180)
         
    return times, forces    

def get_displacement(time, amplitude, mid_time, end_disp):
    """Returns a displacement at a set time for a 1 second interval."""

    if time <= mid_time:    
        displacement = time * amplitude / mid_time
    elif time > mid_time:
        displacement = amplitude + (time - mid_time) * ((end_disp - amplitude)/(1 - mid_time))

    return displacement

if __name__ == "__main__":
    main()