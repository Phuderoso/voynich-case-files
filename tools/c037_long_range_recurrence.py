#!/usr/bin/env python3
"""C037 (new family F-MI, long-range word dependence): does the same Voynich word type recur at distances of
50-500 tokens more often than chance, as words do in natural texts with topics, and does the Timm-Schinner
self-citation generator reproduce the Voynich short/long-range profile?
Pre-registered in case-file/C037-long-range-recurrence.md. Seed 3737.
Run: timeout 600 python3 tools/c037_long_range_recurrence.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L
import c004_generator_sweep as G

SEED, N, NPERM, NGATE, GPERM, NJ = 3737, 16000, 1000, 40, 200, 10
SHORT, LONG = np.arange(1, 11), np.arange(50, 501)
ALPHA = 0.05 / 4
C = 'data/corpora/'

def ids(words):
    voc = {}; return np.array([voc.setdefault(w, len(voc)) for w in words], dtype=np.int32)

def p0(a):
    n = np.bincount(a).astype(float); N_ = len(a); return float((n * (n - 1)).sum() / (N_ * (N_ - 1)))

def cprof(a, ds):
    base = p0(a); return np.array([np.mean(a[:-d] == a[d:]) for d in ds]) / base - 1

def SL(a): return float(cprof(a, SHORT).mean()), float(cprof(a, LONG).mean())

def perm_p(a, rng, nperm):
    obs = SL(a)[1]; nl = np.array([SL(rng.permutation(a))[1] for _ in range(nperm)])
    return obs, float((1 + (nl >= obs).sum()) / (nperm + 1)), float(nl.mean()), float(nl.std())

def jack(a):
    ch = np.array_split(np.arange(len(a)), NJ); v = []
    for k in range(NJ):
        keep = np.concatenate([c for j, c in enumerate(ch) if j != k]); v.append(SL(a[keep]))
    v = np.array(v); m = v.mean(0); se = np.sqrt((NJ - 1) / NJ * ((v - m) ** 2).sum(0))
    return [float(x) for x in se]

def planted(a, rng):
    b = rng.permutation(a).copy(); V = b.max() + 1
    for s in range(0, len(b), 500):
        w = rng.integers(V); idx = s + rng.choice(min(500, len(b) - s), size=max(1, int(0.02 * min(500, len(b) - s))), replace=False)
        b[idx] = w
    return b

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    gens = {}
    for name, cfg in [('Generator_base', {'text.lines_to_create': 2400}),
                      ('Generator_C005matched', dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'], **{'text.lines_to_create': 2400}))]:
        raw = G.generate(cfg, 3701); gens[name] = [w for l in (raw or []) for w in l]
    corp = {'Voynich_ZL3b': [w for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt') for w in ws],
            'Voynich_IT2a': [w for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt') for w in ws], **gens,
            'Latin_Caesar': [w for l in T.gutenberg(C + 'pg218.txt') for w in l],
            'Latin_Descartes': [w for l in T.gutenberg(C + 'pg23306.txt') for w in l],
            'Italian_Dante': [w for l in T.gutenberg(C + 'pg1012.txt') for w in l],
            'Italian_Machiavelli': [w for l in T.gutenberg(C + 'pg56498.txt') for w in l],
            'Spanish_Cervantes': [w for l in T.gutenberg(C + 'pg2000.txt') for w in l],
            'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l],
            'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l]}
    R = dict(N=N, short=[1, 10], long=[50, 500], nperm=NPERM, alpha=ALPHA, seed=SEED, texts={})
    for k, ws in corp.items():
        if len(ws) < N: R['texts'][k] = dict(n=len(ws), error='too short'); print(k, 'too short', len(ws)); continue
        a = ids(ws[:N]); S, Lg = SL(a); obs, p, nm, ns = perm_p(a, rng, NPERM); se = jack(a)
        R['texts'][k] = dict(n_total=len(ws), S=S, L=Lg, p_L=p, null_mean=nm, null_sd=ns, z=(Lg - nm) / ns,
                             jack_se_S=se[0], jack_se_L=se[1], types=int(a.max() + 1))
        print(k, round(S, 3), round(Lg, 4), p, round((Lg - nm) / ns, 1), round(time.time() - t0)); sys.stdout.flush()
    z = ids(corp['Voynich_ZL3b'][:N]); fp = pw = 0
    for g in range(NGATE):
        if perm_p(rng.permutation(z), rng, GPERM)[1] <= ALPHA: fp += 1
        if perm_p(planted(z, rng), rng, GPERM)[1] <= ALPHA: pw += 1
    gate_ok = fp <= 4 and pw >= 36
    nat = [k for k in R['texts'] if not k.startswith(('Voynich', 'Generator')) and 'S' in R['texts'][k]]
    nat_pos = sum(R['texts'][k]['p_L'] <= ALPHA for k in nat)
    rngS = [min(R['texts'][k]['S'] for k in nat), max(R['texts'][k]['S'] for k in nat)]
    rngL = [min(R['texts'][k]['L'] for k in nat), max(R['texts'][k]['L'] for k in nat)]
    def pos(x, r): return 'inside' if r[0] <= x <= r[1] else ('above' if x > r[1] else 'below')
    V = {}
    for k in ['Voynich_ZL3b', 'Voynich_IT2a', 'Generator_base', 'Generator_C005matched']:
        t = R['texts'].get(k, {})
        if 'S' not in t: V[k] = 'not testable (missing)'; continue
        V[k] = dict(H1=('not testable (gates)' if not gate_ok else ('LONG-RANGE RECURRENCE' if t['p_L'] <= ALPHA else 'NO DETECTED LONG-RANGE RECURRENCE')),
                    S_vs_natural=pos(t['S'], rngS), L_vs_natural=pos(t['L'], rngL))
    zt = R['texts']['Voynich_ZL3b']
    for gk in ['Generator_base', 'Generator_C005matched']:
        g = R['texts'].get(gk, {})
        if 'S' in g:
            V[gk]['matches_ZL_within_2SE'] = {m: abs(zt[m] - g[m]) <= 2 * np.hypot(zt['jack_se_' + m], g['jack_se_' + m]) for m in ('S', 'L')}
    R.update(gates=dict(fpr=f'{fp}/{NGATE}', power=f'{pw}/{NGATE}', natural_positive=f'{nat_pos}/{len(nat)}', ok=gate_ok),
             natural_range=dict(S=rngS, L=rngL), verdicts=V, runtime_s=round(time.time() - t0))
    json.dump(R, open('analysis/C037_results.json', 'w'), indent=1, default=float); print(json.dumps(R['gates']), json.dumps(V, default=str))

if __name__ == '__main__': main()
