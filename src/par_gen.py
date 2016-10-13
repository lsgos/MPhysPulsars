# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 14:31:34 2016

Author: Alex Lisboa-Wright
"""

#parameter random number generator
from numpy import random

def make_par(filename,dmlow,dmhigh,f0low,f0high):
    f0 = random.random() *(f0high - f0low) + f0low
    dm = random.random() *(dmhigh - dmlow) + dmlow
    with open(filename,'w') as f:
        f.write("PSR J0000-0000 \nRAJ 00:00:00 \nDECJ 00:00:00 \nPEPOCH 55000 \n")
        f.write("F0 "+ str(f0)+"\n"+"DM "+str(dm)+"\n")
        f.write("UNITS TBD")
    return dm,f0

if __name__ == "__main__":
    filename="test.txt"
    f0low = float(raw_input("Lower pulsar frequency limit: "))
    f0high = float(raw_input("Upper pulsar frequency limit: "))
    dmlow = float(raw_input("Lower DM limit: "))
    dmhigh = float(raw_input("Upper DM limit: "))
    make_par(filename,dmlow,dmhigh,f0low,f0high)
