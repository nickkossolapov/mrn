import numpy as np

def get_plasticity(n):
    """Usage: list params
    
    Returns: list stresses, list strains"""
    testS = [250, 350, 400, 450, 500]
    testE = [0.0, 0.1, 0.2, 0.4, 2.5]

    strains = np.linspace(0, 1.5, 30)
    #using S_t(n) = K(n) * E_p ^ n by Taljat et al. (2009)
    E = 7e4
    Y = 255
    K = Y/((Y/E + 0.002)**n)

    stresses = K * (strains ** n) + Y

    return list(stresses), list(strains)
