#!/usr/bin/env python3
"""After freezing: compare my bsk230 outputs with data/cycle230/R/* (set of 'S' lines and T lines), then her null-equivalent arithmetic."""
import re, glob, os
R = 'kryptos-main/data/cycle230/R/'; O = 'out/'
def load(p):
    S, T = set(), None
    for l in open(p):
        if l.startswith('S '): S.add(l.strip())
        elif l.startswith('T '): T = l.strip()
    return S, T
bad = 0; tot = 0; rows = []
for scope in ('direct', 'bank', 'all'):
    for name in ['k4'] + [f'null{i}' for i in range(10)]:
        a, ta = load(f'{O}{name}_{scope}.txt'); b, tb = load(f'{R}{name}_{scope}.txt'); tot += 1
        same = (a == b and ta == tb)
        if not same: bad += 1; print('DIFF', scope, name, len(a), len(b), ta, tb, sorted(a ^ b)[:3])
print(f'{tot} files compared (K4 + 10 nulls x 3 scopes): {tot - bad} identical S-line sets and T lines, {bad} differ')
print('her extra files in R/:', sorted(os.path.basename(p) for p in glob.glob(R + '*') if not re.match(r'.*/(k4|null\d)_(direct|bank|all)\.txt$', p)))
