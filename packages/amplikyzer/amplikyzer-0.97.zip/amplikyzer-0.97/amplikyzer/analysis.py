# amplikyzer.analysis module
# implements the 'analyze' subcommand
# (c) 2011--2012 Sven Rahmann

"""
Analyze an .sff file.
Split each flowgram sequence in the .sff file into
key, mid, tag, primer, region of interest
and align with given genomic reference sequence.
Write an .akzr file containing the analysis results and alignments.

Use the 'statistics' subcommand to obtain a summary of the results.
Use the 'align' subcommand to format the alignments for output.
Use the 'methylation' subcommand to do methylation analysis on the alignments.

"""

import sys
import itertools
import io
import os.path
import configparser
import multiprocessing

import mamaslemonpy

from .core import *    # amplikyzer constants (DEFAULT_*)
from . import utils    # general utilities
from . import flowdna
from . import scoring
from .sff import SFFFile
from .flowdna import revcomp


############################################################################
# build parser

def buildparser(p):
    p.add_argument("--parallel", "-p", "-j",
        type=int, nargs="?", const=0, metavar="INT",
        help="number of processors to use for analysis [0=max]")
    p.add_argument("--force", "-f", action="store_true", default=False,
        help="force overwriting existing {} file".format(EXT_AMPLIKYZER))
    p.add_argument("--alignflows", action="store_true", default=False,
        help="use experimental flow alignment instead of flowdna")
    p.add_argument("--maxflow", "-M",
        type=int, default=DEFAULT_MAXFLOW, metavar="INT",
        help="maximum flow intensity before cutoff [{}]".format(DEFAULT_MAXFLOW))
    p.add_argument("--certainflow", "-c",
        type=float, default=DEFAULT_CERTAINFLOW, metavar="FLOAT",
        help="fractional flow intensity considered certain [{}]".format(DEFAULT_CERTAINFLOW))
    p.add_argument("--maybefraction", "-m",
        type=float, default=DEFAULT_MAYBEFRACTION, metavar="FLOAT",
        help="maximum fraction of flows marked as 'maybe' during matching [{}]".format(DEFAULT_MAYBEFRACTION))
    p.add_argument("--alignmaybeflow",
        type=float, default=DEFAULT_ALIGNMAYBEFLOW, metavar="FLOAT",
        help="fractional flow optional characters during alignment [{}]".format(DEFAULT_ALIGNMAYBEFLOW))
    p.add_argument("--alignthreshold",
        type=float, default=DEFAULT_ALIGNTHRESHOLD, metavar="FLOAT",
        help="threshold fraction of maximum possbile score for alignments [{}]".format(DEFAULT_ALIGNTHRESHOLD))
    p.add_argument("--alignpseudolength",
        type=int, default=DEFAULT_ALIGNPSEUDOLENGTH, metavar="INT",
        help="additional pseudo-length of ROIs for scoring [{}]".format(DEFAULT_ALIGNPSEUDOLENGTH))
    p.add_argument("--alignmaxlength",
        type=int, default=DEFAULT_ALIGNMAXLENGTH, metavar="INT",
        help="maximal length of ROI for scoring [{}]".format(DEFAULT_ALIGNMAXLENGTH))
    p.add_argument("--sff", "-s",
        nargs="+", default=["*.sff"], metavar="FILE",
        help="SFF file(s) to analyze")
    p.add_argument("--out", "-o", metavar="FILE",
        help="output file; '-' for stdout")
    p.add_argument("--indexpath", "-i",
        default=DEFAULT_INDEXPATH, metavar="PATH",
        help="relative path for index files [{}]".format(DEFAULT_INDEXPATH))
    p.add_argument("--debug", "-D", metavar="ID",
        help="specify a single read ID for debugging")

############################################################################
# main routine

