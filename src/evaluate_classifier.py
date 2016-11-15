"""
Evalute the performance of several classifiers on a dataset in .arff format,
evaluating classification metrics using stratified k-fold cross validation,
and saving fully trained classifiers to disk using joblib if desired.

This code represents our data analysis, and should be usable to reproduce any results we obtain
"""
from __future__ import division
from __future__ import print_function

try:
    import termcolor
    TERMCOLOR = True
except ImportError as e:
    TERMCOLOR = False


import argparse
import os
import ast
import numpy as np

from scipy.stats import ttest_rel

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

args = None


def print_metrics(metrics):
    metric_labels = ["G-Mean","F-Score","Recall","Precision","Specificity","FPR","Accuracy"]
    if TERMCOLOR:
        metric_labels = map(lambda s: termcolor.colored(s,'cyan'), metric_labels)
    for l,(m, stdev) in zip(metric_labels, metrics):
        print("{} {:.4f} +/- {:.4f}, ".format(l,m, stdev), end = '')
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
def mean_calc(l):
    #calculate the mean and standard deviation of a list
    n = len(l)
    mean = sum(l) / n
    stdev = np.sqrt( 1 / (n - 1) * sum([(x - mean)**2 for x in l]))
    return (mean,stdev)

def calculate_metrics_k_fold(classifier, k_folds, x, y, msp_label, parallel_workers, args,shuffle = True):

    skf = StratifiedKFold(n_splits = k_folds, shuffle = shuffle)
    #farm jobs out to the parallel workers
    metrics,msp_recalls = zip (* (parallel_workers(joblib.delayed(_calculate_metrics)(classifier,x,y,msp_label,split,args) for split in skf.split(x,y)) ) )

    metlist = zip(* metrics)


    if args.show_msp_results:
        msp_recall_list = zip(*msp_recalls)[0]
        recalls = metlist[2] #get just the recalls to compare
        msp_recall_list,recalls = zip(*[(m,r) for m,r in zip(msp_recall_list,recalls) if r is not None])
        t_stat, p_val = ttest_rel(recalls,msp_recall_list)
        return (map(mean_calc, metlist), mean_calc(msp_recall_list),(t_stat,p_val))

    return (map(mean_calc, metlist), None,None)

def _calculate_metrics(classifier,x,y,msp_label, split_tup,args):

    train_index, test_index = split_tup


    clf = clone(classifier) #make sure they are not modified outside the loop

    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]
    msp_label_test = msp_label[test_index]

    clf.fit(x_train, y_train)
    #calculate cross validation metrics
    metrics =  fit_metrics(clf,x_test,y_test)
    #split of msps if this flag is set

    if args.show_msp_results:
        msp_x_test = x_test[np.where(msp_label_test)]  #should there be a test in case this is of zero length?
        msp_y_test = y_test[np.where(msp_label_test)]
        if len(msp_x_test) == 0:
            #No msp's in this fold: could happen
            return (metrics,[None])
        msp_metrics = [clf.score(msp_x_test, msp_y_test)] #only the accuracy is really meaningful here

        return (metrics,msp_metrics)
    return (metrics,[None])

def score_test_k_fold(classifier,k_folds, train_x,train_y,test_x,test_y,parallel_workers):
    #score the test set by training stratified folds of the test set to get an
    #estimate of the mean and standard deviation for significance tests.
    skf = StratifiedKFold(n_splits = k_folds, shuffle = True)

    scores = parallel_workers(
        joblib.delayed(_score_test)(classifier,train_x,train_y,test_x,test_y,split) \
        for split in skf.split(train_x,train_y ))
    return mean_calc(scores)


def _score_test(classifier,x,y,test_x,test_y, split_tup):
    train_index,_ = split_tup
    clf = clone(classifier)
    x_train,y_train = x[train_index], y[train_index]

    clf.fit(x_train,y_train)
    score = clf.score(test_x,test_y)

    return score

