"""
If there are any pathological candidates that are
mis-classified by all classifiers, print them to
the screen. Requires classifiers to be pre-trained
and saved using evaluate_classifier.
"""
import argparse
import numpy as np

from sklearn.model_selection import StratifiedKFold

from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier

from JACS_utils import ARFF

def main():
    "main"
    parser = argparse.ArgumentParser(
        description="Print any persistently"
        "missclassified candidates to the screen")
    parser.add_argument(
        "--arff", "-a",
        help="arff file containing pulsar data"
    )
    args = parser.parse_args()
    arff_reader = ARFF.ARFF()
    data, labels, _ = arff_reader.read(args.arff)
    data = data[:, range(1, 9)]

    classifiers = []
    classifiers.append(("CART_tree",
                        DecisionTreeClassifier()))
    classifiers.append(("MLP",
                        Pipeline([('scaler', StandardScaler()),
                                  ('mlp', MLPClassifier())])))
    classifiers.append(("Naive_Bayes", GaussianNB()))
    classifiers.append(("SVM",
                        Pipeline([('scaler', StandardScaler()),
                                  ('svc', SVC(class_weight='balanced'))])))
    classifiers.append(("Random_Forest",
                        RandomForestClassifier()))
    classifiers.append(("AdaBoost", AdaBoostClassifier()))
    #problem_cand_list = []
    for _, clf in classifiers:
        skf = StratifiedKFold(n_splits=5)
        #misclass_set = set()
        for train_inds, test_inds in skf.split(data, labels):
            train_x, test_x = data[train_inds], data[test_inds]
            train_y, test_y = labels[train_inds], labels[test_inds]
            clf.fit(train_x, train_y)
            pred_y = clf.predict(test_x)
            misclassified = [row for row, y, y_
                             in zip(test_x, test_y, pred_y)
                             if y == 1 and y != y_]
            for m in misclassified:
                print " ".join([repr(i) for i in m])
    #problem_cands = problem_cand_list[0]
    #for probset in problem_cand_list[1:]:
    #    problem_cands.intersection_update(probset)

 
if __name__ == "__main__":
    main()