def main(args):
    """analyze an sff file, given command line arguments in args"""
    # check output file
    try:
        filenames = getfilenames(args)
    except MissingArgumentOut:
        print("# must specify '--out outfile' for >= 2 .sff files")
        return
    if len(filenames.sffs) == 0:  # nothing to do
        print("# no .sff files found; nothing to do; check --path =", args.path)
        return
    
    fnout = filenames.out
    if fnout == "-":
        analyze_all_sffs(args, filenames, sys.stdout, sys.stdout)
        # NOTE: both results and messages go to stdout here.
        # Ensure that all message lines start with '#'
    else:
        if os.path.exists(fnout) and not args.force:
            print("# output file '{}' exists, nothing to do.\n" \
                  "# Use --force to re-analyze.".format(fnout))
            return
        with open(fnout, "wt") as fout:
            analyze_all_sffs(args, filenames, fout, sys.stdout)
    pass



Names = collections.namedtuple("Names", ["sffs", "config", "out"])

def getfilenames(args):
    """
    return a namedtuple with attributes
      .sffs (list of strings),
      .config (list of strings),
      .out (string),
    all of which specify filenames derived from arguments <args>.    
    """
    sffs = sum( [utils.filenames_from_glob(args.path,s) for s in args.sff], [])
    config = sum( [utils.filenames_from_glob(args.path,c) for c in args.conf], [])
    out = utils.get_outname(args.out, args.path, sffs, EXT_AMPLIKYZER, "--out")
    names = Names(sffs=sffs, config=config, out=out)
    return names


############################################################################
# read and parse configuration files

_pl_dnatrans = str.maketrans("U", "T")  # replace U (RNA) by T (DNA)
_pl_allowed = frozenset(scoring.valid_genomics)

def parse_loci(info, targetname="LOCI", minlen=12,
               dnatrans=_pl_dnatrans, allowed=_pl_allowed):
    """
    parse target section [LOCI] of configuration files
    (format: GENNAME = foward_primer,ROI,reverse_primer),
    especially 'repair' the special cases, where
    - forward primer ends with C and ROI begins with G -> move C into ROI
    - ROI ends with C and reverse primer begins with G -> move G into ROI
    Return a dict 'seqs' such that
    seqs[name___FWD]=forward_sequence, seqs[name___REV]=reverse_sequence.
    """
    # TODO: What about primers? why not strip/uppercase before testing for allowed?
    loci = info.items(targetname)
    seqs = dict()
    for (name, seq) in loci:
        # translate some of the DNA (e.g., U->T)
        seq = seq.translate(dnatrans)
        # split into forward, ROI, reverse primer
        fsr = seq.split(",")
        if len(fsr) != 3:
            raise FormatError("[{}] section, {}: (not 3 parts, but {}) {}".format(targetname,name,len(fsr),fsr))
        (f,s,r) = map(str.upper,map(str.strip,fsr))  # (forward primer,  string,  reverse primer)
        # check for correctness
        xseq = f + s + r
        nondna = [x not in allowed for x in xseq]
        if any(nondna):
            i = nondna.index(True)
            raise FormatError("[{}] section, {}: non-DNA character '{}' found".format(targetname, name, xseq[i]))
        if len(s) < minlen:
            raise FormatError("[{}] section, {}: (ROI too short, len {}) {}".format(targetname, name,len(s),s))
        # treat special cases for CpGs
        if f[-1] == "C" and s[0] == "G":
            f = f[:-1];  s = "C" + s  # move C to front of ROI
        if s[-1] == "C" and r[0] == "G":
            s += "G";  r = r[1:]      # move G to end of ROI
        # put into dicts
        seqs[name + TAGSUFFIX_FWD] = s
        seqs[name + TAGSUFFIX_REV] = revcomp(s)
    return seqs


