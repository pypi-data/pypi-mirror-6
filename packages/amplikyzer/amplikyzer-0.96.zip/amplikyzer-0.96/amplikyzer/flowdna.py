"""
flowdna module for amplikyzer
(c) 2011--2012 Sven Rahmann
"""

from collections import Counter
from functools import lru_cache
from itertools import groupby

# public constants
from .core import *

# internal constants
_tosmall = dict(A='a', C='c', G='g', T='t', U='t')
_SMALL  = frozenset("acgt")
_BIG  = frozenset("ACGT")
_issmall = lambda x:  x in _SMALL
_isbig = lambda x:  x in _BIG


def dna(flows, flowchars=None, reverse=False, maxflow=99, translation=None):
    return flowdna(flows, flowchars=flowchars,
        reverse=reverse, strip=False, maxflow=maxflow,
        maybeflow=0.51, translation=translation)


def flowdna(flows, flowchars=None,
            reverse=False, strip=True, maxflow=DEFAULT_MAXFLOW,
            certain=DEFAULT_CERTAINFLOW, maybefraction=DEFAULT_MAYBEFRACTION,
            maybeflow=None, translation=None,
            return_lists=False):
    """
    universal flowdna function, in development
    """
    # use default 454 flowchars if None is given
    n = len(flows)  # usually 800
    if flowchars is None:
        nn = len(FLOWCHARS_454)
        if n % nn != 0:
            raise ValueError("len(flows) not divisible by {}".format(nn))
        flowchars = FLOWCHARS_454 * (n//nn)
    # reverse flows and flowchars if desired
    if reverse:
        flows = flows[::-1]
        flowchars = flowchars[::-1]
    # compute flowvalue valleys (intervals for uncertain flows)
    # (valleys is a list of intervals, indexed by 0 .. maxflow-1)
    if maybeflow is not None:
        valleys = compute_valleys_maybeflow(maxflow, maybeflow)
    else:
        (valleys, _) = compute_valleys(flows, maxflow, certain, maybefraction)
        maybeflow = certain 
    # translate flowchars if desired
    if translation is not None:
        flowchars = flowchars.translate(translation)
    # create runs, remove empty ones
    # one list for each run: [big, small, plus]
    plusbound = int(100*(maxflow + maybeflow) + 0.5)
    rlist = runlist(flowchars, flows, valleys, maxflow, plusbound)
    # strip optionals if desired
    if strip:  rlist = strip_optionals(rlist, reverse)
    # construct 3 lists: (dna, optional, plus)
    dna, optional, plus = threelists(rlist)
    if return_lists:
        return (dna, optional, plus)
    # return string
    strings = [_toflow(*dop) for dop in zip(dna,optional,plus)]
    return "".join(strings)

_toflow = lambda d,o,p:  d.lower() if o else (d+"+" if p else d)


def threelists(rlist):
    dna = [];  optional = [];  plus = []
    dappend = dna.append;  oappend = optional.append;  pappend = plus.append
    dextend = dna.extend;  oextend = optional.extend;  pextend = plus.extend
    for (c,big,small,p) in rlist:
        if big == 1:
            assert p == 0
            if small == 0:
                dappend(c)
                oappend(0)
                pappend(0)
            else:
                dappend(c); dappend(c)
                oappend(0); oappend(1)
                pappend(0); pappend(0)
            continue
        if big == 0:
            assert small == 1 and p == 0
            dappend(c)
            oappend(1)
            pappend(0)
            continue
        # general case, big >= 2
        assert (big >= 2) and (0 <= small + p <= 1)
        n = big + small;  z = [0] * n
        dextend([c]*n)
        if small:
            oextend([0]*big + [1])
            pextend(z)
        elif p:
            oextend(z)
            pextend([0]*(big-1) + [1])
        else:
            oextend(z)
            pextend(z)
    ###assert len(dna) == len(optional) == len(plus)
    return (dna, optional, plus)


def runlist(flowchars, flows, valleys, maxflow, plusbound):
    """
    return list of runs
    [[character,big,small,plus],[character,big,small,plus],...],
    such that consecutive characters differ,
    0 <= big <= maxflow and (small + plus) in {0,1}.
    """
    assert plusbound > 100*maxflow
    if len(flows)==0: return []
    null = valleys[0][0]
    L = [];  old = "$"; Lappend = L.append
    for (c,flow) in zip(flowchars, flows):
        if flow < null: continue  # empty run
        big = flow // 100;  small = 0
        if big < maxflow:
            v, V = valleys[big]
            ###assert big*100 <= v <= V <= (big+1)*100, "{} <= {} <= {} / {}".format(big*100, v, (big+1)*100, flow)
            if flow >= V: big += 1
            elif flow >= v: small = 1
        elif flow >= plusbound:
            big = maxflow + 1
        if c == old:  # continuing old run
            obig += big;  osmall += small
            continue
        # we counted a new run but didnt write the old one yet!
        if old != "$":  # do not append first
            if osmall == 0:
                if obig > maxflow:
                    Lappend([old, maxflow, 0, 1])
                else:
                    Lappend([old, obig, 0, 0])
            elif osmall == 1:
                if obig >= maxflow:
                    Lappend([old, maxflow, 0, 1])
                else:
                    Lappend([old, obig, 1, 0])
            else:
                obig += osmall // 2;  osmall %= 2
                if obig + osmall > maxflow:
                    Lappend([old, maxflow, 0, 1])
                else:
                    Lappend([old, obig, osmall, 0])
        old = c;  obig = big;  osmall = small
    # we have not written the last run yet
    obig += osmall // 2;  osmall %= 2
    if obig + osmall > maxflow:
        Lappend([old, maxflow, 0, 1])
    else:
        Lappend([old, obig, osmall, 0])
    return L


def strip_optionals(L, reverse=False):
    if not reverse:  # strip small characters at end
        i = len(L) - 1
        while i >= 0:
            if L[i][1] > 0:
                L[i][2] = 0
                break  # keep this i, but remove optionals
            i -= 1
        return L[:i+1]
    else:  # strip small characters at front
        i = 0
        while i < n:
            if L[i][1] > 0: break  # keep this i
            i += 1
        return L[i:]



@lru_cache(maxsize=10)
def compute_valleys_maybeflow(maxflow, maybeflow):
    m = int(maybeflow * 100 + 0.5)
    return [(100*i+m, 100*(i+1)-m) for i in range(maxflow)]

@lru_cache(maxsize=1)
def compute_valleys(flows, maxflow, certain, maybefraction):
    assert 0.0 <= certain <= 1.0
    c = int(100 * certain + 0.5)
    # compute histogram freqs (as list) from flows, do not use dict-like Counter
    mf = 100*maxflow
    freqs = [0] * (mf+1)
    for f in flows:
        if f < mf: freqs[f] += 1
    valleys = [];  sums = []
    for i in range(maxflow):
        val, s, S = valley(freqs, 100*i, 100*(i+1), fraction=maybefraction, certain=c)
        valleys.append((val[0],val[1]))
        sums.append((s,S))
    return valleys, sums


def valley(freqs, left, right, mid=None, fraction=DEFAULT_MAYBEFRACTION, certain=int(100*DEFAULT_CERTAINFLOW+0.5)):
    assert (type(certain) is int) and (0.0 <= fraction <= 1.0)
    if mid is None: mid = 1 + (left + right)//2
    S = sum(freqs[left:right])
    target = int(fraction * S)
    i = left + certain;  j = mid + 1
    s = sum(freqs[i:j])
    end = right - certain
    found = False
    best = (-1,-1,-1,-1)  # bestleft, bestright, bestwidth, best_s
    while i <= mid:
        while j < end:
            t = s + freqs[j]
            if t > target:  break
            s = t;  j += 1
        # interval i:j has sum s, which is <= target
        ###assert s == sum(freqs[i:j]), "{}: s={}, sum={}".format((i,j),s,sum(freqs[i:j]))
        if s <= target and j - i >= best[2]:
            if j-i > best[2] or s < best[3]:
                best = (i,j,j-i,s)
                found = True
        s -= freqs[i]
        i += 1
        if (end - i) < best[2]: break
        while s > target and j > mid+1:
            j -= 1
            s -= freqs[j]
            ###assert s == sum(freqs[i:j]), "{}: s={}, sum={}".format((i,j),s,sum(freqs[i:j]))
    if not found:  best = (mid, mid+1, 1, freqs[mid])
    return best, best[3], S  # ((left, right, width, sum), sum_in_valley, sum_in_range)


def filter_optionals(fopt, filters=DEFAULT_OPTIONALS_FILTERS, reverse=False):
    """
    filter binary list <fopt> of optionality indicators
    by applying several filters of the form (windowsize, allowed_optionals)
    to avoid dense regions of optional characters.
    Return the filtered list.
    """
    opt = fopt[:]
    n = len(opt)
    for (wlen, allowed) in filters:
        wsum = sum(opt[:wlen-1])
        # TODO FIMXE: initial sum may already violate constraints, we do not repair this
        for wlast in range(wlen-1, n):
            if opt[wlast]:
                if wsum >= allowed:  opt[wlast] = 0
                else:  wsum += 1
            wsum -= opt[wlast - wlen + 1]
    return opt if not reverse else opt[::-1]

        
############################################################################
# DNA utility functions

# reverse-complement a DNA sequence
_revcomptrans = str.maketrans("ATCGUatcgu", "TAGCAtagca")
def revcomp(dna, rc=_revcomptrans):
    """return reverse complement (string) of 'dna' (string)"""
    return dna.translate(rc)[::-1]

# forget gaps in a string
_forgetgapstrans = str.maketrans("","","-+")
def forgetgaps(dna, forget=_forgetgapstrans):
    return dna.translate(forget)
