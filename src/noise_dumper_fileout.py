"""
Split a noise arff file by a period, outputting a file of all noise with a period
less than a specified value and , and the rest of the data with those entries removed.
"""
from __future__ import print_function
import argparse
import re
import numpy as np

arff_re = re.compile(".*\.arff")

def parse_arff_header(f):
    header = []

    while True:
        last_pos = f.tell()
        line = f.readline()
        s = line.strip()
        if s == "":
            continue #ignore blank lines
        elif line[0] == '@':
            #while parsing the header
            header.append(line)
        else:
            f.seek(last_pos) #unread the line
            break
    return header

def make_arff_name(name):
    if arff_re.match(name) is None:
        name = name + '.arff'
    return name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = "Reduce noise in an arff file according to period (assumed to be the first data field). The discarded noise will go to noisedump, the rest to noisered")
    parser.add_argument("--noisered","-n", help = "arff file containing all datapoints to be kept", default = "noise_reduced+psrs.arff")
    parser.add_argument("--noisedump","-d", help = "arff file containing all datapoints to be disarded to balance the training sets", default = "noise_dump.arff")
    parser.add_argument("--splitthresh","-s", help = "Value to split period by", type = float, default = 31.0)
    parser.add_argument("--dumpthresh","-t", help = "Value to split noise below period cutoff by", type = float, default = 0.9)
    parser.add_argument("--splitclass","-c", help = "Value in class field (should be 0 for noise)", type = int, default = 0)
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    assert 0 <= args.dumpthresh <= 1.0,"dumpthresh must be a fraction (i.e. between 0 and 1)"

    with open(args.file) as f:
        header = parse_arff_header(f)
        lines_red = []
        noise_dump_lines = []

        for line in f:
            comment = None
            if line.strip() == "":
                continue
            elif('%' in line):
                 text = line[0:line.index('%')]
                 comment = line[line.index('%'):]
            else:
            	text = line
            fields = text.split(',')
            #assume period is the first field, and class the last
            period = float(fields[0])
            category = int(fields[-1])
            dump_tag = np.random.random()
            # split off excess noise
            if (category == args.splitclass and period < args.splitthresh and dump_tag < args.dumpthresh):
                noise_dump_lines.append(line)
            else:
                lines_red.append(line)

    #write target files
    args.noisered = make_arff_name(args.noisered)
    args.noisedump = make_arff_name(args.noisedump)
    """for l in header + lines_red:
        print(l,end = "")"""

    if args.noisered is not None:
        with open(args.noisered,'w') as f:
            for h in header:
                f.write(h)
            for t in lines_red:
                f.write(t)
    if args.noisered is not None:
        with open(args.noisedump,'w') as f:
            for h in header:
                f.write(h)
            for t in noise_dump_lines:
                f.write(t)