def get_elements(configfiles, sffkey):
    """
    Obtain and process configuration information,
    which is read from <configfiles>, a list of filenames.
    The sequencer key sequence <sffkey> needs to be specified explicitly
    (it must be obtained in advance from the sff file).
    The 454 default key is TCAG.
    
    Return a pair (elementinfo, elements), where
    - elementinfo = [info_1, info_2, ...],
        info_i is an ElementInfoType namedtuple (see utils module)
    - elements = (group_1, group_2, ...),
        group_i = [(id,seq), (id,seq), ...]
    """
    # read configfiles, provide sff_key
    info = configparser.ConfigParser(
        empty_lines_in_values=False, interpolation=None)
    info.optionxform = str  # allow case-sensitive keys
    # artificially insert the sequencer key sequence
    info.read_file(io.StringIO("[KEYS]\nKEY = {}\n".format(sffkey)))
    # read all config files into the info data structure
    for fname in configfiles:
        info.read(fname, encoding="utf-8")
    # obtain elmentinfo, information on the elements of each read
    if "ELEMENTS" not in info:
        f = io.StringIO(CONFIG_STANDARD_ELEMENTS)
        info.read_file(f)
    eilist = sorted( (int(j),e.split(",")) for j,e in info.items("ELEMENTS") )
    eilist = [ [x.strip() for x in e] for (j,e) in eilist ]
    elementinfo = [ ElementInfo._make(eitype(x)
        for eitype,x in zip(ElementInfoTypes,ei)) for ei in eilist ]
    del info["ELEMENTS"]
    # process each config file section, according to elementinfo
    elements = tuple(info.items(ei.section) for ei in elementinfo)
    for group in elements:
        for i in range(len(group)):
            if type(group[i][1]) is str:
                group[i] = (group[i][0], group[i][1].upper())
    # check tags and get target regions
    targets = None
    for ei in elementinfo:
        if ei.special == SPECIAL_TARGET:
            assert targets is None, "cannot have more than one special target element!"
            targets = parse_loci(info, targetname=ei.section, minlen=ei.minlen_max)
        elif ei.special == SPECIAL_TAG:
            for k,_ in info.items(ei.section):
                if not k.startswith((TAG_FWD, TAG_REV)):
                    raise FormatError("All tags must start with '{}' or '{}'.".format(TAG_FWD, TAG_REV))
    return elementinfo, elements, targets


############################################################################
# suffix array creation from elements

_forgetseqnoise = str.maketrans("","",",; \n\t")
_bistransform1 = str.maketrans("Cc","Tt")
_bistransform2 = str.maketrans("Gg","Aa")

def _compact(seq, maxrun):
    """return a string where each homopolymer run of <seq>
    is reduced to a length of at most <maxrun>."""
    if maxrun <= 0:  return seq
    return "".join("".join(homopolymer)[:maxrun] for (_, homopolymer) in itertools.groupby(seq))

def _writeseq(name, seq, file, maxhomopolymer=0, bistransform=None):
    # do bisulfite conversion if desired and compact long homopolymers
    if bistransform is not None:  seq = seq.translate(bistransform)
    if maxhomopolymer > 0:  seq = _compact(seq, maxhomopolymer)
    print(">{}".format(name), file=file)
    print(seq, file=file)
    

def make_suffix_arrays(elements, elementinfo, basename, args):
    """return a dict d of suffix arrays, d[key]=sa,
    indexed by the config file section name of each element"""
    #elements is a list of config file sections
    elsas = dict()
    for element, ei in zip(elements, elementinfo):
        section = ei.section
        # generate fasta
        indexname = basename + section.lower()
        fastaname = indexname + ".fasta"
        with open(fastaname, "wt") as ffasta:
            for (name, seq) in element:
                # forget whitespace and commas in seq;
                # reverse sequence because we will do backward search
                seq = seq.translate(_forgetseqnoise)[::-1]
                if ei.rc == "rc_ok":
                    bt = None if ei.bis == BIS_NONE else _bistransform1
                    _writeseq(name + TAGSUFFIX_FWD, seq, ffasta, args.maxflow, bt)
                    bt = None if ei.bis == BIS_NONE else _bistransform2
                    _writeseq(name + TAGSUFFIX_REV, revcomp(seq), ffasta, args.maxflow, bt)
                else:
                    bt = None if ei.bis == BIS_NONE else _bistransform1
                    _writeseq(name, seq, ffasta, args.maxflow, bt)
        # translate and build suffix array using mamaslemonpy
        mamaslemonpy.main(("--quiet", "translate", "-i",indexname, "-a","dna", fastaname))
        mamaslemonpy.main(("--quiet", "buildindex", "--standard", "--rindex", "--occrate", "1", indexname))
        sa = mamaslemonpy.suffix.SuffixArray.from_indexname(indexname)
        sa.bwt_from_indexname(indexname)
        sa.occ_from_indexname(indexname)
        sa.lcp_from_indexname(indexname, 1)
        sa.rindex_from_indexname(indexname)
        sa.remove_closures()
        elsas[section] = sa
        print("# suffix array '{}': using lcp walking for intervals <= {}".format(ei.name, sa.lcp_threshold))
    return elsas


