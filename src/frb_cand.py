"""
A numpy utitlity to parse the frb candidate files into a numpy
array.
"""

import numpy as np

def read(path):
    """
    takes a filename as an argument, and returns the contents of the file as a np array
    Contents of the file is as follows:

    SNR of the peak,
    time sample of the peak,
    time in seconds of the peak,
    filter width (multiple of time samples),
    DM index, DM, grouped candidates,
    starting time sample of the group,
    ending time sample of the group,
    number of beams,
    beam mask,
    primary beam,
    maximum SNR,
    beam number
    """
    with open(path) as f:
        return np.array([[float(field) for field in line.split('\t')]
                         for line in [line.strip() for line in f]])
                         