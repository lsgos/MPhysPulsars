"""
Train a classifier on a dataset, and then process an arff file of candidates
using the lyon features. Expects the file locations of the original files to 
be appended to the arff files, as with the --meta flag of PulsarFeatureLab

Expect a very large candidate file (~300 GB of raw data from HTRU, so this 
processes the file in lazy batches using a generator, 
"""
from __future__ import print_function
import os
import argparse
import multiprocessing
from itertools import izip, repeat
import numpy as np

from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from JACS_utils.ARFF import ARFF

class ArffBatch(object):
    """
    Reads an arff file in batches, providing the features, class labels and paths of 
    data files in batches of N at a time

    """
    def __init__(self,path):
        self.path = path
        self.current_pos = None
        self.running = True
    def get_batch(self,N):
        X=[]
        Y=[]
        paths = []
        with open(self.path) as f:
            if self.current_pos is not None:
                f.seek(self.current_pos)
            read = 0
            while (read < N):
                line = f.readline()
                # Comments and attribute lines should be ignored.
                if(line.startswith("@") or line.startswith("%")):
                    continue
                elif(line == ''):# EOF reached
                    self.running = False
                    break
                elif(line.strip() == ''): #empty lines
                    continue
                else:
                    line = line.strip()
                    # Extract up to comment character, in case there is an end of line comment.
                    if('%' in line):
                        text = line[0:line.index('%')]
                        comment = line[line.index('%'):]
                        paths.append(comment)
                    else:
                        text = line
                        paths.append("unknown, no path found")
                    # Split on comma since ARFF data is in CSV format.
                    components = text.split(",")

                    features = [float(x) for x in components[0:len(components)-1]]
                    label    = [int(x)   for x in components[len(components)-1:len(components)]]
                    X.append(features)
                    Y.append(label)
                    read += 1
                self.current_pos = f.tell()
        return np.array(X)[:,1:],paths 
    def is_open(self):
        return self.running
    def get_batches(self,N):
        """return the data as a lazy generator, to avoid loading the entire file at once"""
        while self.running:
            yield self.get_batch(N)



def compute_predictions( (classifier, (X, paths)) ):
    """
    Classify X using classifier, returning the paths of the 
    candidates that were classed as pulsars. Takes a slightly 
    odd argument form to support using it in map
    """
    predictions = classifier.predict(X)
    results = [path for (prediction,path) in zip(list(predictions.astype(np.bool)), paths ) if prediction == 1]
    return results

def main():
    parser = argparse.ArgumentParser(description = "A program to find promising candididates in pulsar data")
    parser.add_argument("-t", "--train", help = "Training data to use (arff format)")
    parser.add_argument("-d", "--dataset", help = "Dataset to evaluate (arff format)")
    parser.add_argument("-b", "--batch_size", type = int, help = "Number of points to process at a time", default = 10000)
    parser.add_argument("-o", "--output_dir", help="Directory to write output files to", default = "output_batches")
    args = parser.parse_args()

    arff = ARFF()
    assert(os.path.exists(args.dataset)),"Cannot find dataset file, run with --help for help"
    assert(os.path.exists(args.train)), "Cannot find training file"
    try:
        train_x, train_y, _  = arff.read(args.train)
        #remove period 
        train_x = train_x[:,1:] #TODO change this before you use on Lyon only data
    except:
        print("Cannot find training data file, or none provided: type --help for help")
        quit()
    
    #train a classifier: support vector machine had the best in sample performance, so start with that
    clf = Pipeline([('scaler', StandardScaler()), ('svc',SVC(class_weight ='balanced'))])
    #clf = DecisionTreeClassifier()
    clf.fit(train_x,train_y) 


    #this dispatches the batches of data to the worker pool, returning the results in an 
    #arbitrary order. izip is used to keep the evaluation of the data batches lazy, so we 
    #avoid reading the entire file into memory as a contigous numpy array, which would likely 
    #either crash or be very slow. The worker pool can handle the batches in parallel, speeding 
    #everything up
    data = ArffBatch(args.dataset)
    data_generator = data.get_batches(args.batch_size)
    #spawn a pool of workers as large as the number of cores
    workers = multiprocessing.Pool(multiprocessing.cpu_count())
    batch_number = 0
    if not (os.path.isdir(args.output_dir)):
        os.mkdir(args.output_dir)

    for result in workers.imap_unordered(compute_predictions, izip(repeat(clf), data_generator)):
        #compute the results in an arbitrary order, writing them to files 

        fname = os.path.join(args.output_dir,"batch_" + str(batch_number))
        batch_number += 1
        with open(fname,'w') as f:
            for res in result:
                print(res,file = f)
            print("Processed batch {}".format( batch_number) )
    

if __name__ == "__main__":
    main()
