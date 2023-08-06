"""
This module implements a suffix array of a set of strings over an alphabet.
"""

import math
import array
from bisect import bisect, bisect_left

from . import names
from . import seqs
from . import utils

############################################################################        

class SuffixDLL():
    """a suffix array builder that simulates a doubly linked list"""
    
    def __init__(self, s):
        """prepare building a suffix array of sequence 's',
        which must provide an 'alphabet' attribute (its alphabet class).
        The alphabet must provide its SIZE and an isspecial(ch) method.
        To compute the instance, call one of the build_* methods.
        Remember to explicitly allocate memory for the prv and nxt attributes
        by calling self.allocate() first.
        """
        asize = s.alphabet.SIZE  # alphabet knows its size
        self.isspecial = s.alphabet.isspecial
        self.alphabet = s.alphabet
        self.first = [-1]*asize
        self.last  = [-1]*asize
        self.s     = s
        self.prv = None
        self.nxt = None

    def allocate(self):
        """allocate memory for prv and nxt attributes."""
        self.prv = utils.filled_array("l", len(self.s))
        self.nxt = array.array("l", self.prv)


    _REPORTINTERVAL = 1000000;
    _REPORTMOD = _REPORTINTERVAL - 1
    def __report(self, p, steps, anyway=False, interval=_REPORTINTERVAL, mod=_REPORTMOD):
        if anyway or (p % interval == mod):
            print((p+1)/1000000,"Mbp remaining;",steps,"steps so far")
 
    def build_minLR(self):
        """build the suffix array using the minLR method,
        which ist fast, but needs more memory.
        Upon completion, the pos array is represented as self.prv and self.nxt.
        It is obtained by starting at p = self.firtpos()
        and then iterating p = self.nxt[p].
        This method returns the number of steps needed to build the array.
        """
        first = self.first;  last = self.last
        prv = self.prv;  nxt = self.nxt
        asize = self.alphabet.SIZE
        # insert functions that work on first, last, prv, nxt; use asize
        def insertbetween(p1, p2, i):
            """insert i between p1 and p2"""
            prv[i]=p1
            nxt[i]=p2
            if p2 != -1: prv[p2]=i
            if p1 != -1: nxt[p1]=i
        def insertasfirst(i, ch):
            p = first[ch]
            insertbetween(prv[p],p,i)
            first[ch]=i
        def insertaslast(i, ch):
            p = last[ch]
            insertbetween(p, nxt[p], i)
            last[ch]=i
        def insertasnew(i, ch):
            first[ch] = i; last[ch] = i
            # find next smaller existing character
            cp = ch - 1
            while cp >= 0 and last[cp] == -1:  cp -= 1
            ip = last[cp] if cp >= 0 else -1
            # find next bigger existing character
            cs = ch + 1
            while cs < asize and first[cs] == -1:  cs += 1
            js = first[cs] if cs < asize else -1
            insertbetween(ip,js,i)
        # start to build
        s = self.s
        special = self.isspecial  # function to determine which characters are special
        steps = 0
        for (p,ch) in zip(range(len(s)-1, -1, -1), reversed(s)):
            steps += 1
            if first[ch] == -1:  # ch seen for the first time
                insertasnew(p,ch)
                continue
            elif special(ch):    # ch already seen and special
                insertasfirst(p,ch)
                continue
            # ch already seen, and ch is normal character
            pup = pdn = p+1
            while True:
                # look "up"
                steps += 1
                pup = prv[pup]
                if pup == -1:  # end of list: insert as first
                    insertasfirst(p,ch)
                    break  # from while True
                if s[pup-1] == ch:  # found by walking up: insert
                    pup -= 1
                    if last[ch] == pup:
                        insertaslast(p,ch)
                    else:
                        insertbetween(pup, nxt[pup], p)
                    break  # from while True
                # look "down"
                steps += 1
                pdn = nxt[pdn]
                if pdn == -1:  # end of list: insert as last
                    insertaslast(p,ch)
                    break  # from while True
                if s[pdn-1] == ch:  # found by walking down: insert
                    pdn -= 1
                    if first[ch] == pdn:
                        insertasfirst(p,ch)
                    else:
                        insertbetween(prv[pdn], pdn, p)
                    break  # from while True
            steps -= 1
        return steps

    def firstpos(self):
        for p in self.first:
            if p != -1: return p
        return -1


