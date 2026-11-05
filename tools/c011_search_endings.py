#!/usr/bin/env python3
"""C011: coordinate descent of the Timm-Schinner generator on C010's word-ending divergence D under the four C005
constraints; held-out confirmation on seeds 8001-8010. Cache analysis/C011_cache.jsonl (resumable).
Usage: python3 tools/c011_search_endings.py"""
import os, sys, json, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5, c010_word_endings as c10

CACHE = 'analysis/C011_cache.jsonl'; SEEDS = (9001, 9002); CAP = 360; BAR = 0.028117592375112674
MEMO = {}
if os.path.exists(CACHE):
    for l in open(CACHE): r = json.loads(l); MEMO[r['k']] = r['st']
POOL = ThreadPoolExecutor(10); F = open(CACHE, 'a')

def evals(cfgs, seeds, VE):
    jobs = [(c, s) for c in cfgs for s in seeds]
    keys = [json.dumps([c, s], sort_keys=True) for c, s in jobs]
    new = [(k, j) for k, j in zip(keys, jobs) if k not in MEMO]
    for (k, _), st in zip(new, POOL.map(lambda j: c10.run(j[1][0], j[1][1], VE), new)):
        MEMO[k] = st; F.write(json.dumps(dict(k=k, st=st)) + '\n'); F.flush()
    out = []
    for c in cfgs:
        sts = [MEMO[json.dumps([c, s], sort_keys=True)] for s in seeds]
        sts = [x for x in sts if x]
        out.append({k: float(np.mean([x[k] for x in sts])) for k in sts[0]} if len(sts) == len(seeds) else None)
    return out

if __name__ == '__main__':
    c5.REF = c5.ref(); R = c5.REF
    VE = c10.ends(c4.flat(c3.voynich()))
    ok4 = lambda s: s and all(abs(s[k] - R[k]) <= 0.15 * R[k] for k in ('mwl', 'ttr', 'h2', 'R'))
    starts = [b['cfg'] for b in json.load(open('analysis/C010_results.json'))['best5'][:3]]
    t0 = time.time(); traj = []; finals = []; capped = False
    for si, cur in enumerate(starts):
        cur = dict(cur); best = evals([cur], SEEDS, VE)[0]; d0 = best['D']; hist = [d0]
        improved = True
        while improved and not capped:
            improved = False
            for p, vals in c5.SPACE.items():
                if time.time() - t0 > CAP * (si + 1) / len(starts): capped = True; break
                cands = [dict(cur, **{p: v}) for v in vals if cur.get(p) != v]
                for c, st in zip(cands, evals(cands, SEEDS, VE)):
                    if ok4(st) and st['D'] < best['D']: cur, best, improved = c, st, True
                hist.append(best['D'])
        finals.append(dict(start=si, D_start=d0, D_final=best['D'], search_stats=best, cfg=cur, history=hist))
        print('start', si, 'D', round(d0, 4), '->', round(best['D'], 4), 'capped', capped, flush=True)
        capped = False
    conf = []
    for f in finals:
        reps = evals([f['cfg']], range(8001, 8011), VE)[0]
        conf.append(dict(start=f['start'], means=reps, matches=bool(ok4(reps) and reps['D'] <= BAR)))
    effective = any(f['D_final'] < f['D_start'] for f in finals)
    verdict = ('not testable by this search' if not effective else
               'the generator can match all five statistics' if any(c['matches'] for c in conf) else
               'no configuration found by this search (not excluded)')
    out = dict(bar=BAR, search_seeds=SEEDS, confirm_seeds=[8001, 8010], time_s=time.time() - t0,
               runs_cached=len(MEMO), finals=finals, confirmation=conf, effective=effective, verdict=verdict)
    json.dump(out, open('analysis/C011_results.json', 'w'), indent=1)
    for c in conf: print(c)
    print(verdict)
