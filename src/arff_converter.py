"""
Convert a plain data file to the arff format so we can use Notre Dame's Hellinger tree 
implementation 
"""

import argparse 
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("file", help ="file to convert")

    args = parser.parse_args()
    with open(args.file) as f: 
        field_list = [[float(field) for field in line.strip().split(' ') if field != ""] for line in f]
    data = np.array(field_list)[:,:-1]
    classes = np.array(field_list)[:,-1].astype(np.int)

    data_size = data.shape[1]
    #write header 
    print "@relation data"
    for i in xrange(data_size):
        print "@attribute Feature_{} numeric".format(i)
    print "@attribute class {0,1}"
    print "@data"

    #import ipdb; ipdb.set_trace()
    #write data
    for dat, cat in zip(data, classes):
        dat_line = list(dat)
        dat_line.append(cat)
        line = ",".join(map(str, dat_line))
        print line