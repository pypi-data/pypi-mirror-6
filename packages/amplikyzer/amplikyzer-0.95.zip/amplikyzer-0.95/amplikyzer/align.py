# amplikyzer.align
# (c) Sven Rahmann 2011--2013
"""
Generate and display alignments of reads of specific locus and MID,
optionally of specific alleles.
Several options control the type of alignment, columns to be displayed,
and the output format.
The alignments can be loaded into an alignment viewer or editor.

"""

import sys
import os.path
from collections import Counter
from math import log10
from itertools import product

from . import utils
from .core import *
from .flowdna import revcomp
from .scoring import valid_genomics, IUPAC_sets, GAP


# constants
SENTINEL = "$"
DNA = frozenset(valid_genomics + SENTINEL)  # valid DNA characters
WILDCARDS = frozenset(valid_genomics) - frozenset("ACGT")  # wildcard characters


############################################################
# build parser

ALIGNMENT_TYPES = ("allgaps", "standard", "interesting", "allc", "cpg")
ALIGNMENT_STYLES = ("standard", "simplified", "bisulfite", "unaligned")

def buildparser(p, methylation=False):
    p.add_argument("--loci", "-l", "--locus", nargs="+", metavar="LOCUS", default=["*"],
        help="choose the loci (ROIs) for the alignment (default: '*' = iterate)")
    p.add_argument("--mids", "-m", nargs="+", metavar="MID", default=["*"],
        help="choose the MIDs for the alignment (default: '*' = iterate)")
    p.add_argument("--alleles", "-a", metavar="ALLELE",
        nargs="*", default=["*"],
        help=("only align reads with the given alleles (default: '*' = iterate). "
              + "Use without argument to collect all."))
    p.add_argument("--minreads", "-M", type=int, default=20, metavar="INT",
        help="only create alignments when at least this many reads are present")
    p.add_argument("--remark", "-r", metavar="STRING",
        help="arbitrary remark or comment for these alignments")
    if methylation: return    
    p.add_argument("--type", "-t", default="standard",
        choices=ALIGNMENT_TYPES,
        help="type of alignment (see documentation)")
    p.add_argument("--format", "-f", default="fasta",
        choices=("fasta", "text"),
        help="output format")
    p.add_argument("--style", "-s", default="standard",
        choices=ALIGNMENT_STYLES,
        help="how to display the alignment (see documentation)")
    p.add_argument("--outpath", "-o",
        default=DEFAULT_ALIGNMENTPATH, metavar="PATH",
        help="output path (joined to --path; use '-' for stdout)"),
    p.add_argument("--analysisfiles", nargs="+", metavar="FILE",
        default=["*"+EXT_AMPLIKYZER],
        help="analysis file(s) from which to generate alignments")


############################################################
# main routines

def main(args):
    clock = utils.TicToc()  # get a new clock

    # read labels from config files
    print(clock.toc(), "Reading configuration information...", file=sys.stdout)
    configinfo = utils.read_config_files(args.path, args.conf)
    labels = utils.labels_from_config(configinfo)

    # Build all alignments
    print(clock.toc(), "Building all requested alignments...", file=sys.stdout)
    builders = build_alignments(args.path, args.analysisfiles, args.loci, args.mids)

    # determine list of alleles to process, must not be empty
    alleles = list(args.alleles)
    if len(alleles) == 0:
        alleles = [""]

    # format all alignments
    print(clock.toc(), "Formatting alignments...", file=sys.stdout)
    written = 0
    minreads = args.minreads
    for aps in all_alignment_parameters(builders, alleles, minreads):
        (locus, myallele, mid, builder) = aps
        label = utils.get_label(labels, mid, locus)
        ali = Alignment(locus, myallele, mid, label, builder, args.type, args.remark)
        if ali.nrows < minreads:  continue
        afname = locus + "__" + myallele + "__" + mid + "__" + args.type + "__" + args.style    
        if args.outpath == "-":
            outname = "-"
        else:
            outpath = os.path.join(args.path, args.outpath)
            utils.ensure_directory(outpath)
            outname = os.path.join(outpath, afname)
        if args.style != "unaligned":
            print("Alignment {}: {} rows, {} columns".format(afname, ali.nrows, ali.ncols), file=sys.stdout)
        else:
            print("Unaglined {}: {} rows, length {}".format(afname, ali.nrows, len(ali.builder.reference)), file=sys.stdout)
        ali.write(outname, args.format, args.style)
        written += 1
    print(clock.toc(), "Done. Wrote {} alignments.".format(written), file=sys.stdout)


