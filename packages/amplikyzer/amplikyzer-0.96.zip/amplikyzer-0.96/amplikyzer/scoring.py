"""
scoring and alignment module for amplikyzer
(c) 2011--2013 Sven Rahmann
"""
from sys import stdout
from math import log
from collections import defaultdict

from .core import FLOWCHARS_454


# valid flowdna characters
valid_flowdna = "ACGTacgt+"

# valid genomic characters
valid_genomics = "ACGTNBDHVRYSWKM"

# gap character
GAP = '-'

# DNA IUPAC codes
IUPAC_sets = dict(A=frozenset("A"), C=frozenset("C"),
                  G=frozenset("G"), T=frozenset("T"),
                  B=frozenset("CGT"), D=frozenset("AGT"),
                  H=frozenset("ACT"), V=frozenset("ACG"),
                  R=frozenset("AG"), Y=frozenset("CT"),
                  S=frozenset("CG"), W=frozenset("AT"),
                  K=frozenset("GT"), M=frozenset("AC"),
                  N=frozenset("ACGT"),
                  )

assert frozenset(valid_genomics) == frozenset(IUPAC_sets.keys())

              
_flowdna_to_index_dict = {x: i for i,x in enumerate(valid_flowdna)}
_genomic_to_index_dict = {x: i for i,x in enumerate(valid_genomics)}
                          
def flowdna_to_indices(flowdna, d=_flowdna_to_index_dict):
    """convert a FlowDNA sequence to its score matrix indices"""
    return [ d[x] for x in flowdna ]

def genomics_to_indices(genomics, d=_genomic_to_index_dict):
    """convert a genomic sequence to its score matrix indices"""
    return [ d[x] for x in genomics ]



