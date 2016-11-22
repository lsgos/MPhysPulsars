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

import os


from matplotlib import pyplot as plt

def parse_evaluation_line(line):
    """parse the output of the evaluate_classifier program"""
    try:
        line = line.strip()
        list =  [float(n) for n in line.split(' ')] if line != "" else None
    except:
        ipdb.set_trace()
    return list
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Evaluate the significance of the performance \
    difference as a function of the millisecond pulsar cutoff definition")
    parser.add_argument("--MPhysPath",help = "The system path to the MPhysPulsars root", default = '.')
    parser.add_argument("data",help = "Dataset to analyse. Must be in arff format")
    parser.add_argument("--n_jobs", help = "Number of cores to use")
    args = parser.parse_args()

    SRC = os.path.join(args.MPhysPath, 'src')

    #sanity check: check we have the required files
    try:
        assert(os.path.exists(os.path.join(SRC,"arff_msp_comment.py")))
        assert(os.path.exists(os.path.join(SRC,"evaluate_classifier.py")))
    except AssertionError as e:
        print "Cannot find required python source files: are you running this file in the correct location? Consider setting the MPhysPath option manually"


    #iterate through the range of period cutoffs

    cutoffs = [2 * i for i in range(1,100)]


    d = []
    for cutoff in cutoffs:

        with tempfile.NamedTemporaryFile() as f:
            #comment out pulsars below cutoff, writing the output to a temporary file
            subprocess.check_call(["python",os.path.join(SRC,"arff_msp_comment.py"),"-p", repr(cutoff),args.data], stdout = f)
            #get a simplified version of the output file
            output = subprocess.check_output(["python", os.path.join(SRC,"evaluate_classifier.py"),"--show_msp_results","--simple_output","-j",args.n_jobs,f.name])
            for line in output.split('\n'):
                l = parse_evaluation_line(line)
                if l is not None:
                    d.append(l)

    datafields = zip(*d)

    plt.figure()
    for d in datafields:
        plt.plot(cutoffs,datafields)
    plt.show()