############################################################
# build alignments

def build_alignments(path, akzrfiles, loci, mids):
    """
    Align reads from given mids and loci to the genomic sequences of the given loci.
    Return a dictionary of AlignmentBuilder objects, indexed by (locus,mid).
    each containing the aligned reads from the given (locus, mid).
    These are refined alignments from the given analysis <filenames>.
    """
    # get list of analysis files
    files = []
    for af in akzrfiles:
        files.extend(utils.filenames_from_glob(path, af))
    # determine mids and loci
    mymids = frozenset(mids) if mids else frozenset(["*"])
    myloci = frozenset(loci) if loci else frozenset(["*"])
    
    # obtain the alignment builders, keep only those with >= minreads reads
    midstar = "*" in mymids
    locstar = "*" in myloci
    builders = dict()
    firstelements = []
    for filename in files:
        f = AKZRFile(filename).data()
        elements = next(f)
        if len(firstelements) == 0:
            firstelements = list(elements)
            #print("# elements:", firstelements, file=sys.stdout)  # DEBUG
        else:
            if firstelements != list(elements):
                raise FormatError("Elements mismatch in analysis files "+str(filenames))
        for alignment in f:
            mid = alignment.get('mid', '?')
            if mid.startswith("?") or ((not midstar) and (mid not in mymids)):
                continue
            locus = alignment.get('ROI', '?')
            if locus.startswith("?") or ((not locstar) and (locus not in myloci)):
                continue
            index = (locus, mid)
            b = builders.get(index)
            if b is None:
                b = AlignmentBuilder(*index)
                builders[index] = b
            extend_builder_with_alignment(b, alignment)
    # the builders now contain all alignments, irrespective of the allele
    # we finally set up the position mappings and are done.
    for b in builders.values():
        b.set_positions()
    return builders


def extend_builder_with_alignment(builder, alignment, wildcards=WILDCARDS):
    read = alignment.get('read', '?')
    genomic = alignment.get('genomic', '?')
    direction = alignment.get('direction', '?')
    if read.startswith("?") or genomic.startswith("?") or direction.startswith('?'):
        return
    read, genomic = refine_alignment(read, genomic, direction)
    assert len(read) == len(genomic)
    # collect wildcards to determine allele; it is important to do this after refinement.
    allele = "".join([r for (g,r) in zip(genomic, read) if g in wildcards])
    # add to alignment
    readname = alignment.get('__name__')
    builder.add_read(genomic, read, readname, direction, allele)


