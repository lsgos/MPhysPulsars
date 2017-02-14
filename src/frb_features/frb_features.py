import frb_cand
import numpy as np
from scipy.stats import skew, kurtosis

class FeatureCalculator(object):
    """
    extract features from an FRB observation
    """
    def __init__(self, filename, n_bins=10):
        self.dat_dict = frb_cand.read_dict(filename)
        self.n_bins = 10
    def get_mean(self, field):
        return self.dat_dict[field].mean()
    def get_stdev(self, field):
        return self.dat_dict[field].std()
    def get_skew(self, field):
        return skew(self.dat_dict[field])
    def get_kurt(self, field):
        return kurtosis(self.dat_dict[field])


def main():
    """
    hi
    """
    print "hi"



if __name__ == "__main__":
    main()


