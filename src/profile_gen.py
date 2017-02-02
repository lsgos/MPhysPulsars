#!/usr/bin/env python
"""
A program to generate a simulated pulsar profile as a .asc file to use an an
input for the inject_pulsar program. Can be imported as a module or used from
the command line with unix pipes as preferred.
Authors: Mike Keith, Lewis Smith, Alex Lisboa-Wright
"""


from math import pi,radians,degrees
import numpy as np
from numpy import random
#Allow the catching of warnings like exceptions
import warnings
warnings.filterwarnings('error')
#set numpy warnings to be warnings rather than printing to stdout
np.seterr(all = 'warn')

def make_prof():
    class Success(Exception):
        pass
    while True:
        """
        this rigmarole is to avoid files containing NANs: if width is a very
        small number the exp on line 56 may overflow.to avoid this, catch numpy
        warnings as exceptions and retry the block with different random numbers
        until a non nan result is obtained.
        """
        try:
            out=np.zeros(1024)
            phase=np.linspace(0,2*pi,1024,endpoint=False)
            ncomponents=random.randint(2,8)
            nmp=0
            nip=0
            for icomp in range(ncomponents):
                A = random.lognormal()
                width = random.chisquare(2)*pi/64.0 # put a floor?

                po = random.normal(0,pi/4)
                ip = (random.uniform() < 0.08)
                if ip:
                    po+=pi
                    nip+=1
                    width *= nip
                    if nip==1:
                        A*=2
                else:
                    nmp+=1
                    width *= nmp

                    if nmp==1:
                        A*=2

                comp = np.exp(np.cos(phase-po)/width)
                comp /= comp.sum()
                out += A*comp
            out /= out.sum()
            raise Success
        except Warning:
            continue
        except Success:
            return out

def dump_profile(filename):
    out = make_prof()
    with open(filename,'w') as f:
         for o in out:
             f.write(str(o)+'\n')

if __name__=="__main__":
    out = make_prof()
    for o in out:
       print o
