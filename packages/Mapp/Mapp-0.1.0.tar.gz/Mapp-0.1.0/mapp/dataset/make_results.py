'''
This script can analyze mutation dataset

Script arguments:    -d dataset file
                     -o output directory where results will be saved
                     -w working dir where files will be saved (including logging file)
                     -s default settings
                     -f line in dataset from which analysis starts (fist is 0)
                     -t line in dataset where analysis ends (inclusive) 

Created on Jan 30, 2014
'''
import os
import sys
import argparse
from argparse import ArgumentError
from os.path import join
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import check_positive
from mapp.dataset.evaluators import Evaluator
import logging



def main():
    ''' This script can analyze given dataset and create result files and
    other files needed by mapp analysis (settings, msa file and so on)
    Result file contains header and one data line. Data line is composed 
    from dataset line, hmmer stats and mapp line. '''
    description = "This script can evaluate given dataset and create result files."
    dhelp = "Dataset file."
    ohelp = "In this directory results will be saved."
    whelp = "In this directory working files will be saved (most working file " +\
        "place depends on default settings file)."
    shelp = "Default settings file. For each dataset line the id and sequence value " +\
            "will be change in it."
    fhelp = "From which line of dataset analysis starts. (fist is 0)"
    thelp = "On which line of dataset analysis ends (included)."
    
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-d', required=True, help=dhelp, dest='dataset', type=check_file)
    parser.add_argument('-o', required=True, help=ohelp, dest='outdir', type=check_directory)
    parser.add_argument('-w', required=True, help=whelp, dest='workdir', type=check_directory)
    parser.add_argument('-s', required=True, help=shelp, dest='set', type=check_file)
    parser.add_argument('-f', required=True, help=fhelp, dest='start', type=check_positive)
    parser.add_argument('-t', required=True, help=thelp, dest='to', type=check_positive)
    args = parser.parse_args()
    
    logging.basicConfig(join(args.outdir, filename='datasetanalysis.log'),level=logging.DEBUG)
    
    evaluator = Evaluator(args.dataset, args.set, args.workdir)
    evaluator.resultdir = args.outdir
    #evaluator.make_results_range(args.start, args.to)
    evaluator.make_results_stepwise(args.start, args.to)
    
    
def check_directory(value):
    if not os.path.isdir(value):
        raise AttributeError("%s is not directory" % value)
    return value

def check_file(value):
    try:
        with open(value):
            pass
    except IOError:
        raise ArgumentError("Not possible to open %s file" % value)
    return value


if __name__ == '__main__':
    main()