############################################################################
# analyse all files

# global variable for storing configuration.
# These are read only objects. This way we avoid pickling them.
#_ANALYSIS_CONFIG = None


def analyze_all_sffs(args, filenames, fout, fmsg):
    """analyse several .sff files given by 'filenames.sffs';
    write output to open stream 'fout'.
    """
    clock = utils.TicToc()
    for sff in filenames.sffs:
        analyze_one_sff(args, filenames, sff, fout, fmsg, clock)


def analyze_one_sff(args, filenames, sffname, fout, fmsg, clock):
    """
    analyze a single sff file given by <sffname>;
    write output to open stream <fout>.
    """
    print(clock.toc(),
          "reading files:\n  SFF: {}\n  configs: {}\n  writing to: {}".format(
            sffname, ", ".join(filenames.config), filenames.out), file=fmsg)
    print("@SFF", sffname, file=fout)
    for confname in filenames.config:
        print("@CONF", confname, file=fout)
    for arg in dir(args):
        if arg.startswith("_") or arg=="func": continue
        print("@ARG", arg, getattr(args,arg), file=fout)
    print("#########", file=fout)
    # read sff and config files
    sff = SFFFile(sffname)
    sffkey = sff.key_sequence
    elementinfo, elements, targets = get_elements(filenames.config, sffkey)
    for ei in elementinfo:
        print("@ELEMENT", ei.name, file=fout)
    print("@ALIGNMENT scores", file=fout)
    print("@ALIGNMENT direction", file=fout)
    print("@ALIGNMENT ROI", file=fout)
    print("@ALIGNMENT genomic", file=fout)
    print("@ALIGNMENT read", file=fout)
    print("#########", file=fout)
    # set up sequence index
    indexdir = os.path.join(os.path.dirname(sffname), args.indexpath)
    utils.ensure_directory(indexdir)
    indexbase = os.path.join(indexdir, os.path.splitext(os.path.basename(sffname))[0]) + "-"
    print(clock.toc(), "building indexes as {}*".format(indexbase), file=fmsg)
    elsas = make_suffix_arrays(elements, elementinfo, indexbase, args)
    print(clock.toc(), "done building indexes.", file=fmsg)
    
    # determine size of process pool for parallel or sequential analysis
    nreads = sff.number_of_reads
    prll = args.parallel
    poolsize = 1
    if prll is not None:
        poolsize = multiprocessing.cpu_count() - 1 if prll == 0 else prll
        if poolsize <= 0:  poolsize = 1
    # initialize parallel or sequential map object
    config = (nreads, args, elementinfo, elements, targets, elsas, clock)
    dowork = Worker(config)
    if poolsize > 1:
        # analyze in parallel
        print(clock.toc(), "analyzing reads using {} processes...".format(poolsize), file=fmsg)
        mypool = multiprocessing.Pool(poolsize)
        mymap = mypool.imap_unordered(dowork, enumerate(sff.reads()), chunksize=500)
    else:
        # analyze sequentially
        print(clock.toc(), "analyzing reads sequentially...", file=fmsg)
        mymap = map(dowork, enumerate(sff.reads()))
    # generate and report results using the appropriate map object
    for (result,msg) in mymap:
        if msg: print(msg, file=fmsg)
        print(result, file=fout, end="")
    # done
    if poolsize > 1:  mypool.close();  mypool.join()
    print(clock.toc(),"done", file=fmsg)