def fit_metrics(classifier, x_test, y_test):
    #calculate statistics for a trained classifier on a test set
    y_pred = classifier.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    #ipdb.set_trace()
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
    parser.add_argument("--test", help = "Testing set (optional). If this argument \
                        is supplied, the classifiers trained on the training set \
                        are tested on this set")
    parser.add_argument("--select_features","-f",help = "Features to train the \
                    classification on. By default use all except the period. \
                    Period is field 0, fields 1-8 are those from Lyon et. al.\
                     (default = [1,2,3,4,5,6,7,8])", default = "[1,2,3,4,5,6,7,8]")
    parser.add_argument("--save_classifiers",
        help = "Save trained classifiers to disk using joblib in \
                    this path location if provided")
    parser.add_argument("--k_folds","-k",
        default = 5,type = int, help = "Number of folds to use for cross validation (default 5)")
    parser.add_argument("--n_jobs","-j",
        default = 4, help = "Number of cores to utilize (recommended: ($nproc), default 4)",type = int)
    parser.add_argument("--show_msp_results","-s",type = bool, default = False,
                        help = "Whether to show seperate cross-validation metrics \
                        for msp's based on comment tags (***MSP***) in the arff file")
    parser.add_argument("--termcolor", help = "If the termcolor library is present, \
                        print with pretty colors. default true", type = bool, default = True)

    args = parser.parse_args()

    TERMCOLOR = TERMCOLOR and args.termcolor

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
    try:
        train_x, train_y, train_labelled_msp = arff_reader.read(args.train)
        if args.show_msp_results:
            assert(len(train_labelled_msp[train_labelled_msp == True]) > 0)

    except IOError as e:
        print("Cannot open training data file: does it exist?")
        quit()
    except AssertionError as e:
        print("Cannot provide seperate MSP validation if no data points are labelled as msp's. Msp's should be labelled with a %***MSP*** comment in the arff file")
        quit()
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
        metrics = [(name,calculate_metrics_k_fold(clf, args.k_folds, train_x, train_y, train_labelled_msp,  parallel_workers, args) ) for name, clf in classifiers]
    #print metrics
    print("\t----------CROSS VALIDATION RESULTS--------------")
    for name, (metric, msp_metric, t_stats) in metrics:
        if TERMCOLOR:
            name = termcolor.colored(name,'blue')
        print("{}:".format(name))
        print_metrics(metric)
        if msp_metric is not None:
            m,stdev = msp_metric
            t_stat,p = t_stats
            if TERMCOLOR:
                if p < 0.05:
                    strp = termcolor.colored(str(p),'green')
                else:
                    strp = termcolor.colored(str(p),'red')
            else:
                strp = str(p)
            strp.format()
            print("Accuracy (recall) on labelled MSPs only: {:.3} +/- {:.3}. P value is {}".format(m,stdev,strp))


    if args.save_classifiers is not None:
        for name,clf in classifiers:
            #fit on the whole training set and save the classifier
            clf.fit(train_x,train_y)
        if not os.path.exists(args.save_classifiers):
            raise IOError("Cannot find path specified to save classifiers to")
            joblib.dump(clf, os.path.join(args.save_classifiers,(name+".pkl")))

    if args.test is not None:
        try:
            test_x, test_y,_ = arff_reader.read(args.test)
            test_x = test_x[:,selected_features]

        except IOError as e:
            print("Cannot open training file: does it exist?")
            quit()
        with joblib.Parallel(n_jobs = args.n_jobs) as parallel_workers:
            test_metrics = [(name, score_test_k_fold(clf,args.k_folds,train_x,train_y,test_x,test_y,parallel_workers)) for name,clf in classifiers]
        print("\t----------TEST SET RESULTS (Accuracy)--------------")
        for name,metric in test_metrics:
            if TERMCOLOR:
                name = termcolor.colored(name,'cyan')
            mean,stdev = metric
            print("{}: {} +/- {}".format(name, mean,stdev))
