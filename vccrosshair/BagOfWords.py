import subprocess
import os
from joblib import dump, load
import glob
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from pkg_resources import resource_filename

class BagOfWords:

	def __init__(self):
		self.word_vect = load(resource_filename(__name__, "word_vector.joblib"))
		self.word_transformer = load(resource_filename(__name__, "word_transformer.joblib"))

	def get_word_vect(self, words):
		new_word_counts = self.word_vect.transform(words)
		return self.word_transformer.transform(new_word_counts)

	def get_vocabulary(self):
		with open(resource_filename(__name__, "vocabulary.txt"), "r") as voc:
			vocabulary = voc.readlines()

		return vocabulary + ["Appearance of token '" + v + "'" for v, i in sorted(self.word_vect.vocabulary_.items(), key=lambda item: item[1])]
