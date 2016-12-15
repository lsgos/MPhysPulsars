"""
Weka plots are useful but look a little bit gross, so this script re-creates the
same functionality in matplotlib for graphs we want to put into our reports
"""
from matplotlib import pyplot as plt
import argparse
import numpy as np


def parse_arff(filename):
    """
    parse the header metadata from the arff files
    """
    attribute_names = []
    data = []
    with open(filename,'r') as f:
        for line in f:
            if line.strip() == "":
                continue
            elif line.startswith('@'):
                line = line.strip()
                line = line[1:]
                fields = line.split(' ')
                if fields[0] == "attribute":
                    attribute_names.append(fields[1])
            else:
                #parse the data
                if "%" in line:
                    line = line[0:line.index("%")]
                data.append([float(x) for x in line.split(',')])
    return attribute_names, np.array(data)


def main():
    parser = argparse.ArgumentParser(description = "A program to re-create weka plots easily, but in a more visually appealing way")
    parser.add_argument("file", help = "file containing dataset, must be in arff format.")
    parser.add_argument("-x", help = "attribute to plot on the x axis. Must be an integer in the range [0,9]",type = int)
    parser.add_argument("-y", help = "attribute to plot as the y axis. Must be an integer in the range [0,9]",type = int)
    parser.add_argument("-c", help = "attribute to color the point using. Must be an integer in the range [0,9] (default 9: class)",type = int, default = 9)
    parser.add_argument("--xlabel", help = "user specified x axis label, if desired")
    parser.add_argument("--ylabel", help = "user specified y axis label, if desired")
    parser.add_argument("--cmap", help = "colormap to use. See http://matplotlib.org/examples/color/colormaps_reference.html")
    args = parser.parse_args()

    assert(args.x in range(10) and args.y in range(10) and args.c in range(10)), "All selected fields must by in the interval [0,9]"
    att_names, data = parse_arff(args.file)


    plt.figure()

    colmap = plt.cm.Accent
    if args.cmap is not None:
        try:
            colmap = plt.get_cmap(args.cmap)
        except ValueError as e:
            print "Cannot find that colormap, using default..."
            colmap = plt.cm.Accent

    plt.scatter(data[:,args.x], data[:,args.y], c = data[:,args.c], cmap = colmap, marker = 'x')
    if args.xlabel is not None:
        plt.xlabel(args.xlabel)
    else:
        plt.xlabel(att_names[args.x])
    if args.ylabel is not None:
        plt.ylabel(args.ylabel)
    else:
        plt.ylabel(att_names[args.y])

    plt.show()


if __name__ == "__main__":
    main()
