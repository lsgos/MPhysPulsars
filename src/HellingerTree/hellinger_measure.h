/*
Author: Lewis Smith, Univ. Manchester, 2017
Use the hellinger distance to select features, presenting a similar interface to the FEAST toolbox 


At present, this only works on two class problems 
The hellinger distance is a skew-insensitive feature selection algorithm: see 
Hellinger Distance Trees for Imbalanced Streams by Lyon, Stappers, Brooke and Knowles, 
Schools of Comp. Sci. and Astrophysics, Univ. Manchester 
*/

typedef unsigned int uint;
uint* HellingerDist(uint k, uint noOfSamples, uint noOfFeatures, uint **featureMatrix, uint *classColumn, uint *outputFeatures, double *featureScores);

double calcHellingerDist(uint* feature, uint* classCol, uint noOfSamples);