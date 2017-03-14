"""
This script will search a load of clists for known sources using the psrcat, printing out
the matched source filename to the screen 
"""
import multiprocessing as mp
import argparse
import clist_cand
import atnf_catalogue
import os
from astropy import units

SEP_TOL = units.deg * 1 #default maximum angular seperation to consider a match
P0_TOL = 10                              #default maximum period difference to consider a match
DM_TOL = 20                         # default maximum dm difference to consider a match


def match_known_source(cand):
    pos, period, dm, name = cand
    
    match, _  = atnf_catalogue.return_match(pos, SEP_TOL)
    
    if match is not None and abs(period - match['P0_ms']) < P0_TOL and abs(dm - match['DM']) < DM_TOL:
    	print name
    return 

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Searches a directory for clist files, printing out the filenames of the original sources that match known pulsars in"
    										         "the atnf psrcat")
    parser.add_argument("dir", help = "Directory to search for clist candidates")
    parser.add_argument("--sep", "-s", type = float, help = "Maximum angular seperation of candidates for a match to be considered in degrees (default 1)")
    parser.add_argument("--period", "-p", type = float, help = "Maximum seperation of candidates in period for a match to be considered in milliseconds (default 10)")
    parser.add_argument("--dm", "-d", type = float, help = "Maximum seperation of candidates in DM for a match to be considered in cm^-3 pc (default 20)")
    args = parser.parse_args()
    
    if args.sep is not None:
    	SEP_TOL = units.deg * args.sep
    if args.period is not None:
    	P0_TOL = args.period
    if args.dm is not None:
    	DM_TOL = args.dm
           
        
        
    if os.path.isdir(args.dir):
    	cands = clist_cand.candidates_in(args.dir)
    	
    	#setup a worker pool
    	workers = mp.Pool(mp.cpu_count())
    	workers.imap_unordered(match_known_source, cands)
    
    	
    		
    else:
    	print "Cannot open directory"