# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 09:24:33 2016

@author: Alex Lisboa-Wright
"""

# Code that concatenates a .arff file
from __future__ import print_function
import argparse
import random

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


parser = argparse.ArgumentParser(description = "Concatenates two arff files into \
        a single file. Assumes that they share a header: if this is not the case\
        the output will not be a valid arff file. Prints to stdout")
parser.add_argument('files', nargs='+', help = 'list of files to concatenate')
parser.add_argument('--shuffle','-s', type = bool, default = False, help = "If set to true, shuffle the order of the data points")

args = parser.parse_args()
header = None
lines = []
for filename in args.files:
    with open(filename) as f:
        if header is None:
            header = parse_arff_header(f)
        for line in f:
            # Comments and attribute lines should be ignored.
            if(line.startswith("@") or line.startswith("%")):
                continue
            elif(line.strip() == ''):# Ignore empty lines.
                continue
            fields = line.split(',')
            lines.append(line)

if args.shuffle:
    random.shuffle(lines)


for head in header:
    print (head, end = "")
for line in lines:
    print(line, end="")
