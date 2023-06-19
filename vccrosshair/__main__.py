import argparse
from .Svm import Svm
from .Commit import Commit
from .BagOfWords import BagOfWords

parser = argparse.ArgumentParser(description='Linear Support Vector Machine that classifies a commit as VCC or non-VCC.')
parser.add_argument('-c', '--commit', type=str, default="HEAD", help='Hash of the commit that should be classified')
parser.add_argument('-r', '--repo', type=str, default=".", help='Path to the git repository containing the commit')

args = parser.parse_args()

def main():
    svm = Svm()
    
    bag_of_words = BagOfWords()

    commit = Commit(args.repo, args.commit, bag_of_words)
    try:
        commit.extract_features()
    except Exception as e:
        print("Exception ocurred:", str(e))
        return

    
    svm.vcc_or_unclassified(commit.get_feature_vector(), bag_of_words)
