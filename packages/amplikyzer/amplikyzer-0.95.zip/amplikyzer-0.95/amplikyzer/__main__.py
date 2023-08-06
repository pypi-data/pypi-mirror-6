# amplikyzer
# (c) Sven Rahmann
"""analyze a set of 454 amplicon reads in .sff format
w.r.t. given keys, MIDs, tags, primers, genome loci, etc.
"""
import sys
from   amplikyzer.main import main

sys.argv[0] = "amplikyzer" 
main()
