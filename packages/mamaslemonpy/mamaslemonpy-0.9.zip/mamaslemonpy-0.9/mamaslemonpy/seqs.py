import array
import itertools
from bisect import bisect

from . import names
from . import utils

## Sequence container class
class SequenceContainer():
    """
    a general sequence container that consists of zero or more DNA sequences,
    with a manifest attribute.
    """

    def __init__(self, alphabet):
        """initialize an empty container,
        optionally with an initial sequence 'seq' (string) and 'desc'ription"""
        self.alphabet = alphabet
        self.asize = alphabet.SIZE
        self._buf = array.array("B")
        self.manifest = []
        self.lastssp = []

    def __len__(self):
        return len(self._buf)

    def __str__(self):
        chars = self.alphabet.characters
        return "".join(chars[x] for x in self)

    def _append(self, value):
        """private -- append a value to the end of the current sequence"""
        if value < 0 or value > asize:
            raise ValueError("not an alphabet value")
        self._buf.append(value)

    def __getitem__(self, args):
        return self._buf[args]  # works with int and slice
        

    def append_sequence(self, seq, desc=None, encode=True):
        """append a sequence (string) to the container,
        encoding it in the process"""
        if encode:
            enc = self.alphabet.encoded(seq)
        else:
            enc = seq
        b = self._buf
        start = len(b)
        b.extend(enc)
        lastssp = len(b) - 1
        stop = lastssp 
        if desc is None:
            desc = "unknown DNA [{}:{}]".format(start,stop)
        self.manifest.append((start,stop,lastssp,stop-start,desc))
        self.lastssp.append(lastssp)
        # end/stop refers to position AFTER last sequence character before separator(s);
        # lastssp refers to position OF last separator of sequence
        # end == lastssp iff there is one separator after the sequence
        # len is always difference between end and begin

    def suffixcmp(self, p1,p2, m=0):
        """Let s1/s2 be the suffixes starting at positions p1/p2.
        The function returns (cmp,m), where cmp is:
        0 iff p1==p2,
        -1/+1 if honestly s1<s2 / s1>s2,
        -2/+2 if this result is obtained by position comparison (same special character),
        -3/+3 if this result is obtained from special character comparion;
        and m is the number of honest matches (lcp of p1 and p2).
        If a starting value is given for m, the first m characters are assumed equal.
        """
        isspecial = self.alphabet.isspecial
        while True:
            c1, c2 = self[p1+m], self[p2+m]
            s1 = isspecial(c1)
            if c1==c2:
                if s1: return(-2 if p1<p2 else (0 if p1==p2 else 2), m)
                m += 1;
                continue
            if c1<c2:
                result = -3 if (s1 or isspecial(c2)) else -1
                return(result, m)
            else:
                result = 3 if (s1 or isspecial(c2)) else 1
                return(result, m)

    def lastssp_index(self, position):
        """find largest i such that self.lastssp[i] <= position"""
        return bisect(self.lastssp, position)
        

    def tofile(self, fbuf, fmanifest=None):
        if fmanifest is not None:
            astring = self.alphabet.__name__
            print("# Alphabet: {}".format(astring), file=fmanifest)
            print("# begin end lastssp len description", file=fmanifest)
            for line in self.manifest:
                print(" ".join(str(x) for x in line), file=fmanifest)
        if fbuf is not None:
            self._buf.tofile(fbuf)

    @classmethod
    def fromfile(cls, fbuf, manifest, alphabet):
        s = cls(alphabet)
        nbytes = utils.number_of_items_in_file(fbuf,"B")
        s._buf.fromfile(fbuf,nbytes)
        s.manifest = manifest
        s.lastssp = [entry[2] for entry in manifest]
        return s


