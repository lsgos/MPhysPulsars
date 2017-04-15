
/*
Author: Lewis Smith, Univ. Manchester, 2017
Implement the hellinger distance critereon for a discretised dataset, following the interface of the FEAST toolbox

For a discrete feature X^j and a two class problem with labels + and -, the hellinger distance is 

H^2 = 1 / 2  ( sum_{x in X^j} sqrt(P(x | +)) - sqrt(P(x | -)) )

H = 1 when the distributions are totally seperated, and 0 when they are identical. 
A high H is desirable in a feature, since it means the distribution is well seperated 
by the class
*/

#include "math.h"
#include "stdlib.h"
#include "stdio.h"
#include "hellinger_measure.h"




//Calculate the hellinger distance for a single feature 
double calcHellingerDist(uint* feature, uint* classCol, uint noOfSamples) {
    double INV_SQRT_2 =  ( 1 / (sqrt(2)) );
    double H;
    //Lets make a lazy assumption: the number of bins will always be lower than 50 
    //If they aren't you'll know because the program will segfault
    double sqrt_p_i;
    double sqrt_q_i;
    double incr;
    //also assume the class labels start from one
    uint *n_pos = (uint*) calloc(50, sizeof(uint));  //P(X | +)
    uint *n_neg = (uint*) calloc(50, sizeof(uint));  //P(X | -)
    int i;

    int total_no_pos = 0;
    int total_no_neg = 0;

    //calculate the distributions
    for (i = 0; i < noOfSamples; ++i) {
        switch(classCol[i]) {
            case 0:
                n_pos[feature[i]]++;
                break;
            case 1:
                n_neg[feature[i]]++;
                break;
        }
    }
    for (i = 0; i < 50; ++i) {
        total_no_pos += n_pos[i];
        total_no_neg += n_neg[i];
    }
    ////printf("Should be the same: %d   %d   %u", test_sum_1, test_sum_2, noOfSamples);
    //calculate the (unscaled square of the ) hellinger distance
    for (i = 0; i < 50; ++i) {
        incr = 0.0;
        if (n_pos[i] != 0) { 
            sqrt_p_i = sqrt( ( (double) n_pos[i])  / total_no_pos );
            incr += sqrt_p_i;
        }
        if (n_neg[i] != 0) { 
            sqrt_q_i = sqrt( ( (double) n_neg[i])  / total_no_neg );
            incr -= sqrt_q_i;
        }
        if (incr != 0.0) {
            //only do this if incr hasn't changed to avoid accumulating errors
            H += incr * incr;
        }

    }
    //scale H
    H = sqrt(H);
    H *= INV_SQRT_2;
    //free memory buffers
    free (n_pos);
    free (n_neg);
    return H;
}

    

uint * HellingerDist(uint k, 
                     uint noOfSamples, 
                     uint noOfFeatures,
                     uint **featureMatrix,
                     uint *classColumn, 
                     uint *outputFeatures, 
                     double *featureScores) 
{
    char* selectedFeatures = (char *) calloc(noOfFeatures, sizeof(char));
    double *classH = (double *) calloc(noOfFeatures, sizeof(double));
    double maxH = -1.0;
    int maxHCounter = -1;
    int i,j;

    for (i = 0; i < noOfFeatures; ++i) {
        classH[i] = calcHellingerDist(featureMatrix[i], classColumn, noOfSamples);
        if (classH[i] > maxH) {
            maxH = classH[i];
            maxHCounter = i;
        }
    }
    selectedFeatures[maxHCounter] = 1;
    outputFeatures[0] = maxHCounter;
    featureScores[0] = maxH;

    for (i = 1; i < k; i++) {
        maxH = -1.0;
        for (j = 0; j < noOfFeatures; j++) {
            if (!selectedFeatures[j]) {
                if (maxH < classH[j]) {
                    maxH = classH[j];
                    maxHCounter = j;
                }
            }
        }
        selectedFeatures[maxHCounter] = 1;
        outputFeatures[i] = maxHCounter;
        featureScores[i] = maxH;
    }
    free(classH);
    free(selectedFeatures);

    classH = NULL;
    selectedFeatures = NULL;
    return outputFeatures;
}