'''
Can be run as script and converts input file (in some format)
to output file (in another format).

Biopython must be installed before use this script.

Created on Dec 5, 2013

'''
import argparse
from Bio import Phylo

if __name__ == '__main__':
    formats = "nexus, newick"
    description = 'Convert phylogenetic tree file to another format.\n' +\
                  'Formats can be: ' + formats
    inputhelp = 'Path to the input tree file.'
    informathelp = 'Input file format can be: ' + formats
    outputhelp = 'Path to the output tree file.'
    outformathelp = 'Output file format can be: ' + formats

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--input', required=True, help=inputhelp, dest='input')
    parser.add_argument('-if', '--inputformat', required=True, help=informathelp, dest='informat')
    parser.add_argument('-o', '--output', required=True, help=outputhelp, dest='output')
    parser.add_argument('-of', '--outputformat', required=True, help=outformathelp, dest='outformat')
    args = parser.parse_args()
    
    Phylo.convert(args.input, args.informat, args.output, args.outformat)