class ScorematrixFlowDNAIUPAC():
    """
    Score matrix of size |FlowDNA| x |IUPAC| = 9 x 15.
    User-controlled initialization parameters:
      match = match score (for confirmed nucleotides)
      mismatch = mismatch score (for confirmed nucleotides)
      smallmatch = match score for potential nucleotides
      smallmismatch = mismatch score for potential nucleotides
      bisulfite in {0,1,-1}: adjust score matrix for bisulfite treatment:
          0: no adjustment, 1: C->T substitutions ok, 2: G->A substitutions ok
    Attributes:
      self.maxscore - maximum score of this matrix
      self.minscore - mimimum score of this matrix
      self.range - difference between maxscore and minscore
      self.score - score matrix as a dict of dicts,
          indexed as score[flow][dna], e.g., score["C"]["G"]
      self.matrix - score matrix as a matrix, indexed matrix[1][2],
          use flowdna_to_indices and genomics_to_indices to compute indices.
    Methods:
      self.insflow(fl,fr,g) - score for inserting genomic g between flowdna fl, fr
      self.delflow(f,gl,gr) - score for deleting flow f between genomic gl, gr
    """
    # TODO FEATURE: customize the score constants in insflow and delflow
    # by giving __init__ more arguments
    
    def __init__(self,
            pmatch = 0.95, pmatch_small = 0.96, score_match=10.0,
            bisulfite=0):
        """
        Instantiate a score matrix with the given parameters.
        The default parameters have been chosen empirically and tested.
        pmatch = 0.95: expected number of identities (upper-case flows)
        pmatch_small = 0.96: dito (lower-case flows)
        score_match: final match score, determines scaling constant.
        bisulfite: 0 = no, 1=C->T, 2=G->A.

        Note that pmatch_small should always exceed pmatch.
        """
        flowdna = valid_flowdna
        genomics = valid_genomics
        if bisulfite not in {-1,0,1}:
            raise ValueError("bisulfite parameter must be in {0,1,-1}.")
        if not (pmatch_small >= pmatch):
            raise ValueError("for consistency, pmatch_small >= pmatch required")
        # compute score values
        _MINUS_INFINITY = -999999
        self._MINUS_INFINITY = _MINUS_INFINITY
        s, m = self.compute_scores_from_probs(
            pmatch, pmatch_small, score_match, bisulfite, flowdna, genomics, _MINUS_INFINITY)
        self.score = s
        self.matrix = m
        values = [v for L in m for v in L if v > _MINUS_INFINITY]
        #values = (match, mismatch, smallmatch, smallmismatch)
        self.maxscore = max(values)
        self.minscore = min(values)
        self.range = self.maxscore - self.minscore
        #self.show(file=stdout)
        self.set_insflow_dict(flowdna, genomics)
        self.set_delflow_dict(flowdna, genomics)

    def show(self, file=stdout):
        for f,row in zip(flowdna, self.matrix):
            print(f,row, file=file)
        print("min={}, max={}, range={}".format(self.minscore, self.maxscore, self.range))

    def compute_scores_from_probs(self,
            pmatch, pmatch_small, score_match, bisulfite, flowdna, genomics, minf):
        """
        Compute score dictionary and score matrix.
        Return the pair (score dictionary, score matrix).

        Scores are log-odds.
        For a flow and genomic nucleotide from ACGT,
        the score is the probability of observing (f,g) jointly,
        divided by the probability of observing them independently.
        The probability of observing them jointly in a true alignment
        is 1/4 * pmatch if f==g or else 1/4 * (1-pmatch)/3.
        The probability of observing them independently is 1/4 * 1/4.
        
        When bisulfite treatment is enabled this looks differently.
        For bisulfite == 1 (genomic C -> flow T),  the joint probability
        for (f,g) is as above if g!=C.
        For (f,C) it is 1/4 * pmatch/2 if f==C or f==T,
        and 1/4 * (1-pmatch)/2 if f==A or f==G.
        """
        # compute score factor constant
        asize = 4
        a1 = asize - 1.0
        a2 = asize - 2.0
        p0 = 1.0 / asize
        C = self._compute_score_factor(pmatch, p0, score_match)
        # define joint probabilities        
        if bisulfite == 0:
            _jointprob = lambda f,g,p: p if f==g else (1-p)/a1
        elif bisulfite == 1:  # genomic C -> flow T is ok
            def _jointprob(f,g,p):
                if g != "C":
                    return p if f==g else (1-p)/a1
                return p/2 if f=="T" or f=="C" else (1-p)/a2
        elif bisulfite == -1:  # genomic G -> flow A is ok
            def _jointprob(f,g,p):
                if g != "G":
                    return p if f==g else (1-p)/a1
                return p/2 if f=="A" or f=="G" else (1-p)/a2
        else:
            raise ValueError("bisulfite must be in {0,1,-1}.")
        s = dict()  # dict of dict of scores (score matrix as dict)
        m = list()  # list of list of scores (score matrix as matrix)
        for i,f in enumerate(flowdna):
            s[f] = dict()
            m.append([None]*len(genomics))
            for j,g in enumerate(genomics):
                # compute s[f][g]
                iug = IUPAC_sets[g]
                if f.isupper():
                    pjoint = sum(_jointprob(f,gg,pmatch) for gg in iug)
                    pnull = sum(_jointprob(f,gg,p0) for gg in iug)
                    #if g == "N":  assert pjoint==1, (pjoint, f,g)
                    sc = int(C * log(pjoint/pnull) + 0.5)
                elif f.islower():
                    fu = f.upper()
                    pjoint = sum(_jointprob(fu,gg,pmatch_small) for gg in iug)
                    pnull = sum(_jointprob(fu,gg,p0) for gg in iug)
                    sc = int(C * log(pjoint/pnull) + 0.5)
                else:
                    assert f == "+"
                    sc = minf  # minus infinity for practical purposes
                s[f][g] = m[i][j] = sc
        return s, m

    def _compute_score_factor(self, pmatch_true, pmatch_rand, target):
        """compute score scaling factor"""
        if not (0.0 < pmatch_rand < pmatch_true < 1.0):
            raise ValueError("inconsistent match probabilities given")
        return target / log(pmatch_true / pmatch_rand)
        
    def set_insflow_dict(self, flowdna, genomics):
        """
        return a dict insflow[fl][fr][g] with insertion scores;
        also set the self.insflow attribute
        """
        flowdna = tuple(flowdna) + (None,)
        insf = self.set_insflow_func()
        insflow = dict()
        for fl in flowdna:
            insflow[fl] = dict()
            for fr in flowdna:
                insflow[fl][fr] = dict()
                for g in genomics:
                    insflow[fl][fr][g] = insf(fl,fr,g)
        self.insflow = insflow
        return insflow
        
    def set_insflow_func(self):
        sc = self.score
        def insflow(fl,fr,g):
            """
            penalty for inserting g into flow between fl and fr;
            should be small if fr=="+" and g==fl, but high if they differ.
            We should never insert g before fr if g==fr.
            """
            if fr is None: return 0  # flow exhausted -- do not penalize!
            if fr == "+":
                if fl is None or sc[fl][g] >= 0:
                    return -1    # cheap to insert before +
                else:
                    return self._MINUS_INFINITY  # do not insert anything else before +
            #if ord(fr) > 96:  # small nucleotide
            #    return -30       # should not insert before small nucleotide
            # fr is "big", should not insert same as fr
            return -25 if sc[fr][g] < 0 else -26
        self.insflow = insflow
        return insflow

    def set_delflow_dict(self, flowdna, genomics):
        """
        return a dict delflow[f][gl][gr] with deletion scores;
        also set the self.delflow attribute
        """
        genomics = tuple(genomics) + (None,)
        delf = self.set_delflow_func()
        delflow = dict()
        for f in flowdna:
            delflow[f] = dict()
            for gl in genomics:
                delflow[f][gl] = dict()
                for gr in genomics:
                    delflow[f][gl][gr] = delf(f,gl,gr)
        self.delflow = delflow
        return delflow

    def set_delflow_func(self):
        sc = self.score
        def delflow(f,gl,gr):
            """penalty for deleting flow f between genomic gl, gr;
            should be very high if cl==cr, but small if f is small.
            """
            if f == "+":  return 0  # cheap to delete +
            if ord(f) > 96:  # small nucleotide
                return -5            # cheap to delete small flow nucleotide
            # big flow, should not be deleted, especially not between equal genomic chars
            return -25 if gl != gr else -26
        self.delflow = delflow
        return delflow
        
