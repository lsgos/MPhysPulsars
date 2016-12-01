"""
Split a noise arff file by a period, outputting a file of all noise with a period
less than a specified value and , and the rest of the data with those entries removed.
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
    description = "Split a noise arff file by period (assumed to be the first data field) a file, noise, containing all datapoints that pass period and cutoff tests, and another, noisedump, containing the remaining data")
    parser.add_argument("--noisered","-n", help = "arff file containing all datapoints that failed both conditions", default = "noise_reduced.arff")
    parser.add_argument("--noisedump","-d", help = "arff file containing all datapoints to be disarded to balance the training sets", default = "noise_dump.arff")
    parser.add_argument("--splitthresh","-s", help = "Value to split period by", type = float, default = 31.0)
    parser.add_argument("--dumpthresh","-t", help = "Value to split noise below period cutoff by", type = float, default = 0.9)
    parser.add_argument("--periodfield","-p", help = "Period field (default 1)")
    parser.add_argument("--splitclass","-c", help = "Value in class field (should be 0 for noise)", type = int, default = 0)
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    assert 0 <= args.dumpthresh <= 1.0,"dumpthresh must be a fraction (i.e. between 0 and 1)"

    with open(args.file) as f:
        header = parse_arff_header(f)
        noise_lines = []
        noise_dump_lines = []

        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(',')
            #assume period is the first field, and class the last
            period = float(fields[0])
            category = int(fields[-1])
            dump_tag = np.random.random()
            # split off MSPs
            if (category == args.splitclass and period < args.splitthresh and dump_tag >= args.dumpthresh) or (category == args.splitclass and period >= args.splitthresh):
                noise_lines.append(line)
            elif category != args.splitclass:
                continue
            else:
                noise_dump_lines.append(line)

    #write target files
    args.noisered = make_arff_name(args.noisered)
    args.noisedump = make_arff_name(args.noisedump)

    if args.noisered is not None:
        with open(args.noisered,'w') as f:
            for h in header:
                f.write(h)
            for t in noise_lines:
                f.write(t)
    if args.noisered is not None:
        with open(args.noisedump,'w') as f:
            for h in header:
                f.write(h)
            for t in noise_dump_lines:
                f.write(t)
