#!/usr/bin/env python3
"""C057 design step (F-BURST step 3a): choose a planted-clumping strength with enough power under C056's block
(within-section) null, on its OWN design seed (5757), before any C057 test number. The plant is C055's (PT=20% of
eligible types, PC=10% of chunks as hot spots), varying PM = share of a chosen type's tokens moved into hot chunks.
For each PM: 40 replicates on natural halves (same text rotation and ZL block lengths as C056), p<0.05 counted,
and the planted D_blk recorded so the plant can be compared with the size of the Voynich effect (C056 D_blk 0.16-0.21).
Rule fixed in the C057 case file: smallest PM with design power >= 36/40 (90%) whose median planted D_blk is <= 0.16.
Run: timeout 600 python3 tools/c057_plant_design.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c055_burstiness as C
import c056_burstiness_within_section as W
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang

SEED, NG, ALPHA, PMS = 5757, 40, 0.05, [0.30, 0.40, 0.50, 0.60, 0.80]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = C.B.nat_texts()
    natt = {k: C.flat(v) for k, v in nat.items()}; names = list(nat)
    pl, _, sect = ivtff_pages_lang('data/ZL3b-n.txt'); lab = [sect[p] for p, l in pl for w in l]
    L = [W.runs(lab[h * W.NHALF:(h + 1) * W.NHALF]) for h in (0, 1)]
    R = dict(seed=SEED, NG=NG, PT=C.PT, PC=C.PC, PMs=PMS, rows=[])
    for pm in PMS:
        C.PM = pm; hits = 0; ds = []
        for i in range(NG):
            b = natt[names[(i + 4) % len(names)]][:W.NHALF]; r = W.test(C.plant(b, rng), L[i % 2], rng)
            hits += r.get('p_blk', 1) < ALPHA; ds.append(r.get('D_blk', float('nan')))
        row = dict(PM=pm, power=f'{hits}/{NG}', hits=hits, D_blk_median=float(np.nanmedian(ds)),
                   D_blk_q10=float(np.nanpercentile(ds, 10)), D_blk_q90=float(np.nanpercentile(ds, 90)))
        R['rows'].append(row); print(row, round(time.time() - t0, 1), flush=True)
    ok = [r for r in R['rows'] if r['hits'] >= 36 and r['D_blk_median'] <= 0.16]
    R['chosen_PM'] = ok[0]['PM'] if ok else None; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C057_design.json', 'w'), indent=1); print('chosen', R['chosen_PM'], R['runtime_s'])

if __name__ == '__main__': main()
