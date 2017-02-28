"""
A utility to calculate summary statistics for FRB candidate files
"""
from __future__ import print_function
import os
import re
import argparse
from scipy.stats import skew, kurtosis
import frb_cand
import numpy as np

CAND_FILE_RE = re.compile(r".*allcands_injected$")

class FRB_file(object):
    """
    read and represent a frb candidate file
    """
    def __init__(self, filename, n_bins=10):
        data = frb_cand.read(filename)
        self.n_bins = n_bins
        self.fields = ["snr",
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
        self.n_n_window = 5
        data = data[data[:,0] != np.inf,:] #remove any datapoints with infinite snr
        self.dat = data
    def _calculate_dm(self):
        #returns an array of just the dm values
        return self.dat[:,self.fields.index("dm")]
    def _calculate_width(self):
        #box width = 2 ^ (filter_width), so the filter width should contain the same information, if not slightly more 
        return self.dat[:,self.fields.index("filter_width")]
    def _calculate_num_neighbours(self):
        """
        This is a heuristic me, mike, mat and alex have come up with: rfi often occurs in 'towers', so 
        for each file, record the number of points that occured within +/- a few seconds as a score
        """
        return np.apply_along_axis(self._get_neighbour, 1, self.dat)

    def _get_neighbour(self, datapoint):
        time_pos = datapoint[self.fields.index("time_of_peak")]
        time_low = time_pos - self.n_n_window
        time_hi = time_pos + self.n_n_window
        time_ind = self.fields.index("time_of_peak")
        return np.logical_and( [time_low < self.dat[:,time_ind]], [self.dat[:,time_ind] < time_hi]).astype(np.int).sum()
    def get_features(self):
        """
        returns the features as an iterator in string format, for easy writing to a file
        """
        feat_calc = re.compile("_calculate_.*")
        feature_calcs = [self._calculate_dm, self._calculate_width, self._calculate_num_neighbours] #this defines the order these will be called in 
        features = [feature() for feature in feature_calcs]
        for cand_feats in zip(*features):
            yield " ".join([str(feat) for feat in cand_feats])

def map_dirs(func, path):
    """
    applies func to every file in a directory and recurses on every subdir
    """
    for f in os.listdir(path):
        target = os.path.join(path, f)
        if os.path.isdir(target):
            map_dirs(func, target)
        else:
            func(target)
    return

def process_file(name):
    """process all files that match the filename regular expression"""
    if CAND_FILE_RE.match(name) is not None:
        frb = FRB_file(name)
        for feat in frb.get_features():
    return
            print(feat)

def main():
    """
    program entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="directory to search for files")
    args = parser.parse_args()
    map_dirs(process_file, args.directory)


if __name__ == "__main__":
    main()
