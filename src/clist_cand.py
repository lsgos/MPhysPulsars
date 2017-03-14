import xml.etree.ElementTree as ET
import os
from astropy.coordinates import SkyCoord
from astropy import units
import itertools
import re
import gzip

clist_name = re.compile(".*\.clist.gz")

def read(filename): 
    #files are gzipped: unpack them
    with gzip.open(filename) as f:
    	filedata = f.read()
    
    root = ET.fromstring(filedata)
    
    #This gets the position on the sky of the observation
    co_ord_field = root.find('CLHead').find('Coordinate')
    co_ord_type = co_ord_field.get('type')
    co_ord_data = co_ord_field.text
    
    location = SkyCoord(co_ord_data, unit = (units.deg, units.deg)) 
    #Each file may contain multiple candidates: iterate through them, storing the results in a list 
    
    cands = root.find('CLBody')
    
    #cands are xml subtrees: access the elements via, e.g cand.find('Period').text 	
    
    periods = [cand.find('Period').text for cand in cands]
    dms = [cand.find('Dm').text for cand in cands]
    filenames = [cand.find('CandFile').text for cand in cands]
    
    candidates_info = zip( itertools.repeat(location), periods, dms, filenames )
    return candidates_info
   
def candidates_in(path):
    for root, dirs, files in os.walk(path):
        for fname in files:
            if clist_name.match(fname):
                #todo: read the gzip file
                candidate_info = read( os.path.join(root,fname))
                for cand in candidate_info:
                	yield cand
             
        
 