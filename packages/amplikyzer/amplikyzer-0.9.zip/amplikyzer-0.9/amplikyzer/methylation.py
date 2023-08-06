# amplikyzer.methylation
# (c) Sven Rahmann 2011--2013

"""
Analyze the Cs and CpGs of an alignment for methylation.
Reads can be selected for conversion rate and valid CpGs.
Output the results as text or as image.
Two types of analyses exist (selected by the --type option).

(1) Individual sample analysis:
Show the methylation state of each CpG in each read
of a given set of reads selected by locus, MID, and allele.

(2) Comparative analysis:
shows the methylation rate of each CpG in each read set for a given locus.
The read set is specified my MID and/or allele.

"""

import sys
import os.path
from random import random
from collections import namedtuple

from .core import *
from . import utils
from . import align
from . import graphics

############################################################
# build parser

def buildparser(p):
    """populate the ArgumentParser p with options"""
    align.buildparser(p, methylation=True)  # re-use some of align's arguments
    p.add_argument("--type", "-t", default="smart",
        choices=("individual", "comparative", "all", "smart"),
        help="type of methylation analysis (individual or comparative)")
    p.add_argument("--format", "-f", default="png",
        choices=("png", "svg", "pdf", "text", "txt"),
        help="output format ('text' or image type)")
    p.add_argument("--style", default="color",
        choices=("color", "bw"),
        help="output style for images (color or bw)")
    p.add_argument("--conversionrate", "-c", type=float,
        default=0.95, metavar="FLOAT",
        help="minimum bisulfite conversion rate for using a read")
    p.add_argument("--badcpgs", "-b", type=float,
        default=2.0, metavar="INT/FLOAT",
        help="maximum number (>=1) or rate (<1.0) of untermined CpG states for using a read")
    p.add_argument("--outpath", "-o",
        default=DEFAULT_METHYLATIONPATH, metavar="PATH",
        help="output path (joined to --path; use '-' for stdout)"),
    p.add_argument("--analysisfiles", nargs="+", metavar="FILE",
        default=["*"+EXT_AMPLIKYZER],
        help="analysis file(s) from which to generate the alignment(s)")
    p.add_argument("--showpositions", "-p", action="store_true",
        help="show CpG positions instead of simple indices")
    p.add_argument("--sort", "-s", nargs="+", metavar="OPTION",
        default=["meth:down"],
        help=("by methylation ('meth:down', 'meth:up'), given MIDs ('mids:MID17,MID13,...'), "
              + "alleles ('alleles:GA,GG,CA,CG')") )


############################################################
# comparative methylation analysis

SampleSummary = namedtuple("SampleSummary",
    "total_meth_rate  allele  mid  label  nreads  cpg_meth_rates  cpg_positions")
    # attribute order determines sorting order


