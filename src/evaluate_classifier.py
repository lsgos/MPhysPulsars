"""
Evalute the performance of several classifiers on a dataset in .arff format,
evaluating classification metrics using stratified k-fold cross validation,
and saving fully trained classifiers to disk using joblib.
"""
from __future__ import division
from __future__ import print_function

import argparse
import os

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

def calculate_metrics(classifier, k_folds, x, y, n_jobs,shuffle = True):

    skf = StratifiedKFold(n_splits = k_folds, shuffle = shuffle)
    metrics = joblib.Parallel(n_jobs = n_jobs)(joblib.delayed(_calculate_metrics)(classifier,x,y,split) for split in skf.split(x,y))
    return map(lambda x: sum(x) / len(x), zip(*metrics))

def _calculate_metrics(classifier,x,y, split_tup):
    train_index, test_index = split_tup

    clf = clone(classifier)

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

def _paralleliser(clf_tup):
    return (name,calculate_metrics(clf, args.k_folds, train_x, train_y))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Evaluates the perfomance of several classifiers on a pulsar dataset in .arff format\n. \
                                            Classifiers used: \
                                            CART Decision Tree, \
                                            Multilayer Perceptron, \
                                            Naive Bayes, \
                                            Support Vector Machine, \
                                            Random Forest, \
                                            AdaBoost")
    parser.add_argument("train", help = "Training set. Should be an arff file")
    parser.add_argument("--ignore_period", type = bool, default = True, help = "By default, assume the period is the first field of the arff file, and ignore it (default True)")
    parser.add_argument("--save_classifiers", help = "Save trained classifiers to disk using joblib in this path location if provided")
    parser.add_argument("--k_folds","-k", default = 5, help = "Number of folds to use for cross validation (default 5)")
    parser.add_argument("--n_jobs","-j", default = 4, help = "Number of cores to parallelise over")
    args = parser.parse_args()

    arff_reader = ARFF()

    train_x, train_y = arff_reader.read(args.train)

    if args.ignore_period:
        train_x = train_x[:,1:] #remove the first feature: this is included to sort the pulsars out, not to fit on

    #fit classifiers
    classifiers = []
    classifiers.append(("CART_tree",DecisionTreeClassifier() ) )
    classifiers.append(("MLP",Pipeline([('scaler', StandardScaler()),('mlp',MLPClassifier())]) ) )
    classifiers.append(("Naive_Bayes",GaussianNB() ) )
    classifiers.append(("SVM",Pipeline([('scaler', StandardScaler()), ('svc',SVC(class_weight = 'balanced') )])))
    classifiers.append(("Random_Forest",RandomForestClassifier() ))
    classifiers.append(("AdaBoost", AdaBoostClassifier() ))
    metrics = [(name,calculate_metrics(clf, args.k_folds, train_x, train_y, args.n_jobs) ) for name, clf in classifiers]
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
