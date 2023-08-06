'''
Shuffles sequences written in fasta format.

Created on Jan 17, 2014

'''
import sys, os
import argparse
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import fastalist_from_string, fastastring_from_list
from random import shuffle



def main():
    #parsing comand line argumetns
    parser = argparse.ArgumentParser(description='Shuffles sequences written in fasta format.')
    parser.add_argument('-i', '--input', help='Path to the fasta file. Default is stdin.', dest='input')
    parser.add_argument('-o', '--output', help='Path to the output FASTA file. Can be the same as input file. Default is stdout.', dest='output')
    args = parser.parse_args()
    
    infile = sys.stdin
    if args.input != None:
        infilePath = args.input
        try:
            infile = open(infilePath, 'r')
        except IOError:
            exit("Input file {0} cann't be opened!\n".format(infilePath))
            #read xml file to string
    try:
        instr = infile.read()
        infile.close()
    except IOError:
        sys.stderr.write("ERROR while reading from {0}\n".format(infile.name))
        exit(1)
        #set output
    openedOutFile = sys.stdout
    if args.output != None:
        outfilePath = args.output
        try:
            openedOutFile = open(outfilePath, 'w')
        except IOError:
            exit("Output file {0} cann't be opened!\n".format(outfilePath))
    
    fastalst = fastalist_from_string(instr)
    shuffle(fastalst)
    openedOutFile.write(fastastring_from_list(fastalst))
    openedOutFile.close()
    

if __name__ == '__main__':
    main()