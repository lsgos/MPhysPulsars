"""
Use principal component analysis to improve FRB classification
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier

class PCA_Classifier(object):
    def __init__(self, n_components= 2, noise_label = 0):
        self.pca = PCA(n_components = n_components, svd_solver = 'full')
        self.stump = DecisionTreeClassifier(max_depth=1, criterion='entropy')
        self.noise_label = noise_label

    def fit(self, data, lab):
        self.noise_ratio = ((lab == self.noise_label).astype(np.float).sum() / lab.shape[0] )
        noise_fitting_data = data[lab == self.noise_label]
        self.pca.fit(noise_fitting_data)
        scores = self.pca.score_samples(data).reshape(-1,1)
        self.stump.fit(scores, lab)

    def predict(self, data):
        scores = self.pca.score_samples(data).reshape(-1,1)
        return self.stump.predict(scores)

    def decision_function(self, data):
        return (1 - self.pca.score_samples(data))
