#! /usr/bin/env python
"""
Marks a certain subset of pulsars as 'special', and records the recall of a classifier
on that subset against the mean recall, and it's significance. This is in order to
qualify whether the significance of the difference in recall on millisecond pulsars
is really meaningful
"""

import subprocess
import tempfile
import argparse
import ipdb

import os

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
from matplotlib import patches as mpatches

clf_list = ["DT", "MLP", "NB","SVM","RF","AdB"]

def parse_evaluation_line(line):
    """parse the output of the evaluate_classifier program"""
    
    line = line.strip()
    fields =  [float(n) for n in line.split(' ')] if line != "" else None
    return fields


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Evaluate the significance of the performance \
    difference as a function of the millisecond pulsar cutoff definition")
    parser.add_argument("--MPhysPath",help = "The system path to the MPhysPulsars root", default = '.')
    parser.add_argument("--data",help = "Dataset to analyse. Must be in arff format")
    parser.add_argument("--plot", help = "Precomputed data to plot")
    parser.add_argument("--n_jobs", help = "Number of cores to use", default = "4")
    args = parser.parse_args()

    assert args.data is not None or args.plot is not None,"One of --data or --plot must be provided"

    SRC = os.path.join(args.MPhysPath, 'src')

    #sanity check: check we have the required files
    try:
        assert(os.path.exists(os.path.join(SRC,"arff_msp_comment.py")))
        assert(os.path.exists(os.path.join(SRC,"evaluate_classifier.py")))
    except AssertionError as e:
        print "Cannot find required python source files: are you running this file in the correct location? Consider setting the MPhysPath option manually"
        quit()
    try:
        assert(os.path.exists(args.data))
    except:
        try:
            assert(os.path.exists(args.plot))
        except:
            print "Cannot find required data file, exiting..."
            quit()

    #iterate through the range of period cutoffs
    cutoffs = range(20,500,5)
    d = []
    if args.plot is None:
        for cutoff in cutoffs:

            with tempfile.NamedTemporaryFile() as f:
            #comment out pulsars below cutoff, writing the output to a temporary file
                subprocess.check_call(["python",os.path.join(SRC,"arff_msp_comment.py"),"-p", repr(cutoff),args.data], stdout = f)
            #get a simplified version of the output file
                output = subprocess.check_output(["python", os.path.join(SRC,"evaluate_classifier.py"),"--show_msp_results","--simple_output","-j",args.n_jobs,f.name])
                for line in output.split('\n'):
                    l = None
                    if line.strip() != "":
                        l = parse_evaluation_line(line)
                        d.append(l)

    else:
        with open(args.plot,'r') as f:
            for line in f:
                l = parse_evaluation_line(line)
    
                d.append(l)

    
    datafields = zip(*d)
    num_lines = len(datafields)
    cols = [plt.cm.Set1(x) for x in np.linspace(0,1,num_lines)]

    plt.figure()
    
    for c,dat in zip(cols, [datafields[i:i+4] for i in xrange(0,len(datafields),4)]):
        
        r,rstd,m,mstd = dat
        plt.errorbar(cutoffs, r, yerr = rstd, color = c, linestyle = '--')
        plt.errorbar(cutoffs, m, yerr = mstd, color = c, linestyle = '-')
        
        
    plt.xlabel('Period Cutoff')
    plt.ylabel('Recall')
    
    dash_line = mlines.Line2D([],[], color = 'black', linestyle = '--', label = 'Recall on all data')
    solid_line = mlines.Line2D([],[], color = 'black', linestyle = '-', label = 'Recall below cutoff')

    predleg = [mpatches.Patch(color = c, label = clfname) 
               for c,clfname in zip(cols,clf_list)]
    
    plt.legend(handles=[dash_line,solid_line]+predleg,
               loc=4)



    #write to a file to save running the whole program again
    try:
        with open("classifier_eval_results.dat",'w') as f:
            for l in d:
                f.write(" ".join([repr(i) for i in l]) + "\n")
    except:
        print("failed to write to file")

    plt.show()
