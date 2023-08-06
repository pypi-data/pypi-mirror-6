import sys
import argparse
import array

from .utils import dontprint

# import the subcommand modules
from . import translate
from . import buildindex
from . import statistics
from . import match
from . import mapcount


#######################################################################
# check system

BITS = 0
def checksystem(args):
    global BITS
    _print = dontprint if args.quiet else print
    if sys.version_info < (3,2):
        _print("Python >= 3.2 required", file=sys.stderr)
    a = array.array("l")
    if a.itemsize != 8:
        _print("WARNING: This is not a 64-bit machine!", file=sys.stderr)
    BITS = a.itemsize * 8


#######################################################################

# build full command line arguments parser from subcommands
def buildparser(subcommands):
    p = argparse.ArgumentParser(
        description = "mamaslemon: Mapping with Matching Statistics and Long Exact Matching OligoNucleotides",
        epilog = "In development. Use at your own Risk! Use '{subcommand} -h' for help on subcommands."
        )
    p.add_argument("--quiet", "-q", action="store_true",
                   help="suppress progress output")
    sp = p.add_subparsers(title="Valid subcommands")
    sp.required = True
    sp.dest = "subcommand"
    for (scname,(schelp,scfunction,scbuildparser)) in subcommands.items():
        pp = sp.add_parser(scname, help=schelp)
        pp.set_defaults(func=scfunction)
        scbuildparser(pp)
    return p

# available subcommands: (description, command-function, buildparser-function)
_SUBCOMMANDS = dict(
    translate=("translate (encode) fasta-formatted files into binary .seq",
        translate.main, translate.buildparser),
    buildindex=("build index tables from .seq file: .pos .lcp .bwt .occ ...",
        buildindex.main, buildindex.buildparser),
    statistics=("write index statistics to stdout",
        statistics.main, statistics.buildparser),
    match=("report all starting positions of a pattern to stdout",
        match.main, match.buildparser),
    mapcount=("map FASTQ reads to index using maximal unique matches and write counts to stdout",
        mapcount.main, mapcount.buildparser),              
    )

# get_argument_parser function for geniegui
def get_argument_parser():
    return buildparser(_SUBCOMMANDS)

# main fuction for geniegui
def main(args=None):
    p = get_argument_parser()
    pargs = p.parse_args(args)
    checksystem(pargs)
    pargs.func(pargs)        

def test():
    testargs = ["translate","-i","blubb","-r","x.fa","y.fa","z.fa"]
    main(testargs)

