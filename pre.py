import logging
from string import Template

log = logging.getLogger(__name__)

def make_inp(file_name, stresses, strains, params, friction=0):
    """Usage: string file_name, list stresses, list strains, dict params, float friction

    params requires a dictionary containing:
    "mid_time": float, "end_disp": float, "amplitude": float, "spring_costant": float

    Returns: no returns"""

    if friction != 0:
        params['friction'] = _get_friction_string(friction, params)
    else:
        params['friction'] = ''

    plastic = _parse_p_vals(stresses, strains, file_name)
    filein = open("inp_template.txt", 'r')
    src = Template(filein.read())
    params['plastic'] = plastic
    result = src.substitute(params)

    fileout = open(file_name, 'w')
    fileout.write(result)

    filein.close()
    fileout.close()

    return 1

def _get_friction_string(mu, params):
    card = "*FRICTION\n{}, {}".format(mu, params['spring_constant']/10)

    return card

def _parse_p_vals(stresses, strains, file_name):
    if len(stresses) != len(strains):
        log.error("Stresses and strains for %s don't have the same length", file_name)
        quit()

    p_string = []
    for i in range(len(stresses)):
        p_string.append('{}, {}'.format(stresses[i], strains[i]))
        p_string.append('\n')

    p_string.pop()

    return ''.join(p_string)
