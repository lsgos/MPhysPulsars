# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 14:31:34 2016

Author: Alex Lisboa-Wright
"""

#parameter random number generator
from __future__ import division
from numpy import random

def make_par(filename,dmlow,dmhigh,plow,phigh):

    p = random.random() *(phigh - plow) + plow #generate a uniform distribution in period, then convert to frequency
    f0 = (1.0/p)
    dm = random.random() *(dmhigh - dmlow) + dmlow
    with open(filename,'w') as f:
        f.write("PSR J0000-0000 \nRAJ 00:00:00 \nDECJ 00:00:00 \nPEPOCH 55000 \n")
        f.write("F0 "+ str(f0)+"\n"+"DM "+str(dm)+"\n")
        f.write("UNITS TBD")
    return dm,f0

if __name__ == "__main__":
    filename="test.txt"
    plow = float(raw_input("Lower pulsar frequency limit: "))
    phigh = float(raw_input("Upper pulsar frequency limit: "))
    dmlow = float(raw_input("Lower DM limit: "))
    dmhigh = float(raw_input("Upper DM limit: "))
    make_par(filename,dmlow,dmhigh,plow,phigh)
