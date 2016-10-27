"""
Split an arff file by a period, outputting a file of all pulsars with period
less than a specified value, and the rest of the data with those entries removed.
"""
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
    parser = argparse.ArgumentParser(
    description = "Split an arff file by period (assumed to be the first data field) a file target containing all datapoints that pass the condition and another, rest, containing the remaining data")
    parser.add_argument("--target","-t", help = "arff file containing all datapoints that passed the condition", default = "target.arff")
    parser.add_argument("--rest","-r", help = "arff file containing all datapoints that failed the condition", default = "rest.arff")
    parser.add_argument("--splitthresh","-s", help = "Value to split pulsars by", type = float)
    parser.add_argument("--periodfield","-p", help = "Period field (default 1)")
    parser.add_argument("file", help = "the file to process (must be in arff format)")

    args = parser.parse_args()

    if arff_re.match(args.file) is None:
        raise IOError("Target file must be in arff format")

    with open(args.file) as f:
        header = parse_arff_header(f)
        target_lines = []
        rest_lines = []
        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(',')
            #assume period is the first field, and class the last
            period = float(fields[0])
            category = int(fields[-1])
            if category == 1 and period < args.splitthresh:
                target_lines.append(line)
            else:
                rest_lines.append(line)

    #write target files
    args.target = make_arff_name(args.target)
    args.rest = make_arff_name(args.rest)

    with open(args.target,'w') as f:
        for h in header:
            f.write(h)
        for t in target_lines:
            f.write(t)
    with open(args.rest,'w') as f:
        for h in header:
            f.write(h)
        for t in rest_lines:
            f.write(t)