class ComparativeAnalysis:
    """
    Comparative methylation analysis of one locus
    between different individuals (MIDs).
    """
    def __init__(self, locus, allele=None, mid=None, label=None, remark=None):
        self.locus = locus
        self.allele = allele
        self.mid = mid  # only if mid is constant, generally not specified
        self.label = label  # only if mid is constant, generally not specified
        self.remark = remark  # string, any user-defined remark for plots
        self._samples = []  # private list of individual analyses

    def __len__(self):
        return len(self._samples)

    @property
    def shape(self):
        """matrix shape: a pair (number of samples, number of CpGs)"""
        nrows = len(self._samples)
        lens = [len(a.cpg_meth_rates) for a in self._samples]
        ncols = max(lens) if len(lens) > 0 else 0
        if not all(ell == ncols for ell in lens):
            return (nrows, None)
        return (nrows, ncols)

    @property
    def cpg_positions(self):
        """list of reference positions of CpGs; or None if inconsistent"""
        pos = None
        for a in self._samples:
            if pos is None:
                pos = a.cpg_positions
            else:
                if pos != a.cpg_positions: return None
        return pos

    @property
    def title(self):
        L = [self.locus]
        if self.allele is not None:  L.append(self.allele)
        if self.label is not None:  L.append(self.label)
        return " / ".join(L)

    def add_sample(self, s):
        if not isinstance(s, SampleSummary):
            raise TypeError("argument 's' must be a SampleSummary instance")
        self._samples.append(s)

    def sample_names(self):
        """
        yield a minimal printable name
        for each SampleSummary in this ComparativeAnalysis
        """
        for s in self._samples:
            name = []
            if self.label is None:
                name.append(s.label)
            if self.allele is None:
                name.append(s.allele)
            yield " ".join(name)        

    def sort(self, sortoption):
        """sort the samples in this comparative analysis by the given option"""
        so = sortoption.lower()
        if so in {"meth:up", "meth"}:
            self._samples.sort()
        elif so in {"meth:dn", "meth:down"}:
            self._samples.sort(reverse=True)
        elif so.startswith("mids:"):
            # sort by given MIDs
            mids = [m.strip() for m in sortoption[len("mids:"):].split(",")]
            result = list()
            for mid in mids:
                found = [s for s in self._samples if s.mid == mid]
                result.extend(found)
                if len(found) == 0:
                    print("Warning: MID '{}' not found in samples.".format(mid), file=sys.stdout)
            self._samples = result
        elif so.startswith("alleles:"):
            # sort comparative analysis by given alleles
            alleles = [a.strip() for a in sortoption[len("alleles:"):].split(",")]
            result = list()
            for allele in alleles:
                found = [s for s in self._samples if s.allele.startswith(allele)]
                result.extend(found)
            self._samples = result
        else:
            raise ValueError("unknown --sort option '{}'".format(sortoption))
        
    def as_matrix(self):
        """return a samples x CpG matrix (list of lists) of methylation rates"""
        return [s.cpg_meth_rates for s in self._samples]

    def write(self, fname, format, style, options=None):
        """
        write the comparative analysis to file named <fname>,
        according to <format> (text/image) and <style> (bw/color),
        using the given options dictionary (showpositions).
        Return the success state.
        """
        if options is None:  options=dict()
        if format in ("text", "txt"):
            m, n = self.shape
            if n is None:  return False
            if fname == "-":
                result = self.write_text(sys.stdout, style, options)
            else:
                with open(fname + ".txt", "wt") as f:
                    result = self.write_text(f, style, options)
        elif format in ("png", "svg", "pdf"):
            if fname != "-":
                fname = fname + "." + format
            result = graphics.plot_comparative(self, fname, format, style, options)
        else:
            raise ArgumentError("Output format '{}' not implemented".format(format))
        return result


    def write_text(self, f, style=None, options=None):
        if options is None: options=dict()
        cpgpos = self.cpg_positions
        if cpgpos is None:  return False
        showpositions = options["showpositions"]
        m, n = self.shape
        print("Comparative Analysis of {}".format(self.title), file=f)
        if self.remark is not None:  print(self.remark, file=f)
        print("{} samples, {} CpGs\n".format(m,n), file=f)
        if m == 0 or n == 0:  return False
        if showpositions:
            print(" ".join(["@{:d}".format(pos) for pos in cpgpos]), file=f)
        else:
            print(" ".join("#{:d}".format(i+1) for i,pos in enumerate(cpgpos)), file=f)
        for s, name in zip(self._samples, self.sample_names()):
            # s is a SampleSummary instance
            print(name, end=" ", file=f)
            for x in s.cpg_meth_rates:
                print("{:4.0%} ".format(x), end="", file=f)
            print(" ({:5.1%}, {:4d} reads)".format(s.total_meth_rate, s.nreads), file=f)
        return True


############################################################
# individual methylation analysis class

