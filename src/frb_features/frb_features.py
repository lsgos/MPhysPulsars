"""
A utility to calculate summary statistics for FRB candidate files
"""
from __future__ import print_function
import os
import re
import argparse
from scipy.stats import skew, kurtosis
import frb_cand

CAND_FILE_RE = re.compile(r".*allcands_injected$")

class FRB(object):
    """
    read and represent a frb candidate file
    """
    def __init__(self, filename, n_bins=10):
        self.dat_dict = frb_cand.read_dict(filename)
        self.n_bins = n_bins
    def _extract_dm_mean(self):
        """returns the mean of the DM"""
        return self.dat_dict['dm'].mean()
    def _extract_dm_stdev(self):
        """returns the standard deviation of the dm"""
        return self.dat_dict['dm'].std()
    def _extract_dm_skew(self):
        """extract skew of the dm"""
        return skew(self.dat_dict['dm'])
    def _extract_dm_kurt(self):
        """extract kurtosis of the dm"""
        return kurtosis(self.dat_dict['dm'])
    def _extract_snr_mean(self):
        """return mean SNR of observation"""
        return self.dat_dict['snr'].mean()
    def feature_extractors(self):
        """return all feature extration methods in a list"""
        fns = []
        fns.append(self._extract_dm_mean)
        fns.append(self._extract_dm_stdev)
        fns.append(self._extract_dm_skew)
        fns.append(self._extract_dm_kurt)
        fns.append(self._extract_snr_mean)
        return fns

    def write_features(self):
        """return features as a string to write to a file"""
        feats = [feature() for feature in self.feature_extractors()]
        #add a placeholder for the class label: can be swapped by bash tools, e.g sed 's/?/1/g'
        feats.append("?")
        return " ".join([str(feat) for feat in feats])

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
        frb = FRB(name)
        print(frb.write_features())
    return

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
