import argparse
import numpy as np
from sklearn.model_selection import StratifiedKFold
from scipy import stats as st
import MICalc
#from JACS_utils import ARFF
#import pdb;pdb.set_trace()

#args = parser.parse_args()
#arff_reader = ARFF.ARFF()
#data, labels, _ = arff_reader.read(args.arff)
#data_train = data[:, range(1, 9)]



skf = StratifiedKFold(n_splits=5)

m = MICalc.MICalc(x,y,n_bins = args.bins)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Find the mutual information of features in a dataset')
    parser.add_argument("filename", help = "The file containing the dataset. Must be in CSV or ARFF format")
    parser.add_argument("-b","--bins", type = int, help = "The number of bins to use when discretizing the features (default = 10). If the data has been discretized already, then setting this option to 0 will disable the binning.")

    args = parser.parse_args()

x = [1,2,5,9]
y = [3,5,4,6]

var1 = np.array(x)
var2 = np.array(y)

pcc, ttest_val = st.pearsonr(var1,var2)
print pcc
print ttest_val
