"""
module implementing the statistics subcommand
"""

import sys

from . import names
from . import utils
from . import suffix

def buildparser(p):
    p.add_argument("indexname",
                   help="name of the index (filename without extension)")
    p.add_argument("--uniq","-u","--uniqueness",
                   default=False, action="store_true",
                   help="output uniqueness statistics of substrings")
    p.add_argument("--lcp","-l",
                   default=False, action="store_true",
                   help="output lcp statistics")
    p.add_argument("--max","-m", type=int,
                   default=254, help="maximum exact value for statistics")
    p.add_argument("--lcpmode", type=int, default=1, choices=(-2,-1,0,1,2),
                   help="mode of lcp table to read (advanced option)")


def _lcp_pos_pairs(sa):
    s, head = sa.s, 2
    lcpl = pl = p = -1
    for (lcpr,pr) in zip(sa.lcp, sa.pos):
        if head > 0:
            head -= 1
        else:
            yield(lcpl, lcpr, pl, p, pr)
        lcpl, pl, p = lcpr, p, pr


def _print_statistics(stats, file=None):
    """private helper function to print statistics to a file"""
    if file is None: file = sys.stdout
    total = sum(stats);  cum = 0;  cumpercent = 0.0
    for (i,stat) in enumerate(stats):
        percent = 100*stat/total if total!=0 else 0.0
        cumpercent += percent
        cum += stat
        print("{:3d}  {:d} = {:.2f}% ({:.2f}%)".format(i,stat,percent,cumpercent), file=file)
        if cum >= total: break
        

def main(args):
    """main function of the statistics module, called from core module"""
    clock = utils.TicToc()
    iname = args.indexname
    getsequence = args.uniq
    sa = suffix.SuffixArray.from_indexname(iname)

    if args.uniq or args.lcp:
        # we need the lcp array
        print(clock.toc(),"reading", names.lcp_names[args.lcpmode](iname))
        sa.lcp_from_indexname(iname, mode=args.lcpmode)
    
    if args.uniq:
        # we need the pos array, too
        print(clock.toc(),"reading", names.pos(iname))
        sa.seq_from_indexname(iname)
        sa.pos_from_indexname(iname)
        # compute and print the statistics
        print(clock.toc(),"computing uniqueness statistics")
        us = stats_uniqueness(sa, maxvalue=args.max)
        print(clock.toc(),"done")
        _print_statistics(us)
            
    if args.lcp:
        print(clock.toc(),"computing lcp statistics")
        ls = stats_lcp(sa)
        print(clock.toc(),"done")
        _print_statistics(ls)
           


def stats_uniqueness(sa, maxvalue=254):
    us = [0]*(maxvalue+2)  # can index 0 .. maxvalue+1
    s = sa.s
    special = sa.alphabet.isspecial
    # while in principle, the shortest unique string at position p
    # is obtained by taking length 1+max(lcp[p],lcp[p+1]),
    # we want to skip cases where the "uniqueness granting character"
    # is not regular (but a wildcard or separator).
    # Hence the more complex code:
    for (lcpleft,lcpright,pleft,p,pright) in _lcp_pos_pairs(sa):
        if lcpleft < 0 or lcpright < 0: continue
        if pleft < 0 or p < 0 or pright < 0: continue
        if lcpleft > maxvalue or lcpright > maxvalue:
            us[maxvalue+1] += 1
            continue
        if lcpleft > lcpright:
            if special(s[pleft+lcpleft]) or special(s[p+lcpleft]): continue
            us[lcpleft+1] +=1
        elif lcpright > lcpleft:
            if special(s[p+lcpright]) or special(s[pright+lcpright]): continue
            us[lcpright+1] += 1
        else:  # lcpleft == lcpright
            if special(s[pleft+lcpleft]) or special(s[p+lcpright]) or special(s[pright+lcpright]): continue
            us[lcpright+1] += 1
    return us


def stats_lcp(sa, maxvalue=254):
    ls = [0]*(maxvalue+2)  # can index 0 .. maxvalue+1
    for lcpvalue in sa.lcp:
        #ls[min(maxvalue,lcpvalue)+1] += 1
        if lcpvalue > maxvalue:
            ls[maxvalue+1] += 1
        elif lcpvalue >= 0:
            ls[lcpvalue] += 1
    return ls

### end of module
