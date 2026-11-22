#!/usr/bin/env python3
"""C125 DESIGN PILOT (controls only, no manuscript glyph statistic): does Kryptos's difference-of-differences
DiD = D_front - D_int separate line-to-line copying from pure vocabulary drift, and does it have mean ~0 under pure drift?
D_front = M(F1) - M(F2): F1 = last line of slot s x first line of slot s+1, F2 = second-to-last line of slot s x first of s+1
          (internal boundaries 1 <= s <= nb-3, as C124 M_B).  D_int = M(I1) - M(I2) inside the blocks of the same slots:
          I1 = line 2 x line 3, I2 = line 1 x line 3 (target = last line; distance 1 vs 2, matched by position).
M(.) = sum over the C120 lags (16..256) of the plug-in MI of unit pairs (a, a+d) restricted to the line roles above.
Texts: Latin Caesar (pg218) and one more control from C121, recut into the CB ZL3b page/line template (only line lengths of the
manuscript are used, no glyph). Conditions: none, DR(0.35), DR(0.75), DR(1.0) (C124 drift plant), copy 1.0x4, copy 1.0x99 (C121 plant).
Per condition and control: NREP pseudo-texts (pseudo N-FLIP first, as C124 calibration), each tested under N-FLIP with R draws.
Seed 11860 (pilot; next free 11861).  -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import c124_mi_flip as C4
from c120_mi_distance import recut, LAGS
from c121_mi_calibrated import plant, controls
from c003_position_rigidity import units
import c123_mi_para_block as C3
SEED, R, NREP, AG = 11860, 100, 6, 0.025
_old = C4.cmask
def cmask(name, ra, rb, sa, sb, la, lb, nba):
    intl = (sa >= 1) & (sa <= nba - 3)
    if name == 'F1': return (ra == 3) & (rb == 0) & (sb == sa + 1) & intl
    if name == 'F2': return (ra == 2) & (rb == 0) & (sb == sa + 1) & intl
    if name == 'I1': return (ra == 2) & (rb == 3) & (sb == sa) & intl
    if name == 'I2': return (ra == 1) & (rb == 3) & (sb == sa) & intl
    return _old(name, ra, rb, sa, sb, la, lb, nba)
C4.cmask = cmask
CL = ('F1', 'F2', 'I1', 'I2')
def stats(S, x, o):
    geo = S.geom(o); out = {}
    for c in CL:
        ps = S.class_pairs(c, x, geo, LAGS)
        out[c] = (sum(S.mi_pairs(a, b) for a, b in ps), sum(len(a) for a, _ in ps))
    Df = out['F1'][0] - out['F2'][0]; Di = out['I1'][0] - out['I2'][0]
    return dict(Df=Df, Di=Di, DiD=Df - Di, n={c: out[c][1] for c in CL})
CONDS = [('none', None), ('DR0.35', ('dr', 0.35)), ('DR0.75', ('dr', 0.75)), ('DR1.0', ('dr', 1.0)),
         ('copy1.0x4', ('cp', (1.0, 4))), ('copy1.0x99', ('cp', (1.0, 99)))]
def job(a):
    ci, name, words, eva, k, rep, tmpl = a
    rng = np.random.default_rng([SEED, ci, k, rep]); pages, pids = tmpl
    base = recut(words, pages); ids = pids[:len(base)]; tok = units if eva else list
    ps = C4.pseudo_flip(base, rng); kind = CONDS[k][1]
    if kind and kind[0] == 'dr': ps = C4.plant_drift(ps, rng, kind[1])
    if kind and kind[0] == 'cp': ps = plant(ps, rng, *kind[1])
    S = C4.FStream(ps, ids, tok); o0 = np.arange(S.nw); ob = stats(S, S.x, o0); nl = []
    for _ in range(R):
        o = S.norder('FLIP', rng); nl.append(stats(S, S._reindex(o), o))
    res = dict(control=name, cond=CONDS[k][0], rep=rep, obs=ob)
    for key in ('Df', 'Di', 'DiD'):
        v = np.array([n[key] for n in nl]); sd = v.std(ddof=1)
        res[key] = dict(obs=ob[key], null_mean=float(v.mean()), null_sd=float(sd), E=float(ob[key] - v.mean()),
                        p=float((1 + (v >= ob[key]).sum()) / (R + 1)))
    res['n_null_mean'] = {c: float(np.mean([n['n'][c] for n in nl])) for c in CL}
    return res
if __name__ == '__main__':
    T0 = time.time(); D = C3.pages_of('data/ZL3b-n.txt', 'CB'); tmpl = C3.split_pp(D)
    AC = controls(); ctl = [c for c in AC if c[0] in ('Latin Caesar', 'Spanish Cervantes')]
    print('controls', [c[0] for c in ctl], flush=True)
    jobs = [(ci, n, w, e, k, r, tmpl) for ci, (n, w, e) in enumerate(ctl) for k in range(len(CONDS)) for r in range(NREP)]
    with Pool(min(8, os.cpu_count() or 2)) as P: out = P.map(job, jobs)
    summ = {}
    for ci, (n, _, _) in enumerate(ctl):
        for k, (cn, _) in enumerate(CONDS):
            rs = [r for r in out if r['control'] == n and r['cond'] == cn]; d = {}
            for key in ('Df', 'Di', 'DiD'):
                d[key] = dict(obs_mean=float(np.mean([r[key]['obs'] for r in rs])), obs_sd=float(np.std([r[key]['obs'] for r in rs], ddof=1)),
                              E_mean=float(np.mean([r[key]['E'] for r in rs])), reject=f"{sum(r[key]['p'] <= AG for r in rs)}/{len(rs)}")
            d['n_obs'] = rs[0]['obs']['n']; summ[f'{n} | {cn}'] = d
    json.dump(dict(seed=SEED, R=R, NREP=NREP, alpha=AG, summary=summ, jobs=out), open('analysis/C125_design_pilot.json', 'w'), indent=1)
    for k, d in summ.items():
        print(k, '| Df obs %.4f E %.4f rej %s | Di obs %.4f | DiD obs %.4f sd %.4f E %.4f rej %s | n %s' % (d['Df']['obs_mean'], d['Df']['E_mean'], d['Df']['reject'], d['Di']['obs_mean'], d['DiD']['obs_mean'], d['DiD']['obs_sd'], d['DiD']['E_mean'], d['DiD']['reject'], d['n_obs']))
    print('done %.1fs' % (time.time() - T0))
