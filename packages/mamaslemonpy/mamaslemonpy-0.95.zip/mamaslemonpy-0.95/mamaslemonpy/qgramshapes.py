from collections import Counter
from itertools import combinations, count
import random

SWITCH_MINSIZE = 500
SWITCH_NEVER = 999999999

def binom(n, k):
    """Return the binomial coefficient (n choose k) for integers n>=0, k>=0."""
    if k == 1:  return n
    if k == 2:  return (n*(n-1))//2
    # the following algorithm never produces floats and is accurate.
    b = 1
    for i in range(k):  b = (b*(n-i))//(i+1)
    return b

def number_deficient_ktuples(m, k, covcounter, mincov=1):
    N = binom(m,k)
    d = N - len(covcounter)
    assert d >= 0
    if mincov > 1:
        d += sum(val < mincov for val in covcounter.values())
    return d, N

def numsamples(q, d, samples=None, maxsamples=10):
    """Compute the number of random samples for given q, d."""
    #return 1  # constant number
    if samples is None:
        samples = binom(q,d)//100  # at most 1% of all shapes
        if samples >= maxsamples:  samples = maxsamples  # at most maxsamples
        if samples <= 1:  samples = 1  # at least 1 sample
    return samples

def shapestr(q, dontcares):
    """string that represents a q-gram with dontcares"""
    L = ["#"] * q
    for i in dontcares:  L[i] = "_"
    return "".join(L)

def shapevalues(string):
    """Return (q, dontcares) such that shapestr(q,dontcares) == string"""
    q = len(string)
    dontcares = tuple(i for i, c in enumerate(string) if c == "_")
    return q, dontcares

def shapes(q, d):
    """
    Yield each q-shape with d dontcares in randomized positional order.
    At each border, there is a care character.
    The number of shapes yielded is ((q-2) choose d).
    """
    assert 0 <= d <= q-2
    # generate a random permutation of positions {1, 2, ..., q-2}.
    perm = tuple(random.sample(range(1,q-1), q-2))
    return combinations(perm, d)

#######################################################################

def min_matching_positions(q, dontcares, occmax):  # (mmax, k)
    """
    Let a shape be given by (q, dontcares).
    Return a list "results", such that results[r], r = 0, 1, ..., occmax,
    is the minimum number of matching positions when
    the shape matches r times in a window of length up to mmax with k errors,
    """
    cares = [i for i in range(q) if i not in dontcares]
    bestresults = [r*len(cares) for r in range(occmax+1)]
    if occmax == 0:  return bestresults
    # evaluate up to occmax overlapping shifts recursively
    def _enumerate_matchpos(matches, occs, lastshift):
        result = len(matches)    # number of matches
        if result < bestresults[occs]:
            bestresults[occs] = result
        if occs >= occmax: return
        if result >= bestresults[occs+1]:  return
        for shift in range(lastshift+1, lastshift+q):
            newmatches = sorted(set(matches + [(c + shift) for c in cares]))
            _enumerate_matchpos(newmatches, occs+1, shift)
    # call the defined recursive function to update bestresults          
    _enumerate_matchpos(cares, 1, 0)
    return bestresults


#######################################################################

def _append_new_position(counters, m, q):
    """helper function to update counters from length m-1 to m"""
    maxk = len(counters) - 1  # determine maxk
    valm = m - q  # position m-1 so far covered by (m-1)-q+1 = m-q shifts
    # update each counter
    for k in range(maxk, 2, -1):  # k = maxk..3 (downwards)
        csk = counters[k]
        for k1tup, value in counters[k-1].items():
            if value > valm:  value = valm
            csk[k1tup + (m-1,)] = value
    # special case k=2
    if maxk >= 2:
        csk = counters[2]
        for i, value in counters[1].items():
            if value > valm:  value = valm
            csk[(i,m-1)] = value
    # special case k=1: compute number of shifts (for length m-1)
    if maxk >= 1 and valm > 0:
        counters[1][m-1] = valm