class Worker:
    def __init__(self, config, reportinterval=500):
        self.reportinterval = reportinterval
        self.config = config
                
    def __call__(self, ir):
        """score and align a FlowDNA read against the expected genomic elements.
        arguments must be passed as a single tuple of the form
        allargs = (i, r, config), where
        - i: running number of the read in the sff file
        - r: the read
        - config: configuration information, see 'process_one_read' function
        """
        i, r = ir
        config = self.config
        (nreads, args, _, _, _, _, clock) = config
        msgs = [];  debug = args.debug
        if (i % self.reportinterval == 0 and i > 0 and not debug):
            estimate = round(clock.seconds() * nreads / i)
            msgs.append("{}: #{} / {} -> completion @{}".format(
                clock.toc(), i, nreads, estimate))
        if not debug or r.name == debug:
            result, mymsgs = process_one_read(i, r, config)
        else:  # debug mode, but this is not the read: skip
            result = [];  mymsgs = []
        return "\n".join(result), "\n".join(msgs+mymsgs) 


def process_one_read(t, r, config, anytag=TAGSUFFIX_ANY):
    """
    process the <t>-th single read <r> using configuration <config>:
    config = (nreads, args, elementinfo, elements, targets, elsas, clock):
      - nreads: total number of reads, such that 0 <= i < nreads
      - args: argparsed command line arguments
      - elementinfo = (info_0, info_1, ...);
          info_i = (name_i, section_i, rc_i, bis_i, ETC.);
      - elements: ETC.
      - targets: dict of target (ROI) sequences, indexed by name
      - elsas: element suffix arrays (list of suffix arrays, one per element)
      - clock: the running clock
    Return: pair (result, messages), where
      - result: list of strings to output to analysis file
      - messages: list of message strings to display
    """
    (_, args, elementinfo, elements, targets, elsas, _) = config
    maxflow = args.maxflow
    result = [ ">"+r.name+" "+str(t) ]
    msg = []
    ###debug = args.debug is not None  ### DEBUG
    # we first map each element of the flowdna read against the appropriate index
    # as we use backward search on a suffix array, we need to modify
    # the read (lowercase -> boolean optionality array, no +, reverse)
    (fdna, fopt, _) = flowdna.flowdna(r.flowvalues, flowchars=r.flowchars,
        maxflow=maxflow, certain=args.certainflow, maybefraction=args.maybefraction,
        return_lists=True)
    rdna = encode_rev_flowdna(fdna)
    ropt = flowdna.filter_optionals(fopt, reverse=True)
    m1 = len(rdna) - 1
    if args.debug == r.name:
        rsubstring = pattern_substring_factory(rdna, ropt, "$ACGT.$acgt.")
        result.append( "# mapping " + rsubstring(m1+1-40, m1+1)[::-1] )
    # Try to map each element
    mytag = "?";  mytargets = [];  mytargets_bis = False
    comments = []
    for einfo, element in zip(elementinfo, elements):
        sa = elsas[einfo.section]
        if not sa.has_closures: sa.set_closures()
        begin = m1 - einfo.startpos
        # compute MUMs according to bisulfite state of element
        if einfo.bis == BIS_TAGGED:
            cumms, maxms = bisulfite_cumms(sa, r, args,
                    minlen=einfo.minlen_single, begin=begin, tag=mytag)
        elif einfo.bis == BIS_ALL:
            cumms, maxms = bisulfite_cumms(sa, r, args,
                    minlen=einfo.minlen_single, begin=begin)
        else: # no bisulfite matching
            assert einfo.bis == BIS_NONE, einfo.bis
            tol = einfo.tolerance
            end = m1 - tol if tol >= 0 else None
            cumms, maxms = sa.cumms(rdna, opt=ropt, unique=False,
                minlen=einfo.minlen_single, begin=begin, end=end)
        # process the cuMMs
        desc, toalign, showdesc = best_description(
                cumms, maxms, einfo.minlen_cum, einfo.minlen_max, sa.manifest)
        # Treat special elements 
        if einfo.special == SPECIAL_TAG:
            mytag = desc[:TAG_LEN]  # extract tag prefix
        elif einfo.special == SPECIAL_TARGET:
            mytargets = toalign
            mytargets_bis = (einfo.bis != BIS_NONE)
        # prepare result
        result.append(showdesc)
        if einfo.required > 0 and toalign == []:
            comments.append("required '{}' not found".format(einfo.name))
    # done processing each element
    # check for tag/target match or mismatch
    if mytag != "?":
        # remove direction-mismatching targets from mytargets
        tagend = TAGSUFFIX_SEP + mytag
        mytargets = [t for t in mytargets if t.endswith(tagend)]
    else:
        comments.append("no tag")
        
    # align read full r against selection of targets (mytargets)
    # targets[mytarget] is a ROI sequence
    # TODO: change that to be a triple (fullseq, primerlen, roilen),
    # then extract the ROI (but take care of + and gaps)
    if len(mytargets) == 0:
        s, ali = (0,0,0), ("? no_targets", "? no_targets")
        direction = "?"
    elif targets is None:
        s, ali = (0,0,0), ("? N/A", "? N/A")
        direction = "?"
    else:
        comments.append("aligning to {} targets".format(len(mytargets)))
        ###if len(mytargets) > 1: print("#   {}: {} targets: {}".format(r.name, len(mytargets), mytargets))
        s, ali = (0,0,0), ("? no_good_alignment", "? no_good_alignment")
        besttarget = "?"
        align = align_flowdna if not args.alignflows else align_flows
        for mytarget in mytargets:
            direction = mytarget[-3:]
            xs, xali = align(targets[mytarget], r, args, bis=mytargets_bis, direction=direction)
            if xs[1] > s[1]:
                s = xs;  ali = xali;  besttarget = mytarget
    # output scores, direction, target-roi-name, genomic, read
    result.append("# " + "; ".join(comments))
    result.append("{:.0%} {} {}".format(s[0],s[1],s[2]))
    if ali[0].startswith("?"):
        thetarget = "?"
        thedirection = "?"
    else:
        thetarget = besttarget[:-6] if besttarget.endswith(anytag) else besttarget
        thedirection = besttarget[-3:]
    result.append(thedirection)
    result.append(thetarget)
    result.extend(ali)
    result.append("#########\n\n")
    return (result, msg)


