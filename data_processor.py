import csv
import scipy.signal as sgn

def get_surface():
    """Usage: No inputs

    Returns: list r, list h"""
    with open('raw_data/surface.csv', 'r') as datafile:
        reader = csv.reader(datafile, delimiter=',')
        r = []
        h = []

        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue

            r.append(float(row[0]))
            h.append(float(row[1]))

    return r[::-1], h[::-1]

def get_smooth_surface():
    """Usage: No inputs

    Returns: list r_smooth, list h_smooth"""
    r, h = get_surface()
    r_smooth = sgn.savgol_filter(r, 21, 3)
    h_smooth = sgn.savgol_filter(h, 21, 3)

    return r_smooth, h_smooth

def get_smooth_data(scale=1.0834):
    """Usage: float scale

    Returns: list h_smooth, list f"""
    lo_f, lo_h, un_f, un_h = _get_split_data(scale)

    lohat = sgn.savgol_filter(lo_h, 51, 3)
    unhat = sgn.savgol_filter(un_h, 51, 3)

    h_smooth = list(lohat) + list(unhat)
    f = list(lo_f) + list(un_f)

    return h_smooth, f

def _get_split_data(scale):
    split_data = [[[],[]], [[],[]]]
    files = [open("raw_data/av_loading.csv"), open("raw_data/av_unloading.csv")]
    try:
        for i in range(2):
            reader = csv.reader(files[i], delimiter=',')
            for row in reader:
                split_data[i][0].append(float(row[0])*1000)
                split_data[i][1].append(float(row[1])*scale+0.105)
    finally:
        for file in files:
            file.close()

    return split_data[0][0], split_data[0][1], split_data[1][0], split_data[1][1]

def get_raw_data():
    """Usage: No inputs

    Returns: list h, list f"""
    with open('raw_data/data.csv', 'r') as datafile:
        reader = csv.reader(datafile, delimiter=',')
        av_h = []
        av_f = []

        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue

            av_h.append(float(row[-1])+0.1)
            av_f.append(float(row[-2])*1000)

    return av_h, av_f

def get_all_data():
    """Usage: No inputs

    Returns: list h, list f"""
    datafile = open('raw_data/data2.csv', 'r')

    reader = csv.reader(datafile, delimiter=',')

    f, h = [[], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], []]

    first_row = True
    for row in reader:
        if first_row:
            first_row = False
            continue

        for i in range(8):
            if row[2*i] != '' and row[2*i+1] != 0:
                f[i].append(float(row[2*i]))
                h[i].append(float(row[2*i+1]))

    return h, f