def refine_alignment(flow, genomic, direction, fillgaps=True):
    """
    refine an alignment (treat gaps) as follows:
    genomic: GTTTTTTT-A-A  >> GTTTTTTTAA$
    flow:    GT------+agA  >> GTTTTTTTAA$
    1) gaps in flow before + is filled with previous character,
       and (-,+) columns is removed.
    2) matched lowercase characters (X,y) in flow are converted to uppercase.
    3) unmatched lowercase charactes in flow  (-,y) are removed.
    4) If the read was in the reverse direction,
       flip both flow and genomic to facilitate subsequent multiple alignment.
    5) Add a sentinel $ at the end of the returned sequences.
    Return (refined_flow, refined_genomic)
    """
    fx, gx = [], []  # prepare alignment rows as lists
    n = len(flow)
    assert n == len(genomic)
    i = n-1
    while i >= 0:
        f, g = flow[i], genomic[i]
        if f.islower():
            if g != "-":
                gx.append(g)
                fx.append(f.upper())
            i -= 1
            continue
        if f != "+":  # means: f.isupper() or f=="-": 
            gx.append(g)
            fx.append(f)
            i -= 1
            continue
        # remaining case: f=="+" and g=="-"
        # genomic: TTTTTTT-
        # flow:    T------+
        #          j      i
        assert f == "+" and g == "-", "unmatched flow {} / genomic {}".format(f,g)
        j = i-1
        while flow[j]=="-": j -= 1
        c = flow[j]
        gx.append(genomic[j:i])
        fx.append(c*(i-j))
        i = j-1
    gx, fx = "".join(reversed(gx)), "".join(reversed(fx))
    if direction == TAG_REV:
        gx = revcomp(gx)
        fx = revcomp(fx)
    gx += SENTINEL
    fx += SENTINEL
    # TODO: fill gaps ???
    return(fx,gx)


class AlignmentBuilder:
    """build alignments by inserting read after read"""
    
    def __init__(self, locus, mid):
        self.locus = locus
        self.mid = mid
        self.reference = None  # reference sequence (string)
        self.genomic = None    # aligned reference sequence (list)
        self.columns = None    # columns of the alignment (list of lists)
        self.readnames = None  # list of names (strings) (per read)
        self.directions = None # list of directions (strings) (per read)
        self.alleles = None    # list of alleles (strings) (per read)
        self.refpos_for_col = None  # list: reference position for column
        self.colpos_for_ref = None  # list: column for reference position
        self.refposlines = None     # list of strings: position lines       

    def set_reference(self, reference, dna=DNA):
        assert self.reference is None
        myref = reference.replace("-","").upper()
        assert myref[-1] == "$"
        if not all(x in dna for x in myref):
            raise FormatError("illegal non-DNA characters in reference '{}'".format(myref))
        self.reference = myref
        self.genomic = list(self.reference)
        self.columns = [[] for c in self.reference]
        self.readnames = []
        self.directions = []
        self.alleles = []
            
    def add_read(self, genomic, read, readname, direction, allele, dna=DNA):
        """
        Add a new (compatible) aligned read to the existing alignment.
        The alignment (genomic, read) must be in forward direction.
        The <direction> tag indicates the original direction of the read.
        """
        if self.reference is None:
            self.set_reference(genomic)
        else:
            gx = genomic.replace("-","").upper()
            if gx != self.reference:
                raise FormatError("Disagreement between reference and genomic with read '{}'".format(readname))
        self.readnames.append(readname)
        self.directions.append(direction)
        self.alleles.append(allele)
        cols = self.columns
        ref = self.genomic
        m = len(self.readnames)  # number of reads including new one
        j = 0  # next column to process
        for (i,(g,r)) in enumerate(zip(genomic,read)):
            if g in dna: # not a gap in genomic
                while ref[j]=="-":  # skip gaps in alignment
                    cols[j].append("-")
                    j += 1 
                cols[j].append(r)
            elif g == "-":
                if ref[j]=="-":
                    cols[j].append(r)
                else:  # difficult case; need to insert a new column before j
                    newcol = ["-"]*(m-1) + [r]
                    cols[j:(j+1)] = [newcol, cols[j]]
                    ref[j:(j+1)] = ["-", ref[j]]
            else:
                raise ValueError("Illegal character in genomic: " + g)
            j += 1
        assert all(len(c)==m for c in cols), \
               str(list(len(c) for c in acols)) + " for {} ({})".format(readname,m)

    def get_read(self, i=None, string=False):
        """get row/read i from alignment, use i=None for genomic sequence"""
        if i is None or i < 0:
            result = self.genomic
        else:
            result = [c[i] for c in self.columns]
        return "".join(result) if string else result

    @property
    def nreads(self):
        """number of reads in this alignment (None = not initialized)"""
        names = self.readnames
        return len(names) if names is not None else None
    
    def set_positions(self):
        # compute refpos_for_col and colpos_for_ref:
        # refpos_for_col:  0 1 23  4    colpos_for_ref: 02458
        # reference:       G-G-AA--T    refpos index:   01234
        # column:          012345678
        refpos = [];  j = 0;  colpos = []
        for (i,g) in enumerate(self.genomic):
            if g == "-":
                refpos.append(-1)
            else:
                refpos.append(j)
                colpos.append(i)
                j += 1
        self.refpos_for_col = refpos
        self.colpos_for_ref = colpos
        ndigits = 1 + int(log10(j))
        self.refposlines = utils.positionlines(self.refpos_for_col, ndigits)