#######################################################################

def bisulfite_cumms(sa, r, args, minlen=0, tag="?", begin=None, end=None):
    """
    convert the read to FlowDNA format,
    modifying it according to bisulfite rules and tag (FWD: C->T, REV: G->A).
    Then compute MuMs against suffix array <sa>.
    """
    cumms1 = [];  cumms2 = []
    maxms1 = [];  maxms2 = []
    if tag != TAG_REV:  # do forward MUMs
        ###print("Bisulfite forward")  # DEBUG
        (fdna, fopt, _) = flowdna.flowdna(r.flowvalues, flowchars=r.flowchars,
            maxflow=args.maxflow, certain=args.certainflow,
            maybefraction=args.maybefraction, translation=_bistransform1,
            return_lists=True)
        rdna = encode_rev_flowdna(fdna)
        ropt = flowdna.filter_optionals(fopt, reverse=True)
        cumms1, maxms1 = sa.cumms(rdna, ropt, unique=False, minlen=minlen, begin=begin, end=end)
    if tag != TAG_FWD:  # do backward MUMs
        ###print("Bisulfite reverse")  # DEBUG
        (fdna, fopt, _) = flowdna.flowdna(r.flowvalues, flowchars=r.flowchars,
            maxflow=args.maxflow, certain=args.certainflow,
            maybefraction=args.maybefraction, translation=_bistransform2,
            return_lists=True)
        rdna = encode_rev_flowdna(fdna)
        ropt = flowdna.filter_optionals(fopt, reverse=True)
        cumms2, maxms2 = sa.cumms(rdna, ropt, unique=False, minlen=minlen, begin=begin, end=end)
    if len(cumms1) != 0 and len(cumms2) != 0:
        ###print("#   {},  tag '{}',  mapping to both strands".format(r.name, tag))
        cumms = sorted(cumms1 + cumms2, reverse=True)
        maxms = sorted(maxms1 + maxms2, reverse=True)
        return cumms, maxms
    elif len(cumms1) != 0:
        return cumms1, maxms1
    return cumms2, maxms2


