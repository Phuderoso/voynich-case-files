#!/usr/bin/env python3
"""K085 post-hoc diagnostic (declared post hoc, no decision attached): which KFG pair sets the stage-1 null-max floor
(73.71 in >= half of the null corpora), and is its W shuffle-invariant? Reuses the K085 tool's objects by import-free
re-execution of its loader (its output path redirected to /tmp so it never overwrites analysis/k085_results.json). Seed 6465."""
import runpy, sys, numpy as np
sys.argv = ['k085', 'data/khipu.db', '--loader-only']
src = open('tools/k085_kfg_k020_two_stage.py').read().split('# ---------------- KFG stage 1 ----------------')[0]
src = src.replace("if '--a0-only' in sys.argv", "if False")
src = src.replace("OUT = 'analysis/k085_a0.json' if False else 'analysis/k085_results.json'", "OUT = '/tmp/k085_posthoc_scratch.json'")
g = {'__file__': 'tools/k085_kfg_k020_two_stage.py'}; exec(compile(src, 'k085', 'exec'), g)
P = g['Pipe'](g['kkh'], g['kgr']); rng = np.random.default_rng(6465); cnt = {}
for r in range(20):
    W = P.allW(P.nullc(rng)); p = int(W.argmax()); key = (P.ids[P.AI[p]], P.ids[P.BI[p]], round(float(W[p]), 2)); cnt[key] = cnt.get(key, 0) + 1
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    a, b = k[0], k[1]; print(k, v, 'leaders A', P.LD[a][:20], len(P.LD[a]), 'B', P.LD[b][:20], len(P.LD[b]), g['meta'].get(a), g['meta'].get(b))
