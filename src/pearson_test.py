"""
Calculate the stablility score for a feature selection algorithm, as 
described in Noguiera and Brown, "Measuring the Stability of Feature 
Selection
"""


from __future__ import print_function
import argparse
import tempfile
import subprocess
import numpy as np
from sklearn.model_selection import StratifiedKFold
from scipy.stats import pearsonr

MICALC_LOCATION = "/home/lewis/MPhysPulsars/src/MICalc++/micalc"
SUPPORTED_ALGORITHMS = ["jmi","mi"]
S_ALGS_LONG = ["Joint Mutual Information", "Mutual Information"]

def pearson_stability_score(A):
    """
    Calculate the pearson stability score for the matrix A, 
    as described in "Measuring the Stability of Feature Selection"
    by Sarah Nogueira and Gavin Brown (UoM). The stablility score 
    is given by E[ R(s_i,s_j ) | i,j in M, i /= j] where s_i are the features 
    selected from a possible set in a particular run, and there were 
    M runs performed. The s_i are encoded in the form of a vector with 
    a length equal to the number of possible features which is 1 if the 
    feature with that index was selected and 0 otherwise. For example, 
    if there were 8 possible features and 0,3 and 4 were selected, s 
    for that run would be [1,0,0,1,1,0,0,0]. This function expects a 
    matrix A where A = [s_1,s_2 ... s_M].
    """
    M = A.shape[0]
    sum = 0.0
    for i in xrange(M):
        for j in xrange(M):
            if i != j: 
                pearson,_ = pearsonr(A[i],A[j])
                sum += pearson
    phi = (M * (M - 1)) ** (-1) * sum 
    return phi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find the mutual information of features in a dataset')
    parser.add_argument("filename",help="The file containing the dataset. Must be in arff format")
    parser.add_argument("-k", "--num-splits", type = int, help = "number of splits to use when calculating variance", default=10)
    parser.add_argument("-n", "--num-feats", type = int, help = "number of features to select", default = 4)
    parser.add_argument("-a", "--algorithm", help = "Which feature selection algorithm to evaluate: options: [jmi,mi]", default = "mi")
    args = parser.parse_args()

    if not(args.algorithm in SUPPORTED_ALGORITHMS):
        print("Unknown algorithm option {}".format(args.algorithm))
        print("Supported Algorithms: ")
        for alg,long_alg in zip(SUPPORTED_ALGORITHMS,S_ALGS_LONG): 
            print("{} ({})".format(alg, long_alg))
        quit()
    
    with open(args.filename) as f:
        data = np.array([[int(field) for field in line.split(' ')]
                         for line in [line.strip() for line in f]])
        
    features = data[:,0:-1]
    num_features = features.shape[1]
    labels = data[:,-1]
    A = np.zeros([args.num_splits,num_features])

    skf = StratifiedKFold(n_splits=args.num_splits, shuffle=True)
    
    for run,(_,sub_inds) in enumerate(skf.split(features,labels)):
        sub_feats = features[sub_inds]
        sub_labs  = labels[sub_inds]
        with open('tmp.dat','w') as input_f:
                for i in xrange(sub_labs.shape[0]):
                    line = list(sub_feats[i])
                    line.append(sub_labs[i])
                    print(" ".join([str(field) for field in line]), file = input_f)
        output = subprocess.check_output([MICALC_LOCATION,
                                      '-k', str(args.num_feats),
                                      args.algorithm,
                                      'tmp.dat'])
        selected_features = [int(line.split(' ')[0]) for line in output.split('\n') if line != ""]
        
        A[run][selected_features] = 1
    subprocess.call(["rm", "tmp.dat"]) #get rid of tempfile
    print("Pearson's correlation score: {}".format(pearson_stability_score(A)))
