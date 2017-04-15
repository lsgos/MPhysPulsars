from __future__ import division
import numpy as np
cimport numpy as np
from cython.view cimport array as cvarray

print "Hello, world"

#Seems to work, maybe shld test some more 
cpdef double calcHellingerDistance(np.int64_t [:] features, np.int64_t [:] class_labels):
    if features.shape[0] != class_labels.shape[0]:
        raise ValueError("Feature and class labels must have identical lengths")
    cdef int n_features 
    cdef int i
    cdef int n_samples 
    cdef double H
    cdef np.float64_t total_pos #these should be ints, but do it this way to avoid type casts
    cdef np.float64_t total_neg


    n_features = len(set(features)) #number of discrete features
    n_samples = features.shape[0]

    #assume the features are labelled as 0,1,2...
    cdef np.float64_t[:] p_pos = np.zeros(n_features, dtype=np.float64)
    cdef np.float64_t[:] p_neg = np.zeros(n_features, dtype=np.float64)

    for i in xrange(n_samples):
        if class_labels[i] == 0:
            p_neg[features[i]] += 1
            total_neg += 1
        elif class_labels[i] == 1:
            p_pos[features[i]] += 1
            total_pos += 1
        else:
            raise ValueError("This function only works on two class problems")
    #scale to probabilities
    cdef double p 
    cdef double q
    for i in xrange(n_features):
        p = p_neg[i] / total_neg
        q = p_pos[i] / total_pos
        H += (np.sqrt(p) - np.sqrt(q) )**2
    H = np.sqrt(H)
    H /= np.sqrt(2) #normalise H to the range (0,1)
    return H


cpdef int get_best_feature(np.int64_t [:,:] featureMatrix, np.int64_t [:] class_labels):

    if featureMatrix.shape[0] != class_labels.shape[0]:
        raise ValueError("Feature and class labels must have identical lengths")
    
    cdef int n_features = featureMatrix.shape[1]
    cdef int best_feature = -1
    cdef np.float64_t best_distance = -1 
    cdef np.float64_t distance
    cdef int i
    for i in xrange(n_features):
        distance = calcHellingerDistance(featureMatrix[:,i], class_labels)
        if distance > best_distance:
            best_distance = distance 
            best_feature = i
    return i

    
 #
#double calcHellingerDist(uint* feature, uint* classCol, uint noOfSamples) {
#    double INV_SQRT_2 =  ( 1 / (sqrt(2)) );
#    double H;
#    //Lets make a lazy assumption: the number of bins will always be lower than 50 
#    //If they aren't you'll know because the program will segfault
#    double sqrt_p_i;
#    double sqrt_q_i;
#    double incr;
#    //also assume the class labels start from one
#    uint *p_pos = (uint*) calloc(50, sizeof(uint));  //P(X | +)
#    uint *p_neg = (uint*) calloc(50, sizeof(uint));  //P(X | -)
#    int i;
#
#    int total_no_pos = 0;
#    int total_no_neg = 0;
#
#    //calculate the distributions
#    for (i = 0; i < noOfSamples; ++i) {
#        switch(classCol[i]) {
#            case 0:
#                p_pos[feature[i]]++;
#                break;
#            case 1:
#                p_neg[feature[i]]++;
#                break;
#        }
#    }
#    for (i = 0; i < 50; ++i) {
#        total_no_pos += p_pos[i];
#        total_no_neg += p_neg[i];
#    }
#    ////printf("Should be the same: %d   %d   %u", test_sum_1, test_sum_2, noOfSamples);
#    //calculate the (unscaled square of the ) hellinger distance
#    for (i = 0; i < 50; ++i) {
#        incr = 0.0;
#        if (p_pos[i] != 0) { 
#            sqrt_p_i = sqrt( ( (double) p_pos[i])  / total_no_pos );
#            incr += sqrt_p_i;
#        }
#        if (p_neg[i] != 0) { 
#            sqrt_q_i = sqrt( ( (double) p_neg[i])  / total_no_neg );
#            incr -= sqrt_q_i;
#        }
#        if (incr != 0.0) {
#            //only do this if incr hasn't changed to avoid accumulating errors
#            H += incr * incr;
#        }
#
#    }
#    //scale H
#    H = sqrt(H);
#    H *= INV_SQRT_2;
#    //free memory buffers
#    free (p_pos);
#    free (p_neg);
#    return H;
#}
#