# end of class Scorematrix


_matrix_std = [
    #  A    C    G    T  N          
    [ 10, -15, -15, -15, 0], # f==A
    [-15,  10, -15, -15, 0], # f==C
    [-15, -15,  10, -15, 0], # f==G
    [-15, -15, -15,  10, 0], # f==T
    [  5,  -7,  -7,  -7, 0], # f==a
    [ -7,   5,  -7,  -7, 0], # f==c
    [ -7,  -7,   5,  -7, 0], # f==g
    [ -7,  -7,  -7,   5, 0], # f==t
    [-999999]*5 ]            # f==+

_matrix_bis1 = [
    [ 10, -15, -15, -15, 0], # f==A
    [-15,   5, -15, -15, 0], # f==C -
    [-15, -15,  10, -15, 0], # f==G
    [-15,  10, -15,  10, 0], # f==T *
    [  5,  -7,  -7,  -7, 0], # f==a
    [ -7,   3,  -7,  -7, 0], # f==c -
    [ -7,  -7,   5,  -7, 0], # f==g
    [ -7,   5,  -7,   5, 0], # f==t *
    [-999999]*5  ]           # f==+
    
_matrix_bis2 = [
    [ 10, -15,  10, -15, 0], # f==A *
    [-15,  10, -15, -15, 0], # f==C
    [-15, -15,   5, -15, 0], # f==G -
    [-15, -15, -15,  10, 0], # f==T
    [  5,  -7,   5,  -7, 0], # f==a *
    [ -7,   5,  -7,  -7, 0], # f==c
    [ -7,  -7,   3,  -7, 0], # f==g -
    [ -7,  -7,  -7,   5, 0], # f==t
    [-999999]*5  ]           # f==+


