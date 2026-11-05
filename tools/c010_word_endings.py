#!/usr/bin/env python3
"""C010: word-final glyph distribution (JSD to whole manuscript) as a fifth match statistic over all Voynich-like
generator configurations from C004/C005, with planted control and held-out confirmation (seeds 8001-8010).
Usage: python3 tools/c010_word_endings.py   (resumable cache analysis/C010_screen.jsonl)"""
import os, sys, json, random, math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5

NW = 6000; CACHE = 'analysis/C010_screen.jsonl'

def ends(words):
    c = Counter(c3.units(w)[-1] for w in words); n = sum(c.values()); return {k: v / n for k, v in c.items()}

def jsd(p, q):
    ks = set(p) | set(q); m = {k: (p.get(k, 0) + q.get(k, 0)) / 2 for k in ks}
    kl = lambda a: sum(a[k] * math.log2(a[k] / m[k]) for k in a if a[k] > 0)
    return 0.5 * kl(p) + 0.5 * kl(q)

def full(words, VE):
    st = c4.stats(words); st['D'] = jsd(ends(words), VE)
    e = ends(words); st['H_end'] = -sum(v * math.log2(v) for v in e.values()); return st

def run(cfg, seed, VE):
    L = c4.generate(c5.tocfg(cfg) if 'text.initial_line' in cfg and cfg['text.initial_line'] in c5.LINES else cfg, seed)
    if not L: return None
    w = c4.flat(L)[:NW]; return full(w, VE) if len(w) == NW else None

if __name__ == '__main__':
    c5.REF = c5.ref(); R = c5.REF
    V = c4.flat(c3.voynich()); VE = ends(V); rng = random.Random(10)
    samp = [V[s:s + NW] for s in (rng.randrange(len(V) - NW) for _ in range(40))]
    Ds = [jsd(ends(s), VE) for s in samp]; bar = float(np.percentile(Ds, 99))
    def plant(s):
        out = []
        for w in s:
            u = c3.units(w)
            out.append(''.join(u[:-1]) + 'm' if u[-1] == 'n' and rng.random() < 0.5 else w)
        return out
    Dp = [jsd(ends(plant(s)), VE) for s in samp]; plant_fail = float(np.mean([d > bar for d in Dp]))
    ok4 = lambda s: s and all(abs(s[k] - R[k]) <= 0.15 * R[k] for k in ('mwl', 'ttr', 'h2', 'R'))
    cand = {}
    for l in open('analysis/C004_sweep.jsonl'):
        r = json.loads(l)
        if r.get('ok') and ok4(r): cand.setdefault(json.dumps(r['cfg'], sort_keys=True), r['seed'])
    for l in open('analysis/C005_search.jsonl'):
        r = json.loads(l)
        if ok4(r['st']): cand.setdefault(json.dumps(r['cfg'], sort_keys=True), r['seed'])
    done = {}
    if os.path.exists(CACHE):
        for l in open(CACHE): r = json.loads(l); done[r['key']] = r
    todo = [(k, s) for k, s in cand.items() if k not in done]
    def job(ks):
        k, s = ks; return dict(key=k, seed=s, st=run(json.loads(k), s, VE))
    with ThreadPoolExecutor(10) as ex, open(CACHE, 'a') as f:
        for r in ex.map(job, todo): f.write(json.dumps(r) + '\n'); f.flush(); done[r['key']] = r
    scr = [r for r in done.values() if r['key'] in cand and r['st']]
    passing = sorted([r for r in scr if ok4(r['st']) and r['st']['D'] <= bar], key=lambda r: r['st']['D'])
    sel = json.load(open('analysis/C005_confirm.json'))['A']['selected']
    known = run(sel, 6001, VE)
    conf = []
    for r in passing[:3]:
        reps = [x for x in (run(json.loads(r['key']), s, VE) for s in range(8001, 8011)) if x]
        m = {k: float(np.mean([x[k] for x in reps])) for k in reps[0]}
        conf.append(dict(cfg=json.loads(r['key']), means=m, n=len(reps), matches=ok4(m) and m['D'] <= bar))
    verdict = ('not testable' if plant_fail < 0.95 else
               'some configuration matches all five' if any(c['matches'] for c in conf) else 'no screened configuration matches')
    Dall = sorted(r['st']['D'] for r in scr)
    out = dict(bar=bar, voynich_D=dict(median=float(np.median(Ds)), max=float(max(Ds))),
               planted_fail_rate=plant_fail, planted_D_median=float(np.median(Dp)),
               n_candidates=len(cand), n_screened=len(scr), n_still_4stat=sum(ok4(r['st']) for r in scr),
               n_pass_screen=len(passing), screen_D=dict(min=Dall[0], median=Dall[len(Dall) // 2]),
               screen_H_end=dict(min=min(r['st']['H_end'] for r in scr), max=max(r['st']['H_end'] for r in scr)),
               voynich_H_end=-sum(v * math.log2(v) for v in VE.values()),
               best5=[dict(D=r['st']['D'], H_end=r['st']['H_end'], cfg=json.loads(r['key'])) for r in sorted(scr, key=lambda r: r['st']['D'])[:5]],
               known_negative_C005=known, confirmation=conf, verdict=verdict)
    json.dump(out, open('analysis/C010_results.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'best5'}, indent=1)[:3000])
    for b in out['best5']: print(round(b['D'], 4), round(b['H_end'], 3), b['cfg'].get('text.initial_line'), b['cfg'].get('method.morph.use_word_final_substitutions'))
