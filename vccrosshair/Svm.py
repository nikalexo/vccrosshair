import sys
import os
from sklearn.model_selection import cross_val_score
from sklearn import svm, preprocessing
from sklearn.ensemble import BaggingClassifier
import sqlite3
from joblib import dump, load
import numpy as np
from scipy.sparse import csc_matrix, vstack, hstack


sys.setrecursionlimit(100000000)

class Svm:

    def __init__(self):
        self.model = load(os.path.dirname(os.path.realpath(__file__))+"/model.joblib")
        self.preprocessing = load(os.path.dirname(os.path.realpath(__file__))+"/preprocessing.joblib")


    def vcc_or_unclassified(self, feature_vector, threshold=1):
        scaled_feature_vector = self.preprocess(feature_vector)
        confidence = self.model.decision_function(scaled_feature_vector)
        significance_vector = scaled_feature_vector.multiply(self.model.coef_[0])

        if self.model.predict(scaled_feature_vector): #confidence[0] > threshold:
            print("Commit is prone to be vulnerable!")
            print("Confidence:", str(confidence[0]))
            # print("The significant feature was:" , str(significance_vector.argmax()), "with score", str(significance_vector.max()) + "\n")
            return True
        else:
            print("Commit is not prone to be vulnerable!")
            print("Confidence:", str(confidence[0]))
            return False

    def preprocess(self, vector):
        return hstack(( self.preprocessing.transform(vector.tocsc()[0, :303].toarray()), vector.tocsc()[0, 303:].toarray() )).tocsr()