# Scorematrices for flowdna
flowdna_standard = ScorematrixFlowDNAIUPAC()
flowdna_bisulfiteCT = ScorematrixFlowDNAIUPAC(bisulfite=1)
flowdna_bisulfiteGA = ScorematrixFlowDNAIUPAC(bisulfite=-1)


########################################################################
## flowdna alignment and scoring

def traceback_flowdna(T, j, i, flowdna, genomic, GAP=GAP):
    INVALID, STOP, DIAG, UP, LEFT = range(5)    
    af = [];  ag = []
    while True:
        dd = T[j][i]
        if dd == STOP: break
        if dd == DIAG:
            jj = j - 1;  ii = i - 1
            af.append(flowdna[jj])
            ag.append(genomic[ii])
        elif dd == LEFT:
            jj = j - 1;  ii = i
            af.append(flowdna[jj])
            ag.append(GAP)
        elif dd == UP:
            jj = j;  ii = i - 1
            af.append(GAP)
            ag.append(genomic[ii])
        else:
            raise RuntimeError("INVALID value in traceback matrix")
        j = jj;  i = ii
    return "".join(af[::-1]),  "".join(ag[::-1])


def allocate_flowdna_alignment_matrices(m, n):
    """
    allocate score matrix.
    m is len(genomic), n is len(flowdna).
    Return Sold, Snew, T (old score column, new score colum, Traceback matrix).
    """
    # allocate last and current column of score matrix
    m1 = m + 1
    Sold = [0]*m1
    Snew = [0]*m1
    # allocate T[j][i] as traceback matrix, value 0 indicates uninitialized
    n1 = n + 1
    INVALID = 0
    T = [ [INVALID]*m1 for j in range(n1) ]
    return Sold, Snew, T

def compute_row_thresholds(m, target, maxscore):
    m1 = m + 1
    for x in (m, target, maxscore):  assert type(x) is int
    return [ target - (m-i)*maxscore for i in range(m1) ]