############################################################################        

class OccTable():
    
    def __init__(self, bwt, occrate=128):
        self._occ = None  # array.array("l")
        self._less = None  # normal python list
        self.occrate = occrate      
        self.bwt = bwt
        alphabet = bwt.alphabet
        self.alphabet = alphabet
        self.regulars = alphabet.regulars
        self.firstregular = alphabet.firstregular
        self.isspecial = alphabet.isspecial
        self.at = None    # function at(r,a) computes occ[r,a]
        self.less = None  # function less(a) is number of characters < a

    def set_at_function(self, noslice=False):
        """
        Return the at function;
        at(r,a) is number of a's up to index r in BWT.
        """
        occ = self._occ
        ocr = self.occrate
        bwt = self.bwt
        reg = self.regulars
        fre = self.firstregular
        def _at(r, a):
            if r < 0: return 0
            idx = r // ocr
            x = occ[reg*idx + a - fre]
            x += sum([ b==a for b in bwt[idx*ocr+1 : r+1] ])
            return x
        def _at_noslice(r,a):
            if r < 0: return 0
            idx = r // ocr
            x = occ[reg*idx + a - fre]
            x += sum(bwt[q]==ch for q in range(idx*ocr+1, r+1))
            return x
        def _at1(r, a):
            return occ[reg*r + a - fre] if r >= 0 else 0
        self.at = _at1 if ocr==1 else (_at_noslice if noslice else _at)

    def set_less_function(self, handle_errors=True):
        """
        Return the less function; less(a) is number of characters < a.
        If handle_errors == True, less(a) returns -1 on invalid a
        """
        fre = self.firstregular
        reg = self.regulars
        ls = self._less
        fless_blind = lambda a: ls[a-fre]
        def fless(a):
            i = a - fre
            return ls[i] if i>=0 and i<reg else -1  # -1 indicates error
        self.less = fless if handle_errors else fless_blind

    def compute_from_bwt(self):
        """compute occ and less from bwt by counting characters"""
        occ = array.array("l")
        bwt = self.bwt;  occrate = self.occrate;
        special = self.isspecial;
        regulars = self.regulars;  firstregular = self.firstregular
        occs = [0] * regulars
        nltr = 0  # number of "less than regular" characters
        for (r,b) in enumerate(bwt):
            if not special(b):
                occs[b-firstregular] += 1
            elif b < firstregular:
                nltr += 1
            if r % occrate == 0: occ.extend(occs)
        less = [0] * regulars
        less[0] = nltr
        for c in range(1,regulars):
            less[c] = less[c-1] + occs[c-1]
        self._occ = occ
        self._less = less  # Python list, NOT array.array("l", less) !
        self.set_at_function()
        self.set_less_function()

    def tofile(self, focc):
        """write occ and less to binary file <focc>"""
        self._occ.tofile(focc)
        less = array.array("l", self._less)  # convert to array
        less.tofile(focc)  # and write to disk

    def fromfile(self, focc):
        """read occ and less from binary file <focc>"""
        occ = array.array("l")
        ocr = self.occrate
        items = (ocr - 1 + len(self.bwt)) // ocr
        occ.fromfile(focc, self.regulars * items)
        self._occ = occ
        less = array.array("l")
        less.fromfile(focc, self.regulars)
        self._less = list(less)
        self.set_at_function()
        self.set_less_function()

############################################################################        

