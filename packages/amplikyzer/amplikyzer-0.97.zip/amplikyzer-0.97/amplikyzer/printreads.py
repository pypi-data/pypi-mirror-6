# amplikyzer.printreads
# (c) 2011--2012 Sven Rahmann

"""
Print reads (flowgrams) of an .sff file and analyze their properties.
"""


import sys
import os.path
import webbrowser
from collections import Counter
from subprocess import Popen, PIPE

from .sff import SFFFile
from .utils import filenames_from_glob, get_outname
from .core import *
from . import flowdna

############################################################################

def buildparser(p):
    p.add_argument("--format", "-f",
                   choices=("dna", "flowdna", "flows", "hist", "valleys", "optionals"),
                   default="flowdna", help="output format")
    p.add_argument("--dir", "-d", nargs="+", 
                   choices = ("f","r","fc","c","rc"), default=["f"],
                   help="direction of reads (fwd, rev, [fwd-]compl, rev-compl)")
    p.add_argument("--gnuplot", nargs="?", const="svg", metavar="FORMAT",
                   help="additional output image format for hist and valleys")
    p.add_argument("--show", action="store_true",
                   help = "with --gnuplot, show image in the browser")
    p.add_argument("--maxflow", "-M", type=int, default=DEFAULT_MAXFLOW, metavar="INT",
                   help="maximum flow intensity before cutoff ")
    p.add_argument("--certain", "-c", type=float,
                   default=DEFAULT_CERTAINFLOW, metavar="FLOAT",
                   help="limit for fractional flow intensity considered certain")
    p.add_argument("--maybefraction", "-m", type=float,
                   default=DEFAULT_MAYBEFRACTION, metavar="FLOAT",
                   help="maximum fraction of flows marked as 'maybe'")
    p.add_argument("--sfffiles", "-s",
                   nargs="+", default=["*.sff"], metavar="SFF",
                   help="the .sff file(s) to analyze")
    p.add_argument("--out", "-o", metavar="FILE",
                   help="specify output file instead of deriving from sff,"
                   + " use '-' for stdout")
    p.add_argument("--ids", "-i", nargs="+", metavar="ID",
                   help="specify read IDs to show or analyze")
    p.add_argument("--idfiles", "-F", nargs="+", metavar="FILE",
                   help="specify files with IDs (relative to global --path)")
    

def _get_ids(args):
    ids = []
    if args.ids:
        ids.extend(args.ids)
    if args.idfiles:
        fnames = list()
        for fname in args.idfiles:        
            mynames = filenames_from_glob(args.path, fname, unique=False)
            fnames.extend(mynames)
        for fname in fnames:
            with open(fname, "rt") as f:
                myids = f.readlines()
                ids.extend(myids)
    return frozenset(ids)


def main(args):
    fmt = args.format;  dirs = frozenset(args.dir)
    if fmt == "flows":
        if "f" not in dirs and len(dirs) != 1:
            raise ArgumentError("For '--format flows', only '--dir f' is allowed")
    sffnames = sum([filenames_from_glob(args.path,s) for s in args.sfffiles], [])
    if len(sffnames) == 0: return
    outname = get_outname(args.out, args.path, sffnames, "-reads."+fmt)
    # process all sff files into output file
    if outname == "-":
        if fmt == "hist":
            make_histogram_from_sffs(sffnames, sys.stdout, args, outname)
        elif fmt == "valleys":
            valleys_of_all_sffs(sffnames, sys.stdout, args, outname)
        elif fmt == "optionals":
            optionals_of_all_sffs(sffnames, sys.stdout, args, outname)
        else:
            process_all_sffs(sffnames, sys.stdout, args)
    else:
        with open(outname, "wt") as fout:
            if fmt == "hist":
                make_histogram_from_sffs(sffnames, fout, args, outname)
            elif fmt == "valleys":
                valleys_of_all_sffs(sffnames, fout, args, outname)
            elif fmt == "optionals":
                optionals_of_all_sffs(sffnames, fout, args, outname)
            else:
                process_all_sffs(sffnames, fout, args)


def process_all_sffs(sffnames, f, args):
    fmt = args.format
    dirs = frozenset(args.dir)
    maxflow = args.maxflow
    _flows = lambda r, rev:  (
        " ".join(map(str,r.flowvalues)) )
    _flowdna = lambda r, rev: (
        flowdna.flowdna(r.flowvalues, r.flowchars, rev, maxflow=args.maxflow,
            certain=args.certain, maybefraction=args.maybefraction) )
    _dna = lambda r, rev: (
        flowdna.dna(r.flowvalues, reverse=rev) )
    _formats = dict(flowdna=_flowdna, flows=_flows, dna=_dna)
    myformat = _formats[fmt]
    ids = _get_ids(args)  # empty frozenset if no IDs given
    first = True
    for sffname in sffnames:
        sff = SFFFile(sffname)
        if first and fmt == "flows":
            print("# ",sff.flow_chars, sep="", file=f)
            first = False
        for r in sff.reads():
            rname = r.name
            if (ids) and (rname not in ids): continue
            process_read(r, rname, myformat, dirs, f)


