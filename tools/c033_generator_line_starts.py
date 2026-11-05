#!/usr/bin/env python3
"""C033 (F-LINE step 4): does C032's generator line-start gap (no s-/y-/d- enrichment) hold across Timm-Schinner
generator configurations? 14 texts: base config (seeds 9001-9003), C005 matched config (9001-9003), first 8 random
configs of the C004 sweep (S2.*, ok) with seed 9001. Same target test, null and gates as C032 Look 2.
Writes analysis/C033_results.json. Usage: python3 tools/c033_generator_line_starts.py (needs the jar, see C004)."""
import json, sys, time
import numpy as np
sys.path.insert(0, 'tools')
import c004_generator_sweep as G
import c032_line_edges_two_part as K

SEED, NREP = 3333, 40

def configs():
    rows = [json.loads(l) for l in open('analysis/C004_sweep.jsonl')]
    s2 = [r['cfg'] for r in rows if r['tag'].startswith('S2.') and r['ok']][:8]
    matched = json.load(open('analysis/C005_confirm.json'))['A']['selected']
    out = [('base', {}, s) for s in (9001, 9002, 9003)] + [('C005_matched', matched, s) for s in (9001, 9002, 9003)]
    out += [(f'S2_{i}', c, 9001) for i, c in enumerate(s2)]
    return out

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); res = []; cf = configs(); alpha = 0.05 / len(cf)
    for name, cfg, seed in cf:
        raw = G.generate(cfg, seed)
        if not raw: res.append(dict(name=name, seed=seed, cfg=cfg, error='generation failed')); continue
        lines = [(ws, False) for ws in raw if len(ws) >= 3]
        fp = pw = 0
        for _ in range(NREP):
            sl = K.shuffled_lines(lines, rng)
            fp += K.target_test(sl, rng, 500)['p'] < alpha
            pw += K.target_test(K.plant_target(sl, 0.15, rng), rng, 500)['p'] < alpha
        t = K.target_test(lines, rng); ok = fp <= 4 and pw >= 32
        t.update(name=name, seed=seed, cfg=cfg, n_lines=len(lines), ratio=t['observed'] / t['expected'],
                 fpr=fp / NREP, power=pw / NREP,
                 verdict='NOT TESTABLE' if not ok else ('ENRICHED' if t['p'] < alpha else 'NOT ENRICHED'))
        res.append(t)
        print(name, seed, t['n_lines'], t['observed'], t['expected'], round(t['ratio'], 2), round(t['p'], 4),
              t['fpr'], t['power'], t['verdict'], round(time.time() - t0, 1), 's', flush=True)
    json.dump(dict(texts=res, alpha=alpha, SEED=SEED, NREP=NREP, seconds=round(time.time() - t0, 1)),
              open('analysis/C033_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
