from git import Repo, GitCommandError
import numpy as np
import re
from scipy.sparse import csc_matrix, save_npz, hstack
import math
from .BagOfWords import BagOfWords
import time
import json

class Commit:

	def __init__(self, repo_path, commit):
		# initialize features
		self.features_raw = {
			"repo" : "",
			"hash" : "",
			"past_different_authors" : 0,
			"file_count" : 0,
			"past_changes" : 0,
			"hunk_count" : 0,
			"author_contribution_percent" : 0.0,
			"author_touch_count" : 0,
			"authored_day" : "",
			"authored_hour" : 0,
			"commit_message" : "",
			"added_code" : "",
			"deleted_code" : ""
		}

		self.feature_vector = csc_matrix([])
		self.got_features = False
		self.commit = commit
		self.bag_of_words = BagOfWords()
		self.bag_of_words.load_bag_of_words()
		self.repo_path = repo_path

	def extract_features(self):
		
		#load repo
		self.repo = Repo(self.repo_path)
		if self.repo.bare:
			raise Exception('Found bare repository under \'{0}\'!'.format(path))
		self.features_raw["repo"] = self.repo_path.split("/")[-1]

		self.features_raw["hash"] = str(self.commit)

		# load commit
		self.commit = self.repo.commit(self.commit)

		# skip merge commits
		if (len(self.commit.parents) > 1):
			raise ValueError("Merge commit, skipping", str(self.commit))


		self.features_raw["commit_message"] = self.commit.message

		# handle initial commit
		if len(self.commit.parents) == 0:
			self.commit.parents = [self.repo.tree("4b825dc642cb6eb9a060e54bf8d69288fbee4904")]

		# extract commit information
		files = set()
		for parent in self.commit.parents:
			diffs = parent.diff(self.commit, create_patch=True, unified=0)

			for diff in diffs:
				if is_code_file(diff.a_path):
					files.add(diff.a_path)
				elif is_code_file(diff.b_path):
					files.add(diff.b_path)
				else:
					continue

				local_changes = str(diff).split("@@ -")
				del local_changes[0]
				for local_change in local_changes:
					for line in local_change.splitlines():
						if line != "" and line != "---":
							if line[0] == "+":
								self.features_raw["added_code"] += line[1:]+"\n"
							elif line[0] == "-":
								self.features_raw["deleted_code"] += line[1:]+"\n"

							elif line[0].isdigit():
								self.features_raw["hunk_count"] += 1

					if (len((self.features_raw["added_code"].splitlines()) + self.features_raw["deleted_code"].splitlines())) > 2000:
						raise ValueError("Commit too long, skipping", str(self.commit))


		# extract file information
		if len(files) == 0:
			raise ValueError("Commit does not alter C files, skipping", str(self.commit))
		self.features_raw["file_count"] = len(files)
		past_authors = set()
		for file_name in files:
			history = self.repo.git.rev_list("--format=short", "--skip=1", str(self.commit), "--", file_name)
			for line in history.splitlines():
				if line[:7] == "commit ":
					# feature: past changes
					self.features_raw["past_changes"] += 1
				if line[:8] == "Author: ":
					if str(self.commit.author) in line:
						self.features_raw["author_touch_count"] += 1
					if line not in past_authors:
						past_authors.add(line)
						# feature: past different authors
						self.features_raw["past_different_authors"] += 1
		
		
		# extract information about time of authoring
		time = self.repo.git.show("--no-patch", "--no-notes", "--pretty='%ad'", str(self.commit))[1:].split()
		self.features_raw["authored_day"] = time[0]
		self.features_raw["authored_hour"] = int(time[3][:2])

		# extract contribution information
		author_contributions = int(self.repo.git.rev_list(str(self.commit), "--author", self.commit.author, "--count"))
		commit_count = int(self.repo.git.rev_list(str(self.commit), "--count"))
		self.features_raw["author_contribution_percent"] = (author_contributions / commit_count)
		self.got_features = True

	def get_feature_vector(self):
		features = []
		if not self.got_features:
			return

		# commit features
		features.append(self.features_raw["past_different_authors"])
		features.append(self.features_raw["past_different_authors"]/self.features_raw["file_count"])

		added_line_count = len(self.features_raw["added_code"].splitlines())
		features.append(added_line_count)
		features.append(added_line_count/self.features_raw["file_count"])

		deleted_line_count = len(self.features_raw["deleted_code"].splitlines())
		features.append(deleted_line_count)
		features.append(deleted_line_count/self.features_raw["file_count"])

		if self.features_raw["past_changes"] != 0:
			features.append(self.features_raw["author_touch_count"]/self.features_raw["past_changes"])
			assert(features[-1] <= 1)
			features.append(self.features_raw["author_touch_count"]/self.features_raw["past_changes"]/self.features_raw["file_count"])
		else:
			features.append(1)
			features.append(1)

		features.append(self.features_raw["past_changes"])
		features.append(self.features_raw["past_changes"]/self.features_raw["file_count"])
		features.append(self.features_raw["author_touch_count"])
		features.append(self.features_raw["author_touch_count"]/self.features_raw["file_count"])
		features.append(self.features_raw["hunk_count"])
		features.append(self.features_raw["hunk_count"]/self.features_raw["file_count"])

		# added functions
		added_functions = len(re.findall(r'\s*(?:(?:inline|static)\s+){0,2}\w+\s+\*?\s*\w+\s*\([^!@#$+%^;]+?\)\s*\{', self.features_raw["added_code"]))
		features.append(added_functions)
		# deleted functions
		deleted_functions = len(re.findall(r'\s*(?:(?:inline|static)\s+){0,2}\w+\s+\*?\s*\w+\s*\([^!@#$+%^;]+?\)\s*\{', self.features_raw["deleted_code"]))
		features.append(deleted_functions)

		if added_line_count != 0:
			features.append(added_functions/added_line_count)
		else:
			features.append(0)

		if deleted_line_count != 0:
			features.append(deleted_functions/deleted_line_count)
		else:
			features.append(0)
		features.append(self.features_raw["file_count"])

		# author feature
		features.append(self.features_raw["author_contribution_percent"])

		# keyword features
		added_keywords = {
			"auto" : 0,
			"break" : 0,
			"case" : 0,
			"char" : 0,
			"const" : 0,
			"continue" : 0,
			"default" : 0,
			"do" : 0,
			"double" : 0,
			"else" : 0,
			"enum" : 0,
			"extern" : 0,
			"float" : 0,
			"for" : 0,
			"goto" : 0,
			"if" : 0,
			"int" : 0,
			"long" : 0,
			"register" : 0,
			"return" : 0,
			"short" : 0,
			"signed" : 0,
			"sizeof" : 0,
			"static" : 0,
			"struct" : 0,
			"switch" : 0,
			"typedef" : 0,
			"union" : 0,
			"unsigned" : 0,
			"void" : 0,
			"volatile" : 0,
			"while" : 0,
			"asm" : 0,
			"dynamic_cast" : 0,
			"namespace" : 0,
			"reinterpret_cast" : 0,
			"try" : 0,
			"bool" : 0,
			"explicit" : 0,
			"new" : 0,
			"static_cast" : 0,
			"typeid" : 0,
			"catch" : 0,
			"false" : 0,
			"operator" : 0,
			"template" : 0,
			"typename" : 0,
			"class" : 0,
			"friend" : 0,
			"private" : 0,
			"this" : 0,
			"using" : 0,
			"const_cast" : 0,
			"inline" : 0,
			"public" : 0,
			"throw" : 0,
			"virtual" : 0,
			"delete" : 0,
			"mutable" : 0,
			"protected" : 0,
			"true" : 0,
			"wchar_t" : 0,
			"malloc" : 0,
			"calloc" : 0,
			"realloc" : 0,
			"free" : 0,
			"alloca" : 0,
			"allocinteger" : 0
		}
		
		for added_line in self.features_raw["added_code"].splitlines():
			for token in re.split('[\s\+\-\*\/,;><=()\[\]\{\}]', added_line):
				if token in added_keywords.keys():
					added_keywords[token] += 1

		for key in sorted(added_keywords.keys()):
			features.append(added_keywords[key])
			if added_line_count != 0:
				features.append(added_keywords[key]/added_line_count)
			else:
				features.append(0)

		deleted_keywords = {}
		for key in added_keywords:
			deleted_keywords[key] = 0
		
		for deleted_line in self.features_raw["deleted_code"].splitlines():
			for token in re.split('[\s\+\-\*\/,;><=()\[\]\{\}]', deleted_line):
				if token in deleted_keywords.keys():
					deleted_keywords[token] += 1

		for key in sorted(deleted_keywords.keys()):
			features.append(deleted_keywords[key])
			if deleted_line_count != 0:
				features.append(deleted_keywords[key]/deleted_line_count)
			else:
				features.append(0)

		if self.features_raw["authored_hour"] in [22, 23, 0, 1, 2, 3, 4, 5, 6]:
			features.append(1)
		else:
			features.append(0)
		if self.features_raw["authored_hour"] in [7, 8, 9, 10, 11, 12]:
			features.append(1)
		else:
			features.append(0)
		if self.features_raw["authored_hour"] in [13, 14, 15, 16, 17]:
			features.append(1)
		else:
			features.append(0)
		if self.features_raw["authored_hour"] in [18, 19, 20, 21]:
			features.append(1)
		else:
			features.append(0)

		for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
			if self.features_raw["authored_day"] == day:
				features.append(1)
			else:
				features.append(0)

		# put features into sparse vector
		self.feature_vector = csc_matrix(features)

		# bag of words features
		self.feature_vector = hstack((self.feature_vector, self.bag_of_words.get_word_vect([self.features_raw["added_code"]+"\n"+self.features_raw["deleted_code"]+"\n"+self.features_raw["commit_message"]])))

		return self.feature_vector

def is_code_file(file):
    if file:
        return re.match('^.*\.(c|c\+\+|cpp|h|hpp|cc)$', file) #('^.*\.(c|c\+\+|cpp|h|hpp|php)$', file)
    return False
	
