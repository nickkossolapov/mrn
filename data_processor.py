import csv
import scipy.signal as sgn

def get_smooth_data(scale):
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
    files = [open("av_loading.csv"), open("av_unloading.csv")]
    for i in range(2):
        reader = csv.reader(files[i], delimiter=',')
        for row in reader:
            split_data[i][0].append(float(row[0])*1000)
            split_data[i][1].append(float(row[1])*scale+0.1)

    return split_data[0][0], split_data[0][1], split_data[1][0], split_data[1][1]

def get_raw_data():
    """Usage: No inputs

    Returns: list h, list f"""
    datafile = open('data.csv', 'r')
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

    datafile.close()
    return av_h, av_f
