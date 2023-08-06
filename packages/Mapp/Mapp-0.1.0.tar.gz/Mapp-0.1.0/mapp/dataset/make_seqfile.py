'''

Makes sequence file.

Created on Feb 9, 2014

'''
import argparse
import sys, os
from os import path
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.dataset.files import Dataset
from mapp.utils.common import check_positive
from mapp.dataset.make_results import check_file, check_directory

def main():
    #parsing comand line argumetns
    parser = argparse.ArgumentParser(description='Makes sequence file.')
    parser.add_argument('-l', help='From line in dataset', dest='linenum', type=check_positive)
    parser.add_argument('-d', help='Dataset file path', dest='dataset', type=check_file)
    parser.add_argument('-odir', help='Output dir', dest='out', type=check_directory)
    args = parser.parse_args()
    #get sequences
    dataset=Dataset(args.dataset)
    seq = dataset.seq_range(args.linenum, args.linenum)[0]
    #write to file
    with open(path.join(args.out, "%s.seq" % seq[0]), "w") as f:
        f.write(">%s\n%s\n" %(seq[0], seq[1]))
        print(f.name)
    

if __name__ == '__main__':
    main()