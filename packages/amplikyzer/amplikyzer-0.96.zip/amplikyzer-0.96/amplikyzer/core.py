"""
core module for amplikyzer
(c) 2011--2012 Sven Rahmann
"""

# keep imports to a minimum,
# because other modules will do 'from .core import *'

import collections

############################################################################
# constants 

EXT_AMPLIKYZER = ".akzr"  # amplikyzer analysis file extension
EXT_CONFIG = ".conf"  # config file extension (.cfg is problematic)

DEFAULT_INDEXPATH = "__index__"
DEFAULT_ALIGNMENTPATH = "alignments"
DEFAULT_METHYLATIONPATH = "methylation"

DEFAULT_MAXFLOW = 4  # was 5
DEFAULT_CERTAINFLOW = 0.20    # 0.10, 0.15, (0.20) are reasonable
DEFAULT_MAYBEFRACTION = 0.10  # 0.1
DEFAULT_ALIGNMAYBEFLOW = 0.35 # was 0.25; 0.1 results in bad scores due to many insertions
DEFAULT_ALIGNTHRESHOLD = 0.70 # 0.65 is a reasonable value, fast and accurate
DEFAULT_ALIGNPSEUDOLENGTH = 10
DEFAULT_ALIGNMAXLENGTH = 350
DEFAULT_OPTIONALS_FILTERS = ((20,3),)  # 3/20 = 15%

TAG_FWD = "FWD"
TAG_REV = "REV"
assert len(TAG_FWD) == len(TAG_REV)
TAG_LEN = len(TAG_FWD)
TAGSUFFIX_SEP = "___"
TAGSUFFIX_FWD = TAGSUFFIX_SEP + TAG_FWD
TAGSUFFIX_REV = TAGSUFFIX_SEP + TAG_REV
TAGSUFFIX_ANY = (TAGSUFFIX_FWD, TAGSUFFIX_REV)

FLOWCHARS_454 = "TACG"  # the order of nucleotide flows for 454jr

############################################################################
# elements of a read
# can be customized in a config file with an [ELEMENTS] section
# formatted as described here

ElementInfo = collections.namedtuple("ElementInfo",
    ["name", "section", "rc", "bis",
     "startpos", "tolerance",
     "minlen_single", "minlen_max", "minlen_cum",
     "required", "special"] )
ElementInfoTypes = (str, str, str, str,   int, int,  int, int, int,   int, str)

BIS_NONE, BIS_TAGGED, BIS_ALL = "bis_none", "bis_tagged", "bis_all"
SPECIAL_NONE, SPECIAL_TAG, SPECIAL_TARGET = "special_none", "special_tag", "special_target"

CONFIG_STANDARD_ELEMENTS = """
[ELEMENTS]
# syntax is:
# order = ( name,  config.SECTIONHEADER,  rc_{no|ok},  bis_{none|tagged|all},
#           startpos,  tolstartpos|-1,  minlen_single, minlen_max, minlen_cum,
#           required=0|1, special_{none|tag|target} )
1 = key, KEYS,   rc_no, bis_none,    0,  1,   4,  4,  4,   0, special_none
2 = mid, MIDS,   rc_no, bis_none,    4,  7,   5,  7,  7,   0, special_none
3 = tag, TAGS,   rc_no, bis_none,   12, 34,   4, 10, 12,   0, special_tag
4 = locus, LOCI, rc_ok, bis_tagged, 28, -1,  14, 30, 50,   1, special_target
"""


############################################################################
# Amplikyzer errors and exceptions

class ArgumentError(RuntimeError):
    """illegal combination of arguments given"""
    pass

class MissingArgumentOut(ArgumentError):
    """must specify filename when more than one file of given group is present"""
    pass

class FormatError(RuntimeError):
    """
    an error in the format of a configuration or analysis file,
    or an unrecognized tag has appeared somewhere.
    """
    pass

##############################################################################
# Parsing an .akzr file

class AKZRFile:
    """
    The generator AKZRFile(filename).data() yields each read's elements.
    
    The elements are defined by the @ELEMENT and @ALIGNMENT header lines
    within the file.
    """
    
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        filename = self.filename
        if filename == "-":
            elements, line = self._read_header(sys.stdin)
            yield elements
            for d in self._read_entries(sys.stdin, elements, line):
                yield d
        else:
            with open(filename,  "rt") as f:
                elements, line = self._read_header(f)
                yield elements
                for d in self._read_entries(f, elements, line):
                    yield d
    
    def _read_header(self, f):
        # Read lines starting with @; they contain the element information    
        elements = []
        while True:
            line = _getline(f)
            if line.startswith(">"): break
            if line.startswith(("@SFF ", "@CONF ", "@ARG ")): continue
            if not line.startswith(("@ELEMENT ","@ALIGNMENT ")):
                raise FormatError("expected only @ELEMENT or @ALIGNMENT lines: "+line)
            fields = line.split()
            elements.append(fields[1])
        return elements, line

    def _read_entries(self, f, elements, line):
        current = dict()
        while True:
            # read the information of a single read
            # invariant: current line starts with '>'
            if not line.startswith(">"):
                raise FormatError("header line with '>' expected")
            content = line[1:].split()[0]
            current['__name__'] = content
            for el in elements:
                line = _getline(f)
                content = line.split()[0]
                current[el] = content
            yield current
            try:
                line = _getline(f)
            except StopIteration:
                break
## end class AKZRFile


def _getline(f):
    """
    get next line from filelike <f>,
    skipping empty lines and lines with "#".
    """
    while True:
        line = next(f).strip()
        if not line.startswith("#") and len(line)>0: break
    return line


##############################################################################
