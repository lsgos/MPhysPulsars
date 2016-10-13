#!/usr/bin/env python
"""
A program to insert randomised pulse profiles with a given range of properties
into real noise data. This is more of a shell script with options, providing
a more consise interface to stringing a number of existing programs together.
"""
import subprocess
import argparse
from numpy import random
import profile_gen
import par_gen

def seconds_to_mjd(x):
    return float(x) / (86400.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "A script for insertion of simulated signals into .fil files")
    parser.add_argument("--fil","-f", help = "input .fil file ")
    parser.add_argument("--snrlo", help = "Desired signal to noise ratio of generated signals",type = float)
    parser.add_argument("--snrhi", help = "Desired signal to noise ratio of generated signals",type = float)
    parser.add_argument("--flo", help = "Desired frequency range",type = float)
    parser.add_argument("--fhi", help = "Desired frequency range",type = float)
    parser.add_argument("--dmlo", help = "Desired dispersion measure range", type = float)
    parser.add_argument("--dmhi", help = "Desired dispersion measure range", type = float)
    parser.add_argument("--par","-par", help = "Filename to save the par as", default = "fake.par")
    parser.add_argument("--prof","-prn", help = "Filename to save the profile as", default = "fake_prof.asc")
    parser.add_argument("--outfil", help = "Filename for injected .fil file", default = "fake.fil")

    args = parser.parse_args()

    profile_gen.dump_profile(args.prof) #creates a profile file
    par_gen.make_par(args.par,args.dmlo,args.dmhi,args.flo,args.fhi) #CHANGE
    SNR = random.random() * (args.snrhi - args.snrlo) + args.snrlo
    #get MJD

    try:
        mjd_start = float(check_output("header",args.fil,"-tstart"))
        seconds_len = float(check_output("header", args.fil, "-tobs"))
        mjd_end = mjd_start + seconds_to_mjd(seconds_len)
        tempo2optstring = 'parkes '+str(mjd_start)+' '+str(mjd_end)+'1000 2000 16 2 3600'
        subprocess.check_call("tempo2","-f",args.par,"-pred",tempo2optstring)

        injected_fil = subprocess.check_output("inject_pulsar",
                                    "--pred",
                                    "t2pred.dat"
                                    "--prof",
                                    args.prof,
                                    args.fil,
                                    "-s",
                                     str(SNR))

        with open(args.outfil,'w') as f:
            f.write(injected_fil) #dump the output of inject_pulsar to a file

            subprocess.check_call("dspsr",args.outfil,"-b","-128","-t8","U1","-L30","-A","-D", str(DM),"-P","t2pred.dat")


    except OSError as e:
        print "OS Error detected: are all programs installed correctly?"
        raise e
    except CalledProcessError as e:
        print "A subprocess returned a non-zero error code: check this script or the target files?"
        raise e
