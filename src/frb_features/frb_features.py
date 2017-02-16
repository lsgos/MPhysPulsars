"""
A utility to calculate summary statistics for FRB candidate files
"""
import frb_cand
from scipy.stats import skew, kurtosis
import os

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
        return " ".join([str(feat) for feat in feats])

def map_directories(func, path):
    """
    applies func to every file in a directory and recurses on every subdir
    """
    for thing in os.listdir(path):
        if os.path.isdir(thing):
            map_directories(func, thing)
        else:
            func(thing)
    return


def main(filename):
    """
    program entry point
    """
    fcalc = FRB(filename)
    print fcalc.write_features()


if __name__ == "__main__":
    main("HR2258_injected_7p5sigma_cands")