class MethylationAnalysis(align.Alignment):
    """MethylationAnalysis annotates an Alignment with methylation information"""

    def __init__(self, locus, allele, mid, label, builder,
                 minconvrate=0.0, maxbadcpgs=0.99999, remark=None):
        """
        set attributes
            .rows: selected rows from alignment passing filter
            .cpg_positions: positions of CpGs in reference (1-based)
            .cpg_meth_rates: methylation rate per CpG
            .conversion_rates: bisulfite conversion rate per read
            .bad_cpg_rates: fraction of unidentified CpG status per read
            .read_meth_rates: methylation rate per read
            .total_meth_rate:  overall methylation rate (float)
        """
        super().__init__(locus, allele, mid, label, builder, "cpg", remark)
        refpos = self.builder.refpos_for_col
        self.cpg_positions = [refpos[c]+1 for c in self.columns]
        # compute initial per-read statistics
        (convrates, badrates, _) = self.per_read_statistics()
        # pick rows with sufficient conversion rate and reduce alignment
        maxbadrate = maxbadcpgs/self.ncols if maxbadcpgs >= 1.0 else maxbadcpgs
        self.rows = [i for i,c,b in zip(self.rows, convrates, badrates)
                     if c >= minconvrate and b <= maxbadrate]
        # re-compute per-read statistics for selected rows
        (self.conversion_rates, self.bad_cpg_rates, self.read_meth_rates) = self.per_read_statistics()
        # compute column and overall methylation rates
        (self.cpg_meth_rates, self.total_meth_rate) = self.per_cpg_and_overall_statistics()
        self.sort("random")


    def sort(self, sortoption):
        """re-sort the individual reads according to a given sort option"""
        # permutes self.rows according to sort option.
        # consequently also permutes
        # self.read_meth_rates, self.conversion_rates, self.bad_cpg_rates
        attributes_to_permute = ('rows', 'read_meth_rates', 'conversion_rates', 'bad_cpg_rates')
        L = len(self.rows)
        for attr in attributes_to_permute:
            assert(len(getattr(self,attr)) == L)
        so = sortoption.lower()
        permutation = list(range(L))  # identity permutation
        s = None
        if so == "random":
            s = sorted([ (random(), i) for i in range(len(self.rows)) ])
        elif so in {"meth:up", "meth"}:
            s = sorted([ (m, i) for (i,m) in enumerate(self.read_meth_rates) ])
        elif so in {"meth:dn", "meth:down"}:
            s = sorted([ (m, i) for (i,m) in enumerate(self.read_meth_rates) ], reverse=True)
        elif so.startswith("mids:"):
            # ignore sorting by MID here, makes no sense
            pass
        elif so.startswith("alleles:"):
            alleles = [a.strip() for a in sortoption[len("alleles:"):].split(",")]
            balleles_getitem = self.builder.alleles.__getitem__
            rowalleles = list(map(balleles_getitem, self.rows))
            permutation = list()
            for allele in alleles:
                found = [i for (i,a) in enumerate(rowalleles) if a.startswith(allele)]
                permutation.extend(found)
        else:
            raise ValueError("unknown --sort option '{}'".format(sortoption))
        if s is not None:
            permutation = [info[-1] for info in s]
        for attr in attributes_to_permute:
            attr_getitem = getattr(self, attr).__getitem__
            setattr(self, attr, list(map(attr_getitem, permutation)))


    def per_read_statistics(self):
        """
        Return 3 lists:
        (conversion_rates, bad_cpg_rates, read_methylation_rates).
        Each list contains one value (a rate) for each read.
        """
        bcols = self.builder.columns
        convrates = [];  badrates = [];  methrates = []
        for r in self.rows:
            goodc = badc = 0
            for j in self.columns_ch:  # the pure C columns
                seen = bcols[j][r]
                if seen == "T":  goodc += 1
                elif seen == "C":  badc += 1
            totalc = goodc + badc
            rate = goodc/totalc if totalc != 0 else 0.0
            convrates.append(rate)
            meth = unmeth = badcg = 0
            for j in self.columns_cg:  # the CG columns
                seen = bcols[j][r]
                if seen == "T":  unmeth += 1
                elif seen == "C":  meth += 1
                else:  badcg += 1
            total = meth + unmeth + badcg       
            rate = badcg/total if total != 0 else 1.0
            badrates.append(rate)                
            total = meth + unmeth        
            rate = meth/total if total != 0 else 0.0
            methrates.append(rate)
        return (convrates, badrates, methrates)

    def per_cpg_and_overall_statistics(self):
        """
        Return a pair of a list and a float:
        (cpg_methylation_rates, total_methylation_rate).
        The list contains the methylation rate for each CpG in order.
        """
        bcols = self.builder.columns
        rows = self.rows
        rates = []
        tmeth = tunmeth = 0
        for j in self.columns_cg:  # the CG columns
            col = bcols[j]
            meth = unmeth = 0
            for r in rows:
                seen = col[r]
                if seen == "T":  unmeth += 1
                elif seen == "C":  meth += 1
            total = meth + unmeth
            rate = meth/total if total != 0 else 0.0
            rates.append(rate)
            tmeth += meth;  tunmeth += unmeth
        total = tmeth + tunmeth
        rate = tmeth/total if total != 0 else 0.0
        return (rates, rate)

    def as_matrix(self):
        """
        Return CpG methylation states as matrix (list of lists).
        Each value is in {0: unmethylated, 0.5: unknown, 1: methylated}.
        """
        L = []
        getread = self.builder.get_read
        for r in self.rows:
            L.append(self.reduce_row_to_style(getread(r), "bisulfite_numeric"))
        return L

    def write(self, fname, format, style, options=None):
        """
        write the analysis to file named <fname>,
        according to <format> and <style>.
        """
        if options is None: options = dict()
        if format in ("text", "txt"):
            if fname == "-":
                self.write_text(sys.stdout, style, options)
            else:
                with open(fname + ".txt", "wt") as f:
                    self.write_text(f, style, options)
        elif format in ("png", "svg", "pdf"):
            if fname != "-":
                fname = fname + "." + format
            graphics.plot_individual(self, fname, format, style, options)
        else:
            raise ArgumentError("Output format '{}' not implemented".format(format))


    def write_text(self, f, style=None, options=None):
        if options is None:  options=dict()
        showpositions = options['showpositions']
        print("Methylation Analysis of {}".format(self.title), file=f)
        if self.remark is not None:  print(self.remark, file=f)
        print("{} reads, {} CpGs".format(self.nrows, self.ncols), file=f)
        if self.nrows == 0 or self.ncols == 0:  return
        print("Methylation rate: {:.1%}\n".format(self.total_meth_rate), file=f)
        print(" ".join("{:.0%}".format(m) for m in self.cpg_meth_rates), file=f)
        if showpositions:
            print(" ".join("@{:d}".format(pos) for pos in self.cpg_positions), file=f)
        else:
            print(" ".join("#{:d}".format(i+1) for i,pos in enumerate(self.cpg_positions)), file=f)
        cols = self.columns
        getread = self.builder.get_read
        for r, m in zip(self.rows, self.read_meth_rates):
            row = self.reduce_row_to_style(getread(r), "bisulfite")
            print("{} {:4.0%}".format(row,m), file=f)

    def write_fasta(self, f, style=None, genomicname=None, options=None):
        raise NotImplementedError("FASTA format not available for MethylationAnalysis")
    

