import matplotlib.pyplot as plt
from data_processor import get_smooth_data
from post import get_data
from simulate import run_simulation
from scipy.optimize import minimize
from optimiser import get_plasticity, get_sum_squares

eval_counter = 0
ccx_params = {"mid_time": 0.6, "end_disp": 0.9, "amplitude": -1.547}

def main():
    solution = minimize(optimise_function, (532, 0.142), method='Nelder-Mead', tol = 1e-6)
    print(solution)
    h_exp, f_exp = get_smooth_data()
    disp, force = get_data(eval_counter-1, ccx_params)

    plt.plot(h_exp, f_exp)
    plt.plot(disp, force)
    plt.show()


def optimise_function(fh):
    global eval_counter

    file_num = eval_counter
    stresses, strains = get_plasticity(fh[0], fh[1])
    run_simulation(file_num, stresses, strains, ccx_params)
    disp, force = get_data(file_num, ccx_params)

    ssum = get_sum_squares(disp, force, 50)
    print("K: {},\tn: {},\tSum: {}".format(fh[0],fh[1], ssum))

    eval_counter += 1

    return ssum

if __name__ == "__main__":
    main()
