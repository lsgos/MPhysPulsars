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
from sklearn.svm import SVC, LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier


#my own custom classifier 

from IsolationClassifier import IsolationTreeClassifier, IsolationRatioClassifier

#Helper functions. These cannot go in the class because we are using parallel computation


def _calculate_metrics(clf, x, y, msp_label, show_msp_results, split_tup):

    train_index, test_index = split_tup
    #clf = clone(classifier) #make sure they are not modified outside the loop

    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]
    msp_label_test = msp_label[test_index]
    clf.fit(x_train, y_train)
    #calculate cross validation metrics
    metrics = fit_metrics(clf, x_test, y_test)

    #split off msps if this flag is set
    if show_msp_results:
        msp_x_test = x_test[np.where(msp_label_test)]
        #should there be a test in case this is of zero length?
        msp_y_test = y_test[np.where(msp_label_test)]
        if len(msp_x_test) == 0:
            #No msp's in this fold: could happen
            return (metrics, [None])
        msp_metrics = [clf.score(msp_x_test, msp_y_test)]
        #only the accuracy is really meaningful here
        return (metrics, msp_metrics)
    return (metrics, [None])

def fit_metrics(classifier, x_test, y_test):
    #calculate statistics for a trained classifier on a test set
    y_pred = classifier.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    #ipdb.set_trace()
    stats = ClassifierStats(cm)
    stats.calculate()
    metrics = _get_metrics(stats, len(y_test))
    return metrics

def _get_metrics(C, datalen):
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

def _score_test(clf,x,y,test_x,test_y, split_tup):
    train_index,_ = split_tup
    #clf = clone(classifier)
    x_train,y_train = x[train_index], y[train_index]
    clf.fit(x_train,y_train)
    score = clf.score(test_x,test_y)

    return score