def align_genomic_to_flowdna(genomic, flowdna, score, bestth):
    """
    Align a <flowdna> string to a <genomic> sequence
    using score matrix <score>.
    Return (best_score, best_column_index, alignment),
    where alignment is a pair of strings.
    """
    # genomic must be upper-case DNA and not be empty.
    assert len(genomic) > 0,  "genomic sequence is empty"
    assert len(flowdna) > 0,  "flowdna sequence is empty"
    m = len(genomic);  n = len(flowdna)
    insflow = score.insflow;  delflow = score.delflow;  sc = score.score
    maxscore = score.maxscore
    INVALID, STOP, DIAG, UP, LEFT = range(5)
    Sold, Snew, T = allocate_flowdna_alignment_matrices(m,n)
    th = compute_row_thresholds(m, bestth, maxscore)
    # column j = 0
    f = flowdna[0];  Tj = T[0];  Tj[0] = STOP
    insf = insflow[None][f]
    for i1, g in enumerate(genomic):  # i in range(1, m+1)
        i = i1 + 1
        Snew[i] = si = Snew[i1] + insf[g]
        Tj[i] = UP
        if si >= th[i]: lastgoodi = i
    best, bestj = Snew[m], -1
    # columns j = 1 .. end
    for j in range(1, n+1):  # iterate over flowdna
        Snew, Sold  =  Sold, Snew
        fl = flowdna[j-1]
        fr = flowdna[j] if j < n else None
        Snew[0] = 0
        Tj = T[j];  Tj[0] = STOP  # not LEFT beause of "glocal" alignment
        scfl = sc[fl];  delfl = delflow[fl]; insflfr = insflow[fl][fr]
        for i1, (g, sdi, sup) in enumerate(zip(genomic,Sold,Snew)):  # i in range(1,m+1)
            i = i1 + 1
            if i > lastgoodi:  i = -1;  break
            # diagonal score
            scr = sdi + scfl[g];  trb = DIAG
            # left score
            scrx = Sold[i] + delfl[g][genomic[i] if i<m else None]
            if scrx > scr:  scr = scrx;  trb = LEFT
            # up score
            scrx = sup + insflfr[g]
            if scrx > scr:  scr = scrx;  trb = UP
            # save best choice
            Snew[i] = scr;  Tj[i] = trb
        # treat lastgoodi + 1 specially: don't look left
        if i == -1 and lastgoodi+1 <= m:
            i = lastgoodi + 1
            # diagonal score
            scr = sdi + scfl[g];  trb = DIAG
            # up score
            scrx = sup + insflfr[g]
            if scrx > scr:  scr = scrx;  trb = UP
            # save best choice
            Snew[i] = scr;  Tj[i] = trb
        else:  # we had to compute this all the way down without special treatment
            assert i == lastgoodi == m
        # compute new lastgoodi
        while Snew[i] < th[i]: i -= 1
        lastgoodi = i
        # is j the new best column?  adjust thresholds if reasonable
        if lastgoodi == m and Snew[m] > best:
            best = Snew[m]
            bestj = j
            if (best - bestth >= 4*maxscore) and (n - j >= 5):
                bestth = best
                th = compute_row_thresholds(m, bestth, maxscore)    
    # done, compute traceback
    if bestj < 0: return(-1, -1, ("?", "?"))  # failure
    return (best, bestj, traceback_flowdna(T,bestj,m,flowdna,genomic))



########################################################################
## flow sequence alignment and scoring

