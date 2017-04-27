#!/usr/bin/env python

"""
Search a dataset in ARFF format for outliers using the isolation forest algorithm, printing the
filenames of the most anomlous results
"""

import numpy as np
import argparse

from sklearn.ensemble import IsolationForest

def read(path):
    """
    Converts numerical ARFF data in to X,Y format for use by SciKit-Learn,
    where X is the data and Y the labels. Assumes class label is the last
    item on each row (i.e. the last column of data).

    Does not work with text data.

    Parameters:

    path    -    the path to the ARFF file to load.

    Returns:

    ARFF data in X,Y form. X is a 2D np array, such that each row contains
    a unique data instance. Y is a column vector containing the class labels of
    each data item.
    """

    X=[]
    comments = []
    with open(path) as f:
        for line in f:

            # Comments and attribute lines should be ignored.
            if(line.startswith("@") or line.startswith("%")):
                continue
            elif(line.strip() == ''):# Ignore empty lines.
                continue
            else:

                # Extract up to comment character, in case there is an end of line comment.
                if('%' in line):
                    text = line[0:line.index('%')]
                    comment = line[line.index('%'):]
                else:
                    text = line

                # Split on comma since ARFF data is in CSV format.
                components = [x for x in text.split(",") if x != '']
               
                features = [float(x) for x in components[0:len(components)-1]]

                X.append(features)
                comments.append(comment)
    # Call to ravel below converts label column vector into 1D array.
    return np.array(X), np.array(comments)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("filename", help = "file to process")
	parser.add_argument("-n","--number", type = int, default = 100,
						help="Number of results to return (n most anomalous)")
	
	args = parser.parse_args()
	X,comments =read(args.filename)
	
	#remove period
	X = X[:,1:] #features of the dataset
	
	
	ifst = IsolationForest()
	
	ifst.fit(X)
	
	
	anomaly_scores = ifst.decision_function(X) 
	
	sort_inds = np.argsort(anomaly_scores)
	
	#the decision function is low when x is an anomaly:
	#therefore return the n lowest scores
	
	chosen_inds = sort_inds[:args.number]
	
	for c in comments[chosen_inds]:
		print c


if __name__ == "__main__":
	main()