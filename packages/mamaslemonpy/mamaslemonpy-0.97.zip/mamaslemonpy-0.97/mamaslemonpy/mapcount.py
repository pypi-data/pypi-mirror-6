"""
module implementing the mapcount subcommand;
map a FASTQ file against the index and count features
"""

from collections import Counter
from . import names
from . import utils
from . import seqs
from . import suffix


def buildparser(p):
    p.add_argument("fastq", help="name of fastq file")
    p.add_argument("indexname", help="name of the index")
    p.add_argument("-l", "--minlen", type=int, default=7,
                   help="minimum required length of matches")
    p.add_argument("-m", "--minmatches", type=int, default=14,
                   help="minimum required number of matches")
    p.add_argument("--errors", "-e", type=int, default=0,
                   help="maximum number of allowed errors (mismatches+indels)")

def main(args):
    clock = utils.TicToc()
    iname = args.indexname
    alphabet = seqs.get_alphabet_from_indexname(iname)
    a_encoded = alphabet.encoded
    sa = _get_suffix_array(iname)
    minlen = args.minlen
    minmat = args.minmatches
    errors = args.errors
    rindex = sa.rindex
    results = [0]*len(sa.manifest)

    from sqt.io.fasta import FastqReader
    with FastqReader(args.fastq) as f:
        for (t,record) in enumerate(f):
            pattern = list(a_encoded(record.sequence, terminate=False))
            matches = list(sa.mms(pattern, minlen=minlen, errors=errors, unique=True))
            # each match is a tuple (left, right, ms, L, R)
            index = _process_matches(matches, rindex, minmat) if len(matches) > 0 else None
            if index is not None:
                results[index] += 1
            #print(index, len(matches))
            #if t == 10000: break
    print("feature\tcount")
    for record, res in zip(sa.manifest, results):
        print(record[4], "\t", res, sep="")


def _get_suffix_array(iname):
    sa = suffix.SuffixArray.from_indexname(iname)
    sa.bwt_from_indexname(iname)
    sa.occ_from_indexname(iname, 1)
    sa.lcp_from_indexname(iname, 1)
    sa.seq_from_indexname(iname)
    #sa.pos_from_indexname(iname)
    sa.rindex_from_indexname(iname)
    return sa

def _process_matches(matches, rindex, minmat):
    c = Counter()
    for m in matches:
        (_, _, length, L, R) = m
        for r in range(L, R+1):
            c[rindex[r]] += length
    best = c.most_common(2)
    if len(best) == 1 or (best[0][1] > best[1][1]):
        if best[0][0] >= minmat:               
            return best[0][0]
    return None
        

def do_matching(pat, iname, args, clock):
    mode = args.mode; 
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
            

