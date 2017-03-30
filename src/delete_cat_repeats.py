import argparse
import re

dat_re = re.compile(".*\.dat")

def make_dat_name(name):
    if dat_re.match(name) is None:
        name = name + '.dat'
    return name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description = "Split off data in an INDEX-SORTED .dat file if it matches a previously matched catalogue object")
    parser.add_argument("--cat","-c", help = ".dat file containing one datapoint for all matched catalogue object", default = "cat_objects.dat")
    parser.add_argument("--repeats","-r", help = ".dat file containing datapoints that matched to a catalogue object also matched by a previous datapoint", default = "repeat_detections.dat")
    parser.add_argument("file", help = "the ordered file to process (must be in .dat format)")

    args = parser.parse_args()

    if dat_re.match(args.file) is None:
        raise IOError("Target file must be in .dat format")
    last_index = None
    with open(args.file) as f:
        cat_lines = []
        repeat_lines = []
        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(' ')
            # first field is the directory name, the second is the index of its matched pulsar from the catalogue
            dir_name = fields[0]
            cat_index = int(fields[1])
            if cat_index == last_index:
                repeat_lines.append(line)
            else:
                cat_lines.append(line)
                last_index = cat_index


    # build new files
    args.cat = make_dat_name(args.cat)
    args.repeats = make_dat_name(args.repeats)

    if args.cat is not None:
        with open(args.cat,'w') as f:
            for t in cat_lines:
                f.write(t)
    if args.repeats is not None:
        with open(args.repeats,'w') as f:
            for t in repeat_lines:
                f.write(t)
