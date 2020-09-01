import subprocess
import os
from joblib import dump, load
import glob
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

class BagOfWords:

	def __init__(self):
		self.word_vect = load(os.path.dirname(os.path.realpath(__file__))+"/word_vector.joblib")
		self.word_transformer = load(os.path.dirname(os.path.realpath(__file__))+"/word_transformer.joblib")

	def get_word_vect(self, words):
		new_word_counts = self.word_vect.transform(words)
		return self.word_transformer.transform(new_word_counts)
