'''
This script add sequence from sequence file to fasta formatted file.

Created on Jan 8, 2014

'''
import argparse
import os
import sys

#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import check_fastastring


def main():
    ''' Adds sequence to fasta file '''
    description = "This script add sequence from sequence file to fasta formatted file."
    seqhelp = "File containing sequence to add (in fasta format)."
    filehelp = "File to where sequence will be added."
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-s', required=True, help=seqhelp,
                         dest='seqfile', type=argparse.FileType('r'))
    parser.add_argument('-f', required=True, help=filehelp,
                         dest='thefile', type=argparse.FileType('r+'))
    args = parser.parse_args()
    
    seq = args.seqfile.read()
    args.seqfile.close()
    seq = seq.strip("\n")
    if not check_fastastring(seq):
        exit(os.path.basename(__file__) + ": -s argument error: file" +\
             " is not in fasta format")
    
    before = args.thefile.read()
    args.thefile.seek(0)
    new = seq + "\n" + before
    if not check_fastastring(new):
        args.thefile.close()
        exit(os.path.basename(__file__) + ": new content is not in fasta format")
    args.thefile.write(new)
    args.thefile.truncate()
    args.thefile.close()
    

if __name__ == '__main__':
    main()