def _append_new_defi_position(counters, m, q, mincov):
    """helper function to update deficiency counters from length m-1 to m"""
    maxk = len(counters) - 1  # determine maxk
    defim = mincov - (m - q)  # position m-1 so far covered by m-q shifts
    if defim < 0: defim = 0   # deficiency cannot be negative
    # update each counter
    for k in range(maxk, 2, -1):  # k = maxk..3 (downwards)
        csk = counters[k]
        for k1tup, value in counters[k-1].items():
            if defim > value:  value = defim
            csk[k1tup + (m-1,)] = value
    # special case k=2
    if maxk >= 2:
        csk = counters[2]
        for i, value in counters[1].items():
            if defim > value:  value = defim
            csk[(i,m-1)] = value
    # special case k=1
    if maxk >= 1 and defim > 0:
        counters[1][m-1] = defim

def _switch_counters_to_defi(counters, m, mincov):
    mode_defi = counters[0]
    assert not mode_defi
    # switch the counter for each k
    for k in range(1, len(counters)):
        ck = counters[k]
        c = Counter()
        ktuples = combinations(range(m), k) if k > 1  else range(m)
        for ktup in ktuples:
            defi = mincov - ck[ktup]
            if defi > 0:  c[ktup] = defi
        counters[k] = c
    # set flag to indicate deficiency counters
    counters[0] = True


def mincoverages_upto_maxk(m, q, dontcares, maxk, counters, mincov):
    """
    Compute a list counters[0:makk+1] of Counters such that
    counters[k][position_ktuple], k=1..maxk, i,
    is the number of times that each position_ktuple of m positions
    is covered by all dontcares for the shape given by (q,dontcares),
    where q is the length of the shape,
    and dontcares is a tuple with the indices of the dontcare positions.

    Additionally, compute a list mincoverages[0:maxk+1] such that
    mincoverages[k], k=1..maxk, is the minimum counters[k] values.

    Return the pair (mincoverages, counters).

    For efficiency, if counters are to be computed for an incremented value
    of m in comparison to the previous call, the previous counters (for m-1)
    should be passed as optional argument counters_for_previous_m,
    so they need not be recomputed.
    """
    if counters[0] is True:
        # mode: deficiency counters
        return mincoverages_upto_maxk__defi(m, q, dontcares, maxk, counters, mincov)
    return mincoverages_upto_maxk__covg(m, q, dontcares, maxk, counters)


def mincoverages_upto_maxk__covg(m, q, dontcares, maxk, counters, mincov):
    # standard: count how many shifts cover each k-tuple, k=1..maxk
    endk = maxk + 1
    minc = [0] * endk
    _append_new_position(counters, m, q)
    shift = m - q  # put the q-gram into the window at the rightmost shift
    sdc = list(range(shift)) + [d+shift for d in dontcares]
    counters[1].update(sdc)
    for k in range(2, endk):
        counters[k].update(combinations(sdc, k))
    # compute minimum coverage for each k = 1..maxk
    for k in range(1, endk):
        if len(counters[k]) >= binom(m, k):
            minc[k] = min(counters[k].values())  # else zero, see init.
    return minc, counters

def mincoverages_upto_maxk__defi(m, q, dontcares, maxk, counters, mincov):
    # In deficiency counter mode we act on all deficient ktuples
    # and reduce their deficiency, if appropriate.
    endk = maxk + 1
    minc = [0] * endk    
    _append_new_defi_position(counters, m, q, mincov)
    shift = m - q  # put the q-gram into the window at the rightmost shift
    sdc = list(range(shift)) + [d+shift for d in dontcares]
    sdcset = frozenset(sdc)
    D = len(sdc)
    for k in range(1, endk):
        # iterate over deficient tuples or over k-tuples with all dontcares?
        ck = counters[k]
        if k*len(ck) <= binom(D, k):
            # iterate over keys
            if k == 1:
                to_reduce = [i for i in ck if i in sdcset]
            else:
                to_reduce = [dt for dt in ck if frozenset(dt) <= sdcset]
        else:
            # iterate over k-tuples from sdc
            combos = combinations(sdc, k) if k > 1 else sdc
            to_reduce = [dt for dt in combos if dt in ck]
        # decrement all items of counters[k] in to_reduce
        for key in to_reduce:
            if ck[key] > 1:
                ck[key] -= 1
            else:
                del ck[key]      
        # compute minimum coverage for each k = 1..maxk
        minc[k] = mincov - (max(ck.values()) if len(ck) > 0 else 0)
    return minc, counters

