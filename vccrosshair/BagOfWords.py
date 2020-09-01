import subprocess
import os
from joblib import dump
import glob
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

class BagOfWords:

	def __init__(self):
		self.word_vect = CountVectorizer()
		self.word_transformer = TfidfTransformer()

	def load_bag_of_words(self):
		with open(os.path.dirname(os.path.realpath(__file__))+"/words.txt", "r+") as w:
			word_counts = self.word_vect.fit_transform(w)
			self.word_transformer.fit_transform(word_counts)
		
	def get_word_vect(self, words):
		new_word_counts = self.word_vect.transform(words)
		return self.word_transformer.transform(new_word_counts)

	def save_bag_of_words(self, name):
                dump(self, "Models/"+name+"_bag_of_words.joblib")
