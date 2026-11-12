#!/usr/bin/env python3
"""C107 (F-RHYTHM step 6): is the Currier B line-start length coupling of C106 (word 1 -> word 2, D_S +0.108 IT2a / +0.066 ZL3b,
Holm 0.002 under N1 = run x word-count tercile) carried by the lines whose word 2 is sh-initial?
Lead credited, not a blind discovery: N. Pelling, Cipher Mysteries (8 Nov 2026), 'The mysterious Word 2 sh-initial boost' (Quire 20,
Takahashi); our own C070/C073 replicated the word-2 sh boost in Q20 and Currier B outside Q20. Kryptos's C107 review (12 Nov 2026,
01:06 PT) is built in: class fixed before any D_S; C083 generator cells run under the same N1; her C200 errata linked (case file).
Class (fixed here, before any D_S): word 2 'sh-initial' = the EVA word 2 string starts with 'sh' (so 'sh' is its first glyph unit;
ckh/cth/etc. are not sh). 'other' = every other line. Currier A is not tested (C106: NOT TESTABLE).
Lines/runs: C104 parse_runs verbatim (Currier B, paragraph loci, >= 6 words), lengths in EVA glyph units (C003 units).
Word-count terciles: cut points from the WHOLE Currier B subset of that transcription (as C106), so both classes share strata.
H1 (Holm over 4 = {sh, other} x {IT2a, ZL3b}): r_S = Pearson(len w1, len w2) over the class's lines; N1c = word 2 permuted among
   lines of the same class x run x tercile; D_S = r_S - null mean; two-sided p (C104 ptest), R 2000.
   Verdict per class: DETECTED-COUPLED / -ANTI (both transcriptions Holm <= 0.05, same sign), PARTIAL (one), NOT DETECTED, NOT TESTABLE.
Gates per class x transcription (C106 machinery, amended plant): degeneracy (informative lines >= 50 %); calibration seed 11708,
   q* = smallest q in 0.05..0.60 with mean planted D >= +0.15 (10 pseudo), q_half for +0.075; no q* -> NOT TESTABLE;
   gates seed 11729, 20 fresh pseudo, RG 300: FPR <= 2/20, POS and NEG >= 16/20, broken meter mean D_NEG < 0 < mean D_POS.
   Exact false-fail rate of the 16/20 + 2/20 rules is printed (binomial at true power 0.95 and true FPR 0.05; Kryptos's rule).
Reading rule (registered): both DETECTED -> coupling GENERAL (not carried by the word-2 class); other DETECTED and sh not ->
   NOT CARRIED BY sh (with sh power at q_half quoted); sh DETECTED and other not -> CARRIED BY sh; neither -> DISSOLVED/UNDERPOWERED.
H1b (registered secondary family, own Holm over 4, own gates with the same rules, seed 11731 for its calibration+gates+tests):
   N2c = word 2 permuted within class x word-count tercile over the whole subset (keeps word count, drops runs). Disclosed before
   the run: smoke (1 pseudo per q) found no q* for the sh class under N1c, so sh is likely NOT TESTABLE under H1; H1b was added
   (before any D_S) as the weaker-control fallback. H1b verdicts and reading carry the label 'run-free null'. H1 stays primary.
Generator family (descriptive; Kryptos request): C083 cell 0 (all-default) seeds 11709-11718 and cell 33 (C083 winner) seeds
   11719-11728, 2500 lines each; lines >= 6 words, first N lines with N = the IT2a Currier B line count; pseudo-runs = consecutive
   blocks of 8 lines (B mean run length 7.7-8.3); terciles as above; D_S under N1 (R 500) for all lines and per class; plus word-2
   sh share minus mid-line (3..n-2) sh share. Call per cell: manuscript full-B D_S ABOVE (above all 10 runs) / BELOW / INSIDE.
   Manuscript full-B D_S re-computed here with rng [11730 + 10^6] (same statistic as C106).
Seeds 11708 calibration, 11709-11728 generator, 11729 gates, 11730 tests, 11731 H1b. Next free 11732.
Run: timeout 600 python tools/c107_word2_class_stratum.py analysis/C107_results.json   (SMOKE=1: sizes + gates only, no D_S)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from math import comb
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import FILES
from c003_position_rigidity import units
import c102_word_length_rhythm as W
import c104_rhythm_line_breaks as C4
import c106_start_pair as C6
import c004_generator_sweep as G
import c083_generator_grid as C83

CSEED, GSEED, SEED, RSEED = 11708, 11729, 11730, 11731
GEN = {0: list(range(11709, 11719)), 33: list(range(11719, 11729))}
R, RGEN, ALPHA, RUNLEN = 2000, 500, 0.05, 8
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE:
    R = 50; C6.RG, C6.NG, C6.NC = 20, 2, 1
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

class SC(C6.S):
    """C106 S with groups = class x run x tercile (tercile cuts given from the whole subset); key 'N2c' drops run."""
    def __init__(self, lines, terc, key='N1c'):
        self.lines = lines
        self.w1 = np.array([l['w1'] for l in lines], float); self.w2 = np.array([l['w2'] for l in lines], float)
        self.terc = np.asarray(terc)
        lab = [(l['run'], int(t)) if key == 'N1c' else int(t) for l, t in zip(lines, self.terc)]
        self.groups = C6.groups_of(lab); self.fl = C6.flat(self.groups)
        self.inf = np.zeros(len(lines), bool)
        for g in self.groups:
            if len(g) > 1: self.inf[g] = True

def build(runs):
    out = []
    for ri, r in enumerate(runs):
        for pi, ws in enumerate(r):
            out.append(dict(w1=len(units(ws[0])), w2=len(units(ws[1])), wc=len(ws), run=ri, pos=pi + 1, sh=ws[1].startswith('sh'),
                            mid_sh=sum(w.startswith('sh') for w in ws[2:-2]), mid_n=max(len(ws) - 4, 0)))
    return out

def terciles(L):
    wc = np.array([l['wc'] for l in L]); return np.digitize(wc, np.quantile(wc, [1 / 3, 2 / 3]), right=True)

def split(L, terc, key='N1c'):
    out = {}
    for cls in ('sh', 'other'):
        idx = [i for i, l in enumerate(L) if l['sh'] == (cls == 'sh')]
        out[cls] = SC([L[i] for i in idx], terc[idx], key)
    return out

def binom_tail(n, k, p): return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

def gen_job(a):
    cell, s, nlines = a
    Lg = G.generate(C83.tocfg(C83.grid()[cell]), s)
    if not Lg: return (cell, s, None)
    Lg = [l for l in Lg if len(l) >= 6][:nlines]
    runs = [Lg[i:i + RUNLEN] for i in range(0, len(Lg), RUNLEN)]
    L = build(runs); terc = terciles(L); rng = np.random.default_rng([s, cell])
    full = SC(L, terc).test(rng, RGEN); sp = split(L, terc); cl = {k: v.test(rng, RGEN) for k, v in sp.items()}
    w2sh = float(np.mean([l['sh'] for l in L])); mid = sum(l['mid_sh'] for l in L) / max(sum(l['mid_n'] for l in L), 1)
    return (cell, s, dict(lines=len(L), D_full=full['D'], D_sh=cl['sh']['D'], D_other=cl['other']['D'], n_sh=len(sp['sh'].w1),
                          w2_sh_share=w2sh, mid_sh_share=float(mid), sh_boost=w2sh - float(mid)))

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C107_results.json'
    res = dict(cycle='C107', smoke=SMOKE, seeds=dict(calibration=CSEED, generator=GEN, gates=GSEED, test=SEED, robust=RSEED), next_free_seed=11732)
    res['gate_false_fail'] = dict(POS_or_NEG_below_16_of_20_at_power_0p95=1 - binom_tail(20, 16, 0.95),
                                  FPR_above_2_of_20_at_true_0p05=binom_tail(20, 3, 0.05))
    log('gate false-fail', res['gate_false_fail'])
    L, T, sub = {}, {}, {}
    for k, f in FILES:
        L[k] = build(C4.parse_runs(f)['B']); T[k] = terciles(L[k])
        for cls, Sx in split(L[k], T[k]).items(): sub[f'{k}|{cls}'] = Sx
    res['n'] = {s: dict(lines=len(Sx.w1), groups=len(Sx.groups), informative_frac=float(Sx.inf.mean()), group_size_hist=Sx.size_hist())
                for s, Sx in sub.items()}
    res['n_B_lines'] = {k: len(v) for k, v in L.items()}
    log('n', json.dumps(res['n']))
    def family(subs, rc, rg, rt, tag):
        rng = np.random.default_rng(rc); cal, Gt = {}, {}
        for s, Sx in subs.items(): cal[s] = C6.calibrate(Sx, rng); log(tag, 'cal', s, cal[s]['q_star'], cal[s]['q_half'])
        rng = np.random.default_rng(rg) if rg != rc else rng
        for s, Sx in subs.items():
            qs = cal[s]['q_star']; g = C6.gate(Sx, rng, qs if qs else C6.QGRID[-1], cal[s]['q_half'])
            g['degeneracy_ok'] = float(Sx.inf.mean()) >= 0.5
            g['ok'] = bool(qs and g['degeneracy_ok'] and g['FPR'] <= 2 and g['POS'] >= 16 and g['NEG'] >= 16 and g['D_neg_mean'] < 0 < g['D_pos_mean'])
            Gt[s] = g; log(tag, 'gate', s, g)
        out = dict(calibration=cal, gates=Gt)
        if SMOKE: return out
        rng = np.random.default_rng(rt) if rt != rg else rng
        H = {s: Sx.test(rng, R) for s, Sx in subs.items()}
        ph = W.holm({k: v['p'] for k, v in H.items()})
        for k in H: H[k]['p_holm'] = ph[k]
        ver = {}
        for cls in ('sh', 'other'):
            ks = [f'{k}|{cls}' for k, _ in FILES]
            if not all(Gt[k]['ok'] for k in ks): ver[cls] = 'NOT TESTABLE'; continue
            rej = [k for k in ks if H[k]['p_holm'] <= ALPHA]; sg = {np.sign(H[k]['D']) for k in rej}
            ver[cls] = ('DETECTED-' + ('ANTI' if sg == {-1.0} else 'COUPLED')) if len(rej) == 2 and len(sg) == 1 else 'PARTIAL' if rej else 'NOT DETECTED'
        d = lambda v: v.startswith('DETECTED')
        ver['reading'] = ('GENERAL' if d(ver['sh']) and d(ver['other']) else 'NOT CARRIED BY sh' if d(ver['other']) and not d(ver['sh'])
                          else 'CARRIED BY sh' if d(ver['sh']) else 'DISSOLVED/UNDERPOWERED')
        out.update(tests=H, verdict=ver); log(tag, json.dumps({k: (round(v['D'], 4), v['p_holm']) for k, v in H.items()}), ver)
        return out
    res['H1'] = family(sub, CSEED, GSEED, SEED, 'H1')
    sub2 = {f'{k}|{cls}': Sx for k, _ in FILES for cls, Sx in split(L[k], T[k], 'N2c').items()}
    res['H1b_run_free'] = family(sub2, RSEED, RSEED, RSEED, 'H1b')
    if SMOKE:
        res['elapsed_s'] = round(time.time() - T0, 1); json.dump(res, open(outp, 'w'), indent=1, default=float); log('smoke done (no D_S)'); return
    rng = np.random.default_rng(SEED + 10**6)
    res['manuscript_full_B'] = {k: SC(L[k], T[k]).test(rng, R) for k, _ in FILES}
    res['manuscript_sh_boost'] = {k: dict(w2_sh_share=float(np.mean([l['sh'] for l in L[k]])),
                                          mid_sh_share=sum(l['mid_sh'] for l in L[k]) / sum(l['mid_n'] for l in L[k])) for k in L}
    nl = res['n_B_lines']['IT2a']
    with Pool(8) as p: out = p.map(gen_job, [(c, s, nl) for c, ss in GEN.items() for s in ss])
    gen = {str(c): [o for (cc, s, o) in out if cc == c and o] for c in GEN}
    res['generator'] = gen; calls = {}
    for c, runs in gen.items():
        Ds = np.array([r['D_full'] for r in runs]); calls[c] = {}
        for k in L:
            v = res['manuscript_full_B'][k]['D']
            calls[c][k] = dict(V=v, gen_min=float(Ds.min()), gen_max=float(Ds.max()), n=len(Ds),
                               call='ABOVE' if len(Ds) == 10 and v > Ds.max() else 'BELOW' if len(Ds) == 10 and v < Ds.min() else 'INSIDE' if len(Ds) == 10 else 'NOT CALLED')
    res['generator_calls'] = calls; log('gen', json.dumps(calls))
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('done')

if __name__ == '__main__':
    main()