############################################################
# main routine

def main(args):
    clock = utils.TicToc()  # get a new clock

    # read labels from config files
    print(clock.toc(), "Reading configuration information...", file=sys.stdout)
    configinfo = utils.read_config_files(args.path, args.conf)
    labels = utils.labels_from_config(configinfo)
    
    # build all required alignments
    print(clock.toc(), "Building all requested alignments...", file=sys.stdout)
    builders = align.build_alignments(args.path, args.analysisfiles, args.loci, args.mids)

    # determine list of alleles to process, must not be empty
    alleles = list(args.alleles)
    if len(alleles) == 0:
        alleles = [""]
    
    mystyle = "simple" if args.format in ("text", "txt") else args.style    
    minreads = args.minreads
    cas = dict()  # locus -> ComparativeAnalysis instance

    # process all alignments to produce each individual sample analysis
    print(clock.toc(), "Formatting alignments...", file=sys.stdout)
    analyzed = 0
    for aps in align.all_alignment_parameters(builders, alleles, minreads):
        # produce a new individual sample MethylationAnalysis
        (locus, allele, mid, builder) = aps
        label = utils.get_label(labels, mid, locus)
        #print("    ",locus,allele,mid,label)
        ma = MethylationAnalysis(locus, allele, mid, label, builder,
            args.conversionrate, args.badcpgs, remark=args.remark)
        if ma.nrows < minreads:  continue
        analyzed += 1
        # sort the reads according to sort options
        for sortoption in reversed(args.sort):
            ma.sort(sortoption)
        # collect summary information of this individual sample analysis
        asy = SampleSummary(ma.total_meth_rate, ma.allele, ma.mid, ma.label,
                ma.nrows, tuple(ma.cpg_meth_rates), tuple(ma.cpg_positions))
        if locus not in cas:
            cas[locus] = ComparativeAnalysis(locus, remark=args.remark)
        cas[locus].add_sample(asy)
        # output individual results if desired
        if args.type in ("individual", "all", "smart"):
            afname = locus + "__" + allele + "__" + mid + "__individual__" + mystyle
            if args.outpath == "-":
                outname = "-"
            else:
                outpath = os.path.join(args.path, args.outpath)
                utils.ensure_directory(outpath)
                outname = os.path.join(outpath, afname)
            print("Individual Analysis {}: {} reads, {} CpGs".format(
                    afname, ma.nrows, ma.ncols), file=sys.stdout)
            options = dict(showpositions=args.showpositions)
            ma.write(outname, args.format, args.style, options)

    # done processing all alignments.
    # next, do comparison analysis, if requested
    print(clock.toc(),
        "Analyzed {} alignments with >= {} reads with conversion >= {}".format(
            analyzed, minreads, args.conversionrate),
        file=sys.stdout)
    if args.type == "individual": return
    
    analyzed = 0
    for locus in sorted(cas.keys()):
        ca = cas[locus]
        # sort and filter the samples of the comparative analysis
        for sortoption in reversed(args.sort):
            ca.sort(sortoption)
        if len(ca) < 2 and args.type == "smart":  continue
        if len(ca) == 0: continue
        afname = locus + "__comparative__" + mystyle
        if args.outpath == "-":
            outname = "-"
        else:
            outpath = os.path.join(args.path, args.outpath)
            utils.ensure_directory(outpath)
            outname = os.path.join(outpath, afname)
        options = dict(showpositions=args.showpositions)
        result = ca.write(outname, args.format, args.style, options)
        if not result:  # failed because of different number of CpGs
            print("Comparative Analysis {}: FAILED, different numbers of CpGs".format(
                afname), file=sys.stdout)            
        analyzed += 1
        print("Comparative Analysis {}: {} individual samples".format(
            afname, len(ca)), file=sys.stdout)
    print(clock.toc(),
          "Finished comparative analysis for {} loci".format(analyzed),
          file=sys.stdout)