class ScorematrixFlowIUPAC:

    _score_probs = [
        # probabilities must take into account
        # both sequencing errors and true variants.
        (0.05, 0.05),  # |genomic|==0, probability at distance 1 (left, right)
        (0.05, 0.10),  # |genomic|==1: proabilities for (0, 2)
        (0.15, 0.20),  # |genomic|==2: for (1, 3)
        (0.25, 0.30),  # 3: (2, 4)
        (0.30, 0.35),  # 4: (3, 5)
        (0.40, 0.50),  # 5: (4, 6)
        (0.60, 0.70),  # 6: (5, 7)
        (0.70, 0.75),  # 7: (6, 8)
        (0.80, 0.90),  # 8: (7, 9), and so on.
        ]

    _prob_ok = 0.5

    def __init__(self,
        score_match=10, score_mismatch=-15,
        score_delete_one=-15, score_genomic_vs_gap=-20,
        bisulfite=0, probs=_score_probs, prob_ok=_prob_ok):
        """initialize score matrix with given parameters"""
        if bisulfite == 0:
            self.iupac = dict(IUPAC_sets)
        elif bisulfite == 1:
            _additional_T = frozenset("T")
            self.iupac = {k: (v | _additional_T) if "C" in v else v  for k,v in IUPAC_sets.items()}
        elif bisulfite == -1:
            _additional_A = frozenset("A")
            self.iupac = {k: (v | _additional_A) if "G" in v else v  for k,v in IUPAC_sets.items()}
        else:
            raise ValueError("bisulfite must be in {0,1,-1}")
        self.probs = probs
        self.lambdas = [ (-log(pleft), -log(pright)) for (pleft, pright) in probs ]
        self.prob_ok = prob_ok
        self.logprob_ok = log(prob_ok)
        self.C = score_delete_one / (log(probs[1][0]) - self.logprob_ok)
        self.genomic_vs_gap = score_genomic_vs_gap
        self.score_match = score_match
        self.score_mismatch = score_mismatch
        self.f = self.get_scoring_function()
        

    def compute_score(self, flowchar, flow, genomic):
        """
        Return the score of aligning flowchar^flow to genomic substring.
        flow must be real-valued (e.g. 1.23).
        """
        # score component for length difference: double exponential
        leng = len(genomic)
        lambdas = self.lambdas
        index = leng if leng < len(lambdas) else -1
        lambdalr = lambdas[index]
        if flow < leng:
            lambd = lambdalr[0]
            delta = leng - flow
        else:
            lambd = lambdalr[1]
            delta = flow - leng
        sc = int(self.C * (-lambd*delta - self.logprob_ok))
        # score component for each genomic against flowchar
        iupac = self.iupac
        match_list = [flowchar in iupac[g] for g in genomic]
        matches = sum(match_list)
        sc += matches * self.score_match + (leng-matches) * self.score_mismatch
        # extra penalty for non-matching characters at end
        #if len(match_list) > 0:
        #    if not match_list[0]:  sc += score_mismatch
        #    if not match_list[-1]:  sc += score_mismatch
        return sc

    def get_scoring_function(self):
        lambdas = self.lambdas
        C = self.C
        logprob_ok = self.logprob_ok
        _score_len = defaultdict(dict)
        for leng in range(13):
            for ff in range(100):
                index = leng if leng < len(lambdas) else -1
                lambdalr = lambdas[index]
                flow = ff / 10.0
                if flow < leng:
                    lambd = lambdalr[0]
                    delta = leng - flow
                else:
                    lambd = lambdalr[1]
                    delta = flow - leng
                _score_len[leng][ff] = int(C * (-lambd*delta - logprob_ok))
        def f(flowchar, flow, genomic,
              iupac=self.iupac,
              sl=_score_len, sm=self.score_match, smm=self.score_mismatch):
            leng = len(genomic)
            s = sl[leng].get(flow)
            if s is None:
                return self.compute_score(flowchar, flow/10.0, genomic)
            matches = sum([flowchar in iupac[g] for g in genomic])
            return s + matches*sm + (leng-matches)*smm
        return f

# Scorematrices for flows
flow_standard = ScorematrixFlowIUPAC()
flow_bisulfiteCT = ScorematrixFlowIUPAC(bisulfite=1)
flow_bisulfiteGA = ScorematrixFlowIUPAC(bisulfite=-1)




TRACE_FLOW_INVALID = -3
TRACE_FLOW_STOP = -2
TRACE_FLOW_UP = -1

def allocate_flow_alignment_matrices(m, n, INVALID=TRACE_FLOW_INVALID):
    """
    allocate alignment score/edit matrix.
    m is len(genomic), n is len(flowdna).
    Return Sold, Snew, T (old score column, new score colum, Traceback matrix).
    """
    # allocate last and current column of score matrix
    m1 = m + 1
    Sold = [0] * m1
    Snew = [0] * m1
    # allocate T[j][i] as traceback matrix; INVALID means uninitialized
    n1 = n + 1
    T = [ [INVALID]*m1 for j in range(n1) ]
    return Sold, Snew, T


def traceback_flows(T, j, i, flows, flowchars, genomic,
                    suppress_gaps=False, GAP=GAP, 
                    STOP=TRACE_FLOW_STOP, UP=TRACE_FLOW_UP):
    af = [];  ag = []
    while True:
        dd = T[j][i]
        if dd == STOP:  break
        elif dd == UP:  # genomic character deleted (not aligned to flow)
            jj = j;  ii = i - 1
            af.append(GAP) 
            ag.append(genomic[ii])
        elif dd >= 0:  # dd genomic character(s), even 0, aligned to one flow
            jj = j - 1;  ii = i - dd
            gg = genomic[ii:i]
            #ff = flowchars[jj] + "{:.2f}".format(flows[jj]/100)
            if suppress_gaps:
                ff = flowchars[jj] * len(gg)
            else:
                ff = flowchars[jj] * int(flows[jj]/100 + 0.5)
                ll = len(gg) - len(ff)
                if ll > 0:
                    ff = GAP*ll + ff
                elif ll < 0:
                    gg = GAP*(-ll) + gg
            af.append(ff)
            ag.append(gg)
        else:
            raise RuntimeError("INVALID value {} in flow traceback matrix".format(dd))
        j = jj;  i = ii
    return "".join(af[::-1]),  "".join(ag[::-1])



