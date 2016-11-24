#! /usr/bin/env python
# coding=utf-8

"""
This script is designed to extend the noise tail of the Dm index in a simulated
phcx archive. This is a bit of a hack, but it saves processing time if it works.
"""

from xml.dom import minidom
import numpy as np

import argparse
import gzip
import os

from matplotlib import pyplot as plt

def getDM_FFT(xmldata):
    """
    Copied from pulsar_feature_lab
    Extracts the DM curve from the DM data block in the phcx file.

    Parameters:
    xmldata    -    a numpy.ndarray containing the DM data in decimal format.
    section    -    the section of the xml file to find the DM data within. This
                    is required sine there are two DM sections in the phcx file.

    Returns:

    An array containing the DM curve data in decimal format.

    """
    section=0 #HACK: This is a temporary fix to a bug. Hopefully this will be fixed in the upstream pulsar_feature_lab soon. In the meantime, this works for the file we are using
    # Extract data.
    dec_value = []
    block = xmldata.getElementsByTagName('DataBlock') # gets all of the bits with the title 'section'.
    points = block[section].childNodes[0].data

    # Transform data from hexadecimal to decimal values.
    x=0
    while x < len(points):
        if points[x] != "\n":
            try:
                hex_value = points[x:x+2]
                dec_value.append(int(hex_value,16)) # now the profile (shape, unscaled) is stored in dec_value
                x = x+2
            except ValueError:
                break
        else:
            x = x+1

    return dec_value

def encode_to_base16(dec):
    #convert a list of integers into a single base 16 string
    hex_str = "".join([format(d,'02X') for d in dec])
    return hex_str


def noise_generator(l, noise_min, noise_max, noise_rate):
    #generates exponentially distributed fake noise tails for dm curves
    if np.floor(noise_rate) != 0:
        raise ValueError("Noise rate must be in the interval [0,1]")

    return [np.random.randint(noise_min,noise_max) if np.random.random() < noise_rate else 0 for i in xrange(l) ]

def save_modified_phcx(basexml, dec, targetfilename):
    #saves a copy of basefile with its dm replaces by dec
    section = 0

    dm_info = basexml.getElementsByTagName('DmIndex')[0] #get the first DM index section, the only one we are using
    dm_info.attributes['nVals'].value =unicode(str(len(dec))) # change the dm index information

    basexml.getElementsByTagName('DataBlock')[section].childNodes[0].data = unicode(encode_to_base16(dec))
    #replace the dm data block with the hex representation of dec

    #save modifed xml
    with gzip.open(targetfilename,'w') as f:
        basexml.writexml(f)


def process_file(filename, pad_length, target_filename, noise_min, noise_max, noise_rate):
    if ".gz" in filename:
        filedata = gzip.open(filename)
    else:
        filedata = open(filename,'r')
    xml = minidom.parse(filedata)
    dec = getDM_FFT(xml)
    noise_dec = dec + noise_generator((args.pad_length - len(dec)), noise_min, noise_max, noise_rate)

    if not ".gz" in target_filename:
        target_filename = target_filename + ".gz"
    save_modified_phcx(xml,noise_dec, target_filename)

def process_directory(dirname,pad_length,target_dir,noise_min, noise_max, noise_rate, lowratelim, uppratelim):
    assert os.path.exists(dirname)
    assert os.path.exists(target_dir)
    ls = os.listdir(dirname)
    for f in ls:
        noise_rate= lowratelim + np.random.random()*(abs(uppratelim-lowratelim))
        if os.path.isdir(f):
            process_directory(os.path.join(dirname,f), pad_length, target_dir, noise_min, noise_max, noise_rate, lowratelim, uppratelim)
        elif ".phcx" in f:
            process_file(os.path.join(dirname,f),pad_length,os.path.join(target_dir,f ), noise_min, noise_max, noise_rate)

def plot_dm(filename,padlength, noise_min, noise_max, noise_rate):

    if ".gz" in filename:
        filedata = gzip.open(filename)
    else:
        filedata = open(filename,'r')
    xml = minidom.parse(filedata)
    dec = getDM_FFT(xml)

    plt.figure(1)
    plt.plot(dec)

    plt.figure(2)

    noise_dec = dec + noise_generator((padlength - len(dec)),noise_min, noise_max, noise_rate)
    plt.plot(noise_dec)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Pads fake pulsar files with noise tails, writin copies of the phcx files to outdir.")
    parser.add_argument("dir", help = "directory to process. Will process all files phcx recursively")
    parser.add_argument("outdir", help = "directory to write modified files to")
    parser.add_argument("--pad_length", help = "length to pad dm out to", default = 1119, type = int)
    parser.add_argument("--noise_rate", help = "rate of dm noise", default = 0.09, type = float)
    parser.add_argument("--noise_max", help = "maximum value of dm noise", default = 50.0, type = float)
    parser.add_argument("--noise_min", help = "minimum value of dm noise", default = 10.0, type = float)
    parser.add_argument("--lowratelim", help = "lower limit of rate of dm noise", default = 0.01, type = float)
    parser.add_argument("--uppratelim", help = "upper limit of rate of dm noise", default = 0.1, type = float)
    parser.add_argument("--plot_f",action = "store_true", help = "plot a file instead (overrides default behaviour)")
    args = parser.parse_args()

    if args.plot_f:
        plot_dm(args.dir,args.pad_length,args.noise_min,args.noise_max,args.noise_rate)
    else:
        process_directory(args.dir,args.pad_length,args.outdir,args.noise_min,args.noise_max,args.noise_rate,args.lowratelim,args.uppratelim)
