#!/usr/bin/env python3
"""C054 (F-REP step 3): is there a Timm-Schinner setting that sits where the manuscript sits on BOTH exact-repeat
numbers at once (C052 R0 excess X and raw R0 rate)? Fixed search space: every ok S2 config of the C004 sweep that
has method.canFollow = statistic (27 configs, chosen before any C054 number). Screen: seed 9001, first 15,000 tokens,
115-token pseudo-pages, within-page shuffle (300). Window: X in [1.20, 1.50] and raw rate in [0.80%, 1.30%].
Confirm (at most the 3 screen hits closest to (1.32, 1.0%)): held-out seeds 9002-9004, per-text FPR/plant gates
at alpha 0.05/9. Also records R1 X. Pre-registered in case-file/C054-matched-repeat-fit.md. Seed 5454.
Run: timeout 600 python3 tools/c054_matched_repeat_fit.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c052_adjacent_repetition as R
import c051_context_spelling_ab as B
import c004_generator_sweep as G

SEED, N, NSH = 5454, 15000, 300
XW, RW, TGT = (1.20, 1.50), (0.0080, 0.0130), (1.32, 0.010)
R.NSH = NSH

def space():
    rows = [json.loads(l) for l in open('analysis/C004_sweep.jsonl')]
    return [(r['tag'], r['cfg']) for r in rows if r['tag'].startswith('S2.') and r['ok'] and r['cfg'].get('method.canFollow') == 'statistic']

def pages(cfg, seed):
    c = dict(cfg); c.setdefault('text.lines_to_create', 3400)
    L = G.generate(c, seed); n = sum(map(len, L)) if L else 0
    if not L or n < N + 500: return None, n
    pl = R.as_units(B.pseudo_pages(L, 0, N + 500)); return R.take_pages(pl, 0, N), n

def inwin(X, r): return X is not None and XW[0] <= X <= XW[1] and RW[0] <= r <= RW[1]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); S = space(); scr = []
    for tag, cfg in S:
        pl, n = pages(cfg, 9001)
        if pl is None: scr.append(dict(tag=tag, cfg=cfg, n=n, ok=False)); print(tag, 'no text', n, flush=True); continue
        t = R.test(pl, rng); o = t['R0']
        scr.append(dict(tag=tag, cfg=cfg, n=n, ok=True, X=o['X'], rate=o['rate'], p=o['p'], X1=t['R1']['X'], hit=inwin(o['X'], o['rate'])))
        print(tag, n, round(o['X'], 3), round(o['rate'] * 100, 2), round(o['p'], 4), round(t['R1']['X'], 3), scr[-1]['hit'], round(time.time() - t0, 1), flush=True)
    hits = sorted([s for s in scr if s.get('hit')], key=lambda s: abs(s['X'] - TGT[0]) / TGT[0] + abs(s['rate'] - TGT[1]) / TGT[1])[:3]
    alpha = 0.05 / 9; conf = []
    for s in hits:
        for seed in (9002, 9003, 9004):
            pl, n = pages(s['cfg'], seed)
            if pl is None: conf.append(dict(tag=s['tag'], seed=seed, n=n, verdict='NO TEXT')); continue
            t = R.test(pl, rng); o = t['R0']
            f = R.test(R.shuffle_pages(pl, rng), rng)['R0']['p']; p = R.test(R.plant(pl, rng), rng)['R0']['p']
            ok = f >= alpha and p < alpha
            v = 'NOT TESTABLE' if not ok else ('IN WINDOW' if inwin(o['X'], o['rate']) and o['p'] < alpha else 'OUT')
            conf.append(dict(tag=s['tag'], seed=seed, n=n, X=o['X'], rate=o['rate'], p=o['p'], X1=t['R1']['X'], fpr_p=f, plant_p=p, verdict=v))
            print('confirm', s['tag'], seed, round(o['X'], 3), round(o['rate'] * 100, 2), round(o['p'], 4), round(t['R1']['X'], 3), f, p, v, round(time.time() - t0, 1), flush=True)
    matched = [s['tag'] for s in hits if all(c['verdict'] == 'IN WINDOW' for c in conf if c['tag'] == s['tag'])]
    nt = sum(1 for s in scr if s['ok'])
    V = ('NOT TESTABLE' if nt < 20 else 'MATCH FOUND' if matched else 'PARTIAL' if hits else 'NO MATCH')
    out = dict(seed=SEED, N=N, NSH=NSH, window=dict(X=XW, rate=RW), n_space=len(S), n_screened_ok=nt, screen=scr,
               confirm=conf, matched=matched, verdict=V, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C054_results.json', 'w'), indent=1, default=float); print(V, nt, matched, out['runtime_s'])

if __name__ == '__main__': main()