def align_genomic_to_flows(genomic, flows, flowchars=None,
    scorematrix=flow_standard, suppress_gaps=False,
    INVALID=TRACE_FLOW_INVALID, STOP=TRACE_FLOW_STOP, UP=TRACE_FLOW_UP):
    """
    Align a <genomic> sequence to a sequence of <flows>,
    the flow nucleotides are <flowchars> (e.g., TACG).

    Compute DP score matrix column by column (flow by flow).
    i/j  .  T1.0 A2.1 C1.1 G2.2 T3.1 A0.1 C2.7 G0.2 (n)
    .    0  0    0    0    0    0    0    0    0
    T   -d  +
    A  -2d 
    A  -3d
    G  -4d
    G   .
    A   .
    T   .
    G   . 
    T   .
    C   .
    C   .
    (m)
             
    Return (best_score, best_column_index, alignment),
    where alignment is a pair of strings.
    """
    # genomic must be upper-case DNA and not be empty.
    assert len(genomic) > 0,  "genomic sequence is empty"
    assert len(flows) > 0,  "flow sequence is empty"
    m = len(genomic);  n = len(flows)
    if flowchars is None:
        nn = len(FLOWCHARS_454)
        if n % nn != 0:
            raise ValueError("len(flows) not divisible by {}".format(nn))
        flowchars = FLOWCHARS_454 * (n//nn)
    assert len(flowchars) == len(flows)
    Sold, Snew, T = allocate_flow_alignment_matrices(m, n, INVALID=INVALID)
    threshold = int(0.95 * m * scorematrix.score_match)
    genomic_vs_gap = scorematrix.genomic_vs_gap
    score = scorematrix.f
    # column j = 0: compute Snew
    Tj = T[0]
    for i in range(m+1):
        Snew[i] = i * genomic_vs_gap
        Tj[i] = STOP if i == 0 else UP
    best = Snew[m];  bestj = 0
    # column j = 1 .. n,  referring to flows[j-1]
    for j in range(1, n+1):
        Snew, Sold = Sold, Snew
        fc = flowchars[j-1]
        fl = (flows[j-1] + 5) // 10  # int -> real-valued flow
        irange = int(1.5 * (1 + flows[j-1] / 100.0) + 0.5)
        Snew[0] = 0
        Tj = T[j];  Tj[0] = STOP  # "glocal" alignment
        for i in range(1, m+1):
            # consider deleting one genomic nucleotide (genomic vs nothing)
            sc = Snew[i-1] + genomic_vs_gap
            t = UP
            # consider substrings genomic[k:i] for k <= i
            # starting at startk = i - 2*(1+int(f)) [or 0 if that is negative]
            startk = i - irange
            if startk < 0:  startk = 0
            for k in range(startk, i+1):
                gsub = genomic[k:i]
                # compute score to align gsub to fc^f
                sk = Sold[k] + score(fc, fl, gsub)
                if sk >= sc:
                    sc = sk
                    t = i - k
            Snew[i] = sc;  Tj[i] = t
        if Snew[m] > best and Snew[m] >= threshold:
            best = Snew[m]
            bestj = j
    # done, compute traceback
    if bestj <= 0:  return(-1, -1, ("?", "?"))  # failure
    return (best, bestj, traceback_flows(
        T, bestj, m, flows, flowchars, genomic, suppress_gaps=suppress_gaps))
