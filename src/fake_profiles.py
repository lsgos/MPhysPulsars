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
    DM,_ = par_gen.make_par(args.par,args.dmlo,args.dmhi,args.flo,args.fhi) #CHANGE
    SNR = random.random() * (args.snrhi - args.snrlo) + args.snrlo
    #get MJD

    try:
        mjd_start = float(subprocess.check_output(["header",args.fil,"-tstart"]))
        seconds_len = float(subprocess.check_output(["header", args.fil, "-tobs"]))
        mjd_end = mjd_start + seconds_to_mjd(seconds_len)
        tempo2optstring = 'parkes '+str(mjd_start-0.05)+' '+str(mjd_end+0.05)+' 1000 2000 16 2 3600'
        subprocess.check_call(["tempo2","-f",args.par,"-pred",tempo2optstring])

	with open(args.outfil,'w') as f:

		injected_fil = subprocess.check_call(["inject_pulsar",
					    "--pred",
					    "t2pred.dat",
					    "--prof",
					    args.prof,
					    args.fil,
					    "-s",
					     str(SNR)],stdout=f)


	with open("fake.snr",'w') as f:
		f.write("%f\n"%SNR)

	subprocess.check_call(["dspsr",args.outfil,"-b","-128","-t8","-U1","-L30","-A","-D", str(DM),"-P","t2pred.dat","-j","'F 16'", "-O","fake"])


    except OSError as e:
        print "OS Error detected: are all programs installed correctly?"
        raise e
    except subprocess.CalledProcessError as e:
        print "A subprocess returned a non-zero error code: check this script or the target files?"
        raise e
