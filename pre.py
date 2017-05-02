from string import Template

def make_inp(num, params):
    """Usage: string num, list stresses, list strains
    
    params requires a dictionary containing:
    float mid_time, float end_time, float amplitude"""

    plastic = _parse_p_vals(stresses, strains)
    filein = open("inp_template.txt", 'r')
    src = Template(filein.read())

    d = {'plastic': plastic, 'mid_time': mid_time, 'end_disp': end_disp, 'amplitude': amplitude}
    result = src.substitute(d)

    fileout = open('mrn{}.inp'.format(num), 'w')
    fileout.write(result)

    filein.close()
    fileout.close()
    return 1


def _parse_p_vals(stresses, strains):
    if (len(stresses) != len(strains)):
        print("Stresses and strains don't have the same length")
        quit()

    p_string = []
    for i in range(len(stresses)):
        p_string.append('{}, {}'.format(stresses[i], strains[i]))
        p_string.append('\n')
    
    p_string.pop()
    
    return ''.join(p_string)