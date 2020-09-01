import argparse
from .Svm import Svm
from .Commit import Commit

parser = argparse.ArgumentParser(description='Linear Support Vector Machine that classifies a commit as VCC or non-VCC.')
parser.add_argument('-c', '--commit', type=str, default="HEAD", help='Hash of the commit that should be classified')
parser.add_argument('-r', '--repo', type=str, default=".", help='Path to the git repository containing the commit')
# add confidence

args = parser.parse_args()

def main():
    svm = Svm()

    commit = Commit(args.repo, args.commit)
    commit.extract_features()
    
    svm.vcc_or_unclassified(commit.get_feature_vector())


'''
if __name__ == '__main__':
    print("hö")
    main(".", "HEAD") #args.repo, args.commit)
'''