"""
A simple model defining a 'semi-supervised' classifier based on isolation trees: 
it fits a tree to the negatives in the dataset, then trains a decision 
stump on the anomaly scores given by the isolation tree. 

It is defined here to present a unified sklearn type API 
"""
from __future__ import division
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.tree import DecisionTreeClassifier


class IsolationTreeClassifier(object):
    """
    A semi-supervised classifier designed for imbalanced 
    problems where the positive class can be considered as 
    outliers to the negative distribution 
    """
    def __init__(self, max_samples = 256, n_estimators=100, noise_label=0):
        self.iForest = IsolationForest(max_samples = max_samples, n_estimators=n_estimators)
        self.stump = DecisionTreeClassifier(max_depth=1, criterion='entropy')
        self.noise_label = noise_label

    def fit(self, X, Y):
        """
        Fit the isolation forest only on negative data, then train a threshold 
        stump on the isolation score
        """
        train_noise = X [Y == self.noise_label]
        #fit the isolation forest 
        self.iForest.fit(train_noise)

        #transform the dataset using the outlier detector and train the 
        #stump to pick the threshold 

        anomaly_train = self.iForest.decision_function(X).reshape(-1,1)
        self.stump.fit(anomaly_train, Y)

    def predict(self, X):
        anomaly_scores = self.iForest.decision_function(X).reshape(-1,1)
        return self.stump.predict(anomaly_scores)
    def decision_function(self, X):
        return (-1) * self.iForest.decision_function(X)
    def score(self, X, Y):
        """Accuracy score for the classifier """
        anomaly_scores = self.iForest.decision_function(X).reshape(-1,1)
        return self.stump.score(anomaly_scores, Y)



class IsolationRatioClassifier(object):
    """
    A semi-supervised classifier designed for imbalanced 
    problems where the positive class can be considered as 
    outliers to the negative distribution 
    """
    def __init__(self, max_samples = 256, n_estimators=100, noise_label=0):
        self.iForest = IsolationForest(max_samples = max_samples, n_estimators=n_estimators)
        self.noise_ratio = None
        self.noise_label = noise_label

    def fit(self, X, Y):
        """
        Fit the isolation forest only on negative data, then train a threshold 
        stump on the isolation score
        """

        #NB: We training on noise only is much better at finding pulsars 
        #Maybe you should change this back and look at it in the report ...
        #THIS IS IMPORTANT DO NOT FORGET YOU DID IT 
        self.noise_ratio = ((Y == self.noise_label).astype(np.float).sum() / Y.shape[0] )
        train_noise = X [Y == self.noise_label]
        self.iForest.contamination = (1 -self.noise_ratio)
        self.iForest.fit(train_noise)

    def predict(self, X):
        preds = self.iForest.predict(X)
        preds[preds == 1] = self.noise_label
        preds[preds == -1] = 1
        return preds


    def decision_function(self, X):
        return (-1) * self.iForest.decision_function(X)
    def score(self, X, Y):
        """Accuracy score for the classifier """
        Y_ = self.predict(X)
        return (Y == Y_).astype(np.float).sum() / X.shape[0]