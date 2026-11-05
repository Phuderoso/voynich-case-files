#!/usr/bin/env python3
"""C031 (F-LINE step 2): repair of C030's calibration. Re-lineation now cuts every original line at a random
interior word (never at an old boundary), so each new line = tail of old line i + head of old line i+1 and no new
line edge coincides with an old one. Same statistics, null, plant and alpha as C030 (imported).
Descriptive: per-unit start/end lift (observed/expected) of manuscript vs generator, Spearman correlation.
Writes analysis/C031_results.json. Usage: python3 tools/c031_line_start_repaired.py"""
import json, sys, time
import numpy as np
sys.path.insert(0, 'tools')
import c030_line_edge_glyphs as C
from c003_position_rigidity import units

SEED = 3131

def relineate_interior(lines, rng):
    """new boundary inside each old line at a random interior position 1..len-1 (old line i tail + line i+1 head)."""
    cuts = [int(rng.integers(1, len(ws))) for ws, _ in lines]
    out = []
    for i in range(len(lines)):
        a = lines[i][0][cuts[i]:]
        b = lines[i + 1][0][:cuts[i + 1]] if i + 1 < len(lines) else []
        if len(a) + len(b) >= 3: out.append((a + b, False))
    return out

def lifts(lines, which):
    codes = C.encode(lines, which); pos = -1 if which == 'end' else 0
    obs, exp = {}, {}
    for l in codes:
        e = l[pos if which == 'end' else 0]
        obs[e] = obs.get(e, 0) + 1
        for c in l: exp[c] = exp.get(c, 0) + 1 / len(l)
    return {u: (obs.get(u, 0), exp[u]) for u in exp}

def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y)); return float(np.corrcoef(rx, ry)[0, 1])

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); C.relineate = relineate_interior
    texts = {'voynich_ZL3b': C.ivtff_paragraphs('data/ZL3b-n.txt'), 'ts_generator': C.generator(),
             'voynich_IT2a': C.ivtff_paragraphs('data/IT2a-n.txt')}
    res = {}
    for name, lines in texts.items():
        r = dict(n_lines=len(lines), gates=C.gates(lines, rng))
        for which in ('end', 'start'):
            r[which] = C.test(C.encode(lines, which), which, rng)
            ok = r['gates'][which]['passed']
            r[which]['verdict'] = ('DETECTED' if r[which]['p'] < C.ALPHA else 'NOT DETECTED') if ok else 'NOT TESTABLE'
        res[name] = r
        print(name, {k: (round(r[k]['D'], 4), r[k]['p'], r[k]['verdict']) for k in ('end', 'start')}, r['gates'],
              round(time.time() - t0, 1), 's', flush=True)
    desc = {}
    for which in ('end', 'start'):
        v = lifts(texts['voynich_ZL3b'], which); g = lifts(texts['ts_generator'], which)
        common = [u for u in v if u in g and v[u][1] >= 20 and g[u][1] >= 20]
        lv = [np.log((v[u][0] + 0.5) / v[u][1]) for u in common]; lg = [np.log((g[u][0] + 0.5) / g[u][1]) for u in common]
        desc[which] = dict(units=common, log_lift_voynich=[round(x, 2) for x in lv], log_lift_generator=[round(x, 2) for x in lg],
                           spearman=round(spearman(np.array(lv), np.array(lg)), 3))
        print(which, desc[which], flush=True)
    res['descriptive_lift_comparison'] = desc
    res['_meta'] = dict(SEED=SEED, NPERM=C.NPERM, NREP=C.NREP, ALPHA=C.ALPHA, PLANT_F=C.PLANT_F, seconds=round(time.time() - t0, 1))
    json.dump(res, open('analysis/C031_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
