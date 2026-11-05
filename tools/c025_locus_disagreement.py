"""C025: within-page test of ZL 3b vs IT2a disagreement by locus type (label / circular+radial vs paragraph).
Pre-registered in case-file/C025-locus-disagreement.md. Seed 25025. Run: timeout 600 python3 tools/c025_locus_disagreement.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import re, json, random, sys
from collections import defaultdict
sys.path.insert(0, 'tools')
from c024_common import clean, lev

def typed_lines(path):
    out = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)\.(\d+),(.)(\w)\w*>\s*(.*)', line.rstrip('\n'))
        if m: out[(m.group(1), int(m.group(2)))] = (m.group(4), clean(m.group(5)))
    return out

ZL, IT = typed_lines('data/ZL3b-n.txt'), typed_lines('data/IT2a-n.txt')
GL = 'acdefhiklmnopqrstvxy'
pairs, unmatched = [], 0
for k, (t, a) in ZL.items():
    if k in IT and a and IT[k][1]: pairs.append((k[0], t, a, IT[k][1]))
    else: unmatched += 1

def corrupt(s, rate, rng):
    return ''.join(rng.choice(GL) if rng.random() < rate else c for c in s)

BASE = [lev(a, b) for _, _, a, b in pairs]   # computed once; plants only recompute the planted lines

def build(look_types, plant=0.0, rng=None):
    pages = defaultdict(list)
    for (p, t, a, b), ed in zip(pairs, BASE):
        cls = 'X' if t in look_types else ('P' if t == 'P' else None)
        if cls is None: continue
        if cls == 'X' and plant: b = corrupt(b, plant, rng); ed = lev(a, b)
        pages[p].append((cls, ed, max(len(a), len(b))))
    return [v for v in pages.values() if {'X', 'P'} <= {c for c, _, _ in v}]

def stat(pages, labels):
    num = den = 0.0
    for v, lab in zip(pages, labels):
        e = {'X': 0, 'P': 0}; g = {'X': 0, 'P': 0}
        for (c, ed, ln), l in zip(v, lab): e[l] += ed; g[l] += ln
        d = e['X'] / g['X'] - e['P'] / g['P']; num += g['X'] * d; den += g['X']
    return num / den

def test(pages, rng, nperm):
    lab = [[c for c, _, _ in v] for v in pages]
    obs = stat(pages, lab); ge = 0
    for _ in range(nperm):
        sh = [rng.sample(l, len(l)) for l in lab]
        ge += stat(pages, sh) >= obs
    return obs, (1 + ge) / (1 + nperm)

def shuffled(pages, rng):
    out = []
    for v in pages:
        lab = rng.sample([c for c, _, _ in v], len(v))
        out.append([(l, ed, ln) for l, (_, ed, ln) in zip(lab, v)])
    return out

rng = random.Random(25025); A = 0.025; res = {'unmatched_zl_lines': unmatched, 'matched_pairs': len(pairs)}
for name, types in [('L', {'L'}), ('CR', {'C', 'R'})]:
    pages = build(types)
    nx = sum(1 for v in pages for c, _, _ in v if c == 'X'); np_ = sum(1 for v in pages for c, _, _ in v if c == 'P')
    gx = sum(ln for v in pages for c, _, ln in v if c == 'X'); ex = sum(ed for v in pages for c, ed, _ in v if c == 'X')
    gp = sum(ln for v in pages for c, _, ln in v if c == 'P'); ep = sum(ed for v in pages for c, ed, _ in v if c == 'P')
    obs, p = test(pages, rng, 4000)
    fpr = sum(test(shuffled(pages, rng), rng, 400)[1] < A for _ in range(40)) / 40
    power = {}
    for pl in (0.01, 0.02, 0.04):
        power[pl] = sum(test(build(types, pl, rng), rng, 400)[1] < A for _ in range(40)) / 40
    mde = next((pl for pl in (0.01, 0.02, 0.04) if power[pl] >= 0.8), None)
    gates = fpr <= 0.075 and mde is not None
    verdict = 'NOT TESTABLE' if not gates else ('DETECTED' if p < A else 'NOT DETECTED')
    res[name] = dict(pages=len(pages), x_lines=nx, p_lines=np_, x_rate=ex / gx, p_rate=ep / gp, D=obs, p=p,
                     fpr=fpr, power=power, mde=mde, verdict=verdict)
    print(name, json.dumps(res[name]), flush=True)
json.dump(res, open('analysis/C025_results.json', 'w'), indent=1)