def descriptions(mms, minlen, manifest):
    """
    return list of descriptions (names) of sequences
    from sorted list of matching statistics [ [ms, seqnumber], ... ].
    """
    bestms = mms[0][0]
    descs = [];  values = []
    for ms, idx in mms:
        if ms < bestms or ms < minlen: break
        descs.append(manifest[idx][-1])
        values.append(ms)
    return descs, values, (bestms - ms)


def best_description(cumms, maxms, cminlen, mminlen, manifest):
    """
    """
    cdesc, cval, cgap = descriptions(cumms, cminlen, manifest)
    mdesc, mval, mgap = descriptions(maxms, mminlen, manifest)
    clen = len(cdesc);  mlen = len(mdesc)
    info = "cum={} <{}>,  max={} <{}>".format(
            list(zip(cdesc,cval)), cgap, list(zip(mdesc,mval)), mgap)
    if clen == 0:
        if mlen == 0:
            showdesc = "? 0  nothing"
            toalign = []  # 0/0: nothing to choose
        elif mlen == 1:
            showdesc = "{} {}  max".format(mdesc[0], mval[0])
            toalign = mdesc  # 0/1: unique choice
        else:
            showdesc = "? {}  0/+  {}".format(mval[0], info)
            toalign = []  # 0/+: reasonable to ignore mdesc
    elif clen == 1:
        if mlen == 0:
            showdesc = "{} {}  cum".format(cdesc[0], cval[0])
            toalign = cdesc  # 1/0: unique choice
        elif mlen == 1:
            if mdesc == cdesc:  # lists of length 1 are equal 
                showdesc = "{} {} {}  both".format(cdesc[0],cval[0],mval[0])
                toalign = cdesc # 1=1: unique choice
            else:
                showdesc = "? {} {}  1/1/conflict  {}" .format(cval[0],mval[0],info)
                toalign = cdesc + mdesc  # 1/1: align both
        else:  # mlen >= 2
            if cdesc[0] in mdesc:
                showdesc = "{} {}  1/+/ok  {}".format(cdesc[0], cval[0], info)
                toalign = cdesc  # 1<+: align the one [cdesc] or all [mdesc]
            else:
                showdesc = "? {}  1/+/conflict  {}".format(cval[0], info)
                toalign = set(cdesc+mdesc) #  1/+: align all
    else:  # clen >=2 :
        if mlen == 0:
            showdesc = "? {}  +/0  {}".format(cval[0], info)
            toalign = []  # +/0: reasonable to ignore cdesc
        elif mlen == 1: 
            if mdesc[0] in cdesc:
                showdesc = "{} {}  +/1/ok  {}".format(mdesc[0], mval[0], info)
                toalign = cdesc  # +>1: align the one [mdesc] or all [cdesc]
            else:
                showdesc = "? {}  +/1/conflict  {}".format(mval[0], info)
                toalign = set(cdesc+mdesc)  # +/1: align all
        else:
            showdesc = "? {} {}  +/+  {}".format(cval[0], mval[0], info)
            toalign = set(cdesc+mdesc)  # align all
    desc = showdesc.split(None,1)[0]  # showdesc up to first space
    return desc, toalign, showdesc


