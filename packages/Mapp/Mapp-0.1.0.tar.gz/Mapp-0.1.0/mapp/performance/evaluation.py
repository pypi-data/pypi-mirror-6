'''
Contains functions that evaluate mapp analysis.
It can be run as a script file. This script takes mapp file and corrected mutations
and create csv table of evaluated values.

Script arguments:       -n neutral_mutations file
                        -d deleterious_mutations file
                        -o output csv file
                        mapp file

Created on Jan 2, 2014

'''
from __future__ import division
import sys, os, math, argparse
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.utils.common import MappFile, parse_mutations
from mapp.utils.common import AminoAcids  as aalist


def main():
    ''' This script takes mapp file and create
        csv table of evaluated values. '''
    description = "This script takes mapp file and mutations file and create evaluation of analysis."
    neutralhelp = "File with neutral mutations in format letterNUMBERletter."
    deleterhelp = "File with deleterious mutations in format letterNUMBERletter."
    outhelp = "Output file in csv format. Delimited by tabs."
    filehelp = "Mapp file."
    
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-n', required=True, help=neutralhelp, dest='neut', type=argparse.FileType('r'))
    parser.add_argument('-d', required=True, help=deleterhelp, dest='dele', type=argparse.FileType('r'))
    parser.add_argument('-o', required=True, help=outhelp, dest='out', type=argparse.FileType('w'))
    parser.add_argument('file', metavar='F', help=filehelp)
    args = parser.parse_args()
    
    mutations = list()
    for mutation in parse_mutations(args.neut.read()):
        mutations.append((mutation, "neu"))
    args.neut.close()
    for mutation in parse_mutations(args.dele.read()):
        mutations.append((mutation, "del"))
    args.dele.close()
    
    evaluate = evaluate_file(mutations, args.file)
    for line in evaluate:
        args.out.write("\t".join(map(str, line)) + "\n")
    args.out.close()
    


def evaluate_file(mutations, mappfile):
    '''
    It evaluates mapp mappfile in argument. Results are saved in list.
    One list line for each file. The list line is list of values.
    
    :param mutations: list of doubles - [(mutation, type), ...]
        - mutation is tuple (letter, number, letter)
        - type is "del" or "neu"
    :param mappfile: file that will be analyzed
    
    :returns: list of evaluation lines. Every line is list of values.
        First line is header.
    '''
    #first row is header
    outlines = [["mappfile", "tp", "tn", "fp", "fn", "mutations", "accuracy",
                "mcc", "coverage", "sensitivity", "specificity", "ppv", "npv"]]
    f = open(mappfile, "r")
    evaluation = evaluate_mapp(f, mutations)
    f.close()
    outlines.append([os.path.basename(mappfile),
                    evaluation["tp"],
                    evaluation["tn"],
                    evaluation["fp"],
                    evaluation["fn"],
                    evaluation["mutations"],
                    evaluation["accuracy"],
                    evaluation["mcc"],
                    evaluation["coverage"],
                    evaluation["sensitivity"],
                    evaluation["specificity"],
                    evaluation["ppv"],
                    evaluation["npv"]])
    #end of for
    return outlines    
    


def evaluate_mapp(mapp, mutations, pvalue=0.1):
    '''
    Takes mapp and counts True Positives, False positives and another
    measures according via list of mutations.
    
    :param mapp: itereable with mapp lines (mapp header included)
    :param mutations: list of doubles - [(mutation, type), ...]
        - mutation is tuple (letter, number, letter)
        - type is "del" or "neu"
    :param pvalue: threshold for decision about protein mutation
    
    :returns: dictionary with keys:
        tp (true positive)
        tn (true negative)
        fp (false positive)
        fn (false negative)
        mutations (number of mutations)
        accuracy
        mcc
        coverage (0.75 means that 3 of 4 mutations was predicted by mapp,
            others wasn't predicted at all)
        sensitivity
        specificity
        ppv (positive predictive value)
        npv (negative predictive value)
    '''
    result = {"tp": 0, "tn":0, "fp":0, "fn":0, "mutations":0}
    noteval = 0
    
    mapplines = list(mapp)
    
    for mutation in mutations:
        mutnumber = mutation[0][1]
        muttype = mutation[1]
        mutletter = mutation[0][2]
        result["mutations"] += 1        
        
        mappline = mapplines[mutnumber]
        mappline = mappline.split("\t")
        align_column = mappline[MappFile.alignmentOffset]
        if mutation[0][0] not in align_column:
            print("Mutation %s doesn't appear in alignment column %s!" % \
                            (str(mutation), align_column))
            continue            
        if (mappline[MappFile.naOffset] == "N"): # values are predicted by mapp
            mut_pvalue = float(mappline[MappFile.pvalueOffset 
                                 + aalist.list.index(mutletter)])
            if (mut_pvalue > pvalue): #mutation is predicted neutral
                if (muttype == "neu"):
                    result["tn"] += 1
                else:
                    result["fn"] += 1
            else: #mutation is predicted deleterious
                if (muttype == "del"):
                    result["tp"] += 1
                else:
                    result["fp"] += 1
        else: #prediction is not defined for this mutation
            noteval += 1
            
    result["accuracy"] = accuracy(result["tp"], result["fp"], result["tn"], result["fn"])
    result["sensitivity"] = sensitivity(result["tp"], result["fn"])
    result["mcc"] = mcc(result["tp"], result["fp"], result["tn"], result["fn"])
    result["coverage"] = (result["mutations"] - noteval) / result["mutations"]
    result["sensitivity"] = sensitivity(result["tp"], result["fn"])
    result["specificity"] = specifity(result["tn"], result["fp"])
    result["ppv"] = ppv(result["tp"], result["fp"])
    result["npv"] = npv(result["tn"], result["fn"])
    return result


def accuracy(tp, fp, tn, fn):
    try:
        return (tp / (tp + fn) + tn / (tn + fp)) / 2
    except ZeroDivisionError:
        return float('nan')

def sensitivity(tp, fn):
    try:
        return tp / (tp + fn)
    except ZeroDivisionError:
        return float('nan')

def specifity(tn, fp):
    try:
        return tn / (fp + tn)
    except ZeroDivisionError:
        return float('nan')

def ppv(tp, fp):
    try:
        return tp / (tp + fp)
    except ZeroDivisionError:
        return float('nan')

def npv(tn, fn):
    try:
        return tn / (fn + tn)
    except ZeroDivisionError:
        return float('nan')

def mcc(tp, fp, tn, fn):
    try:
        return ((tp * tn) - (fp * fn)) / math.sqrt((tp + fn) * (tn + fp) * (tp + fp) * (tn + fn))
    except ZeroDivisionError:
        return float('nan')


if __name__ == "__main__":
    main()