######################################################################################
## Alignments (views on AlignmentBuilders)
    
def all_alignment_parameters(builders, desired_alleles, minreads):
    """
    Yield (locus, allele, mid, builder) for each alignment to be produced.
    builders: dict {(locus, mid): AlignmentBuilder}
    desired_alleles: list of user-desired alleles, e.g. ["", "*", "A", "GT"]
      Assuming 3 IUPAC characters in the reference,
      this is  equivalent ["NNN", "*", "ANN", "GTN"], where 
      "*" is expanded to an enumeration of all abundant alleles.
    minreads:  minmum number of reads necessary to produce an alignment.
    """
    keys = sorted(builders.keys())
    for key in keys:  # key is a pair (locus, mid)
        (locus, mid) = key
        b = builders[key]  # b is the builder for (locus, mid)
        if b.nreads < minreads: continue
        if b.nreads <= 0:  continue
        
        # Which alleles exist in builder (=in reads), and how often ?
        # Note: some alleles may contain GAP characters: e.g., "A-T"
        allele_counter = Counter(b.alleles)
        # sanity check: ensure that all alleles have the same length
        allele_len = len(b.alleles[0])
        assert all(allele_len == len(a) for a in allele_counter.keys())

        # create expanded desired alleles (exdes_alleles)
        # by expanding desired_alleles to current allele length
        # and expanding "*" to the existing sufficiently abundant alleles.
        exdes_alleles = [ (a + "N"*(allele_len - len(a)) if a!="*" else "*")
                          for a in desired_alleles ]
        star = [w for w, n in allele_counter.items() if n >= minreads]
        while "*" in exdes_alleles:
            starindex = exdes_alleles.index("*")
            exdes_alleles[starindex:starindex+1] = star
            star = []
        for a in exdes_alleles:
            # Count how many reads match allele a
            # Note: a may contain gaps (if "*" has been expanded)
            counter = sum(allele_counter[x] for x in matching_alleles(a))
            if counter < minreads:  continue
            yield (locus, a, mid, b)



_IUPACS = dict(IUPAC_sets)
_IUPACS[GAP] = frozenset(GAP)
# Note: Having gaps in _IUPACS is crucial when we expand gap-containing
# IUPAC sequences to all of their DNA realizations using itertools.product.

def allele_match(observed, desired, iupacs=_IUPACS):
    """
    return True iff observed allele (e.g., "ATT")
    matches desired allele with IUPAC wildcards (e.g., "RTN").
    Arguments must be strings of the same length.
    """
    if len(observed) != len(desired):
        raise ValueError("allele_match: agument length mismatch")
    for (obs, des) in zip(observed, desired):
        if obs not in iupacs[des]:  return False
    return True


def matching_alleles(iupac_allele, iupacs=_IUPACS):
    """
    yield each allele that matches the string iupac_allele,
    which may contain IUPAC wildcards and gaps.
    For example, iupac_allele='Y-NG' would yield 8 strings,
    described by the product [CT] x [-] x [ACGT] x [G].
    """
    sets = [iupacs[c] for c in iupac_allele]
    for allele in product(*sets):
        yield "".join(allele)


#########################################################################

