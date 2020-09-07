import sys
import os
from sklearn import svm, preprocessing
from joblib import dump, load
import numpy as np
from scipy.sparse import csc_matrix, vstack, hstack
from pkg_resources import resource_filename


sys.setrecursionlimit(100000000)

class Svm:

    def __init__(self):
        self.model = load(resource_filename(__name__, "model.joblib"))
        self.preprocessing = load(resource_filename(__name__, "preprocessing.joblib"))


    def vcc_or_unclassified(self, feature_vector, bag_of_words, threshold=1):
        scaled_feature_vector = self.preprocess(feature_vector)
        confidence = self.model.decision_function(scaled_feature_vector)
        significance_vector = scaled_feature_vector.multiply(self.model.coef_[0])
        metadata_features = significance_vector.tocsc()[0, :387].toarray()

        if self.model.predict(scaled_feature_vector):
            print("Commit is prone to be vulnerable!")
            print("Confidence:", str(confidence[0]))
            print("The most significant feature overall was:" , bag_of_words.get_vocabulary()[significance_vector.argmax()], "score:", significance_vector.max())
            for i, val in enumerate(metadata_features[0]):
                if val == max(metadata_features[0]):
                    score = val
                    index = i
            print("The most significant metadata feature was:" , bag_of_words.get_vocabulary()[index], "score:", score)
            return True
        else:
            print("Commit is not prone to be vulnerable!")
            print("Confidence:", str(confidence[0]))
            print("The most significant feature was:" , bag_of_words.get_vocabulary()[significance_vector.argmin()], "score:", significance_vector.min())
            for i, val in enumerate(metadata_features[0]):
                if val == min(metadata_features[0]):
                    score = val
                    index = i
            print("The most significant metadata feature was:" , bag_of_words.get_vocabulary()[index], "score:", score)
            return False

    def preprocess(self, vector):
        return hstack(( self.preprocessing.transform(vector.tocsc()[0, :303].toarray()), vector.tocsc()[0, 303:].toarray() )).tocsr()
