"""
A program to calculate the mutual imformation of each feature in a dataset w.r.t the class labels. Expects a file in csv format, and outputs the scores as a table printed to the command line.

"""
from __future__ import division
import numpy as np
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
        CSV data in X,Y form. X is a 2D numpy array, such that each row contains
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
        return numpy.array(X),numpy.ravel(numpy.array(Y),order='C')

class MICalc:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        self.data_size = len(Y)
        if len(X) != self.data_size:
            raise RuntimeError("Data arrays not of equal size")
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

    def get_probs(self):
        #count the number of occurences of each class and return a probability distribution as a dict
        classes, counts = np.unique(self.Y, return_counts = True)
        self.p_y = {}
        for i in range(len(classes)):
            self.p_y[classes[i]] = counts[i] / self.data_size


        




