#!/usr/bin/python

"""
This script can take cd-hit file where are sorted clusters and
file with representative sequences.
From these files can obtain representative sequences sorted by
size of its cluster. This sequences and it's names are not changed.
(There could be some unexpected characters).
Arguments        -c sorted cluster cd-hit file (if not defined then output sequences are chosen randomly)
                 -f sequence fasta file
                 -m max number of sequences
                 -o output fasta file with sequences (names aren't changed).

Created on Jan 14, 2014

"""
import sys
import argparse
import os
import random
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import fastalist_from_string, check_positive_nozero,\
    fastastring_from_list
import re




def main():
    description = 'Pick sequences randomly or by bigger cluster from fasta file.'
    chelp = 'Sorted cluster cd-hit file.'
    fhelp = 'Sequence fasta file.'
    mhelp = 'Max number of sequences.'
    ohelp = 'Output fasta file.'
    
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', help=chelp)
    parser.add_argument('-f', required=True, help=fhelp, type=argparse.FileType('r'))
    parser.add_argument('-m', help=mhelp, type=check_positive_nozero, default=sys.maxint)
    parser.add_argument('-o', help=ohelp, type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()
    
    seqs = fastalist_from_string(args.f.read())
    maxseq = args.m if args.m <= len(seqs) else len(seqs)
    #pokud je c parametr
    if args.c:
        with open(args.c) as clustf:
            newseqs = from_sorted_cdhit(clustf.read(), seqs, maxseq)
    else:
        newseqs = from_sequences_random(seqs, maxseq)

    args.o.write(fastastring_from_list(newseqs))
    args.o.close()
    

def from_sorted_cdhit(sortedstr, seqs, maxseq):
    ''' Parse contents of sorted cluster cd-hit and find sequences names.
    Then returns list of sequences [(name, sequence), ... ] founded by name
    from fastastr (contents of non-aligned fasta file)
    
    :param sortedstr: Content of sorted cd-hit cluster file.
    :param seqs: List of sequences (see `mapp.utils.common.fastalist_from_string` method)
    :param maximum of returned sequences
    
    :returns: List of sequences [(name, sequence), ... ]
    '''
    
    dseqs = dict(seqs)
    names = parse_clustsorted(sortedstr, maxseq)
    return [(name, dseqs[name]) for name in names]

def from_sequences_random(seqs, maxseq):
    return random.sample(seqs, maxseq)


def parse_clustsorted(cluststr, maxseq=sys.maxint):
    '''
    Parses sorted cd-hit cluster file.
    
    :param cluststr: Content of sorted cd-hit cluster file.
    :param maxseq: maximum of returned sequences
    
    :returns: list of sequence's names ["A4X329_SALTO", "E6SAU5_INTC7", ...]
        Names in list aren't changed (could containt inappropriate characters)
    
    :throws AttributeError: if no sequence name wasn't found
    '''
    r = re.compile('>([^/\n]*.*)\.\.\. \*')
    #generate only maxseq sequences not all sequences
    seqnames = [m.group(1) for m, _ in zip(r.finditer(cluststr), xrange(maxseq))]
    if len(seqnames) == 0:
        raise AttributeError("Parsing sorted cd-hit cluster file found 0 names.")
    maxseq = maxseq if maxseq <= len(seqnames) else len(seqnames)
    return seqnames[:maxseq]
    
    


if __name__ == '__main__':
    main()