class DNAXContainer(SequenceContainer):
    """
    a DNAX container that consists of zero or more DNA sequences,
    encoded as DNAX (2 characters per byte).
    DNAX is an extended 6-letter DNA alphabet with a fixed encoding:
    0=sep  1=A,a  2=C,c  3=G,g  4=T,U,t,u  5=other.
    Each byte holds two characters.
    """
    def __init__(self, alphabet):
        if alphabet != DNAX: raise ValueError("alphabet must be DNAX")
        SequenceContainer.__init__(self, alphabet)
        self._n = 0  # total length of sequences, not the length of _buf

    def __len__(self):
        return self._n
            
    def _append(self, value):
        """private -- append a value to the end of the current sequence"""
        if value < 0 or value > asize:
            raise ValueError("not an alphabet value")
        b = self._buf
        if self._n & 1 == 0:
            b.append(value)
        else:
            v = self._buf[-1]
            b[-1] = 16*value + v
        self._n += 1
        assert (self._n + 1) // 2 == len(self._buf), "buffer length mismatch"

    def __getitem__(self, i):
        if type(i) is int:
            if i < 0: i = self._n + i
            if i >= self._n: raise IndexError()
            w = self._buf[i//2]
            v = w&15 if i&1==0 else w//16
            return v
        if type(i) is not slice: raise TypeError("argument must be int or slice")
        # deal with slice
        r = i.indices(self._n)
        b = self._buf
        getter = lambda j: (b[j//2]//16) if j&1 else (b[j//2] & 15)
        return [getter(j) for j in range(*r)]
        
    def append_sequence(self, seq, desc=None, encode=True):
        if encode:
            even = 1 if len(seq)%2 == 0 else 0
            enc = self.alphabet.encoded(seq)
        else: # do not encode, assume even length, but do not consider it!
            even = 0  # even though even, set it to zero!
            enc = seq
        start = self._n
        self._buf.extend(self.alphabet.paircodes(enc))
        self._n = len(self._buf)*2
        lastssp = self._n - 1
        stop = lastssp - even
        if desc is None:
            desc = "unknown DNA [{}:{}]".format(start,stop)
        self.manifest.append((start,stop,lastssp,stop-start,desc))

    @classmethod
    def fromfile(cls, fbuf, manifest, alphabet):
        s = cls(alphabet)
        nbytes = utils.number_of_items_in_file(fbuf,"B")
        s._buf.fromfile(fbuf,nbytes)
        s.manifest = manifest
        s._n = len(s._buf)*2
        slen = s.manifest[-1][2]+1
        assert slen == s._n
        return s


##########################################################################
## alphabet types

class EmptyAlphabet:
    characters = "$"  # string with characters
    SIZE = len(characters)
    charcodes  = dict()
    containerclass = SequenceContainer
    regulars = 0
    firstregular = None

    @classmethod
    def isspecial(cls, x):
        return True  # all characters are special
    

class DNA:
    characters = "$ACGT."  # string with characters
    SIZE = len(characters)
    charcodes = dict(A=1, C=2, G=3, T=4, U=4, a=1, c=2, g=3, t=4, u=4)
    containerclass = SequenceContainer
    regulars = 4
    firstregular = 1

    @classmethod
    def isspecial(cls, x):
        return x<1 or x>4  # 0 and 5.. are special (non-ACGT)

    _RCTRANS = str.maketrans('ACGTacgt', 'TGCAtgca')
    @classmethod
    def revcomp(cls,dna):
        return dna.translate(DNA._RCTRANS)[::-1]

    @classmethod
    def encoded(cls, dna, terminate=True):
        """return an iterator yielding encoded DNA values according to charcodes"""
        cg = cls.charcodes.get  # get method of the charcodes dict
        if terminate:
            return itertools.chain( (cg(x,5) for x in dna), (0,) )
        return (cg(x,5) for x in dna)


class DNAX(DNA):
    containerclass = DNAXContainer
    
    @classmethod
    def encoded(cls, dna, terminate=True):
        """return an iterator yielding encoded DNA values according to charcodes"""
        cg = cls.charcodes.get  # get method of the charcodes dict
        if terminate:
            rep = 2 if len(dna) % 2 == 0 else 1
            return itertools.chain( (cg(x,5) for x in dna), itertools.repeat(0,rep) )
        return (cg(x,5) for x in dna)
        

    @classmethod
    def paircodes(cls, iterable):
        """convert an even-length sequence of codes with range 0..15
        into a byte sequence, aggregating two codes into a byte.
        Interpretation of the sequence is (lo,hi,lo,hi,...).
        Example: (1,2,3,4) is converted into (33, 67), as 33=1+2*16, 67=3+4*16.
        """
        it = iter(iterable)
        while(it):
            lo = next(it)
            hi = next(it)
            yield lo + 16*hi


#############################################################################

# reading methods
def get_container_from_indexname(iname):
    """return a sequence container with manifest for index 'iname'"""
    with open(names.manifest(iname),"r") as fmanifest:
        manifest, aclass = _manifest_fromfile(fmanifest)
    container = aclass.containerclass
    s = container(aclass)
    s.manifest = manifest
    return s

def _manifest_fromfile(fmanifest):
    manifest = []
    for line in fmanifest:
        if line.startswith("# Alphabet: "):
            (_,aname) = line.split("# Alphabet: ")
            alphabet = eval(aname)
        if line.startswith("#"): continue
        (start,stop,lastssp,length,desc) = line.rstrip().split(None,4)
        start=int(start); stop=int(stop); lastssp=int(lastssp); length=int(length)
        manifest.append((start,stop,lastssp,length,desc))
    return (manifest, alphabet)

def get_alphabet_from_indexname(iname):
    """return the alphabet from the manifest of index 'iname'"""
    alphabet = None
    with open(names.manifest(iname),"r") as fmanifest:
        for line in fmanifest:
            if line.startswith("# Alphabet: "):
                (_,aname) = line.split("# Alphabet: ")
                alphabet = eval(aname)
                break
    return alphabet


###########################################################################

def test():
    dna = "ACGTXXARRTcgQuT"
    s = DNAXSequence(dna)
    print(s._buf, len(s))
    print(s)
    print(s.manifest)
    print(len(s._buf))
    print(len(dna))

if __name__ == "__main__":
    test()
    

