import numpy as np

def get_plasticity(n):
    """Usage: list params

    Returns: list stresses, list strains"""

    strains = np.linspace(0, 1.5, 30)
    #using S_t(n) = K(n) * E_p ^ n by Taljat et al. (2009)
    E = 7e4
    Y = 255
    K = Y/((Y/E + 0.002)**n)

    stresses = K * (strains ** n)
    stresses[0] = Y

    return list(stresses), list(strains)
