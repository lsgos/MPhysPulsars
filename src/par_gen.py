# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 14:31:34 2016

Author: Alex Lisboa-Wright
"""

#parameter random number generator
from numpy import random


    
def par_gen(dmlow,dmhigh,f0low,f0high):
    if (dmlow, dmhigh, f0low, f0high >=0):
        if f0low > f0high:
            f0low, f0high = f0high, f0low
        return f0low, f0high
    

def make_par(filename,dmlow,dmhigh,f0low,f0high):
    f0 = random.random(f0low, f0high)
    dm = random.random(dmlow, dmhigh)
    with open(filename,'w') as f:
        f.write("PSR J0000-0000 \nRAJ 00:00:00 \nDECJ 00:00:00 \nPEPOCH 55000 \n")
        f.write("F0 "+ str(f0)+"\n"+"DM "+str(dm)+"\n")
        f.write("UNITS TBD")
        
        
if __name__ == "__main__":
    filename="test.txt"
    f0low = raw_input("Lower pulsar frequency limit: ")
    f0high = raw_input("Upper pulsar frequency limit: ")
    dmlow = raw_input("Lower DM limit: ")
    dmhigh = raw_input("Upper DM limit: ")
    make_par(filename,dmlow,dmhigh,f0low,f0high)
    