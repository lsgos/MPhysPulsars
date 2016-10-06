"""
A program to calculate the mutual imformation of each feature in a dataset w.r.t the class labels. Expects a file in csv format, and outputs the scores as a table printed to the command line.

"""
from __future__ import division
import argparse
import numpy as np
import re
import os
import ipdb
class CSV:
    def read(self,path):
        """
        Converts numerical CSV data in to X,Y format for use by SciKit-Learn,
        where X is the data and Y the labels. Assumes the class label is the last
        item on each row (i.e. the last column of data).
        Does not work with text data.
        Parameters:
        path    -    the path to the CSV file to load.
        Returns:
        CSV data in X,Y form. X is a 2D np array, such that each row contains
        a unique data instance. Y is a column vector containing the class labels of
        each data item.
        """
        X=[]
        Y=[]
        with open(path,mode = 'U') as f:
            for line in f:
                if(line.strip() == ''):# Ignore empty lines.
                    continue
                # Split on comma since ARFF data is in CSV format.
                components = line.split(",")
                features = [float(x) for x in components[0:len(components)-1]]
                label    = [int(x)   for x in components[len(components)-1:len(components)]]
                X.append(features)
                Y.append(label)
        # Call to ravel below converts label column vector into 1D array.            
        return np.array(X),np.ravel(np.array(Y),order='C')

def read_label_file(filename):
    with open(filename,mode = 'U') as f:
        warn = False
        done = False
        for line in f:
            if line.strip() == '':
                continue
            if done == False:
                line = line.rstrip()
                labels = line.split(",") # read the first line only
                done = True
            else:
                warn = True
        if warn:
            print "Warning: labels file contained multiple readable lines. The label format should contain a single line only, eg."
            print "label1,label2,label3,label4"
        return labels

class MICalc:
    def __init__(self,X,Y,n_bins = None):
        if n_bins is None:
            n_bins = 10
        self.X = X
        self.Y = Y
        self.data_size = len(Y)
        if len(X) != self.data_size:
            raise RuntimeError("Data arrays not of equal size")

        self.bin_x(n_bins = n_bins)
        self.get_mutual_info()

    def bin_x(self, n_bins = 10):
        #discretize x into equal width bins
        _,attr = self.X.shape
        for i in range(attr):
            mini = np.amin(self.X[:,i])
            maxi = np.amax(self.X[:,i]) 
            bins = np.linspace(mini,maxi,n_bins+1)
            bins[-1] +=1
            #digitize sorts by a <= x < b, so this ensures the max is actually binned
            self.X[:,i] = np.digitize(self.X[:,i],bins)

    def get_probs(self,X):
        #generate a probability distribution of a feature/class X
        classes, counts = np.unique(X, return_counts = True)
        p = {}
        for i in range(len(classes)):
            p[classes[i]] = counts[i] / self.data_size
        return p


    def entropy(self,X):
        #define the shannon entropy H of a feature X
        H = 0
        p_x = self.get_probs(X)
        for x_i in p_x:
            H = H - p_x[x_i] * np.log2(p_x[x_i])
        return H

    def px_given_y(self,x,y):
        #calculate the conditional probability of x given y: P(x intersect y) / P(y)
        if len(x)!= len(y):
            raise RuntimeError("Array lengths must be equal")
        p_y = self.get_probs(y)
        classes_x = np.unique(x)
        p_x_cond_y = {}
        for i in xrange(len(classes_x)):
            p_x_cond_y[classes_x[i]] = {}
            for y_j in p_y:
                p_x_cond_y[classes_x[i]][y_j] = 0
        for i in xrange(len(x)):
            p_x_cond_y[x[i]][y[i]] +=1
        #now p_x_cond_y contains the frequencies: normalize it to the data size to make it a probability distribution, and divide by corresponding p_y to get p(x|y)
        for i in p_x_cond_y:
            for j in p_x_cond_y[i]:
                p_x_cond_y[i][j] = p_x_cond_y[i][j] / self.data_size
        for i in p_x_cond_y:
            for j in p_x_cond_y[i]:
                p_x_cond_y[i][j] = p_x_cond_y[i][j] / p_y[j]
        return p_x_cond_y

    def cond_entropy(self,x,y):
        #calculate the conditional entropy of a feature x given a feature y (the class)
        p_x_cond_y = self.px_given_y(x,y)
        p_y = self.get_probs(y)
        H = 0
        for y_i in p_y:
            for x_j in p_x_cond_y:
                if p_x_cond_y[x_j][y_i] == 0:
                    continue
                H = H - p_y[y_i] * p_x_cond_y[x_j][y_i] * np.log2(p_x_cond_y[x_j][y_i])
        return H

    def mutual_info(self,x,y):
        return self.entropy(x) - self.cond_entropy(x,y)

    def get_mutual_info(self):
        _,attr = self.X.shape
        self.MI = []
        for att in xrange(attr):
            self.MI.append( (att, self.mutual_info(self.X[:,att], self.Y)) )

    def printMutualInfo(self, labels = None):
        print "Feature           | Mutual Information"
        print "______________________________"
        self.MI.sort(key = lambda tup: tup[1], reverse = True)
        for feature,mi in self.MI:
            if labels is None:
                print("{:<18}| {:2.3f}".format(feature,mi))
            else:
                print("{:<18}| {:2.3f}".format(labels[feature],mi))




#----------begin main--------------#

allowed_filenames = re.compile(".*\.csv")

parser = argparse.ArgumentParser(description = 'Find the mutual information of features in a dataset')
parser.add_argument("filename", help = "The file containing the dataset. Must be in CSV format")
parser.add_argument("-b","--bins", type = int, help = "The number of bins to use when discretizing the features (default = 10)")
parser.add_argument("-q","--quiet", action = "store_true", help = "Whether to print the output to command line as a table")
parser.add_argument("-d", "--dest", help = "Filename of a destination file")
parser.add_argument("-f", "--format", help = "The output file format (default CSV)", default = "csv")
parser.add_argument("-l", "--labels", help = "An optional file containing labels for the features. Must be a single csv line in the same order as the features in the target file")

args = parser.parse_args()
if args.labels is not None:
    labels = read_label_file(args.labels)
else:
    labels = None

if allowed_filenames.match(args.filename) is None:
    print "Target file must be in .csv format"
    os.Exit(0)

csv = CSV()
x,y = csv.read(args.filename)
m = MICalc(x,y,n_bins = args.bins)
if not args.quiet:
    m.printMutualInfo(labels)