_transtable = str.maketrans("ACGTUacgtu", "TGCAAtgcaa")

def process_read(r, name, myformat, dirs, f, transtable=_transtable):
    if "f" in dirs:
        print(">", name, sep="", file=f)
        print(myformat(r, False), file=f)
    if "r" in dirs:
        print(">", name, "__R", sep="", file=f)
        print(myformat(r, True), file=f)
    if "fc" in dirs or "c"in dirs:
        print(">", name, "__C", sep="", file=f)
        print(myformat(r, False).translate(transtable), file=f)
    if "rc" in dirs:
        print(">", name, "__RC", sep="", file=f)
        print(myformat(r, True).translate(transtable), file=f)


########## histograms #####################################################
        
def histogram_of_flows(read, freqs=None): 
    """
    return a collections.Counter object <freqs> (like a dict int->int)
    containing the frequency freqs[i] of each flow value i.
    If an existing <freqs> is given, it is updated with the read's flow values.
    """
    if freqs is None: freqs = Counter()
    freqs.update(read.flowvalues)
    return freqs

_GNUPLOT_HIST_HEADER = """
set xrange [{}:{}]
#set logscale y
set title 'Histogram of flow intensities'
set xlabel 'flow value'
set terminal {}
set output '{}'
plot '-' u 1:2 w histeps title "frequency"
"""


def make_histogram_from_sffs(sffnames, fout, args, outname):
    """count intensity frequencies"""
    maxflow = args.maxflow
    maybeflow = args.certain
    umaybeflow = 1 - maybeflow
    ids = _get_ids(args)  # empty frozenset if no IDs given
    freqs = Counter()
    for sffname in sffnames:
        sff = SFFFile(sffname)
        for r in sff.reads():
            if (ids) and (r.name not in ids): continue
            freqs.update(r.flowvalues)
    # clean up right tail of histogram, if ids is not given
    while not ids:  
        maxint = max(freqs.keys())
        if freqs[maxint] == 1 and freqs[maxint-1] == 0:
            del freqs[maxint]
        else:
            break
    # output the histrogram
    maxint = max(freqs.keys())
    allflows = sum(freqs.values())
    maybe = 0;  big = 0;  small = 0
    for i in range(maxint+1):
        f = freqs[i]
        value = i / 100.0;  frac = value - int(value)
        if value < maybeflow: small += f
        if maybeflow <= frac < umaybeflow: maybe += f
        if value >= maxflow + maybeflow: big += f
        print(i, f, file=fout)  # write histogram to file
    # output statistics
    notsmall = allflows - small
    print("# parameters: maxflow = {}, certain = {}".format(maxflow, args.certain), file=fout)
    print("# {:5.2%} zero        ({})".format(small/allflows,small), file=fout)
    print("# {:5.2%} not certain ({}) [{:5.2%}]".format(maybe/allflows,maybe,maybe/notsmall), file=fout)
    print("# {:5.2%} capped      ({}) [{:5.2%}]".format(big/allflows,big,big/notsmall), file=fout)
    # turn histogram output into a GNUPLOT script (--gnuplot option)
    if not args.gnuplot: return
    gnuname = outname if outname != "-" else "_-reads.hist"
    gnuname += "." + args.gnuplot
    fmin = max(int(maybeflow * 100) - 2, 0)
    fmax = int((maxflow+1) * 100)
    with Popen([_GNUPLOT_EXECUTABLE], stdin=PIPE, universal_newlines=True) as gnuplot:
        g = gnuplot.stdin
        print(_GNUPLOT_HIST_HEADER.format(fmin,fmax,args.gnuplot,gnuname), file=g)
        for i in range(maxint+1):
            print(i, freqs[i], file=g)
        print(_GNUPLOT_FOOTER, file=g)
        g.flush();  g = None
    if args.show:
        url = "file://"+ os.path.abspath(gnuname)
        webbrowser.open(url, new=2)


######################### valleys #########################################

_GNUPLOT_VALLEYS_HEADER = """
set title 'Histogram of valley widths (maybefraction {:.1%}, {} certain)'
set xlabel 'valley width'
set ylabel 'number of reads'
set key top left
set terminal {}
set output '{}'
plot '-' u 1:2 w histeps title '0-100', '-' u 1:2 w histeps title '100-200', '-' u 1:2 w histeps title '200-300'
"""
   
