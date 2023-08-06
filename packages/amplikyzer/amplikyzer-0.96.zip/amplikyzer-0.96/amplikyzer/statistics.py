# amplikyzer.statistics 
# (c) 2011--2012 Sven Rahmann

"""
Print several statistics for an amplikyzer analysis file.

"""

import sys
from collections import Counter, OrderedDict

from . import utils
from .core import *

######################################################################

def buildparser(p):
    p.add_argument("--out", "-o", metavar="FILE",
                   help="output file (relative to path); '-' for stdout")
    p.add_argument("--tabulate", "-t", nargs="+", default=["ROI,mid"],
                   help="combinations of elements to tabulate; "
                   + "default is 'ROI,mid'", metavar="ELEMENTS")
    p.add_argument("--mincount", "-m", type=int, default=20, metavar="INT",
                   help="do not display counters below this value")
    p.add_argument("--analysisfile", "--file", "-a",
                   default="*"+EXT_AMPLIKYZER, metavar="FILE",
                   help="analysis file(s), relative to path")
    


def main(args):
    """
    Main function for the statistics subcommand.
    Output statistics on each defined element in an amplikyzer analysis file,
    plus optionally, on combinations of such elements.
    """
    element_counters = OrderedDict()  # OrderedDict of dict
    combi_counters = OrderedDict()
    combi_elements = OrderedDict()
    anames = utils.filenames_from_glob(args.path, args.analysisfile)
    if len(anames) == 0: return  # nothing to do
    outname = utils.get_outname(args.out, args.path, anames, ".stats")
    print("# computing statistics", file=sys.stdout)
    print("# writing to {}".format("<stdout>" if outname=="-" else outname), file=sys.stdout)
    for aname in anames:
        process_analysis_file(aname, element_counters, combi_counters, combi_elements, args)
    # join element_counters and combi_counters
    all_counters = OrderedDict(element_counters)
    all_counters.update(combi_counters)
    # print results
    if outname == "-":
        print_stats(sys.stdout, all_counters, args)
    else:
        with open(outname, "wt") as fout:
            print_stats(fout, all_counters, args)


def process_analysis_file(fname, element_counters, combi_counters, combi_elements,
        args, skip=("genomic","read")):
    print("# processing {}".format(fname), file=sys.stdout)
    # Read lines starting with @; they contain the element information
    f = AKZRFile(fname).data()
    myelements = next(f)    
    if len(element_counters) == 0:
        # initialize element counters
        for el in myelements: element_counters[el] = Counter()
        print("# defined counters:", ", ".join(element_counters.keys()), file=sys.stdout)
        # initialize combi counters
        for combi in args.tabulate:
            elements = [x.strip() for x in combi.split(",")]
            if any([x not in element_counters for x in elements]):
                raise ValueError("error: --tabulate option '{}' contains an argument not from '{}'".format(
                    combi,", ".join(element_counters.keys())))
            key = " / ".join(elements)
            combi_counters[key] = Counter()
            combi_elements[key] = tuple(elements)
    else:  # not the first file, elements should match existing ones!
        print("# previous counters:", ",".join(element_counters.keys()))
        for e1, e2 in zip(myelements, element_counters.keys()):
            if e1 != e2: raise FormatError("elements from multiple files must match!")
    for current in f:
        ###print("current:", current)
        for el in myelements:
            if el not in skip:
                element_counters[el][current[el]] += 1
        for key, elements in combi_elements.items():
            counterkey = " / ".join([current[el] for el in elements])
            combi_counters[key][counterkey] += 1
    # done, we now have updated element_counters and combi_counters


def print_stats(f, all_counters, args):
    """
    print collected statistics in <element_counters> to given stream <f>
    """
    mincount = args.mincount
    for e, edict in all_counters.items():
        if len(edict) == 0: continue
        print("[{}]".format(e), file=f)
        # compute width of keys
        width = max(len(key) for key in edict.keys())
        s = sum(edict.values())
        if s == 0: s = 1  # avoid division by zero
        for key in sorted(edict.keys()):
            c = edict[key]
            if c >= mincount:
                print("{:{width}} = {:7d} = {:6.1%}".format(key, c, c/s, width=width), file=f)
        print("",file=f)
    # done.
        