#####################################################################

class ShapeResult:
    """
    class that represents properties of a shape
    and allows comparison of two such sets of properties
    """
    def __init__(self, mstars, critical_tuples=None, switched_at=0):
        self.mstar = mstars[-1]
        self.mstars = mstars
        self.critical_tuples = critical_tuples
        self.switched_at = switched_at
        self._cmp = mstars[-1:0:-1]
    __eq__ = lambda self, other: self._cmp == other._cmp
    __lt__ = lambda self, other: self._cmp < other._cmp
    __le__ = lambda self, other: self._cmp <= other._cmp


def evaluate_one_shape(q, dontcares, maxk, mincov, lastm=None,
                       report_critical=False, switch_at=SWITCH_MINSIZE):
    """
    Evaluate the shape given by (q, dontcares), where
    - q is the length of the shape,
    - dontcares is a tuple with the indices of the dontcare positions,
    according to different criteria, which are stored in a ShapeResult object.
    - attribute "mstars":
      Compute the smallest window sizes mstars[k] such that
      any combination of k <= maxk errors is covered by k dontcares
      in >= mincov shifts.
      (The search is stopped at lastm and the resulting value is None
      if not successful. If lastm is None, then the procedure is guaranteed
      to find the true values of mstars and never results in None.
      This can take a very long time, depending on the parameters.)
    - attribute "mstar" is short for mstars[maxk].
    - attribute "critical_tuples":
      a tuple of kmax-tuples that just reach coverage mincov and not more.
      This is only computed if report_critical=True; otherwise it is None.

    Return the pair (result, lastm), where
    - the components of result have been explained above,
    - lastm is the smaller of the given lastm and the found m*.
    """
    endk = maxk+1
    mstars = [None] * endk
    allow_defi = not report_critical
    mode_defi = False;  switched = 0
    mincov_fun = mincoverages_upto_maxk__covg
    counters = [mode_defi] + [Counter() for i in range(1, endk)]

    # search for each mstars[k] by increasing m step by step, up to lastm, or forever.
    for m in count(q):
        #minc, counters = mincoverages_upto_maxk_old(m, q, dontcares, maxk, counters)
        minc, counters = mincov_fun(m, q, dontcares, maxk, counters, mincov)
        # are the coverages sufficient?
        for k in range(1, endk):
            if mstars[k] is None and minc[k] >= mincov:  mstars[k] = m
        if mstars[-1] == m:
            if (lastm is None) or (m < lastm):  lastm = m    
            break
        if (lastm is not None) and (m >= lastm):
            break
        # can and should we switch the counters to deficiency type?
        if mode_defi or not allow_defi:  continue
        covered = len(counters[maxk])
        if covered < switch_at:  continue
        if covered <= binom(m, maxk)//2:  continue
        defi, _ = number_deficient_ktuples(m, maxk, counters[maxk], mincov)
        if defi <= covered:
            #print("! switching at m={}, {} < {}".format(m, defi, covered))
            _switch_counters_to_defi(counters, m, mincov)
            mode_defi = True
            mincov_fun = mincoverages_upto_maxk__defi
            switched = covered

    # Build and return the appropriate result object and lastm.
    if mstars[-1] is None:  # no m* found due to lastm:
        return (None, lastm)  # no ShapeResult object is returned.
    if report_critical:
        mode_defi = counters[0]
        assert not mode_defi
        critical = tuple(ktuple for ktuple, c in counters[maxk].items() if c == mincov)
        result = ShapeResult(mstars, critical, switched)            
    else:
        result = ShapeResult(mstars, None, switched)
    return (result, lastm)


