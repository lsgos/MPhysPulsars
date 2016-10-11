#!/usr/bin/env python
"""
A program to generate a simulated pulsar profile as a .ast file to use an an input for the inject_pulsar program. 
"""

from __future__ import division
import numpy as np
import argparse




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generates a simulated pulse profile as a .ast file for use with the inject_pulsar program")
    parser.add_argument("-sr","--sample_rate", help = "the sample rate of the pulse profile")
