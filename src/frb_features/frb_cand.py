"""
A numpy utitlity to parse the frb candidate files into a numpy array.
"""

import numpy as np
from math import isinf
min_dm = 10

def read(path):
    """
    takes a filename as an argument, and returns the contents of the file as a np array
    Contents of the file is as follows:

    SNR of the peak,
    time sample of the peak,
    time in seconds of the peak,
    filter width (multiple of time samples),
    DM index,
    DM,
    grouped candidates,
    starting time sample of the group,
    ending time sample of the group,
    number of beams,
    beam mask,
    primary beam,
    maximum SNR,
    beam number
    """
    with open(path) as f:
        try:
            field_list = [[float(field) for field in line.strip().split(' ') if field != ""] for line in f]
        except:
            import pdb; pdb.set_trace()
        all_data = np.array( field_list ) #remove infinite SNR candidates caused by RFI straight away, as they will screw up the maths
        return all_data[:,0:-1], all_data[:,-1].astype(np.int) #data,class labels

def read_dict(path):
    """
    return the data as a dict of labelled numpy arrays, in case this is more convenient
    """
    data, labels = read(path)
    data_dict = {}
    fields = ["snr",
              "time_sample",
              "time_of_peak",
              "filter_width",
              "dm_index",
              "dm",
              "grouped_cands",
              "start_time_group",
              "end_time_group",
              "no_beams",
              "beam_mask",
              "primary_beam",
              "max_snr",
              "beam_num"]
    for ind, field in enumerate(fields):
        data_dict[field] = data[:, ind]
    return data_dict, labels

