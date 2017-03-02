#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse
def score_line(dm,starttime, line):
    fields = map(float,line.strip().split("\t"))
    this_dm = fields[5]
    this_st = fields[2]
    score = (this_st - starttime) **2 + (this_dm - dm) **2
    return score

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dm", type = float)
    parser.add_argument("starttime", type = float)
    parser.add_argument("name")
    args = parser.parse_args()
    
    lines = [line for line in sys.stdin]
    if len(lines) == 1:
        print( line, end = "")
        return
        
    bestscore = None
    bestline = None
    for line in lines:
        score = score_line(args.dm, args.starttime, line)
        if bestscore is None or score < bestscore:
            bestline = line 
            bestscore = score
    if bestline is not None:
        print( bestline, end = "")
    else:
        print("WARNING: NO FRB FOUND IN CANDIDATE {}".format(args.name))
    return 

if __name__ == "__main__":
    main()
