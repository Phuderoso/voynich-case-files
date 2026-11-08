#!/usr/bin/env python3
"""C053 (F-REP step 2): does C052's exact-repeat gap (generator X(R0) 0.72-0.92 vs Voynich 1.30-1.34) hold across
Timm-Schinner generator configurations? Same 14 texts as C033: base config (seeds 9001-9003), C005 matched config
(9001-9003), first 8 ok S2 configs of the C004 sweep with seed 9001; 3,400 lines unless the config sets it.
Statistic and null as C052 (first 15,000 tokens, 115-token pseudo-pages, within-page shuffle), 300 shuffles.
Pre-registered in case-file/C053-generator-repeats-sweep.md. Seed 5353.
Run: timeout 600 python3 tools/c053_generator_repeats_sweep.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c052_adjacent_repetition as R
import c051_context_spelling_ab as B
import c004_generator_sweep as G
from c033_generator_line_starts import configs

SEED, N, NSH, VMIN = 5353, 15000, 300, 1.30
R.NSH = NSH

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); cf = configs(); alpha = 0.05 / len(cf); res = []
    for name, cfg, seed in cf:
        c = dict(cfg); c.setdefault('text.lines_to_create', 3400)
        L = G.generate(c, seed); n = sum(map(len, L)) if L else 0
        if not L or n < 10000: res.append(dict(name=name, seed=seed, cfg=cfg, n=n, verdict='NO TEXT')); print(name, seed, 'no text', n, flush=True); continue
        pl = R.as_units(B.pseudo_pages(L, 0, N + 500)); pl = R.take_pages(pl, 0, N)
        o = R.test(pl, rng)['R0']; f = R.test(R.shuffle_pages(pl, rng), rng)['R0']; p = R.test(R.plant(pl, rng), rng)['R0']
        ok = f['p'] >= alpha and p['p'] < alpha
        reach = o['X'] is not None and o['X'] >= VMIN and o['p'] < alpha
        res.append(dict(name=name, seed=seed, cfg=cfg, n=n, R0=o, fpr_p=f['p'], plant_p=p['p'], gate_ok=ok,
                        verdict='NOT TESTABLE' if not ok else ('REACHES' if reach else 'SHORT')))
        print(name, seed, n, o['obs'], round(o['exp'], 1), round(o['X'], 3), round(o['rate'] * 100, 2), round(o['p'], 4), f['p'], p['p'], res[-1]['verdict'], round(time.time() - t0, 1), flush=True)
    t = [r for r in res if r['verdict'] in ('REACHES', 'SHORT')]
    V = 'NOT TESTABLE' if len(t) < 10 else ('GAP CLOSED' if any(r['verdict'] == 'REACHES' for r in t) else 'GAP HOLDS')
    out = dict(seed=SEED, N=N, NSH=NSH, alpha=alpha, vmin=VMIN, texts=res, verdict=V, testable=len(t), runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C053_results.json', 'w'), indent=1, default=float); print(V, len(t), out['runtime_s'])

if __name__ == '__main__': main()