def valleys_of_all_sffs(sffnames, fout, args, outname):
    fraction = args.maybefraction
    certain = args.certain
    ids = _get_ids(args)  # empty frozenset if no IDs given
    # keep interval definition consistent with _GNUPLOT_VALLEYS_HEADER string
    intervals = ((0,100),(100,200),(200,300)) 
    histograms = [Counter() for i in intervals]
    for sffname in sffnames:
        sff = SFFFile(sffname)
        for r in sff.reads():
            rname = r.name
            if (ids) and (rname not in ids): continue
            valleys_of_read(r, fout, intervals, histograms, fraction, certain)
    if not args.gnuplot: return
    # create a gnuplot histogram of valley widths
    gnuname = outname if outname != "-" else "_-reads.valleys"
    gnuname += "." + args.gnuplot
    with Popen([_GNUPLOT_EXECUTABLE], stdin=PIPE, universal_newlines=True) as gnuplot:
        g = gnuplot.stdin
        print(_GNUPLOT_VALLEYS_HEADER.format(fraction,int(100*certain+0.5),args.gnuplot,gnuname), file=g)
        for z,_ in enumerate(intervals):
            h = histograms[z]
            for i in range(int(100*(1-2*certain)+2.5)):
                print("{} {}".format(i, h[i]), file=g)
            print(_GNUPLOT_FOOTER, file=g)
            g.flush()
        g = None
    if args.show:
        url = "file://"+ os.path.abspath(gnuname)
        webbrowser.open(url, new=2)

def valleys_of_read(r, fout, intervals, histograms, fraction, certain):
    maxflow = intervals[-1][-1] // 100
    valleys, sums = flowdna.compute_valleys(r.flowvalues, maxflow, certain=certain, maybefraction=fraction)
    print(">", r.name, sep="", file=fout)
    for (z,(start,end)) in enumerate(intervals):
        i,j = valleys[z]
        s,S = sums[z]
        print(j-i,i,j, " ", s, S, file=fout)
        histograms[z][j-i] += 1


    
# optionals ###############################################################

_GNUPLOT_OPTIONALS_HEADER = """
set title 'Optional character distribution (maybefraction {:.1%}, certain {:.2f})'
set xlabel 'percentage of optional characters in read'
set ylabel 'number of reads'
set terminal {}
set output '{}'
plot '-' u 1:2 w histeps title 'unfiltered', '-' u 1:2 w histeps title 'filtered'
"""
_TRTABLE = {'std': None,
            'bi1': str.maketrans("Cc","Tt"),
            'bi2': str.maketrans("Gg","Aa") }
_TRANSLATIONS = tuple(_TRTABLE.keys())


def optionals_of_all_sffs(sffnames, fout, args, outname):
    ids = _get_ids(args)  # empty frozenset if no IDs given
    hist = dict()
    for tr in _TRANSLATIONS:
        hist[tr] = Counter()
        hist[tr+"0"] = Counter()
    for sffname in sffnames:
        sff = SFFFile(sffname)
        for r in sff.reads():
            rname = r.name
            if (ids) and (rname not in ids): continue
            optionals_of_read(r, hist, fout, args)
    if not args.gnuplot: return
    # create a gnuplot histogram of optional characters
    gnuname = outname if outname != "-" else "_-reads.optionals"
    gnuname += "." + args.gnuplot
    with Popen([_GNUPLOT_EXECUTABLE], stdin=PIPE, universal_newlines=True) as gnuplot:
        g = gnuplot.stdin
        print(_GNUPLOT_OPTIONALS_HEADER.format(args.maybefraction,args.certain,args.gnuplot,gnuname), file=g)
        for sfx in ("", "0"):        
            for k,v in sorted(hist["std"+sfx].items()):
                print("{} {}".format(k,v), file=g)
            print(_GNUPLOT_FOOTER, file=g)
        g.flush()
        g = None
    if args.show:
        url = "file://"+ os.path.abspath(gnuname)
        webbrowser.open(url, new=2)

def optionals_of_read(r, hist, fout, args):
    print(">", r.name, sep="", file=fout)
    for tr in _TRANSLATIONS:
        translation = _TRTABLE[tr]
        (fdna, fopt, _) = flowdna.flowdna(r.flowvalues, r.flowchars,
            maxflow=args.maxflow, certain=args.certain, maybefraction=args.maybefraction,
            translation=translation, return_lists=True)
        n = len(fdna)
        if n == 0: n = 1
        
        optionals = sum(fopt);  
        perc = int(100 * optionals / n + 0.5)  # resolution of 1%
        hist[tr][perc] += 1
        
        ffopt = flowdna.filter_optionals(fopt)
        foptionals = sum(ffopt)
        fperc = int(100 * foptionals / n + 0.5)  # resolution of 1%
        hist[tr+"0"][fperc] += 1
        
        print("{}: {}/{} = {:.1%} --> {}/{} = {:.1%}".format(
                tr, optionals, n, optionals/n, foptionals, n, foptionals/n),
            file=fout)
        

# gnuplot #################################################################

_GNUPLOT_EXECUTABLE = "gnuplot"
_GNUPLOT_FOOTER =  """
e
"""

# END