class Evaluator:

    def __init__(self,train_x,train_y, msp_labels, k_folds, n_jobs = None, show_msp_results = False, shuffle_train = True, use_termcolor = True):
        """
        Constructor, initialise the evaluator class with command line options
        """
        self.k_folds = k_folds
        self.train_x = train_x
        self.train_y = train_y
        self.msp_labels = msp_labels
        self.shuffle_train = shuffle_train
        self.termcolor = use_termcolor
        self.show_msp_results = show_msp_results
        self.n_jobs = n_jobs

        self.classifiers = []
        self.classifiers.append(("CART_tree", DecisionTreeClassifier()))
        self.classifiers.append(("MLP", Pipeline([('scaler', StandardScaler()), ('mlp',MLPClassifier())])))
        self.classifiers.append(("Naive_Bayes", GaussianNB()))
        self.classifiers.append(("SVM", Pipeline([('scaler', StandardScaler()), ('svc',SVC(class_weight ='balanced'))])))
        self.classifiers.append(("Linear SVM", Pipeline([('scaler', StandardScaler()), ('svc',LinearSVC(class_weight ='balanced'))])))
        self.classifiers.append(("Random_Forest", RandomForestClassifier()))
        self.classifiers.append(("AdaBoost", AdaBoostClassifier()))
        self.classifiers.append(("IsolationForestClassifier", IsolationTreeClassifier(max_samples=8000)))
        self.classifiers.append(("IsolationRatioClassifier (currently training on noise only)", IsolationRatioClassifier(max_samples=8000)))
        self.metric_labels = ["G-Mean", "F-Score", "Recall", "Precision", "Specificity", "FPR", "Accuracy"]

        self.metrics = None
        self.test_metrics = None

        if self.termcolor:
            self.metric_labels = map(lambda s: termcolor.colored(s, 'cyan'), self.metric_labels)

    def calculate(self):
        with joblib.Parallel(n_jobs = self.n_jobs) as parallel_workers:
            self.metrics = [(name,self.calculate_metrics_k_fold(clf,self.train_x, self.train_y, self.msp_labels,  parallel_workers) ) for name, clf in self.classifiers]

    def calculate_test(self, test_x, test_y):
        with joblib.Parallel(n_jobs = self.n_jobs) as parallel_workers:
            self.test_metrics = [(name, self.score_test_k_fold(clf,test_x,test_y,parallel_workers)) for name,clf in self.classifiers]

    def pretty_print_cross_val(self):
        print("\t----------CROSS VALIDATION RESULTS--------------")
        for name, (metric, msp_metric, t_stats) in self.metrics:
            if self.termcolor:
                name = termcolor.colored(name,'blue')
            print("{}:".format(name))
            self.print_metrics(metric)
            if msp_metric is not None:
                m,stdev = msp_metric
                t_stat,p = t_stats
                if self.termcolor:
                    if p < 0.05:
                        strp = termcolor.colored(str(p),'green')
                    else:
                        strp = termcolor.colored(str(p),'red')
                else:
                    strp = str(p)
                strp.format()
                print("Accuracy (recall) on labelled MSPs only: {:.3}, stdev {:.3}. P value is {}".format(m,stdev,strp))
    def pretty_print_test_stats(self):
        assert self.test_metrics is not None, "test metrics have not been calculated yet"


        print("\t----------TEST SET RESULTS (Accuracy)--------------")
        for name,metric in self.test_metrics:
            if self.termcolor:
                name = termcolor.colored(name,'cyan')
            mean,stdev = metric
            print("{}: {}, stdev {}".format(name, mean,stdev))

    def print_simple_output(self):
        """
        Print the output in a simplified format: just the recall for each classifier, then the recall on the labelled set
        """
        for name,(metrics,msp_metrics, t_stats) in self.metrics:
            recall,r_stdev = metrics[2]
            msp_recall, m_stdev = msp_metrics
            print(recall, r_stdev, msp_recall, m_stdev, end = " ")
        print()

    def dump_classifiers(self, savepath):
        if not os.path.exists(savepath):
            raise IOError("Cannot find path specified to save classifiers to")
        for name,clf in self.classifiers:
            #fit on the whole training set and save the classifier
            clf.fit(self.train_x,self.train_y)
            joblib.dump(clf, os.path.join(savepath,(name+".pkl")))

    def print_metrics(self, metrics):
        for l,(m, stdev) in zip(self.metric_labels, metrics):
            print("{} {:.4f} stdev {:.4f}, ".format(l,m, stdev), end = '')
        print("")


    def _mean_calc(self,l):
        #calculate the mean and standard deviation of a list
        n = len(l)
        mean = sum(l) / n
        stdev = np.sqrt( 1 / (n - 1) * sum([(x - mean)**2 for x in l]))
        return (mean,stdev)
    def calculate_metrics_k_fold(self,classifier, x, y, msp_label, parallel_workers):

        skf = StratifiedKFold(n_splits = self.k_folds, shuffle = self.shuffle_train)
        #farm jobs out to the parallel workers
        metrics,msp_recalls = zip (* (parallel_workers(joblib.delayed(_calculate_metrics)(classifier,x,y,msp_label,self.show_msp_results,split) for split in skf.split(x,y)) ) )

        metlist = zip(* metrics)
        if self.show_msp_results:
            msp_recall_list = zip(*msp_recalls)[0]
            recalls = metlist[2] #get just the recalls to compare
            msp_recall_list,recalls = zip(*[(m,r) for m,r in zip(msp_recall_list,recalls) if r is not None])
            t_stat, p_val = ttest_rel(recalls,msp_recall_list)
            return (map(self._mean_calc, metlist), self._mean_calc(msp_recall_list),(t_stat,p_val))
        return (map(self._mean_calc, metlist), None,None)

    def score_test_k_fold(self,classifier,test_x,test_y, parallel_workers):
        #score the test set by training stratified folds of the test set to get an
        #estimate of the mean and standard deviation for significance tests.
        skf = StratifiedKFold(n_splits = self.k_folds, shuffle = True)
        scores = parallel_workers(joblib.delayed(_score_test)(classifier,self.train_x,self.train_y,test_x,test_y,split) for split in skf.split(self.train_x,self.train_y))
        return self._mean_calc(scores)




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
    parser.add_argument("--show_msp_results","-s",action = "store_true",
                        help = "Whether to show seperate cross-validation metrics \
                        for msp's based on comment tags (***MSP***) in the arff file (default false)")
    parser.add_argument("--no_termcolor", help = "If the termcolor library is present, \
                        print with pretty colors. default true", action = "store_true")

    parser.add_argument("--simple_output", help = "If this flag is present, print results in an easily parsable, less human readable format", action = "store_true")
    args = parser.parse_args()

    TERMCOLOR = TERMCOLOR and (not args.no_termcolor)

    try:
        selected_features = ast.literal_eval(args.select_features)
        #test to see if the features are valid
        if len( set(selected_features) - valid_features) > 0:
            raise ValueError

    except ValueError as v:
        print ("Unable to parse selected features: please specify a \
                valid list of integers in the range [0,8]")
        print ("Feature 0 = Period, Features 1-8: See Lyon et. al.")
        raise v

    arff_reader = ARFF()
    try:
        train_x, train_y, train_labelled_msp = arff_reader.read(args.train)
        if args.show_msp_results:
            assert(len(train_labelled_msp[train_labelled_msp == True]) > 0)

    except IOError as e:
        print("Cannot open training data file: does it exist?")
        raise e
    except AssertionError as e:
        print("Cannot provide seperate MSP validation if no data points are labelled as msp's. Msp's should be labelled with a %***MSP*** comment in the arff file")
        raise e

    #select features

    train_x = train_x[:,selected_features]

    evaluator = Evaluator(train_x,train_y, train_labelled_msp, args.k_folds, args.n_jobs,args.show_msp_results, use_termcolor = TERMCOLOR)

    evaluator.calculate()

    if args.save_classifiers is not None:
        evaluator.dump_classifiers(args.save_classifiers)
    if args.test is not None:
        try:
            test_x, test_y,_ = arff_reader.read(args.test)
            test_x = test_x[:,selected_features]
        except IOError as e:
            print("Cannot open testing file: does it exist?")
            raise e
        evaluator.calculate_test(test_x,test_y)

    #printing of output
    if not args.simple_output:
        evaluator.pretty_print_cross_val()
        if args.test:
            evaluator.pretty_print_test_stats()
    else:

        evaluator.print_simple_output()
