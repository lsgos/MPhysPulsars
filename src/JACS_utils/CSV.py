"""
This file is part of the JACS ML Tutorial.

JACS ML Tutorial is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JACS ML Tutorial is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JACS ML Tutorial.  If not, see <http://www.gnu.org/licenses/>.

File name:    CSV.py
Created:      October 30th, 2014
Author:       Rob Lyon
 
Contact:    rob@scienceguyrob.com or robert.lyon@postgrad.manchester.ac.uk
Web:        <http://www.scienceguyrob.com> or <http://www.cs.manchester.ac.uk> 
            or <http://www.jb.man.ac.uk>

Represents a CSV (comma separated value) file, and provides functions that enables
their use with SciKit-Learn.

Designed to run on python 2.4 or later. 
 
"""

import numpy

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class CSV:
    """                
    Represents a CSV file.
    
    """
    
    # ****************************************************************************************************
        
    def read(self,path):
        """
        Converts numerical CSV data in to X,Y format for use by SciKit-Learn,
        where X is the data and Y the labels. Assumes the class label is the last
        item on each row (i.e. the last column of data).
        
        Does not work with text data.
        
        Parameters:
        
        path    -    the path to the CSV file to load.
        
        Returns:
        
        CSV data in X,Y form. X is a 2D numpy array, such that each row contains
        a unique data instance. Y is a column vector containing the class labels of
        each data item.
        """
        
        X=[]
        Y=[]
        
        with open(path,mode = 'U') as f:
            
            for line in f:
                
                if(line.strip() == ''):# Ignore empty lines.
                    continue
                
                # Split on comma since ARFF data is in CSV format.
                components = line.split(",")
                
                features = [float(x) for x in components[0:len(components)-1]]
                label    = [int(x)   for x in components[len(components)-1:len(components)]]
                
                X.append(features)
                Y.append(label)
                    
        # Call to ravel below converts label column vector into 1D array.            
        return numpy.array(X),numpy.ravel(numpy.array(Y),order='C')
                          
                
    # **************************************************************************************************** 