class LcpTable():
    def __init__(self):
        self.mode = None
        self._lcp = None
        self._xind = None
        self._xval = None
        self.getter = None
        self.nexceptions = None
        self.at = None  # self.at(r) == lcp[r]
        self.xfind = None  # self.xfind(r) == lcp[r] if r is a large-value-exception
        
    #def __getitem__(self,r):
    #    return self.getter(r)

    def fromfile(self, mode=0, fv=None, fx=None):
        typecode = {0:'l', 1:'B', 2:'H', -1:'B', -2:'H'}
        tc = typecode[mode]
        self._lcp = array.array(tc)
        n = utils.number_of_items_in_file(fv,tc)
        self._lcp.fromfile(fv,n)
        if mode > 0:  # only load lcp exceptions when mode is positive.
            nx = utils.number_of_items_in_file(fx,"l") // 2
            self._xind = array.array("l")
            self._xval = array.array("l")
            self._xind.fromfile(fx,nx)
            self._xval.fromfile(fx,nx)
            self.nexceptions = nx
        self.mode = mode
        self.set_at_function(mode=mode)

    def set_at_function(self, mode=0):
        # define exception finder
        _xind = self._xind
        _xval = self._xval
        def xfind(r):
            """Locate the leftmost index exactly equal to r"""
            i = bisect_left(_xind, r)
            if i != len(_xind) and _xind[i] == r:
                return _xval[i]
            raise ValueError(str(r)+" should be an lcp exception, but was not found")
        self.xfind = xfind
        # define item getters
        lcp = self._lcp
        get0 = lambda r: lcp[r]
        def get1(r):
            lv = lcp[r]
            return lv if lv < 255 else xfind(r)
        def get2(r):
            lv = lcp[r]
            return lv if lv < 65535 else xfind(r)
        # set functions in self
        atfunction = {0:get0, 1:get1, 2:get2, -1:get0, -2:get0}[mode]
        self.at = atfunction
        
############################################################################        