def evaluate_shapes_of_type(w, q, maxk=1, mincov=1, samples=None, switch_at=SWITCH_MINSIZE):
    """
    Evaluate all shapes with w cares and d=q-w dontcares.
    Consider up to maxk errors, such that each maxk-tuple
    of erroneous positions is covered >= mincov times by all dontcares.

    Before starting the systematic search over all shapes of type w/q,
    evaluate a few random samples (given by the optional samples parameter,
    samples=None picks an appropriate number) to get a ballpark estimate.

    Return a pair (bestresult, bestshapes) consisting of
    - a result property tuple indicating optimal properties for shape type w/q,
      The properties are described in the docstring of 'evaluate_one_shape'.
    - the set of shapes that achieve these optimal properties.
    """
    d = q - w
    assert d >= 0 and d < q
    bestresult = None;  bestshapes = []
    lastm = None
    switches = 0;  finished = 0

    # do a quick random search to lower lastm to a small value.
    #print("Random search {}/{}, maxk={}, mincov={}".format(w, q, maxk, mincov))
    samples = numsamples(q, d, samples)
    for i in range(samples):
        dontcares = sorted(random.sample(range(1,q-1), d))  # a random sample of d dontcares
        result, lastm = evaluate_one_shape(q, dontcares, maxk, mincov, lastm, switch_at=switch_at)
        bestresult = result if result is not None else bestresult
        #print("{}/{}, maxk={}, mincov={}: {} {}".format(w, q, maxk, mincov, shapestr(q, dontcares), bestresult))

    #print("Systematic search {}/{}, maxk={}, mincov={}: lastm={}".format(w, q, maxk, mincov, lastm))
    for dontcares in shapes(q,d):
        dontcares = sorted(dontcares)
        #test_shape_defi(q,dontcares,maxk,mincov)  # DEBUG
        result, lastm = evaluate_one_shape(
            q, dontcares, maxk, mincov, lastm, switch_at=switch_at)
        if result is None: continue
        finished += 1
        if result.switched_at != 0:  switches +=1
        if result <= bestresult:
            if result < bestresult:            
                bestresult = result
                bestshapes = [dontcares]
            else:
                bestshapes.append(dontcares)
            #print("{}/{}, maxk={}, mincov={}: {} {}. sw/fi={}/{}.".format(
            #    w, q, maxk, mincov, shapestr(q, dontcares), bestresult.mstars[-1:0:-1], switches, finished))
    return bestresult, frozenset(tuple(dontcares) for dontcares in bestshapes)


############################################################################


def test():
    shape = "##_#__###_#__###_#"  # type w/q = 11/18
    maxk, mincov = 6, 1
    # optimal m for maxk, mincov = (2,1) is mstar = 24.
    # There are no better or equivalent shapes (only the symmetric one) with 11/18.
    # There is a better one of type 11/17.

    # run the test proper
    q, dontcares = shapevalues(shape)
    test_shape_defi(q, dontcares, maxk, mincov)
    # show mimimum number of matchin positions
    q, dontcares = shapevalues(shape)
    mmps = min_matching_positions(q, dontcares, mincov)
    print("Minimum number of matching positions for i shape matches:")
    for i, mmp in enumerate(mmps):
        print(i, mmp)
    # DONE.


