"""
module implementing thebuildindex subcommand,
control of suffix array creation
"""

from . import names
from . import utils
from .utils import dontprint
from . import suffix


def buildparser(p):
    p.add_argument("indexname",
                   help="name of the index (.seq file without extension)")
    p.add_argument("--standard", action="store_true",
                   help="build only the standard index tables")
    p.add_argument("--all", action="store_true",
                   help="build all available index tables or files")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--readnextpos", action="store_true",
                   help="read nextpos table from file instead of building it")
    g.add_argument("--nextpos", action="store_true",
                   help="build nextpos table")
    p.add_argument("--pos", action="store_true",
                   help="build pos table")
    p.add_argument("--lcp", action="store_true",
                   help="build (long) lcp table")
    p.add_argument("--lcp1", action="store_true",
                   help="build 1-byte lcp table with exceptions")
    p.add_argument("--lcp2", action="store_true",
                   help="build 2-byte lcp table with exceptions")
    p.add_argument("--bwt", action="store_true",
                   help="build bwt table")
    p.add_argument("--occ", action="store_true",
                   help="build occ table")    
    p.add_argument("--occrate", default=256, type=int,
                   help="sampling rate for occ table [256]; 0 to disable occ")
    p.add_argument("--rindex", action="store_true",
                   help="build rindex table (rank -> manifest index)")


def main(args):
    clock = utils.TicToc()
    _print = dontprint if args.quiet else print
    
    iname = args.indexname
    readnextpos = args.readnextpos
    nextpos = args.nextpos; pos = args.pos
    lcp = args.lcp; lcp1 = args.lcp1; lcp2 = args.lcp2
    bwt = args.bwt; occ = args.occ; occrate = args.occrate
    rindex = args.rindex
    if args.standard:
        pos = lcp = lcp1 = bwt = occ = True
    elif args.all:
        nextpos = pos = lcp = lcp1 = lcp2 = bwt = occ = True
    if occrate <= 0: occ = False
    anytable = pos or lcp or lcp1 or lcp2 or bwt or occ
    if (not anytable) and (not readnextpos):
        nextpos = True
        _print(clock.toc(),"nothing to do; well, let's build nextpos!")
    nextposrequired = pos or lcp
    if nextposrequired and (not readnextpos): nextpos = True
    
    # read manifest and sequence
    _print(clock.toc(),"reading {},{}...".format(names.manifest(iname), names.seq(iname)))
    sa = suffix.SuffixArray.from_indexname(iname)
    sa.seq_from_indexname(iname)
    _print(clock.toc(),"  alphabet is",sa.alphabet.__name__)
    _print(clock.toc(),"  length:",sa.length,"bp.")
    
    # nextpos
    npname = names.nextpos(iname)
    if nextpos and not readnextpos:
        _print(clock.toc(),"allocating space")
        sa._initialize_nextpos()
        _print(clock.toc(),"building nextpos and prevpos")
        sa.nextpos_from_s()
        _print(clock.toc(),"writing",npname)
        with open(npname,"wb") as fnextpos:
            sa.nextpos.tofile(fnextpos)
    if readnextpos:
        _print(clock.toc(),"reading",npname)
        sa.nextpos_from_indexname(iname)

    # get lcp from nextpos
    if lcp:
        _print(clock.toc(),"generating plcp from nextpos")
        lname = names.lcp(iname)
        sa.plcp_from_nextpos()
        _print(clock.toc(),"writing", lname)
        with open(lname,"wb") as flcp:
            for a in sa.lcp_from_plcp_generator():
                a.tofile(flcp)

    # get pos from nextpos
    if pos:
        _print(clock.toc(),"generating pos from nextpos")
        pname = names.pos(iname)
        sa.pos_from_nextpos()
        _print(clock.toc(),"writing", pname)
        with open(pname,"wb") as fpos: sa.pos.tofile(fpos)

    if rindex:
        _print(clock.toc(),"generating rindex from pos")
        riname = names.rindex(iname)
        sa.rindex_from_pos()
        _print(clock.toc(),"writing", riname)
        with open(riname,"wb") as fri:  sa.rindex.tofile(fri)

    # get lcp1, lcp2 from lcp
    if lcp1:
        lname, l1name, l1xname = names.lcp(iname), names.lcp1(iname), names.lcp1x(iname)
        _print(clock.toc(),"compressing",lname,"to",l1name,"and",l1xname)
        with open(lname,"rb") as flcp, open(l1name,"wb") as flcp1, open(l1xname,"wb") as flcp1x:
            sa.lcpn_from_lcp_streaming(flcp, flcp1, flcp1x)
    if lcp2:
        lname, l1name, l1xname = names.lcp(iname), names.lcp2(iname), names.lcp2x(iname)
        _print(clock.toc(),"compressing",lname,"to",l1name,"and",l1xname)
        with open(lname,"rb") as flcp, open(l1name,"wb") as flcp1, open(l1xname,"wb") as flcp1x:
            sa.lcpn_from_lcp_streaming(flcp, flcp1, flcp1x, n=2)

    # get bwt from pos
    if bwt:
        bname, pname = names.bwt(iname), names.pos(iname)
        _print(clock.toc(),"generating",bname,"from",pname)
        sa.pos = utils.ensure_array(sa.pos, pname)
        sa.bwt_from_pos()
        with open(bname,"wb") as fbwt: sa.bwt.tofile(fbwt)
            
    # get occ from bwt
    if occ:
        bname, occname = names.bwt(iname), names.occ(iname,occrate)
        _print(clock.toc(),"generating",occname,"from",bname,"with rate",occrate)
        sa.bwt_from_indexname(iname)
        sa.occ_from_bwt(occrate)
        with open(occname,"wb") as focc:
            sa.occ.tofile(focc)
            
    # done
    _print(clock.toc(),"done")