def encode_rev_flowdna(fdna, encoded=mamaslemonpy.seqs.DNA.encoded):
    """
    prepare a FlowDNA string/list (letters in {ACGTacgt+})
    for suffix array mapping
    by returning the reversed encoded DNA (charcters in {12345}) list.
    """
    enc = list(encoded(fdna, terminate=False))
    return enc[::-1]

def pattern_substring_factory(pat, opt, characters):
    """return a function that on input (p,q)
    returns the substring pat[p:q] of the pattern <pat>.
    """
    _ALPH = len(characters)
    ch = characters + characters.lower()
    def substring(p,q):
         return "".join(ch[pat[i] + _ALPH*opt[i]] for i in range(p,q))
    return substring

#######################################################################

def align_flowdna(genomic, r, args, bis=False, direction=None, cutprefix=40):
    """
    align genomic sequence <genomic> to read <r> from sff file.
    """
    fdna = flowdna.flowdna(r.flowvalues, flowchars=r.flowchars,
            maxflow=args.maxflow, maybeflow=args.alignmaybeflow)
    if bis:
        if direction==TAG_FWD:
            score = scoring.flowdna_bisulfiteCT
        elif direction==TAG_REV:
            score = scoring.flowdna_bisulfiteGA
        else:  raise ValueError("align with bisulfite requires direction")
    else:
        score = scoring.flowdna_standard
    fdna_short = cut_fdna(fdna, cutprefix)
    # compute score threshold according to arguments
    n = len(genomic)
    if n > args.alignmaxlength:  n = args.alignmaxlength
    pseudo = args.alignpseudolength
    s_pseudo = score.maxscore * pseudo
    s_possible = score.maxscore * (n+pseudo)
    if s_possible <= 1:  s_possible = 1
    score_th = int( (args.alignthreshold * s_possible) - s_pseudo + 0.5)
    # do the alignment; returned <al> is (read, genomic), not (genomic, read)
    (s, _, al) = scoring.align_genomic_to_flowdna(
                    genomic, fdna_short, score, score_th)
    aligned_gr = (al[1], al[0])  # ali = (aligned_genomic, aligned_read)
    # compute score percentage
    sc = s + s_pseudo
    if sc < 0:  sc = 0
    perc = sc / s_possible
    if perc > 0.99: perc = 0.99
    return (perc, sc, s_possible), aligned_gr
    

def cut_fdna(fdna, j):
    """
    cut the length-j prefix of fdna away;
    thus in principle return fdna[j:];
    however, pay attention if the first char of the rest is "+".
    """
    rest = fdna[j:]
    if len(rest)==0 or rest[0] != "+":  return rest
    # rest is not empty and starts with a "+":
    # prepend the previous symbol in upper case
    return fdna[j-1].upper() + rest


#######################################################################


def align_flows(genomic, r, args, bis=False, direction=None, cutprefix=40):
    """
    align genomic sequence <genomic> to read <r> from sff file,
    using its flows.
    Return pair (scoring, alignment)
    """
    if bis:
        if direction==TAG_FWD:
            scorematrix = scoring.flow_bisulfiteCT
        elif direction==TAG_REV:
            scorematrix = scoring.flow_bisulfiteGA
        else:
            raise ValueError("align_flows with bisulfite requires direction")
    else:
        scorematrix = scoring.flow_standard
    flowchars = r.flowchars[cutprefix:]
    flows = r.flowvalues[cutprefix:]
    # do the alignment
    (score, _, al) = scoring.align_genomic_to_flows(
        genomic, flows, flowchars, scorematrix, suppress_gaps=True)
    alignment = (al[1], al[0])
    # compute percentage (DUMMY -- we do not do this here)
    s_possible = scorematrix.score_match * len(genomic)
    percentage = score / s_possible
    if percentage > 1.0:  percentage = 1.0
    return (percentage, score, s_possible), alignment


## END.