class Alignment:
    """Alignments represent a subset of rows and columns of an AlignmentBuilder"""
    
    def __init__(self, locus, allele, mid, label, builder, alignmenttype, remark=None):
        self.locus = locus          # string
        self.allele = allele        # string
        self.mid = mid              # string
        self.label = label          # string
        self.builder = builder      # AlignmentBuilder
        self.remark = remark        # string
        self.genomic = self.adjusted_genomic(builder.genomic, allele)
                                    # list of chars ending with $
        self.rows = self.choose_rows(allele)  # list of ints
        self._columns_cg = None
        self._columns_ch = None
        self.columns = self.choose_columns(alignmenttype) if self.nrows != 0 else []

    @property
    def title(self):
        L = [self.locus]
        if self.allele is not None and self.allele != "":
            L.append(self.allele)
        if self.label is not None:  L.append(self.label)
        return " / ".join(L)        

    @property
    def nrows(self):
        """number of rows (reads) in alignment"""
        return len(self.rows)

    @property
    def ncols(self):
        """number of columns in alignment"""
        return len(self.columns)

    @property
    def columns_cg(self):
        """indexes of CG columns in self.builder"""
        if self._columns_cg is None:
            self._columns_cg = self.find_columns("C", "G", True)
        return self._columns_cg
    
    @property
    def columns_ch(self):
        """indexes of CH columns in self.builder"""
        if self._columns_ch is None:
            self._columns_ch = self.find_columns("C", "G", False)
        return self._columns_ch

    @property
    def selected_genomic(self):
        gg = self.genomic
        cc = self.columns
        return "".join([gg[j] for j in cc])

    def adjusted_genomic(self, genomic, myallele, wildcards=WILDCARDS):
        """replace wildcards in <genomic> by characters from <myallele>"""
        mygenomic = list(genomic)  # make a copy to modify
        pos = [j for j,g in enumerate(mygenomic) if g in wildcards]
        assert len(pos) == len(myallele), "{} {} {} {} {}".format(self.locus, self.allele, self.mid, pos, myallele)
        for j, a in zip(pos, myallele):
            mygenomic[j] = a
        return mygenomic

    def choose_rows(self, allele):
        """choose alignment from builder according to allele"""
        b = self.builder
        balleles = b.alleles
        rows = [i for i in range(b.nreads) if allele_match(balleles[i], allele)]
        return rows

    def find_columns(self, nuc1, nuc2, match2=True):
        """
        return list of builder column indices,
        such that <nuc1><nuc2> occurs at given columns (if match2==True),
        or such that <nuc1>[^<nuc2>] occurs at given columns (otherwise).
        """
        b = self.builder
        ref = b.reference
        colpos = b.colpos_for_ref
        chosen = []
        ncols = len(ref) - 1  # skip the sentinel $
        for j in range(ncols):
            g, h = ref[j:j+2]
            if g != nuc1: continue
            if (match2 and h==nuc2) or ((not match2) and h!=nuc2):
                chosen.append(colpos[j])
        return chosen

    def choose_columns(self, atype, threshold=0.05):
        """choose alignment columns form bulder according to type"""
        nrows = self.nrows
        if nrows == 0:
            return []
        if atype == "cpg":
            return self.columns_cg
        if atype == "allc":
            return sorted(self.columns_ch + self.columns_cg)
        b = self.builder
        ncols = len(b.columns) - 1  # skip the sentinel $
        if atype == "allgaps":
            return list(range(ncols))
        assert atype in ("interesting", "standard")
        chosen = []
        gen = self.genomic
        for j in range(ncols):
            g = gen[j]
            if atype == "standard" and g!="-":
                chosen.append(j)
                continue
            c = b.columns[j]
            colj = [c[i] for i in self.rows]
            frac = sum(x!=g for x in colj) / nrows
            if frac >= threshold:  chosen.append(j)
        return chosen
        
    def write(self, fname, format, style):
        """
        write the alignment to file named <fname>,
        according to <format> and <style>.
        """
        if format in ("text", "txt"):
            if fname == "-":
                self.write_text(sys.stdout, style)
            else:
                with open(fname + ".txt", "wt") as f:
                    self.write_text(f, style)
        elif format == "fasta":
            if fname == "-":
                self.write_fasta(sys.stdout, style)
            else:
                with open(fname + ".fasta", "wt") as f:
                    self.write_fasta(f, style)
        else:
            raise ArgumentError("Unknown alignment format '{}'".format(format))


    def write_text(self, f, style="standard"):
        print("# Alignment of {}".format(self.title), file=f)
        if self.remark is not None:  print("#", self.remark, file=f)
        print("# {} reads, {} columns".format(
            self.nrows, self.ncols), file=f)
        if self.nrows == 0 or self.ncols ==0:  return
        # print position lines and genomic
        cols = self.columns
        refposlines = self.builder.refposlines
        for line in reversed(refposlines):
            print(".", "".join([line[j] for j in cols]), file=f)
        genomeline = "@ {}  dir  name".format(self.selected_genomic)
        print(genomeline, file=f)
        # print reads
        directions = self.builder.directions
        readnames = self.builder.readnames
        getread = self.builder.get_read
        for r in self.rows:
            fullrow = getread(r)
            row = self.reduce_row_to_style(fullrow, style)
            print("> {}  {}  {}".format(row, directions[r], readnames[r]), file=f)
        # repeat genomic and position lines
        print(genomeline, file=f)
        for line in reversed(refposlines):
            print(".", "".join([line[j] for j in cols]), file=f)

    def write_fasta(self, f, style="standard", genomicname=None):
        if genomicname is None:
            genomicname = "{}__{}__{}".format(self.locus, self.allele, self.mid)
        length = self.ncols if style != "unaligned" else len(self.builder.reference)
        print(">{} {} {} {}".format(genomicname, style, self.nrows, length),
              file=f)
        print(utils.to_fasta(self.selected_genomic), file=f)
        directions = self.builder.directions
        readnames = self.builder.readnames
        getread = self.builder.get_read
        for r in self.rows:
            fullrow = getread(r)
            row = self.reduce_row_to_style(fullrow, style)
            print(">{} {}".format(readnames[r], directions[r]), file=f)
            print(utils.to_fasta(row), file=f)
        
    def reduce_row_to_style(self, row, style):
        cols = self.columns
        gen = self.genomic
        if style == "bisulfite":
            cpgs = frozenset(self.columns_cg)
            styledrow = [_transformed_bis(row[j], "@" if j in cpgs else gen[j]) for j in cols]
            return "".join(styledrow)
        if style == "standard":
            return "".join([row[j] for j in cols])
        if style == "unaligned":
            return "".join([row[j] for j in cols if row[j]!="-"])
        if style == "simplified":
            styledrow = [_transformed_simple(row[j], gen[j]) for j in cols]
            return "".join(styledrow)
        if style == "bisulfite_numeric":
            cpgs = frozenset(self.columns_cg)
            styledrow = [_transformed_bis_num(row[j], "@" if j in cpgs else gen[j]) for j in cols]
            return styledrow
        raise ArgumentError("Unknown alignment style '{}'.".format(style))
    
##############################################################################
# alignment transformation rules

def _transformed_bis(x, g):
    if g == "@":  # C of a CpG
        return "o" if x=="T" else ("#" if x=="C" else x)
    if g == "C":  # other C
        return "_" if x=="T" else ("!" if x=="C" else x)
    if g == "-":  # gap
        return "!" if x=="C" else x
    return "_" if x==g else ("!" if x=="C" else x)

def _transformed_bis_num(x, g):
    if g == "@":  # C of a CpG
        return 0 if x=="T" else (1 if x=="C" else 0.5)
    return 0.5

def _transformed_simple(x, g):
    return "_" if (x==g and g!="-") else x


##############################################################################
