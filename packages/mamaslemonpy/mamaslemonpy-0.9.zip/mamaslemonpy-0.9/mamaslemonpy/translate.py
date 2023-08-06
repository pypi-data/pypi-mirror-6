"""
module implementing the translate subcommand
"""

import os
import io

from . import names
from . import utils
from . import seqs

def buildparser(p):
    p.add_argument("files", metavar="FASTAFILE", nargs="*",
                   help="DNA .fasta file for translation")
    p.add_argument("-i", "--indexname",
                   help="name of index to generate",
                   required=True)
    p.add_argument("-r", "--rc", "--reverse-complement",
                   default=False, action="store_true",
                   help="add reverse complements to index (only for DNA type sequences)")
    p.add_argument("-f", "--filefile", nargs="+",
                   help="obtain names of .fasta files from file(s), processed after given files",
                   default=[])
    p.add_argument("-p", "--path", default="",
                   help="path for input files, prepended to all files in files")
    p.add_argument("-a", "--alphabet", choices=("dna", "dnax"), default="dnax",
                   help="alphabet/encoding of sequences [dnax]")


def getallfiles(args):
    allfiles = args.files[:]
    for fname in args.filefile:
        with open(fname, "r") as f:
            L = f.readlines()
        p = args.path
        allfiles.extend([os.path.join(p,x.rstrip()) for x in L])
    return allfiles
    
def main(args):
    alph = args.alphabet
    if alph in {"dna", "dnax"}:
        translateDNA(args)
    else:
        raise NotImplementedError("translation for given alphabet not implemented")
    
def translateDNA(args):
    _print = print if not args.quiet else utils.dontprint
    aclass = dict(dna=seqs.DNA, dnax=seqs.DNAX)[args.alphabet]
    s = aclass.containerclass(aclass)
    allfiles = getallfiles(args)
    clock = utils.TicToc()
    for fname in allfiles:
        if len(fname)==0: continue
        _print(clock.toc(),"translating {}...".format(fname))
        gzipped = fname.endswith((".gz",".gzip",".gzipped"))
        myopen = open if not gzipped else gzip.open
        with myopen(fname) as f:
            myf = f if not gzipped else io.TextIOWrapper(f,encoding='ascii')
            for (header,seq) in utils.readfasta(myf):
                _print("    ",header)
                s.append_sequence(seq,header)
                if args.rc:
                    rcheader = "rc-"+header
                    _print("    ",rcheader)
                    rcseq = "".join(aclass.revcomp(seq))
                    s.append_sequence(rcseq, rcheader)
            if gzipped: myf.close()
    iname = args.indexname
    seqname, manifestname = names.seq(iname), names.manifest(iname)
    _print(clock.toc(),"writing {}, {}...".format(seqname,manifestname))
    with open(seqname,"wb") as fbuf, open(manifestname,"wt") as fmanifest:
        s.tofile(fbuf, fmanifest)
    _print(clock.toc(),"done")
