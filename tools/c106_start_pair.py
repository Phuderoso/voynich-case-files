#!/usr/bin/env python3
"""C106 (F-RHYTHM step 5): is the line-START pair (word 1 -> word 2) length coupling of C105 (descriptive, Currier B
D_S +0.15/+0.12 under the run re-pairing null) real once line word-count is held in the null?
C105 blind spot (told to Kryptos): its null kept paragraph runs and edge positions but not the line word-count or the
line order. Longer lines could carry both longer word 1 and longer word 2 (layout squeeze), which a run-only null keeps
in the statistic. Kryptos's three pre-run review points are built in: (1) informative lines per stratum printed and a
degeneracy gate; (2) 'gallows-initial' defined here before any D_S is seen; (3) the planted gate certifies an effect of
about +0.15 (calibrated plant size), not only huge plants.
Lines/runs: C104 parse_runs verbatim (paragraph loci, no '<->', words [a-z]+, >= 6 words). Lengths in EVA glyph units.
Strata: word-count tercile cut points (np.quantile 1/3, 2/3 of the subset's line word counts; bin = np.digitize(wc,cuts,
right=True) -> 0,1,2).
H1: r_S = Pearson over lines of (len word 1, len word 2). N1 (registered null): word 2 permuted among the lines of the
   same group (paragraph run x word-count tercile). D_S = r_S - null mean; p two-sided (C104 ptest), R 2000; Holm over 4.
   Verdict per language: DETECTED-COUPLED / DETECTED-ANTI (both transcriptions Holm <= 0.05 same sign), PARTIAL (one),
   NOT DETECTED (none), NOT TESTABLE (any gate fails).
Degeneracy gate (review point 1): informative lines (in groups of size >= 2) >= 50 % of lines in every subset, and printed
   per tercile; else NOT TESTABLE.
Robustness (registered, not in Holm family; reading rule in the case file): R1 N2 = word 2 permuted within word-count
   DECILE over the whole subset (keeps word-count finely, drops runs); R2 = run-first lines removed (line 2 vs later),
   N1 groups re-formed on the remaining lines.
Descriptive (no verdict): D_S by run position (1, 2, >= 3) and by gallows-initial word 1 (first glyph unit in k t p f, or
   word starts with ckh cth cph cfh) vs not, each under N2 within the class.
Plants: in a pseudo replicate (word 2 re-paired under N1), with prob q per line, word 2 of the line is swapped with the
   word 2 of its N1 group closest in length to word 1 of the line (POS) or most distant (NEG).
   Calibration (seed 11703, 10 pseudo per q, per subset): q* = smallest q in 0.05..0.60 (step 0.05) with mean planted D_POS
   >= +0.15; q_half = smallest with mean >= +0.075 (descriptive power only). No q* -> NOT TESTABLE.
   Gates (seed 11704, 20 fresh per subset, RG 300): FPR <= 2/20; POS and NEG at q* >= 16/20 right sign; broken meter
   mean D_NEG < 0 < mean D_POS. Power at q_half reported.
Seeds 11703 calibration, 11704 gates, 11705 tests, 11706 robustness, 11707 descriptive. Next free 11708.
Run: timeout 600 python tools/c106_start_pair.py analysis/C106_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import FILES
from c003_position_rigidity import units
import c102_word_length_rhythm as W
import c104_rhythm_line_breaks as C4

CSEED, GSEED, SEED, RSEED, DSEED = 11703, 11704, 11705, 11706, 11707
R, RG, NG, NC, ALPHA = 2000, 300, 20, 10, 0.05
QGRID = tuple(round(0.05 * i, 2) for i in range(1, 13))
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: R, RG, NG, NC = 50, 20, 2, 1
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

GAL = ('ckh', 'cth', 'cph', 'cfh')
def gallows_initial(w): return w.startswith(GAL) or units(w)[0] in ('k', 't', 'p', 'f')

def groups_of(labels):
    """index arrays of equal labels (labels: list of hashables)."""
    d = {}
    for i, l in enumerate(labels): d.setdefault(l, []).append(i)
    return [np.array(v) for v in d.values()]

def flat(groups):
    return np.concatenate(groups), np.concatenate([np.full(len(g), i) for i, g in enumerate(groups)])

def perm(v, fl, rng):
    idx, lab = fl; o = v.copy(); o[idx] = v[idx[np.lexsort((rng.random(len(idx)), lab))]]; return o

class S:
    """lines: list of dicts with w1, w2 (lengths), wc, run, pos, gal."""
    def __init__(self, lines, key='N1'):
        self.lines = lines
        self.w1 = np.array([l['w1'] for l in lines], float); self.w2 = np.array([l['w2'] for l in lines], float)
        wc = np.array([l['wc'] for l in lines])
        cuts = np.quantile(wc, [1 / 3, 2 / 3]); self.terc = np.digitize(wc, cuts, right=True)
        dec = np.digitize(wc, np.quantile(wc, np.arange(1, 10) / 10), right=True)
        lab = [(l['run'], int(t)) for l, t in zip(lines, self.terc)] if key == 'N1' else [int(d) for d in dec]
        self.groups = groups_of(lab); self.fl = flat(self.groups)
        self.inf = np.zeros(len(lines), bool)
        for g in self.groups:
            if len(g) > 1: self.inf[g] = True
    def r(self, w2): return float(np.corrcoef(self.w1, w2)[0, 1])
    def test(self, rng, r, w2=None):
        w2 = self.w2 if w2 is None else w2
        return C4.ptest(self.r(w2), np.array([self.r(perm(w2, self.fl, rng)) for _ in range(r)]))
    def plant(self, w2, rng, q, kind):
        w2 = w2.copy()
        for g in self.groups:
            if len(g) < 2: continue
            for j in g:
                if rng.random() < q:
                    d = np.abs(w2[g] - self.w1[j]); c = g[int(np.argmin(d) if kind == 'POS' else np.argmax(d))]
                    w2[j], w2[c] = w2[c], w2[j]
        return w2

def build(runs):
    out = []
    for ri, r in enumerate(runs):
        for pi, ws in enumerate(r):
            out.append(dict(w1=len(units(ws[0])), w2=len(units(ws[1])), wc=len(ws), run=ri, pos=pi + 1, gal=gallows_initial(ws[0])))
    return out

def calibrate(Sx, rng):
    tab = {}
    for q in QGRID:
        tab[q] = float(np.mean([Sx.test(rng, RG, Sx.plant(perm(Sx.w2, Sx.fl, rng), rng, q, 'POS'))['D'] for _ in range(NC)]))
        if tab[q] >= 0.15: break
    qs = next((q for q in QGRID if q in tab and tab[q] >= 0.15), None)
    qh = next((q for q in QGRID if q in tab and tab[q] >= 0.075), None)
    return dict(table={str(k): v for k, v in tab.items()}, q_star=qs, q_half=qh)

def gate(Sx, rng, q, qh):
    fp = pos = neg = ph = 0; dp, dn = [], []
    for _ in range(NG):
        p0 = perm(Sx.w2, Sx.fl, rng); t = Sx.test(rng, RG, p0); fp += t['p'] <= ALPHA
        t = Sx.test(rng, RG, Sx.plant(p0, rng, q, 'POS')); pos += t['p'] <= ALPHA and t['D'] > 0; dp.append(t['D'])
        t = Sx.test(rng, RG, Sx.plant(p0, rng, q, 'NEG')); neg += t['p'] <= ALPHA and t['D'] < 0; dn.append(t['D'])
        if qh: t = Sx.test(rng, RG, Sx.plant(p0, rng, qh, 'POS')); ph += t['p'] <= ALPHA and t['D'] > 0
    return dict(q=q, FPR=int(fp), POS=int(pos), NEG=int(neg), D_pos_mean=float(np.mean(dp)), D_neg_mean=float(np.mean(dn)),
                q_half=qh, POS_half=int(ph))

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C106_results.json'
    res = dict(cycle='C106', smoke=SMOKE, seeds=dict(calibration=CSEED, gates=GSEED, test=SEED, robust=RSEED, descriptive=DSEED), next_free_seed=11708)
    L, sub = {}, {}
    for k, f in FILES:
        pr = C4.parse_runs(f)
        for c in 'AB': L[f'{k}|{c}'] = build(pr[c]); sub[f'{k}|{c}'] = S(L[f'{k}|{c}'])
    res['n'] = {s: dict(lines=len(Sx.w1), groups=len(Sx.groups), informative=int(Sx.inf.sum()), informative_frac=float(Sx.inf.mean()),
                        per_tercile={str(t): dict(lines=int((Sx.terc == t).sum()), informative=int((Sx.inf & (Sx.terc == t)).sum())) for t in range(3)},
                        gallows_initial=int(sum(l['gal'] for l in L[s])), run_first=int(sum(l['pos'] == 1 for l in L[s])),
                        run_second=int(sum(l['pos'] == 2 for l in L[s]))) for s, Sx in sub.items()}
    log('n', json.dumps(res['n']))
    degen = {s: res['n'][s]['informative_frac'] >= 0.5 for s in sub}
    rng = np.random.default_rng(CSEED); cal = {}
    for s, Sx in sub.items(): cal[s] = calibrate(Sx, rng); log('cal', s, cal[s]['q_star'], cal[s]['q_half'])
    res['calibration'] = cal
    rng = np.random.default_rng(GSEED); G = {}
    for s, Sx in sub.items():
        qs = cal[s]['q_star']
        g = gate(Sx, rng, qs if qs else QGRID[-1], cal[s]['q_half'])
        g['degeneracy_ok'] = degen[s]
        g['ok'] = bool(qs and degen[s] and g['FPR'] <= 2 and g['POS'] >= 16 and g['NEG'] >= 16 and g['D_neg_mean'] < 0 < g['D_pos_mean']); G[s] = g
        log('gate', s, g)
    res['gates'] = G
    if SMOKE:
        res['elapsed_s'] = round(time.time() - T0, 1); json.dump(res, open(outp, 'w'), indent=1, default=float); log('smoke done (no statistic computed)'); return
    rng = np.random.default_rng(SEED); H = {s: Sx.test(rng, R) for s, Sx in sub.items()}
    ph = W.holm({k: v['p'] for k, v in H.items()})
    for k in H: H[k]['p_holm'] = ph[k]
    res['H1'] = H; ver = {}
    for c in 'AB':
        ks = [f'{k}|{c}' for k, _ in FILES]
        if not all(G[k]['ok'] for k in ks): ver[c] = 'NOT TESTABLE'; continue
        rej = [k for k in ks if H[k]['p_holm'] <= ALPHA]; sg = {np.sign(H[k]['D']) for k in rej}
        ver[c] = ('DETECTED-' + ('ANTI' if sg == {-1.0} else 'COUPLED')) if len(rej) == 2 and len(sg) == 1 else 'PARTIAL' if rej else 'NOT DETECTED'
    res['verdict_H1'] = ver; log('H1', ver)
    rng = np.random.default_rng(RSEED); Rb = {}
    for s in sub:
        r1 = S(L[s], 'N2').test(rng, R)
        rest = [l for l in L[s] if l['pos'] >= 2]; r2 = S(rest).test(rng, R)
        Rb[s] = dict(R1_N2=r1, R2_no_run_first=dict(r2, lines=len(rest)))
    res['robustness'] = Rb
    rng = np.random.default_rng(DSEED); Dd = {}
    for s in sub:
        d = {}
        for name, f in (('pos1', lambda l: l['pos'] == 1), ('pos2', lambda l: l['pos'] == 2), ('pos3plus', lambda l: l['pos'] >= 3),
                         ('gallows', lambda l: l['gal']), ('non_gallows', lambda l: not l['gal'])):
            ls = [l for l in L[s] if f(l)]
            d[name] = dict(S(ls, 'N2').test(rng, 1000), lines=len(ls)) if len(ls) >= 30 else dict(lines=len(ls), note='< 30 lines')
        Dd[s] = d
    res['descriptive'] = Dd
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('done')

if __name__ == '__main__':
    main()