def test_shape_defi(q, dontcares, maxk, mincov):
    d = len(dontcares);  w = q - d
    print("Testing shape {} of type {}/{} with {} dontcares, using maxk={}, mincov={}.".format(shapestr(q,dontcares),w,q,d,maxk,mincov))
    counters = None
    counters2 = [False] + [Counter() for i in range(1,maxk+1)]
    for m in count(q):
        print("m =", m)
        # variant "standard"
        minc, counters = mincoverages_upto_maxk(m, q, dontcares, maxk, counters)
        # variant "defi"
        minc2, counters2 = mincoverages_upto_maxk(m, q, dontcares, maxk, counters2, mincov)
        # switch counters for variant "defi" from standard to defi?        
        if  counters2[0] is False:
            defi, _ = number_deficient_ktuples(m, maxk, counters[maxk], mincov)
            if defi <= len(counters[maxk]):
                print("!!!! SWITCHING TO DEFICIENCY COUNTERS after m={}:  {} -> {}".format(m,len(counters[maxk]),defi))
                _switch_counters_to_defi(counters2, m, mincov)
                assert counters2[0] is True

        # check for equal results
        mode_defi = counters2[0]
        if mode_defi:
            cc = [len(counters[k]) for k in range(1,maxk+1)]
            dc = [len(counters2[k]) for k in range(1,maxk+1)]
            print("    {} / {}".format(dc,cc))
            print("    savings: {} / {} = {:.1%}".format(sum(dc), sum(cc), sum(dc)/sum(cc)))
        for k in range(1,maxk+1):
            if mode_defi:
                # mode is defi, check for consistency with other mode.
                defi_is = len(counters2[k])
                defi_be, _ = number_deficient_ktuples(m, k, counters[k], mincov)
                assert minc[k] == minc2[k] or (minc[k] > minc2[k] and minc2[k] == mincov), "k={}, minc[k]={}, minc2[k]={}".format(k,minc[k],minc2[k])
                assert defi_is == defi_be, "k={}: deficient tuples observed / expected: {} / {}: {}".format(k, defi_is, defi_be, len(counters2[k]))
            else:
                # mode is standard, must have equal results
                assert minc[k] == minc2[k], "k={}, minc[k]={}, minc2[k]={}".format(k,minc[k],minc2[k])
                assert counters[k] == counters2[k], "k={}. counter={} deficounter={}".format(k,counters[k],counters2[k])
        # are we done?
        if minc[maxk] >= mincov and minc2[maxk] >= mincov:  break
    print("Success.")
    # DONE.


############################################################3    

def main():
    (w, maxk, mincov, dstart, dstop) = (11, 2, 2, 5, 5)
    switch_at = 500  # SWITCH_NEVER or 2000
    #(w, maxk, mincov, dstart, dstop) = (11, 4, 1, 0, 8)
    random.seed(1717)  # for reproducibility, fix the random seed.
    print("% switching only for counter length >", switch_at)
    print("% w  q  d    k  cov  m*[k..1]  #opt.shapes, #matches")
    evaluate_all_shapes_with_weight(w, maxk, mincov, dstart, dstop, switch_at)


def evaluate_all_shapes_with_weight(w, maxk, mincov, dstart=0, dstop=None, switch_at=SWITCH_MINSIZE):
    for d in count(dstart):
        q = w + d
        bestresult, bestshapes = evaluate_shapes_of_type(w, q, maxk, mincov, switch_at=switch_at)
        mstars = bestresult.mstars[-1:0:-1]
        print("{}  {}  {}    {}  {}    ".format(w,q,d,maxk,mincov), end="")
        print("  ".join(map(str, mstars)), end="")
        mostmatches = 0
        for dc in sorted(bestshapes):
            s = shapestr(q, dc)
            mmps = min_matching_positions(q, dc, mincov)
            matches = mmps[-1]
            if matches > mostmatches:
                mostmatches = matches
                print(s)
            #print("% shape: {}, {} matches".format(s, mmps[-1]))
            #result, mm = evaluate_one_shape(q, dc, maxk, mincov, report_critical=True)
            #print("% position {}-tuples with coverage {}: {}".format(maxk, mincov, result.critical_tuples))
            #assert mm == mstar == result.mstar
        print("    {} shapes, {} matches".format(len(bestshapes), mostmatches))
        if dstop is not None and d >= dstop:  break

if __name__ == "__main__":
    main()
    
