"""
A class factory to abstract the creation of a semi-supervised classifier 
from a novelty detection method 
"""
from sklearn.tree import DecisionTreeClassifier

class SemiSupervisedClassifier(object):
    def __init__(self, novelty_detector, noise_label = 0):
        self.novelty_clf = novelty_detector
        self.stump = DecisionTreeClassifier(max_depth=1, criterion='entropy')
        self.noise_label = noise_label

    def fit(self, X, Y):
        """
        Fit the isolation forest only on negative data, then train a threshold 
        stump on the isolation score
        """
        train_noise = X [Y == self.noise_label]
        #fit the isolation forest 
        self.novelty_clf.fit(train_noise)

        #transform the dataset using the outlier detector and train the 
        #stump to pick the threshold 

        anomaly_train = self.novelty_clf.decision_function(X).reshape(-1,1)
        self.stump.fit(anomaly_train, Y)

    def predict(self, X):
        anomaly_scores = self.novelty_clf.decision_function(X).reshape(-1,1)
        return self.stump.predict(anomaly_scores)
    def decision_function(self, X):
        return (-1) * self.novelty_clf.decision_function(X)
    def score(self, X, Y):
        """Accuracy score for the classifier """
        anomaly_scores = self.novelty_clf.decision_function(X).reshape(-1,1)
        return self.stump.score(anomaly_scores, Y)
