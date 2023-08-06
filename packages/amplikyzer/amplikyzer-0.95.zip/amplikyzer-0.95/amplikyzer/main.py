# amplikyzer.main
# (c) Sven Rahmann 2011--2012
"""
Parse the command line arguments and execute the appropriate submodule.

"""

import argparse
from   collections import OrderedDict

from sff3 import SFFFile

from . import analysis
from . import statistics
from . import align
from . import methylation
from . import printreads
from .core import EXT_CONFIG

## main; interface for geniegui ############################################

def get_argument_parser():
    """return an ArgumentParser object p with this module's options;
    with an additional dict attribute p._geniegui to specify
    "special" treatment (file/path dialogs) for some options.
    """
    # define available subcommands as dict:
    # name = (sort_order, helpstring, module)
    # each module must have a buildparser function and a main function.
    _subcommands = dict(
        printreads = (0, "print reads of an .sff file",
            printreads),
        analyze = (1, "analyze an .sff file (identify key, mid, tag, primer, ROI for each read)",
            analysis),
        statistics = (2, "show statistics for an analyzed dataset",
            statistics),
        align = (3, "output a multiple alignment of all reads of a locus for a given MID",
            align),
        methylation = (4, "do a methylation analysis of a given locus and MID",
            methylation),
        )
    # obtain the ArgumentParser object 'p'
    p = argparse.ArgumentParser(
        description = "amplikyzer: an amplicon analyzer",
        epilog = "In development. Use at your own Risk!"
        )
    p._geniegui = dict()
    # global options for all subcommands
    p.add_argument("--path","-p", default="",
        help = "project path (directory) containing an .sff file")
    p._geniegui["--path"] = "dir"
    p.add_argument("--conf",
        nargs="+", default=["*"+EXT_CONFIG], metavar="FILE",
        help="names of configuration files with MIDS, TAGS, LOCI, LABELS")
    # add subcommands to parser
    subs = p.add_subparsers()
    subs.required = True
    subs.dest = 'subcommand'
    subcommands = OrderedDict(sorted(_subcommands.items(), key=lambda x: x[1][0]))
    for (scname,(_,schelp,scmodule)) in subcommands.items():
        subcommandparser = subs.add_parser(scname, help=schelp, description=scmodule.__doc__)
        subcommandparser.set_defaults(func=scmodule.main)
        scmodule.buildparser(subcommandparser)
    return p


def main(args=None):
    """main function; interface for geniegui"""
    p = get_argument_parser()
    pargs = p.parse_args() if args is None else p.parse_args(args)
    pargs.func(pargs)  # call the appropriate subcommand function


__NOTES = """
Description of CWF format and other formats:
http://454.com/my454/documentation/gs-flx-system/emanuals.asp
"""
