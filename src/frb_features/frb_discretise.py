"""
Script to discretize an FRB data file ready for feature selection
"""

import numpy as np
import argparse
import re
import fileinput

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = "Discretise fields in a .dat file and output to a new .dat file")
   
    parser.add_argument("--binNumb","-b", help = "number of bins used for discretisation", default = 10)

    #this is to allow this program to be used in pipes like a standard unix tool
    args, others = parser.parse_known_args()
    if len(others) > 0:
    	args.file = others[0] 
    else:
    	args.file = None #read from stdin
    


    
    discr_lines = []

    try:
        field_list = [[float(field) for field in line.strip().split(' ') if field != ""] for line in fileinput.input(args.file)]
    except:
        import pdb; pdb.set_trace()
    all_data = np.array( field_list ) #remove infinite SNR candidates caused by RFI straight away, as they will screw up the maths
    #disc_arr = all_data[:].astype(np.int) #data,class labels
    classes = (all_data[:,-1]).astype(np.int)
    all_data = all_data[:,0:-1]
    _, rows = all_data.shape
    for i in xrange(rows):
        row = all_data[:,i]
        bins = np.linspace(row.min(), row.max(), args.binNumb)
        digitized_row = np.digitize (all_data[:,i], bins)
        discr_lines.append(digitized_row)
    discr_lines.append(classes)
    final=zip(*discr_lines)
    for line in final:
        print " ".join([str(f) for f in line])

