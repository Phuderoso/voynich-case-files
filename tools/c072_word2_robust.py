#!/usr/bin/env python3
"""C072 (F-LINE step 6): robustness of the C070 word-2 sh-initial boost (Pelling 2026-11-08; REPLICATED in C070).
Same lines, statistic D, within-line permutation null (positions 2..n-2 permuted, word 1 and last two fixed, R = 4000) and
gates (FPR <= 2/20; plant q 0.10 swap power >= 16/20) as tools/c070_word2_sh.py, applied to strata:
 W1short = word 1 has <= 3 glyph units; W1long = >= 4 units; W1y = word 1 ends in 'y'; W1noty = does not;
 H1, H2, H3 = Fagin Davis scribe ($H) 1, 2, 3 (the only hands with >= 700 usable lines).
Tests: 7 strata x {IT2a, ZL} = 14, Holm alpha 0.05. Verdict per stratum: HOLDS (both reject), PARTIAL, NOT DETECTED, NOT TESTABLE.
Overall ROBUST if every testable stratum HOLDS.
Generator sweep (pre-registered criterion, no p): C004 one-at-a-time settings S1 (18 settings x 3 fresh seeds 10501-10554,
setting i uses seeds 10501+3i..10503+3i) and 30 C004 random configs S2[0:30] x 1 seed (10601-10630); 1,500 lines, lines >= 5
words. GAP-ROBUST if no S1 setting mean D and no S2 run D reaches half the manuscript's Currier-B D (IT2a, C070: 0.0976 -> 0.0488);
otherwise REACHED-BY (settings listed). Also reported: max D overall.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c070_word2_sh as W
import c003_position_rigidity as T3
import c004_generator_sweep as G4
from c004_generator_sweep import generate

SEED, ALPHA, HALF = 7272, 0.05, 0.0976 / 2
STRATA = ('W1short', 'W1long', 'W1y', 'W1noty', 'H1', 'H2', 'H3')

def hands(path):
    meta = {}
    for raw in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))).get('H')
    return meta

def stratum(lines, s, H):
    if s == 'W1short': return [l for l in lines if len(T3.units(l['words'][0])) <= 3]
    if s == 'W1long': return [l for l in lines if len(T3.units(l['words'][0])) >= 4]
    if s == 'W1y': return [l for l in lines if l['words'][0].endswith('y')]
    if s == 'W1noty': return [l for l in lines if not l['words'][0].endswith('y')]
    return [l for l in lines if H.get(l['page']) == s[1]]

def test_job(a):
    k, s = a; f = dict(W.FILES)[k]; lines = stratum(W.parse(f), s, hands(f)); F = W.flags(lines)
    d, p = W.perm_test(F, np.random.default_rng(SEED + STRATA.index(s)))
    fp, pw = W.gate(F, SEED + 10 * STRATA.index(s) + (0 if k == 'IT2a' else 5))
    return k, s, dict(n_lines=len(F), D=d, p=p, fpr=fp, power=pw, gate=fp <= 2 and pw >= 16,
                      share2=sum(int(x[1]) for x in F) / len(F), share_mid=sum(int(x[2:-2].sum()) for x in F) / sum(len(x) - 4 for x in F))

def gen_job(a):
    tag, cfg, s = a; c = dict(cfg); c['text.lines_to_create'] = 1500
    Lg = generate(c, s)
    if not Lg: return tag, s, None
    F = W.flags([dict(words=l) for l in Lg if len(l) >= 5])
    return tag, s, (W.stat(F) if len(F) >= 1000 else None)

def main():
    t0 = time.time()
    S2 = G4.s2_configs()[:30]
    jobs = [(f'S1_{i}', c, 10501 + 3 * i + j) for i, c in enumerate(G4.S1) for j in range(3)] + [(f'S2_{i}', c, 10601 + i) for i, c in enumerate(S2)]
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, jobs, chunksize=1)
        T = {f'{k}_{s}': r for k, s, r in pool.map(test_job, [(k, s) for k, _ in W.FILES for s in STRATA], chunksize=1)}
        print('tests', json.dumps(T), flush=True)
        GR = gj.get()
    names = [t for t in T if T[t]['gate']]; ps = [T[t]['p'] for t in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for s in STRATA:
        if not all(T[f'{k}_{s}']['gate'] for k, _ in W.FILES): ver[s] = 'NOT TESTABLE'; continue
        m = sum(rej.get(f'{k}_{s}', False) for k, _ in W.FILES); ver[s] = 'HOLDS' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    testable = [v for v in ver.values() if v != 'NOT TESTABLE']
    ver['overall'] = 'ROBUST' if testable and all(v == 'HOLDS' for v in testable) else 'NOT ROBUST'
    gen = {}
    for tag, s, d in GR: gen.setdefault(tag, []).append(d)
    labels = {f'S1_{i}': c for i, c in enumerate(G4.S1)}; labels.update({f'S2_{i}': c for i, c in enumerate(S2)})
    summ = {t: dict(cfg=labels[t], D=[x for x in v if x is not None], mean=(float(np.mean([x for x in v if x is not None])) if any(x is not None for x in v) else None)) for t, v in gen.items()}
    reached = [t for t, v in summ.items() if v['mean'] is not None and v['mean'] >= HALF]
    allD = [x for v in summ.values() for x in v['D']]
    gv = dict(verdict='GAP-ROBUST' if not reached else 'REACHED-BY', reached=reached, max_D=max(allD), n_runs=len(allD),
              top5=sorted(((v['mean'], t) for t, v in summ.items() if v['mean'] is not None), reverse=True)[:5])
    out = dict(seed=SEED, tests=T, holm=rej, verdict=ver, generator=gv, generator_runs=summ, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C072_results.json', 'w'), indent=1, default=str)
    for k in ('holm', 'verdict', 'runtime_s'): print(k, json.dumps(out[k]))
    print('generator', json.dumps(gv, default=str))

if __name__ == '__main__':
    main()
