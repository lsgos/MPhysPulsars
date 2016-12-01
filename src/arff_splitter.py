"""
Split an arff file by a period, outputting a file of all pulsars with period
less than a specified value, and the rest of the data with those entries removed.
"""
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
    description = "Split an arff file by period (assumed to be the first data field) a file, msp, containing all datapoints that pass both conditions, another, pulsar, that fails the period condition but passes the pulsar condition and another, noise, containing the remaining data")
    parser.add_argument("--msp","-m", help = "arff file containing all datapoints that passed the msp and general pulsar conditions", default = "msp.arff")
    parser.add_argument("--pulsar","-u", help = "arff file containing all datapoints that failed the msp condition but passed the pulsar condition", default = "pulsar.arff")
    parser.add_argument("--noise","-n", help = "arff file containing all datapoints that failed both conditions", default = "noise.arff")
    parser.add_argument("--splitthresh","-s", help = "Value to split pulsars by", type = float, default = 31.0)
    parser.add_argument("--periodfield","-p", help = "Period field (default 1)")
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    with open(args.file) as f:
        header = parse_arff_header(f)
        msp_lines = []
        pulsar_lines = []
        noise_lines = []

        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(',')
            #assume period is the first field, and class the last
            period = float(fields[0])
            category = int(fields[-1])
            # split off MSPs
            if category == 1 and period < args.splitthresh:
                msp_lines.append(line)
            elif category == 1 and period >= args.splitthresh:
                pulsar_lines.append(line)
            else:
                noise_lines.append(line)

    #write target files
    args.msp = make_arff_name(args.msp)
    args.pulsar = make_arff_name(args.pulsar)
    args.noise = make_arff_name(args.noise)

    if args.msp is not None:
        with open(args.msp,'w') as f:
            for h in header:
                f.write(h)
            for t in msp_lines:
                f.write(t)
    if args.pulsar is not None:
        with open(args.pulsar,'w') as f:
            for h in header:
                f.write(h)
            for t in pulsar_lines:
                f.write(t)
    if args.noise is not None:
        with open(args.noise,'w') as f:
            for h in header:
                f.write(h)
            for t in noise_lines:
                f.write(t)
