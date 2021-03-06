#!/usr/bin/env python

"""
A program to calculate the mutual information of each feature in a dataset w.r.t the class labels.
Expects a file in csv format, and outputs the scores as a table printed to the command line.

"""

from __future__ import division
import argparse
import numpy as np
import re
import os
import sys
from JACS_utils.ARFF import ARFF
import ipdb

csv_name = re.compile(".*\.csv")
arff_name = re.compile(".*\.arff")

INSTALLPATH = os.path.join('/', 'home', 'lewis', 'MPhysPulsars', 'src')

class CSV:
    def read(self, path):
        X = []
        Y = []
        with open(path, mode='U') as f:
            for line in f:
                if line.strip() == '':# Ignore empty lines.
                    continue
                # Split on comma since ARFF data is in CSV format.
                components = line.split(",")
                try:
                    features = [float(x) for x in components[0:len(components)-1]]
                except:
                    ipdb.set_trace()
                label = [int(x) for x in components[len(components)-1:len(components)]]
                X.append(features)
                Y.append(label)
        # Call to ravel below converts label column vector into 1D array.
        return np.array(X), np.ravel(np.array(Y), order='C')

def read_label_file(filename):
    with open(filename, mode='U') as f:
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
    def __init__(self, X, Y, n_bins=None):
        if n_bins is None:
            n_bins = 10
        self.X = X
        self.Y = Y
        self.data_size = len(Y)
        if len(X) != self.data_size:
            raise RuntimeError("Data arrays not of equal size")
        if n_bins > 0:
            self.bin_x(n_bins=n_bins)
        self.get_mutual_info()
        self.JMI_rank = self.joint_MI_rank()
    def bin_x(self, n_bins=10):
        #discretize x into equal width bins
        _, attr = self.X.shape
        for i in range(attr):
            mini = np.amin(self.X[:, i])
            maxi = np.amax(self.X[:, i])
            bins = np.linspace(mini, maxi, n_bins+1)
            bins[-1] += 1
            #digitize sorts by a <= x < b, so this ensures the max is actually binned
            self.X[:, i] = np.digitize(self.X[:, i], bins)

    def get_probs(self, X):
        #generate a probability distribution of a feature/class X
        classes, counts = np.unique(X, return_counts=True)
        p = {}
        for i in range(len(classes)):
            p[classes[i]] = counts[i] / self.data_size
        return p


    def entropy(self, X):
        #define the shannon entropy H of a feature X
        H = 0
        p_x = self.get_probs(X)
        for x_i in p_x:
            H = H - p_x[x_i] * np.log2(p_x[x_i])
        return H

    def px_joint_y(self, x, y):
        if len(x) != len(y):
            raise RuntimeError("Array lengths must be equal")
        classes_x = np.unique(x)
        classes_y = np.unique(y)
        p_x_joint_y = {}
        for i in xrange(len(classes_x)):
            p_x_joint_y[classes_x[i]] = {}
            for j in xrange(len(classes_y)):
                p_x_joint_y[classes_x[i]][classes_y[j]] = 0
        for i in xrange(len(x)):
            p_x_joint_y[x[i]][y[i]] += 1
        #now p_x_joint_y contains the frequencies:
        #normalize it to the data size to make it a probability distribution,
        #and divide by corresponding p_y to get p(x|y)


        for i in p_x_joint_y:
            for j in p_x_joint_y[i]:
                p_x_joint_y[i][j] = p_x_joint_y[i][j] / self.data_size
        return p_x_joint_y

    def px_given_y(self, x, y):
        #calculate the conditional probability of x given y: P(x intersect y) / P(y)
        p_y = self.get_probs(y)
        p_x_cond_y = self.px_joint_y(x, y)
        for i in p_x_cond_y:
            for j in p_x_cond_y[i]:
                p_x_cond_y[i][j] = p_x_cond_y[i][j] / p_y[j]
        return p_x_cond_y

    def joint_entropy(self, x, y):
        H = 0
        joint_x_y = self.px_joint_y(x, y)
        for xi in joint_x_y:
            for yj in joint_x_y[xi]:
                if joint_x_y[xi][yj] == 0:
                    continue
                H -= joint_x_y[xi][yj] * np.log2(joint_x_y[xi][yj])
        return H

    def cond_entropy(self, x, y):
        #calculate the conditional entropy of a feature x given a feature y (the class)
        p_x_cond_y = self.px_given_y(x, y)
        p_y = self.get_probs(y)
        H = 0
        for y_i in p_y:
            for x_j in p_x_cond_y:
                if p_x_cond_y[x_j][y_i] == 0:
                    continue
                H = H - p_y[y_i] * p_x_cond_y[x_j][y_i] * np.log2(p_x_cond_y[x_j][y_i])
        return H
    def cond_joint_entropy(self, x1, x2, y):
        #conditional entropy of x1 intersect x2 | y
        if len(x1) != len(x2) != len(y):
            raise RuntimeError("Array lengths not equal")
        cls_x1 = np.unique(x1)
        cls_x2 = np.unique(x2)
        cls_y = np.unique(y)
        p_y = self.get_probs(y)
        cond_p = {}
        for i in xrange(len(cls_x1)):
            cond_p[cls_x1[i]] = {}
            for j in xrange(len(cls_x2)):
                cond_p[cls_x1[i]][cls_x2[j]] = {}
                for k in xrange(len(cls_y)):
                    cond_p[cls_x1[i]][cls_x2[j]][cls_y[k]] = 0
        for i in xrange(len(x1)):
            cond_p[x1[i]][x2[i]][y[i]] += 1
        for i in cond_p:
            for j in cond_p[i]:
                for k in cond_p[i][j]:
                    cond_p[i][j][k] /= self.data_size
                    cond_p[i][j][k] /= p_y[k]
        #now we have p(x1 n x2 | y): calculate the entropy
        H = 0
        for y in p_y:
            for x1 in cond_p:
                for x2 in cond_p[x1]:
                    if cond_p[x1][x2][y] == 0:
                        continue
                    H -= p_y[y]*cond_p[x1][x2][y] * np.log2(cond_p[x1][x2][y])
        return H
    def joint_mutual_info(self, x1, x2, y):
        return self.joint_entropy(x1, x2) - self.cond_joint_entropy(x1, x2, y)

    def joint_MI_rank(self, max_features=None):
        #s and f are lists of the feature indicies to score.

        #initialize the algorithm with the highest MI scoring feature.
        if self.MI is None:
            self.get_mutual_info()
        S = [self.MI[0][0]]
        #selected features: start our algorithm with the attribute with highest MI
        F = set([self.MI[i][0] for i in range(1, len(self.MI))])
        #the remaining features to be sorted
        while len(F) > 0:
            if max_features is not None:
                if len(S) >= max_features:
                    break
            bestJMI = 0
            bestF = None
            for f in F:
                JMIScore = 0
                for s in S:
                    JMIScore += self.joint_mutual_info(self.X[:,  f],  self.X[:,  s],  self.Y)
                if JMIScore > bestJMI:
                    bestF = f
                    bestJMI = JMIScore
            S.append(bestF)
            F.remove(bestF)
        #S is now a list containing all features (or max_features if specified), ranked by JMI
        return S

    def mutual_info(self, x, y):
        return self.entropy(x) - self.cond_entropy(x, y)

    def get_mutual_info(self):
        _, attr = self.X.shape
        self.MI = []
        for att in xrange(attr):
            self.MI.append((att, self.mutual_info(self.X[:, att], self.Y)))
        self.MI.sort(key=lambda tup: tup[1], reverse=True) #sort in decending order


    def printMutualInfo(self, labels=None):
        if self.MI is None:
            self.get_mutual_info()

        print "Feature                           | Mutual Information | JMI Rank"

        print "__________________________________________________________________"
        _, attr = self.X.shape
        if labels is not None and attr != len(labels):
            print "error: number of labels suppiled not equal to number of attributes"
            sys.exit(0)
        for feature, mi in self.MI:
            if labels is None:
                print "{:<34}| {:2.6f}           | {:2d}".format(feature,
                                                                 mi,
                                                                 self.JMI_rank.index(feature)+1)
                #the +1 makes the ranks 1 indexed instead of zero indexed, to match Lyon et. al.
            else:
                print "{:<34}| {:2.6f}           | {:2d}".format(labels[feature],
                                                                 mi,
                                                                 self.JMI_rank.index(feature)+1)


    def writeToFile(self, filename, labels=None):
        _, attr = self.X.shape
        if labels is not None and attr != len(labels):
            print "error: number of labels suppiled not equal to number of attributes"
            sys.exit(0)

	#sort MI back to feature order
        self.MI.sort(key=lambda tup: tup[0])
        with open(filename, 'w') as f:
            for feature, mi in self.MI:
                if labels is None:
                    f.write("{},{},{}\n".format(feature, mi, self.JMI_rank.index(feature)+1))
                else:
                    f.write("{},{},{}\n".format(labels[feature],
                                                mi,
                                                self.JMI_rank.index(feature)+1))






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Find the mutual information of features in a dataset')
    parser.add_argument("filename", help = "The file containing the dataset. Must be in CSV or ARFF format")
    parser.add_argument("-b","--bins", type = int, help = "The number of bins to use when discretizing the features (default = 10). If the data has been discretized already, then setting this option to 0 will disable the binning.")
    parser.add_argument("-q","--quiet", action = "store_true", help = "Whether to print the output to command line as a table")
    parser.add_argument("-d", "--dest", help = "Filename of a destination file")
    parser.add_argument("-l", "--labels", help = "An optional file containing labels for the features. Must be a single csv line in the same order as the features in the target file. Alternatively, the options 'Lyon' or 'Thornton' will use stored label files for these feature sets.")

    args = parser.parse_args()
    if args.labels is not None:
        if args.labels == 'Lyon':
            args.labels = os.path.join(INSTALLPATH,'resources','lyonlabels.csv')
        elif args.labels == 'Thornton':
            args.labels = os.path.join(INSTALLPATH,'resources','thorntonlabels.csv')
        elif args.labels == 'Combined':
            args.labels = os.path.join(INSTALLPATH,'resources','combinedlabels.csv')
        elif args.labels == 'Period+Lyon':
            args.labels = os.path.join(INSTALLPATH,'resources','period+lyonlabels.csv')

        labels = read_label_file(args.labels)
    else:
        labels = None

    if csv_name.match(args.filename) is not None:
        csv = CSV()
        x,y = csv.read(args.filename)
    elif arff_name.match(args.filename) is not None:
        arff = ARFF()
        x,y = arff.read(args.filename)
    else:
        print "File must be in either arff or csv format"
        quit()
    m = MICalc(x,y,n_bins = args.bins)
    if not args.quiet:
        m.printMutualInfo(labels)
    if args.dest is not None:
        if allowed_filenames.match(args.dest) is None:
            args.dest = args.dest + '.csv'
        m.writeToFile(args.dest)
