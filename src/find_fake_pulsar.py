#!/usr/bin/env python
"""
A script to parse the files generated by the output of the pulsar profile injection.
It will take a directory containing the output as an argument, and return the most
likely match to the injected pulsar, given it's known frequency and DM, printing
the result to stdout for use by other scripts
"""

import os
import argparse
import re

# tolerance on parameters
def get_p_tol(p):
    #return the period tolerance, calculated from the doppler shift due to the earth's motion
    delta_f = 9.93e-02*(1.0 /p)
    delta_p = delta_f*((p^2)/1000) + 0.1
    return delta_p



dm_tol = 0.5

fil_re= re.compile('.*\.lis')
par_re= re.compile('.*fake\.par')


def parse_par_file(f):
    dm = None
    period = None
    for line in f:
        l = line.strip()
        if l == '':
            continue
        att, val = l.split(' ')
        if att == 'DM':
            dm = float(val)
        elif att == 'F0':
            period = 1000.0 / float(val)
        else:
            continue

    if period is None or dm is None:
        raise RuntimeError('Unable to parse .par file, may be missing attributes')
    return period,dm

def parse_lis_line(l):
    """takes the string line from the .lis file and extracts the relevant info"""
    line = l.split('\t')
    fname = line[0]
    snr = float(line[1])
    period = float(line[2])
    dm = float(line[3])
    return fname,snr,period,dm

def score_cand(target_p,target_dm,p,dm):
    """A similarity score for the pulsar candidate: maybe extend to include the expected snr? 0 is perfect"""
    loss = (1.0 - (p) / target_p) **2 + (1.0 - dm / target_dm) **2
    return loss



def process_directory(dir_name):
    lis_names = [l for l in os.listdir(dir_name) if fil_re.match(l) is not None]
    par_names = [p for p in os.listdir(dir_name) if par_re.match(p) is not None]

    if len(lis_names) != 1 or len(par_names) != 1:
        return False
    lis_name = os.path.join(dir_name,lis_names[0])
    par_name = os.path.join(dir_name,par_names[0])
    try:
        with open(par_name) as f:
            target_p,target_dm = parse_par_file(f)

        with open(lis_name) as f:
            candnames = []
            for line in f:
                fname,snr,period,dm = parse_lis_line(line)
                p_tol = get_p_tol(period)
                if (target_dm - dm_tol) < dm < (target_dm + dm_tol) and (target_p - p_tol) < period < (target_p + p_tol):
                    loss = score_cand(target_p,target_dm,period,dm)
                    candnames.append((fname,loss))

    except IOError as e:
        print "Required files not found: does the directory contain the processor output?"
        raise e
    except RuntimeError as e:
        raise e
    candnames.sort(key = lambda x: x[1])
    if len(candnames) == 0:
        print('## No matching pulsars found in directory {}'.format(dir_name))

    for n,_ in candnames:
        print os.path.join(dir_name,n) #print to stdout in decreasing order of likehood

    return True

def search_directories(dir_name):

    if process_directory(dir_name):
        return

    for d in os.listdir(dir_name):
        newdir = os.path.join(dir_name,d)
        if os.path.isdir(newdir):
            search_directories(newdir)
        else:
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "A script to filter directories containing injected pulsar data in order to find the 'pulsars', and return their filenames")
    parser.add_argument("dir_name", help = "The target directory, containing the output of the processing pipeline and injected data files")

    args = parser.parse_args()
    search_directories(args.dir_name)
