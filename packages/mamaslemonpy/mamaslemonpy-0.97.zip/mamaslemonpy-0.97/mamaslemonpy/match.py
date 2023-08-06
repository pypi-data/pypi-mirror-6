"""
module implementing the match subcommand;
matching patterns against the index
"""

from . import names
from . import utils
from . import seqs
from . import suffix

def buildparser(p):
    p.add_argument("pattern", help="string to match against the index")
    p.add_argument("indexname", help="name of the index")
    p.add_argument("--mode", "-m", default="full",
                   choices={"full","suffix","prefix","bms","mum","mm"},
                   help="search mode (default: full)")
    p.add_argument("--minlen", type=int, default=0,
                   help="minimum length of matches to report")
    p.add_argument("--errors", "-e", type=int, default=0,
                   help="maximum number of allowed errors (mismatches+indels)")
    p.add_argument("--nolcp", action="store_true",
                   help="never use the lcp array (save memory, waste time)")
    p.add_argument("--occrate", default=0, type=int,
                   help="specify which *.occ file should be used [0: choose fastest]")


def main(args):
    clock = utils.TicToc()
    iname = args.indexname
    
    # encode the pattern according to index alphabet
    alphabet = seqs.get_alphabet_from_indexname(iname)
    pattern = list(alphabet.encoded(args.pattern, terminate=False))
    #print("pattern is {} with length {}".format(pattern,len(pattern)))
    
    mode = args.mode
    if mode in {"full", "suffix", "prefix", "mum", "mm"}:
        do_matching(pattern, iname, args, clock)
    elif mode in {"bms"}:
        do_bms(pattern, iname, args, clock)
    else:
        raise NotImplementedError("Method / mode {} not implemented".format(mode))
    # done
    print(clock.toc(),"done")


def _get_suffix_array(iname, args, clock):
    mode = args.mode
    # get an empty suffix array
    sa = suffix.SuffixArray.from_indexname(iname)
    # we need bwt and occ in any case
    print(clock.toc(),"reading {}, {}...".format(names.bwt(iname),names.occ(iname,"*")))
    sa.bwt_from_indexname(iname)
    sa.occ_from_indexname(iname, args.occrate)
    print(clock.toc(),"  occrate =", sa.occ.occrate)
    # in some cases, we need lcp1 as well
    if mode in {"prefix","mm","mum","bms"} and not args.nolcp:
        print(clock.toc(),"reading {}...".format(names.lcp1(iname)))
        sa.lcp_from_indexname(iname,1)
    return sa
    

def do_matching(pat, iname, args, clock):
    sa = _get_suffix_array(iname, args, clock)
    mode = args.mode;  minlen = args.minlen;  errors = args.errors;
    print(clock.toc(),"matching backwards...")
    if mode in {"full", "suffix"}:
        matches = sa.backward_search(pat, minlen=minlen, errors=errors)
    elif mode in {"prefix"}:
        matches = sa.prefix_search(pat, minlen=minlen, errors=errors)
    elif mode in {"mm", "mum"}:
        matches = sa.mms(pat, minlen=minlen, errors=errors, unique=(mode=="mum"))
    matches = list(matches)
    # now, matches is a list with (i, matchlen, L, R) tuples
    # to report, we need the sequence and the pos array
    sa.bwt = None;  sa.occ = None
    print(clock.toc(),"reading {}, {}...".format(names.seq(iname),names.pos(iname)))
    sa.seq_from_indexname(iname)
    sa.pos_from_indexname(iname)
    m = len(pat)
    for (i, j, mlen, L, R) in matches:
        if mlen < m and args.mode == "full": continue
        for r in range(L, R+1):
            p = sa.pos[r]
            print(i, j, mlen, p, sa.substring(p, p+mlen))
            
def do_bms(pat, iname, args, clock):
    sa = _get_suffix_array(iname, args, clock)
    minlen = args.minlen
    print(clock.toc(),
        "computing backward matching statistics (lcp_threshold={})...".format(sa.lcp_threshold))
    bms = sa.backward_matching_statistics(pat, errors = args.errors)
    oldstartpos = len(pat)
    for (i,startpos,mlen,L,R) in bms:
        if mlen >= minlen:
            if startpos == oldstartpos:
                jump = "."
            else:
                jump = "+U" if R==L else "+"            
            print(i, startpos, mlen, R-L+1, jump)
        oldstartpos = startpos
            

