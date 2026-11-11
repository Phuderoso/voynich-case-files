#!/usr/bin/env python3
"""C105 (F-RHYTHM step 4, C104 correction): does word length carry over across the line break between the truly
ADJACENT words (last word of line i -> first word of line i+1)?
C104 paired the last KEPT word with the first KEPT word, a lag-4 pair in running text, so its question about the adjacent
rhythm was NOT TESTABLE. Edge words are special in Voynich lines, so the null here keeps positions: it re-pairs line ends
with line starts of OTHER lines in the same paragraph run (successor first words permuted among the successor lines of
the run). Paragraph-level heterogeneity and the edge-position marginals are therefore kept in the null.
Lines: C104 parse_runs verbatim (paragraph loci, no '<->', all words [a-z]+, >= 6 words; runs = consecutive loci inside a
paragraph). Lengths in EVA glyph units (C003 units()). Only runs with >= 3 lines carry information under this null.
H1 (cross-break adjacent carry-over): r_E = Pearson over adjacent-line pairs of (len word n of line i, len word 1 of line
   i+1). Null: within each run, the first words of lines 2..k permuted among those lines. D_E = r_E - null mean.
   p two-sided = (1 + #|r*-m| >= |r-m|)/(R+1), R 2000; Holm over 4 = {Currier A,B} x {IT2a,ZL3b}.
   Verdict per language: DETECTED-PERSISTENT/-ALTERNATING (both transcriptions Holm <= 0.05, same sign), PARTIAL (one),
   NOT DETECTED (none), NOT TESTABLE (any gate fails).
H2 (break vs line-end comparator, secondary): within-line edge pair (word n-1, word n) on the same lines, same re-pairing
   logic (word n permuted among the lines of the run, lines 1..k). Delta = D_E - D_N. 95% percentile CI from a run-level
   bootstrap (B 1000, each replicate recomputes both D with R_B 200 null draws). Registered reading: CI excludes 0 ->
   "the break differs from the line-end pair" (sign says which); CI covers 0 -> "no difference resolved". Not Holm-corrected
   with H1 (secondary, disclosed). Also descriptive: (word 1, word 2) start pair D_S under the same logic.
Plants (pseudo replicate = successor first words randomly re-paired within runs): with prob q per pair, the first word of
   line j+1 is swapped with the successor first word of the same run closest in length to the last word of line j (POS) or
   the most distant (NEG). Design (seed 11698): q = smallest of (0.10, 0.20, 0.40) with p <= 0.05 and right sign in >= 9/10
   replicates for both plants in all 4 subsets (RG 300); none -> NOT TESTABLE. Gates (seed 11699, 20 fresh): FPR <= 2/20,
   POS and NEG >= 16/20, broken meter mean D_NEG < 0 < mean D_POS.
Natural prose reference (descriptive): Caesar, Descartes, Dante, Cervantes, Kivi cut into pseudo-lines (word counts from
   IT2a Currier B lines, runs of 8, seed 11701, R 500), letters as units: D_E, D_N, Delta where breaks are layout-only.
Audit C104: H1a observed r_X of the four subsets must equal the published values to 1e-12.
Seeds 11698 design, 11699 gates, 11700 tests (+1 bootstrap -> 11701 is natural; bootstrap uses 11702). Next free 11703.
Run: timeout 600 python tools/c105_edge_pair_break.py analysis/C105_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import FILES
from c003_position_rigidity import units, gutenberg
import c102_word_length_rhythm as W
import c104_rhythm_line_breaks as C4

DSEED, GSEED, SEED, NSEED, BSEED = 11698, 11699, 11700, 11701, 11702
R, RG, NG, B, RB, ALPHA, QS = 2000, 300, 20, 1000, 200, 0.05, (0.10, 0.20, 0.40)
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: R, RG, NG, B, RB = 50, 20, 2, 20, 20
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

class E:
    """runs: list of runs; each line = array of all word lengths (>= 6 words)."""
    def __init__(self, runs):
        runs = [r for r in runs if len(r) >= 1]
        self.runs = runs
        L = [l for r in runs for l in r]
        self.run = np.concatenate([np.full(len(r), i) for i, r in enumerate(runs)])
        self.w1 = np.array([l[0] for l in L], float); self.w2 = np.array([l[1] for l in L], float)
        self.wn = np.array([l[-1] for l in L], float); self.wm = np.array([l[-2] for l in L], float)
        self.pair = self.run[1:] == self.run[:-1]
        idx = np.arange(len(L))
        # successor lines (index j+1 for paired j) grouped by run; all lines grouped by run
        succ = idx[1:][self.pair]; ug, st = np.unique(self.run[succ], return_index=True); self.succ_groups = np.split(succ, st[1:])
        self.all_groups = np.split(idx, np.cumsum([len(r) for r in runs])[:-1])
        self.pi = idx[:-1][self.pair]; self.si = idx[1:][self.pair]
        self.fS, self.fA = E.flat(self.succ_groups), E.flat(self.all_groups)  # cached for speed (C105 run fix)
    def rE(self, w1): return float(np.corrcoef(self.wn[self.pi], w1[self.si])[0, 1])
    def rN(self, wn): return float(np.corrcoef(self.wm, wn)[0, 1])
    def rS(self, w2): return float(np.corrcoef(self.w1, w2)[0, 1])
    @staticmethod
    def flat(groups):
        return np.concatenate(groups), np.concatenate([np.full(len(g), i) for i, g in enumerate(groups)])
    @staticmethod
    def perm(v, groups, rng):
        """within-group permutation, vectorised: random keys sorted inside each group label.
        groups = list of index arrays, or a precomputed (idx, lab) pair (speed only; identical draws)."""
        idx, lab = groups if isinstance(groups, tuple) else E.flat(groups)
        o = v.copy(); o[idx] = v[idx[np.lexsort((rng.random(len(idx)), lab))]]
        return o
    def null(self, which, rng, r):
        if which == 'E': return np.array([self.rE(self.perm(self.w1, self.fS, rng)) for _ in range(r)])
        if which == 'N': return np.array([self.rN(self.perm(self.wn, self.fA, rng)) for _ in range(r)])
        return np.array([self.rS(self.perm(self.w2, self.fA, rng)) for _ in range(r)])
    def obs(self, which): return {'E': lambda: self.rE(self.w1), 'N': lambda: self.rN(self.wn), 'S': lambda: self.rS(self.w2)}[which]()
    def test(self, which, rng, r): return C4.ptest(self.obs(which), self.null(which, rng, r))

def lens_runs(pr): return [[np.array([len(units(w)) for w in l], float) for l in r] for r in pr]

def pseudo(S, rng):
    w1 = E.perm(S.w1, S.succ_groups, rng); out, k = [], 0
    for r in S.runs:
        rr = []
        for l in r: x = l.copy(); x[0] = w1[k]; rr.append(x); k += 1
        out.append(rr)
    return out

def plant(runs, rng, q, kind):
    for r in runs:
        for j in range(1, len(r)):
            if rng.random() < q and len(r) > 2:
                cand = list(range(1, len(r))); vals = np.array([r[c][0] for c in cand]); d = np.abs(vals - r[j - 1][-1])
                c = cand[int(np.argmin(d) if kind == 'POS' else np.argmax(d))]
                r[j][0], r[c][0] = r[c][0], r[j][0]
    return runs

def gate(S, rng, q, ng):
    fp = pos = neg = 0; dp, dn = [], []
    for _ in range(ng):
        P0 = pseudo(S, rng); t = E(P0).test('E', rng, RG); fp += t['p'] <= ALPHA
        t = E(plant([[x.copy() for x in r] for r in P0], rng, q, 'POS')).test('E', rng, RG); pos += t['p'] <= ALPHA and t['D'] > 0; dp.append(t['D'])
        t = E(plant([[x.copy() for x in r] for r in P0], rng, q, 'NEG')).test('E', rng, RG); neg += t['p'] <= ALPHA and t['D'] < 0; dn.append(t['D'])
    return dict(FPR=int(fp), POS=int(pos), NEG=int(neg), D_pos_mean=float(np.mean(dp)), D_neg_mean=float(np.mean(dn)))

def delta_ci(S, rng):
    obs = S.test('E', rng, RB)['D'] - S.test('N', rng, RB)['D']; bs = []
    for _ in range(B):
        Sb = E([S.runs[i] for i in rng.integers(0, len(S.runs), len(S.runs))])
        bs.append(Sb.test('E', rng, RB)['D'] - Sb.test('N', rng, RB)['D'])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return dict(delta=float(obs), ci=[float(lo), float(hi)], reading=('BREAK HIGHER' if lo > 0 else 'BREAK LOWER' if hi < 0 else 'no difference resolved'))

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C105_results.json'
    res = dict(cycle='C105', smoke=SMOKE, seeds=dict(design=DSEED, gates=GSEED, test=SEED, natural=NSEED, bootstrap=BSEED), next_free_seed=11703)
    sub, raw = {}, {}
    for k, f in FILES:
        pr = C4.parse_runs(f)
        for L in 'AB': raw[f'{k}|{L}'] = pr[L]; sub[f'{k}|{L}'] = E(lens_runs(pr[L]))
    res['n'] = {s: dict(lines=len(S.w1), runs=len(S.runs), runs_ge3=int(sum(len(r) >= 3 for r in S.runs)), pairs=int(S.pair.sum()),
                        informative_pairs=int(sum(len(g) for g in S.succ_groups if len(g) > 1))) for s, S in sub.items()}; log('n', res['n'])
    pub = json.load(open('analysis/C104_results.json'))['H1']; A = {}
    for s in sub:
        S4 = C4.Runs(raw[s]); A[s] = dict(r=S4.rX(S4.first, S4.last), published=pub[f'H1a|{s}']['r'])
    res['audit_C104'] = dict(values=A, exact=all(abs(v['r'] - v['published']) < 1e-12 for v in A.values())); log('audit', res['audit_C104']['exact'])
    rng = np.random.default_rng(DSEED); qd = None; tab = {}
    for q in QS:
        tab[q] = {s: gate(S, rng, q, 10 if not SMOKE else 1) for s, S in sub.items()}; log('design', q)
        if all(g['POS'] >= (9 if not SMOKE else 0) and g['NEG'] >= (9 if not SMOKE else 0) for g in tab[q].values()): qd = q; break
    res['design'] = dict(q=qd, table={str(k): v for k, v in tab.items()})
    rng = np.random.default_rng(GSEED); G = {}
    for s, S in sub.items():
        g = gate(S, rng, qd if qd else QS[-1], NG)
        g['ok'] = bool(qd and g['FPR'] <= 2 and g['POS'] >= 16 and g['NEG'] >= 16 and g['D_neg_mean'] < 0 < g['D_pos_mean']); G[s] = g
    res['gates'] = G; log('gates done')
    if SMOKE:
        res['elapsed_s'] = round(time.time() - T0, 1); json.dump(res, open(outp, 'w'), indent=1, default=float); log('smoke done'); return
    rng = np.random.default_rng(SEED); H = {s: S.test('E', rng, R) for s, S in sub.items()}
    ph = W.holm({k: v['p'] for k, v in H.items()})
    for k in H: H[k]['p_holm'] = ph[k]
    res['H1'] = H; ver = {}
    for L in 'AB':
        ks = [f'{k}|{L}' for k, _ in FILES]
        if not all(G[k]['ok'] for k in ks): ver[L] = 'NOT TESTABLE'; continue
        rej = [k for k in ks if H[k]['p_holm'] <= ALPHA]; sg = {np.sign(H[k]['D']) for k in rej}
        ver[L] = ('DETECTED-' + ('ALTERNATING' if sg == {-1.0} else 'PERSISTENT')) if len(rej) == 2 and len(sg) == 1 else 'PARTIAL' if rej else 'NOT DETECTED'
    res['verdict_H1'] = ver
    res['comparators'] = {s: dict(N=S.test('N', rng, R), S=S.test('S', rng, R)) for s, S in sub.items()}
    rng = np.random.default_rng(BSEED); res['H2'] = {s: delta_ci(S, rng) for s, S in sub.items()}
    rng = np.random.default_rng(NSEED)
    from c070_word2_sh import parse
    ll = np.array([len(l['words']) for l in parse(dict(FILES)['IT2a']) if l['L'] == 'B'])
    NL = {}
    for name, fn in (('Latin Caesar', 'pg218.txt'), ('Latin Descartes', 'pg23306.txt'), ('Italian Dante', 'pg1012.txt'),
                     ('Spanish Cervantes', 'pg2000.txt'), ('Finnish Kivi', 'pg11940.txt')):
        w = [x for l in gutenberg('data/corpora/' + fn) for x in l]; lines, i = [], 0
        while i < len(w) and len(lines) < 2000:
            n = int(rng.choice(ll)); lines.append(w[i:i + n]); i += n
        lines = [np.array([len(x) for x in l], float) for l in lines if len(l) >= 6]
        S = E([lines[j:j + 8] for j in range(0, len(lines), 8)])
        te, tn = S.test('E', rng, 500), S.test('N', rng, 500)
        NL[name] = dict(D_E=te['D'], p_E=te['p'], D_N=tn['D'], p_N=tn['p'], delta=te['D'] - tn['D'])
    res['natural'] = NL
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('verdict', ver)

if __name__ == '__main__':
    main()
