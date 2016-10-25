#!/usr/bin/env python
"""
A utility to convert combined datasets into just Lyon features, but with the
period added as the first field to enable filtering out of by period.
"""
import argparse
import sys
def print_header(fname):
    print "@relation some_pulsars" #maybe come up with something less crap?
    print "@attribute Period numeric"
    print "@attribute Profile_Mean numeric"
    print "@attribute Profile_Sdtdev numeric"
    print "@attribute Profile_Skewness numeric"
    print "@attribute Profile_Kurtosis numeric"
    print "@attribute DM_SNR_Mean numeric"
    print "@attribute DM_SNR_Stddev numeric"
    print "@attribute DM_SNR_Skewness numeric"
    print "@attribute DM_SNR_Kurtosis numeric"
    print "@attribute class {0,1}"
    print "@data"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Convert an arff file to Lyon features, with period added for sorting purposes. Prints to stdout")
    parser.add_argument("file",help = "filename to convert")
    args = parser.parse_args()

    print_header(args.file)

    with open(args.file,'r') as f:
        for line in f:
            if line[0] == '@':
                continue
            else:
                l = line.split(',')
                print('{19},{0},{1},{2},{3},{4},{5},{6},{7},{30}'.format(*l) )
