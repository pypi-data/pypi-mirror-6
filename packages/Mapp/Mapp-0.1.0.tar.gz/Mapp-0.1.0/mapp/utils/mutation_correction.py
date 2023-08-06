'''
This script can correct mutations (their position).

Arguments    -m mutation file
             -a alignment file with analysing sequence at first position
             -s sequence id of original sequence whitch is searching in alignment file
             -o corrected mutations
             
Created on Jan 8, 2014

'''

import os
import sys
import re
import argparse
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.core.exceptions import MappError
from mapp import utils 



def main():
    '''This script can correct mutations (their position).'''
    description = "mutations_correction.py"
    mutfilehelp = "File with mutations in format letterNUMBERletter."
    msafilehelp = "File with multiple sequence alignment"
    seqhelp = "id of original sequence which will be searching for in alignment file."
    outfilehelp = "File to which new mutations are written."
    
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-m', required=True, help=mutfilehelp, dest='muts', type=argparse.FileType('r'))
    parser.add_argument('-a', required=True, help=msafilehelp, dest='msa', type=argparse.FileType('r'))
    parser.add_argument('-s', required=True, help=seqhelp, dest='seqid')
    parser.add_argument('-o', required=True, help=outfilehelp, dest='out', type=argparse.FileType('w'))
    args = parser.parse_args()
    
    muts = utils.common.parse_mutations(args.muts.read())
    args.muts.close()
    msa = args.msa.read()
    args.msa.close()
    newmutslist = correct_mutations(args.seqid, muts, msa)
    newmuts = "\n".join(["".join(map(str, mutation)) for mutation in newmutslist]) + "\n"
    args.out.write(newmuts)
    

def correct_mutations(seqid, muts, msa):
    '''
    Corrects mutation positions according to multiple sequence file.
    
    :param muts: List of tuples [(letter, position, new letter), ... ]
        for parsing see `mapp.utils.common.parse_mutations` method.
    :param msa: Multiple sequence alignment string (mostly readed from file).
    
    :returns: List of tuples [(letter, position, new letter), ... ] with
        corrected position
    '''
    fastalist = utils.common.fastalist_from_string(msa)
    #search for original sequence
    try:
        sequence = [seq for sid, seq in fastalist if sid == seqid][0]
    except IndexError:
        raise MappError("Mutations correction error",
                        "seqid hasn't been founded in alignment")
    newmuts = list()
    for mut in muts:
        oldpos = mut[1]
        lettercount = 0
        newposition = 0
        while lettercount < oldpos:
            newposition += 1
            try:
                if re.match("[a-zA-Z]", sequence[newposition-1]):
                    lettercount += 1
            except IndexError:
                raise MappError("Mutations correction error",
                        "sequence {0} is shorter than mutation position {1}".\
                            format(seqid, mut))
        if (sequence[newposition-1].lower() != mut[0].lower()):
            print("Seq: " + sequence[:15] + ", mut: " + str(mut) + \
                  ", ERROR. Mutation letter is wrong. Mutation is excluded." )
        else:
            newmut = (mut[0], newposition, mut[2])
            newmuts.append(newmut)
    return newmuts
    

if __name__ == '__main__':
    main()