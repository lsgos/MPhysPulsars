# -*- coding: utf-8 -*-
"""
Created on Thu Nov 03 11:30:34 2016

@author: Alex Lisboa-Wright
"""
from __future__ import print_function
# code that changes the "class" label of a dataset
import argparse
import re

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
    parser = argparse.ArgumentParser()
    #parser.add_argument("--commarff","-c", help = "arff file containing all data from original input file with msps commented", default = "htru2_msp_commented.arff")
    parser.add_argument("--mspcomment","-n", help = "msp comment to be added", default = "%***MSP***")
    parser.add_argument("--mspcutoffperiod","-p", help = "cutoff period between MSPs and non-MSP pulsars (in ms)", default = 31.0, type = float)
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    with open(args.file) as f:
        header = parse_arff_header(f)
        mspcomm_lines = []
        for line in f:
            #ignore empty data lines
            if line.strip() == "":
                continue
            fields = line.split(',')
            #assume period is the first field, and class the last
            period = float(fields[0])
            category = int(fields[-1])
            #add comment to MSP lines only
            if category == 1 and period < args.mspcutoffperiod:
                line = line[:-1] + args.mspcomment + "\n"
                #append comment to MSPs
                mspcomm_lines.append(line)
            else:
                mspcomm_lines.append(line)

    #write target file
    #args.commarff = make_arff_name(args.commarff)

    for l in header + mspcomm_lines:
        print(l,end = "")
#   with open(args.commarff,'w') as f:
#       for h in header:
#           f.write(h)
#       for t in mspcomm_lines:
#           f.write(t)
