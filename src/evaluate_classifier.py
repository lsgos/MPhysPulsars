"""
Evalute the performance of several classifiers on a dataset in .arff format,
evaluating classification metrics using stratified k-fold cross validation,
and saving fully trained classifiers to disk using joblib.
"""
from __future__ import division
from __future__ import print_function

import argparse
import os
import ast

from JACS_utils.ARFF import ARFF
from JACS_utils.ClassifierStats import ClassifierStats

from sklearn.base import clone
from sklearn.externals import joblib


from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix

from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier




def print_metrics(metrics):
    metric_labels = ["G-Mean","F-Score","Recall","Precision","Specificity","FPR","Accuracy"]
    for l,m in zip(metric_labels, metric):
        print("{} {}, ".format(l,m), end = '')
    print("")

def get_metrics(C, datalen):
    """
    extract the metrics we are interested in from the ClassifierStats class
    returns them in the order listed in the Lyon paper
    """
    metrics = []
    metrics.append(C.getGMean())
    metrics.append(C.getfScore())
    metrics.append(C.getRecall())
    metrics.append(C.getPrecision())
    metrics.append(C.getSpecificity())
    metrics.append(C.getFP() / datalen) #fpr
    metrics.append(C.getAccuracy())
    return metrics

def calculate_metrics(classifier, k_folds, x, y, parallel_workers,shuffle = True):

    skf = StratifiedKFold(n_splits = k_folds, shuffle = shuffle)
    #farm jobs out to the parallel workers
    metrics = parallel_workers(joblib.delayed(_calculate_metrics)(classifier,x,y,split) for split in skf.split(x,y))
    #average over the runs and return results
    return map(lambda x: sum(x) / len(x), zip(*metrics))

def _calculate_metrics(classifier,x,y, split_tup):
    train_index, test_index = split_tup

    clf = clone(classifier) #make sure they are not modified outside the loop

    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]

    clf.fit(x_train, y_train)
    #calculate cross validation metrics
    y_pred = clf.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    stats = ClassifierStats(cm)
    stats.calculate()
    metrics = get_metrics(stats, len(y_test))
    return metrics


if __name__ == "__main__":
    valid_features = set([0,1,2,3,4,5,6,7,8]) #the allowed features

    parser = argparse.ArgumentParser(description = "Evaluates the perfomance \
            of several classifiers on a pulsar dataset in .arff format\n. \
                                    Classifiers used: \
                                    CART Decision Tree, \
                                    Multilayer Perceptron, \
                                    Naive Bayes, \
                                    Support Vector Machine, \
                                    Random Forest, \
                                    AdaBoost")
    parser.add_argument("train", help = "Training set. Should be an arff file")
    parser.add_argument("--select_features",help = "Features to train the \
                    classification on. By default use all except the period. \
                    Period is field 0, fields 1-8 are those from Lyon et. al.\
                     (default = [1,2,3,4,5,6,7,8])", default = "[1,2,3,4,5,6,7,8]")
    parser.add_argument("--save_classifiers",
        help = "Save trained classifiers to disk using joblib in \
                    this path location if provided")
    parser.add_argument("--k_folds","-k",
        default = 5, help = "Number of folds to use for cross validation (default 5)")
    parser.add_argument("--n_jobs","-j",
        default = 4, help = "Number of cores to utilize (recommended: ($nproc), default 4)",type = int)
    args = parser.parse_args()

    try:
        selected_features = ast.literal_eval(args.select_features)
        #test to see if the features are validation
        if len( set(selected_features) - valid_features) > 0:
            raise ValueError

    except ValueError as v:
        print ("Unable to parse selected features: please specify a \
                valid list of integers in the range [0,8]")
        print ("Feature 0 = Period, Features 1-8: See Lyon et. al.")
        quit()

    arff_reader = ARFF()

    train_x, train_y = arff_reader.read(args.train)

    #select features
    train_x = train_x[:,selected_features]


    #fit classifiers
    classifiers = []
    classifiers.append(("CART_tree",DecisionTreeClassifier() ) )
    classifiers.append(("MLP",Pipeline([('scaler', StandardScaler()),('mlp',MLPClassifier())]) ) )
    classifiers.append(("Naive_Bayes",GaussianNB() ) )
    classifiers.append(("SVM",Pipeline([('scaler', StandardScaler()), ('svc',SVC(class_weight = 'balanced') )])))
    classifiers.append(("Random_Forest",RandomForestClassifier() ))
    classifiers.append(("AdaBoost", AdaBoostClassifier() ))

    #cross validation is embarrassingly parallel: parallelize the calculation for speed, re-using the worker pool.
    with joblib.Parallel(n_jobs = args.n_jobs) as parallel_workers:
        metrics = [(name,calculate_metrics(clf, args.k_folds, train_x, train_y, parallel_workers) ) for name, clf in classifiers]
    #print metrics
    for name, metric in metrics:
        print("{}:".format(name))
        print_metrics(metrics)


    if args.save_classifiers is not None:
        if not os.path.exists(args.save_classifiers):
            raise IOError("Cannot find path specified to save classifiers to")
        for name,clf in classifiers:
            #fit on the whole training set and save the classifier
            clf.fit(train_x,train_y)
            joblib.dump(clf, os.path.join(args.save_classifiers,(name+".pkl")))
