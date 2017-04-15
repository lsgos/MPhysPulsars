"""
A One class SVM semi-supervised classifier 
"""
from sklearn.svm import OneClassSVM
from sklearn.tree import DecisionTreeClassifier

class OneClassSVMClassifier(object):
    """
    A class that uses a One Class SVM novelty detection algorithm to 
    classify examples
    """
    def __init__(self, gamma = 'auto', kernel = 'rbf', nu = 0.5, noise_label=0):
        self.svm = OneClassSVM(gamma=gamma, kernel =kernel, nu=nu)
        self.stump = DecisionTreeClassifier(max_depth=1, criterion='entropy')
        self.noise_label = noise_label

    def fit(self, X, Y):
        """
        Fit the isolation forest only on negative data, then train a threshold 
        stump on the isolation score
        """
        train_noise = X [Y == self.noise_label]
        #fit the isolation forest 
        self.svm.fit(train_noise)

        anomaly_train = self.svm.decision_function(X).reshape(-1,1)
        self.stump.fit(anomaly_train, Y)

    def predict(self, X):
        anomaly_scores = self.svm.decision_function(X).reshape(-1,1)
        return self.stump.predict(anomaly_scores)
    def decision_function(self, X):
        return (-1) * self.svm.decision_function(X)
    def score(self, X, Y):
        """Accuracy score for the classifier """
        anomaly_scores = self.svm.decision_function(X).reshape(-1,1)
        return self.stump.score(anomaly_scores, Y)

