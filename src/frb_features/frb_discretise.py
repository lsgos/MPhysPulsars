"""
Script to discretize an FRB data file ready for feature selection
"""

import numpy as np
import argparse
import re

dat_re = re.compile(".*\.dat")

"""def make_dat_name(name):
    if dat_re.match(name) is None:
        name = name + '.dat'
    return name"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = "Discretise fields in a .dat file and output to a new .dat file")
    parser.add_argument("file", help = "the file to be discretised (must be in .dat format)")
    parser.add_argument("--binNumb","-b", help = "number of bins used for discretisation", default = 10)

    args = parser.parse_args()

    if dat_re.match(args.file) is None:
        raise IOError("Target file must be in .dat format")

    with open(args.file) as f:
        discr_lines = []

        try:
            field_list = [[float(field) for field in line.strip().split(' ') if field != ""] for line in f]
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
        #print final
        #disc_arr
        #write target file
        """args.outfile = make_dat_name(args.outfile)

        if args.outfile is not None:
            with open(args.outfile,'w') as f:
                for t in final:
                    f.write(t)"""
