# -*- coding: utf-8 -*-
"""
Created on Thu Nov 03 11:30:34 2016

@author: Alex Lisboa-Wright
"""

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
    parser.add_argument("--fileoutarff","-f", help = "arff file containing all data from original input file with a new category value", default = "htru2_msp_newcateg.arff")
    parser.add_argument("--newcateg","-n", help = "new category value", default = "2")
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    with open(args.file) as f:
        header = parse_arff_header(f)
        newcateg_lines = []
        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(',')
            #assume class is the last
            new_fields = fields[:-1]
            #put new class in
            new_fields.append(args.newcateg+"\n")
            new_line = ",".join(new_fields)
            newcateg_lines.append(new_line)

    #write target file
    args.fileoutarff = make_arff_name(args.fileoutarff)

    with open(args.fileoutarff,'w') as f:
        for h in header:
            f.write(h)

        for t in newcateg_lines:
            f.write(t)
