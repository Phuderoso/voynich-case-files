#!/usr/bin/env python3
"""C032 (F-LINE step 3): two-part calibration for line-edge tests.
(a) size/power on texts with no line structure (all words shuffled across the text, recut with the original line lengths);
(b) leakage bound L = max D over 40 offset re-lineated (C030) + 40 interior re-lineated (C031) texts; require D > 3 L.
Plus a targeted test: are generator line starts enriched in the manuscript's s-/y-/d- start units?
Writes analysis/C032_results.json. Usage: python3 tools/c032_line_edges_two_part.py"""
import json, sys, time
import numpy as np
sys.path.insert(0, 'tools')
import c030_line_edge_glyphs as C
from c031_line_start_repaired import relineate_interior
from c003_position_rigidity import units

SEED, FACTOR, TARGET = 3232, 3.0, ('s', 'y', 'd')

def shuffled_lines(lines, rng):
    stream = [w for ws, _ in lines for w in ws]; rng.shuffle(stream); out, i = [], 0
    for ws, _ in lines:
        out.append((stream[i:i + len(ws)], False)); i += len(ws)
    return out

def d_only(lines, which, rng):
    return C.test(C.encode(lines, which), which, rng, 1)['D']

def target_test(lines, rng, nperm=1000):
    """count of line-initial words (paragraph-first lines excluded) whose first unit is in TARGET; within-line null."""
    keep = [ws for ws, pf in lines if not pf]
    hit = [np.array([units(w)[0] in TARGET for w in ws]) for ws in keep]
    lens = np.array([len(h) for h in hit]); flat = np.concatenate(hit); off = np.concatenate([[0], np.cumsum(lens)[:-1]])
    obs = int(flat[off].sum()); null = np.array([flat[off + (rng.random(len(lens)) * lens).astype(int)].sum() for _ in range(nperm)])
    exp = float(sum(h.mean() for h in hit))
    return dict(observed=obs, expected=round(exp, 1), null_mean=float(null.mean()), p=float((1 + np.sum(null >= obs)) / (nperm + 1)))

def plant_target(lines, f, rng):
    out = []
    for ws, pf in lines:
        ws = list(ws)
        if rng.random() < f:
            cand = [j for j, w in enumerate(ws) if units(w)[0] in TARGET]
            if cand: w = ws.pop(int(rng.choice(cand))); ws = [w] + ws
        out.append((ws, pf))
    return out

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); res = {}
    texts = {'voynich_ZL3b': C.ivtff_paragraphs('data/ZL3b-n.txt'), 'ts_generator': C.generator(),
             'voynich_IT2a': C.ivtff_paragraphs('data/IT2a-n.txt')}
    for name, lines in texts.items():
        r = {}
        for which in ('end', 'start'):
            tgt = C.third_unit(lines, which); fp = pw = 0
            for _ in range(C.NREP):
                sl = shuffled_lines(lines, rng)
                fp += C.test(C.encode(sl, which), which, rng, 200)['p'] < C.ALPHA
                pw += C.test(C.encode(C.plant(sl, which, tgt, C.PLANT_F, rng), which), which, rng, 200)['p'] < C.ALPHA
            leak = [d_only(C.relineate(lines, rng), which, rng) for _ in range(C.NREP)] + \
                   [d_only(relineate_interior(lines, rng), which, rng) for _ in range(C.NREP)]
            t = C.test(C.encode(lines, which), which, rng)
            L = max(leak); ok = fp <= 4 and pw >= 32
            verdict = 'NOT TESTABLE' if not ok else ('DETECTED' if t['p'] < C.ALPHA and t['D'] > FACTOR * L else 'NOT DETECTED')
            r[which] = dict(D=t['D'], p=t['p'], z=t['z'], fpr=fp / C.NREP, power=pw / C.NREP, plant_unit=tgt,
                            leak_max=L, leak_offset_max=max(leak[:C.NREP]), leak_interior_max=max(leak[C.NREP:]),
                            ratio_to_leak=t['D'] / L, verdict=verdict)
            print(name, which, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r[which].items()},
                  round(time.time() - t0, 1), 's', flush=True)
        res[name] = r
    # targeted generator test
    g = texts['ts_generator']; fp = pw = 0
    for _ in range(C.NREP):
        sl = shuffled_lines(g, rng)
        fp += target_test(sl, rng, 200)['p'] < 0.05
        pw += target_test(plant_target(sl, C.PLANT_F, rng), rng, 200)['p'] < 0.05
    tt = target_test(g, rng); ok = fp <= 4 and pw >= 32
    tt.update(fpr=fp / C.NREP, power=pw / C.NREP,
              verdict='NOT TESTABLE' if not ok else ('ENRICHED' if tt['p'] < 0.05 else 'NOT ENRICHED'))
    res['generator_syd_start'] = tt
    res['manuscript_syd_start_descriptive'] = target_test(texts['voynich_ZL3b'], rng)
    print('gen syd', tt, 'voy syd', res['manuscript_syd_start_descriptive'], flush=True)
    res['_meta'] = dict(SEED=SEED, FACTOR=FACTOR, TARGET=TARGET, NPERM=C.NPERM, NREP=C.NREP, ALPHA=C.ALPHA,
                        PLANT_F=C.PLANT_F, seconds=round(time.time() - t0, 1))
    json.dump(res, open('analysis/C032_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