class SuffixArray():
    def __init__(self, s):
        """initialize a new suffix array from a sequence container 's'"""
        self.s = s              # container type from seqs module
        self.alphabet = None    # alphabet type from seqs module
        self.length = None      # int
        self.manifest = None    # list of tuples
        if s is not None:
            self.alphabet = s.alphabet
            self.length = len(s)
            self.manifest = s.manifest
        self.dll = None         # SuffixDLL
        self.firstpos = None    # array("l")
        self.nextpos = None     # array("l")
        self.prevpos = None     # array("l")
        self.buffer = None      # array("l")
        self.pos = None         # array("l")
        self.plcp = None        # array("l")
        self.bwt = None         # container type from seqs module
        self.occ = None         # OccTable
        self.lcp = None         # LcpTable
        self.rindex = None      # array("?"), maps r -> manifest index
        self.lcp_threshold = 0  # interval length below which lcp should be used

    @classmethod
    def from_indexname(cls, iname):
        sa = cls(None)  # obtain an empty shell for suffix array
        s = seqs.get_container_from_indexname(iname)
        sa.s = s
        sa.alphabet = s.alphabet
        sa.manifest = s.manifest
        sa.length = s.manifest[-1][2] + 1
        return sa

    def __len__(self):
        return self.length

    def substring(self, p, q):
        """return the s[p:q] as a human-readable string object,
        where s is the ecoded  sequence in the suffix array"""
        ch = self.alphabet.characters
        s = self.s
        return "".join(ch[s[i]] for i in range(p,q))

    def description_at(self, rank=None, pos=None):
        """return the name/description of the sequence
        at position <pos> or rank <rank> from the manifest.
        Specify either <rank> or <pos>, but not both."""
        if not ((rank is None) ^ (pos is None)):
            raise ValueError("give either pos or rank, but not both")
        desc = self.rindex
        if rank is not None:
            if desc is not None:
                i = desc[rank]
            else:
                pos = self.pos[rank]  # compute via self.pos instead
        if pos is not None:
            # find largest i such that lastssp[i] <= pos
            i = bisect(self.s.lastssp, pos) # see lastssp_index() in seqs
        return self.manifest[i][-1]

    def seq_from_indexname(self, iname):
        """obtain encoded sequence from file"""
        # we assume that s is aleady a container
        # but the sequence buffer is not yet filled.
        manifest = self.manifest; aclass = self.alphabet
        container = aclass.containerclass
        assert container is self.s.__class__
        seqname = names.seq(iname)
        with open(seqname,"rb") as fbuf:
            s = container.fromfile(fbuf, manifest, aclass)
        self.s = s

    def _initialize_nextpos(self):
        dll = SuffixDLL(self.s)
        dll.allocate()
        self.dll = dll

    def nextpos_from_s(self):
        if self.dll is None: self._initialize_nextpos()
        steps = self.dll.build_minLR()
        self.nextpos = self.dll.nxt
        self.prevpos = self.dll.prv
        self.firstpos = self.dll.firstpos()
        self.dll = None
        self.buffer = self.prevpos
        
    def nextpos_from_indexname(self, iname):
        fname = names.nextpos(iname)
        self.nextpos = utils.ensure_array(self.nextpos, fname)
        # firstpos is the only number in {-1,0,1,...,items-1} that is not in nextpos
        sfull = sum(range(-1,len(self.nextpos)))
        s = sum(self.nextpos)
        self.firstpos = sfull - s

    def pos_from_nextpos(self, p=None):
        # re-use buffer (from prevpos), or allocate new array for pos
        self.prevpos = None
        self.pos = self.buffer
        if self.pos is None:
            self.pos = array.array("l",self.nextpos)
        pos, nxt = self.pos, self.nextpos
        # start filling pos from position p (default: firstpos)
        if p is None: p = self.firstpos
        r = 0
        while p != -1:
            pos[r] = p
            r += 1
            p = nxt[p]

    def pos_from_indexname(self, iname):
        self.pos = utils.ensure_array(self.pos, names.pos(iname))

    def rindex_from_pos(self):
        tc = utils.typecode_unsigned(len(self.manifest))
        rindex = array.array(tc)
        pos = self.pos;  lastssp = self.s.lastssp
        for r in range(self.length):
            rindex.append(bisect(lastssp, pos[r]))
        self.rindex = rindex
        
    def rindex_from_indexname(self, iname):
        tc = utils.typecode_unsigned(len(self.manifest))
        self.rindex = utils.ensure_array(self.rindex, names.rindex(iname), typecode=tc)

    def plcp_from_nextpos(self):
        # re-use buffer (from prevpos), or allocate new array for pos
        self.prevpos = None
        self.plcp = self.buffer if self.buffer is not None else array.array("l",self.nextpos) 
        plcp, nxt, s = self.plcp, self.nextpos, self.s
        scmp = s.suffixcmp
        ll = 0
        for (p,pp) in enumerate(nxt):
            # p = 0..n-1 and always pp = nxt[p]
            if ll>0: ll -= 1
            if pp == -1:
                ###assert ll==0
                plcp[self.firstpos] = -1
                continue
            # Compute lcp between suffixes at p and pp, store at pp for now
            # We know the length is at least ll and attempt to compare addl chars.
            (result, ll) = scmp(p,pp,ll)
            ###assert result<0, "lcp({},{})={}, result={}".format(p,pp,ll,result)
            plcp[pp] = ll


    def lcp_from_plcp_generator(self, bufsize=(1<<22)):
        a = array.array("l", [0]*bufsize)
        plcp, nxt = self.plcp, self.nextpos
        remaining = len(nxt)
        p = self.firstpos
        while remaining >= bufsize:
            for r in range(bufsize):
                a[r] = plcp[p]
                p = nxt[p]
            yield a
            remaining -= bufsize
        a = array.array("l", [0]*remaining)
        for r in range(remaining):
            a[r] = plcp[p]
            p = nxt[p]
        yield a

    def lcpn_from_lcp_streaming(self, flcp, flcpn, flcpnx, n=1, bufsize=(1<<20)):
        if n<1 or n>2: raise ValueError("must choose n=1 or n=2")
        data = (None, ("B", 255), ("H", 65535))
        (typecode, maxval) = data[n]
        remaining = len(self.s)
        lcpnxi = array.array("l")
        lcpnxv = array.array("l")
        lcpn = array.array(typecode, [0]*bufsize)
        r = 0
        while True:
            while remaining >= bufsize:
                lcp = array.array("l")
                lcp.fromfile(flcp,bufsize)
                for (rr,lv) in enumerate(lcp):
                    if lv<0 or lv>=maxval:
                        lcpn[rr]=maxval
                        lcpnxi.append(r)
                        lcpnxv.append(lv)
                    else:
                        lcpn[rr]=lv
                    r += 1
                lcpn.tofile(flcpn)
                remaining -= bufsize
            if remaining == 0: break
            bufsize = remaining
            lcpn = array.array(typecode, [0]*bufsize)
        assert len(lcpnxi) == len(lcpnxv), "lcpn length mismatch"
        lcpnxi.tofile(flcpnx)
        lcpnxv.tofile(flcpnx)
        del lcpnxi, lcpnxv, lcp, lcpn

    def lcp_from_indexname(self, iname, mode=1):
        """set self.lcp to the appropriate LcpTable object,
        read from the given index 'iname'"""
        lname = names.lcp_names[mode](iname)
        lcp = LcpTable()
        if mode !=0 :
            xname = names.lcp_xnames[mode](iname)
            with open(lname,"rb") as flcp, open(xname,"rb") as fx:
                lcp.fromfile(mode, flcp, fx)
        else:
            with open(lname,"rb") as flcp:
                lcp.fromfile(mode, flcp, None)
        self.lcp = lcp
    
    def bwt_from_pos(self):
        s, pos = self.s, self.pos
        containerclass = s.__class__
        bwt = containerclass(self.alphabet)
        bwt.append_sequence((s[p-1] for p in pos), "__BWT__", encode=False)
        self.bwt = bwt

    def bwt_from_indexname(self, iname, reload=False):
        if self.bwt is not None and not reload: return
        s = self.s
        containerclass = s.__class__
        bwtclass = containerclass(self.alphabet)
        bname = names.bwt(iname)
        with open(bname,"rb") as fbwt:
            b = bwtclass.fromfile(fbwt, s.manifest, self.alphabet)
        self.bwt = b

    def occ_from_bwt(self, occrate):
        occ = OccTable(self.bwt, occrate)
        occ.compute_from_bwt()
        self.occ = occ
        self.set_lcp_threshold()

    def occ_from_indexname(self, iname, occrate=0):
        """read occ table from file <iname>.<occrate>.occ.
        If occrate is not given (or <= 0), use the file with the smallest occrate.
        """
        if occrate <= 0:
            occrate, occfile = names.occtables(iname)[0]
        else:
            occfile = names.occ(iname, occrate)
        occ = OccTable(self.bwt, occrate)
        with open(occfile, "rb") as focc:
            occ.fromfile(focc)
        self.occ = occ
        self.set_lcp_threshold()

    # TODO: optimize factor, offset
    def set_lcp_threshold(self, factor=2, offset=1):
        # let k be the current interval length, n the text length
        # After cutting of the last one, it will grow to an expected asize*k,
        # needing (asize-1)*k lcp hops (good for small k)
        # For interval length k, the expected match length is
        # m = log(n/k)/log(asize), since k = n / asize**m.
        # The alternative is to do m-1 (or say, m) backward search steps,
        # which requires an expected (m-1)*occrate/2 lookups.
        # Now find the largest k such that
        # (asize-1)*k  <=  occrate/2 * log(n/k) / log(asize)
        # That k is the lcp_threshold.
        # For shorter intervals (long matches), we should go by lcp.
        # For longer intervals (short matches), we should bo by BWS.
        n = self.length
        log = math.log
        asize = self.alphabet.SIZE;  a1 = asize-1;  loga = log(asize)
        C = factor * self.occ.occrate / (2*loga)
        lcptime = lambda k: a1*k
        bwstime = lambda k: C * log(n/k)
        k = 1
        while lcptime(k) <= bwstime(k): k += 1
        # for this k, lcptime(k) > bwstime(k), so subtract 1; then add offset
        t = int(k - 1 + offset)
        self.lcp_threshold = t
        return t

    # search methods  ###################################################
    
    def backward_search(self, pat, minlen=0, errors=0):
        mspos = len(pat) - 1
        bms = self.backward_matching_statistics(pat, begin=mspos, end=mspos, errors=errors)
        for (i, left, ms, L, R) in bms:
            if ms < minlen: continue
            yield (left, i, ms, L, R)

    def prefix_search(self, pat, minlen=0, errors=0):
        bms = self.backward_matching_statistics(pat, errors=errors)
        for (i, left, ms, L, R) in bms:
            if left == 0 and ms >= minlen:
                yield (left, i, ms, L, R)
                break
        
    def mms(self, pat, opt=None, minlen=0, errors=0,
            begin=None, end=None, unique=False):
        """for all maximal [unique] matches (M[U]Ms) of the pattern 'pat'
        in this suffix array, yield (i, ms, L, R), resp. (i, ms, L),
        where i is the starting position in the pattern,
        ms is the length of the match, and
        L..R are the suffix array ranks of the match positions.
        The actual positions must be obtained by self.pos[L:R+1].
        """
        if opt is None:
            bms = self.backward_matching_statistics(
                pat, begin=begin, end=end, errors=errors)
        else:
            if errors != 0: raise NotImplementedError("errors not supported with optional characters")
            bms = self.backward_matching_statistics_with_optional_characters(
                pat, opt, begin=begin, end=end)
        oldleft = len(pat)
        for (i, left, ms, L, R) in bms:
            if left < oldleft and ms > 0:  # jump in matching statistics
                if ms >= minlen:  # minimum length requirement ok
                    if not unique or (R == L):  # unique necessitates singleton interval
                        yield (left, i, ms, L, R)
            oldleft = left
                    
    def backward_matching_statistics(self, pat,
                begin=None, end=None, errors=0, lcp_threshold=None):
        """yield backward matching statistics, i.e., tuples (i, len, L, R),
        where i is the starting position of the match in <pat>,
        len is the maximal match length backward from that position,
        and [L, R] is the suffix array interval of such matches.
        Requires bwt and occ of the suffix array, but *not* pos or the sequence.
        """
        if errors != 0:
            raise NotImplementedError("error-tolerant matching statistics not yet supported")
        n = self.length;  m = len(pat)
        if (begin is None) or (begin > m - 1): begin = m - 1
        if (end is None) or (end < 0): end = 0
        if end > begin: end = begin
        occ = self.occ;  o = occ.at;  less = occ.less;
        lcp = self.lcp
        if lcp is not None:  lcp = lcp.at
        if lcp_threshold is None: lcp_threshold = self.lcp_threshold
        j = begin
        for i in range(begin, end-1, -1):
            # start matching backward at position i of the pattern
            # assume that j is set to next position to examine
            if j >= i:  j = i;  (L, R) = (0, n-1)  # reset
            while j >= 0:
                # cannot use "for j in range(i,-1,-1)" because of break/termination
                # update L,R by prepending letter <a>
                a = pat[j]
                ls = less(a)  # returns a negative value for illegal character
                if ls < 0: break  # failure, keep old interval
                Lnew = ls + o(L-1, a)
                Rnew = ls + o(R, a) - 1
                if Lnew > Rnew: break  # failure, keep old interval
                L, R = Lnew, Rnew
                j -= 1
            # successful backward match found at i, of length i - j
            ms = i - j
            yield (i, j+1, ms, L, R)
            # prepare j for the next i (which is i-1)
            if (lcp is None) or (R-L > lcp_threshold):
                # long interval: recompute next ms from scratch
                if ms <= 0:
                    assert j == i  and L == 0 and R == n-1  # nothing was matched
                j = i
                continue
            # long match, so widen (L,R) using lcp array
            ms -= 1
            ###assert lcp(L) <= ms and (R == n - 1 or lcp(R+1) <= ms)
            while lcp(L) >= ms: L -= 1
            while True:
                if R == n-1 or lcp(R+1) < ms: break
                R += 1


    def backward_matching_statistics_with_optional_characters0(
        self, pat, opt=None, begin=None, end=None, lcp_threshold=None):
        """yield backward matching statistics of pattern <pat>
        with some characters marked as optional via a boolean list <opt>
        Matching statistics are yielded as tuples (i, len, L, R),
        where i is the starting position of the match in <pat>,
        len is the maximal match length backward from that position,
        and [L, R] is the suffix array interval of such matches.
        Requires bwt and occ of the suffix array, but *not* pos or the sequence.
        """
        # internal representation of suffix array intervals:
        # (ms, i, j, L, R, skipped), where
        #  ms      = #matched characters (w/o skipped)
        #  i       = rightmost position of match in pattern
        #  j       = leftmost position of match in pattern
        #  L,R     = suffix array interval
        #  skipped = tuple of skipped pattern positions 
        n = self.length;  m = len(pat)
        if (begin is None) or (begin > m - 1): begin = m - 1
        if (end is None) or (end < 0): end = 0
        if end > begin: end = begin
        if opt is None: opt = (False,) * m
        if lcp_threshold is None: lcp_threshold = self.lcp_threshold
        cutlast = self._cut_last;  extend = self._extend
        emptyset = frozenset();  emptytuple = tuple()
        intervals = emptyset  # set of intervals

        for i in range(begin, end-1, -1):
            # cut off last character for each interval for current i            
            intervals = frozenset(cutlast(intervals, pat, lcp_threshold, n))
            if len(intervals) == 0:
                intervals = frozenset( [(0, i, i+1, 0, n-1, emptytuple)] )
            # extend each interval 
            intervals = frozenset( extend(intervals, pat, opt) )
            ###assert len(intervals) >= 1
            # report longest interval
            ###for iv in intervals: print("       ", iv)
            (ms, i, j, L, R, skipped) = max(intervals)
            yield (i, j, ms, L, R)
                
    def _cut_last0(self, intervals, pat, lcpt, n):
        lcp = self.lcp
        if lcp is not None: lcp = lcp.at
        for (ms, i, j, L, R, skipped) in intervals:  # skipped is a tuple
            # update i -> i - 1,  so remove i from skipped if present
            assert len(skipped)==0 or skipped[0] <= i
            if skipped[0] == i:
                skipped = skipped[1:]
            else:
                ms -= 1
                if ms < 0: continue
            ###assert all(skip < i for skip in skipped), str((ms,i,j,L,R,skipped))
            # update L, R
            if (lcp is None) or (R-L > lcpt):
                # for a wide interval (short match), re-compute from scratch
                matched = [pat[k] for k in range(j,i) if k not in skipped]
                iv = list(self.backward_search(matched))
                assert len(iv) == 1,  "{} / {}".format(iv, matched)
                (_, _, _, L, R) = iv[0]
            else: 
                # for a narrow interval (long match), cut by lcp
                ###assert lcp(L) <= ms and (R == n - 1 or lcp(R+1) <= ms)
                while lcp(L) >= ms: L -= 1
                while True:
                    if R == n-1 or lcp(R+1) < ms: break
                    R += 1
            yield (ms, i-1, j, L, R, skipped)

    def _extend0(self, intervals, pat, opt):
        o = self.occ.at;  less = self.occ.less
        for (ms, i, j, L, R, skipped) in intervals:
            # j is the last position that was successfully matched
            while j > 0:
                jnew = j - 1  # attempt the next j
                if opt[jnew] and jnew < i:  # branch by skipping this jnew
                    subintervals = frozenset((ms, i, jnew, L, R, skipped+(jnew,)),)
                    for iv in self._extend(subintervals, pat, opt):
                        yield iv
                # attempt to update [L,R]
                a = pat[jnew]
                ls = less(a)  # returns a negative value for illegal character
                if ls < 0: break  # failure, keep old interval
                Lnew = ls + o(L-1, a)
                Rnew = ls + o(R, a) - 1
                if Lnew > Rnew: break  # failure, keep old interval
                L, R, j = Lnew, Rnew, jnew
                ms += 1
            yield (ms, i, j, L, R, skipped)
        

    ### closure-based implementation with skip-tuples instead of sets
    def backward_matching_statistics_with_optional_characters(
        self, pat, opt=None, begin=None, end=None, lcp_threshold=None):
        """yield backward matching statistics of pattern <pat>
        with some characters marked as optional via a boolean list <opt>
        Matching statistics are yielded as tuples (i, len, L, R),
        where i is the starting position of the match in <pat>,
        len is the maximal match length backward from that position,
        and [L, R] is the suffix array interval of such matches.
        Requires bwt and occ of the suffix array, but *not* pos or the sequence.
        """
        # internal representation of suffix array intervals:
        # (ms, i, j, L, R, skipped), where
        #  ms      = #matched characters (w/o skipped)
        #  i       = rightmost position of match in pattern
        #  j       = leftmost position of match in pattern
        #  L, R    = suffix array interval
        #  skipped = tuple of skipped pattern positions 
        n = self.length;  m = len(pat)
        if (begin is None) or (begin > m - 1): begin = m - 1
        if (end is None) or (end < 0): end = 0
        if end > begin: end = begin
        if opt is None: opt = (False,) * m
        if lcp_threshold is None: lcp_threshold = self.lcp_threshold
        o = self.occ.at;  less = self.occ.less
        lcp = self.lcp
        if lcp is not None: lcp = lcp.at

        def extend(intervals):
            for (ms, i, j, L, R, skipped) in intervals:
                # j is the last position that was successfully matched
                while j > 0:
                    jnew = j - 1  # attempt the next j
                    if opt[jnew] and jnew < i:
                        # branch by skipping this jnew
                        skipintervals = [ (ms, i, jnew, L, R, skipped+(jnew,)) ]
                        for iv in extend(skipintervals): yield iv
                    # attempt to update [L,R]
                    a = pat[jnew]
                    ls = less(a)  # returns a negative value for illegal character
                    if ls < 0: break  # failure, keep old interval
                    Lnew = ls + o(L-1, a)
                    Rnew = ls + o(R, a) - 1
                    if Lnew > Rnew: break  # failure, keep old interval
                    L, R, j = Lnew, Rnew, jnew
                    ms += 1
                yield (ms, i, j, L, R, skipped)

        def cutlast(intervals):
            for (ms, i, j, L, R, skipped) in intervals:  # skipped is a tuple
                # update i -> i - 1,  so remove i from skipped if present
                assert len(skipped)==0 or skipped[0] <= i
                if len(skipped) > 0 and skipped[0] == i:
                    skipped = skipped[1:]
                else:
                    ms -= 1
                    if ms < 0: continue
                ###assert all(skip < i for skip in skipped), str((ms,i,j,L,R,skipped))
                # update L, R
                if (lcp is None) or (R-L > lcp_threshold):
                    # for a wide interval (short match), re-compute from scratch
                    matched = [pat[k] for k in range(j,i) if k not in skipped]
                    iv = list(self.backward_search(matched))
                    assert len(iv) == 1,  "{} / {}".format(iv, matched)
                    (_, _, _, L, R) = iv[0]
                else: 
                    # for a narrow interval (long match), cut by lcp
                    ###assert lcp(L) <= ms and (R == n - 1 or lcp(R+1) <= ms)
                    while lcp(L) >= ms: L -= 1
                    while True:
                        if R == n-1 or lcp(R+1) < ms: break
                        R += 1
                yield (ms, i-1, j, L, R, skipped)
                
        # body of backward_matching_statistics_with_optional characters
        nothing_skipped = tuple()  # empty tuple
        intervals = []  # intervals from last iteration        
        for i in range(begin, end-1, -1):
            # cut off last character for each interval for current i            
            intervals = frozenset(cutlast(intervals))
            if len(intervals) == 0:
                intervals = [(0, i, i+1, 0, n-1, nothing_skipped)]
            # extend each interval 
            intervals = list(extend(intervals))
            assert len(intervals) >= 1
            # report longest interval
            (ms, i, j, L, R, skipped) = max(intervals)
            yield (i, j, ms, L, R)
                

    
############################################################################        
