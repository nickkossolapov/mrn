from string import Template

def make_inp(file_name, stresses, strains, params):
    """Usage: string file_name, list stresses, list strains, dict params

    params requires a dictionary containing:
    "mid_time": float, "end_disp": float, "amplitude": float"""

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


def _parse_p_vals(stresses, strains, file_name):
    if len(stresses) != len(strains):
        print("Stresses and strains for {} don't have the same length".format(file_name))
        quit()

    p_string = []
    for i in range(len(stresses)):
        p_string.append('{}, {}'.format(stresses[i], strains[i]))
        p_string.append('\n')

    p_string.pop()

    return ''.join(p_string)
