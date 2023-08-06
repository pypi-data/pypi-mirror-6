'''
This script should be used for purge sequences from blast or another program
before multiple sequence aligning and tree construction.
Takes file containting (not aligned) sequences in FASTA format and
removes sequences witch contain non standart letters or duplicate sequences.
Arguments     -i input file with sequences
              -o output purified file with sequences
              [- m] number of sequences; default max integer

Created on Jan 8, 2014

'''
import sys, os
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import check_fastastring, fastalist_from_string,\
    AminoAcids, fastastring_from_list, transform_fasta_for_mapp
    
import argparse
import re


def main():
    ''' Purifies fasta file '''
    description = "This script takes file with fasta sequences and it removes" +\
                    "sequences with non standard letters and duplicate ones."
    infilehelp = "File with sequences to be purified."
    outfilehelp = "File with good sequences. Can be the same as input file."
    maxhelp = "Maximum number of sequences that will be in the output file."
    
    
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-i', required=True, help=infilehelp,
                         dest='input')
    parser.add_argument('-o', required=True, help=outfilehelp,
                         dest='output')
    parser.add_argument('-m', help=maxhelp, default=sys.maxint,
                         dest='maxseq', type=int)
    args = parser.parse_args()
    
    #set input
    infile = sys.stdin
    if args.input != None:
        infilePath = args.input
        try:
            infile = open(infilePath, 'r')
        except IOError:
            exit(os.path.basename(__file__) + 
                 ":Input file {0} cann't be opened!\n".format(infilePath))
    try:
        instr = infile.read()
        infile.close()
    except IOError:
        exit(os.path.basename(__file__) + 
                         ":ERROR while reading from {0}\n".format(infile.name))
        #set output
    openedOutFile = sys.stdout
    if args.output != None:
        outfilePath = args.output
        try:
            openedOutFile = open(outfilePath, 'w')
        except IOError:
            exit(os.path.basename(__file__) + 
                 ":Output file {0} cann't be opened!\n".format(outfilePath))
    
    outstr = purge_sequences(instr, maxseqs=args.maxseq)
    openedOutFile.write(outstr)
    openedOutFile.close()


def purge_sequences(instr, maxseqs=sys.maxint):
    ''' Deletes non unique sequences and sequences witch contain
        non standard letters and non unique.
        
        :param instr: string in fasta format
        
        :returns: string in fasta format with unique and standard-letters
            sequences
        
        :throws AttributeError: if `instr` isn't in fasta format
    '''
    instr = transform_fasta_for_mapp(instr)
    if not check_fastastring(instr):
        raise AttributeError("Attribute instr isn't in fasta format!")
    check_regexp = re.compile("^[" + "".join(AminoAcids.list) + "]+$", re.IGNORECASE)
    fastalist = fastalist_from_string(instr)
    newfastalist = list()
    checkset = set()
    excluded = 0
    exclseqs = list()
    seqcount = 0
    for seqid, seq in fastalist:
        seqcount += 1
        if seqcount > maxseqs:
            break
        #it is unique sequence and contains only standard letters
        if seq not in checkset: 
            if check_regexp.match(seq):
                newfastalist.append((seqid, seq))
                checkset.add(seq)
            else:
                excluded += 1
                exclseqs.append(seqid)
                sys.stdout.write("Purge fasta: sequence %s doesn't match sequence regexp\n" % seqid)
        else:
            excluded += 1
            exclseqs.append(seqid)
    exclseqs.sort()
    message = "Purge fasta: " + str(excluded) + " sequences was excluded.\n" +  str(exclseqs) + "\n"
    sys.stdout.write(message)
    return fastastring_from_list(newfastalist) 
            

        
        


if __name__ == '__main__':
    main()