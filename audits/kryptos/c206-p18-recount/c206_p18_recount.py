#!/usr/bin/env python3
"""Independent recount of kryptos-case-files case file 206 (cycle 220), null cells.
Inputs: ONLY data/cycle220/SHA256SUMS and data/cycle220/results_null*.txt.
Rule (read from the files themselves): every hit is one 'H' line; field 8 (1-based,
'H' = field 1) is the period p. Cell (seed, p) = number of H lines with that p.
Cross-check: the header line '# per p strict/one-error: pK=s/e' must equal the H-line
count for every p (strict + one-error; strict is 0 everywhere here).
Writes counts.json (frozen before any comparison) and breakdown_null209249_p18.json."""
import hashlib, json, re, sys, os, glob, itertools
from collections import Counter, defaultdict
D = sys.argv[1]
out = sys.argv[2]
sums = {}
for ln in open(os.path.join(D, 'SHA256SUMS')):
    h, f = ln.split(None, 1); sums[f.strip().lstrip('./')] = h
ver = {}
files = sorted(glob.glob(os.path.join(D, 'results_null*.txt')))
for f in files:
    b = os.path.basename(f)
    h = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    ver[b] = {'sha256': h, 'listed': sums.get(b), 'ok': h == sums.get(b)}
assert all(v['ok'] for v in ver.values()), ver
cells = {}; per_p = {}; hdr_ok = {}; dup = {}; breakdown = None
for f in files:
    b = os.path.basename(f); seed = int(re.search(r'null(\d+)', b).group(1))
    lines = open(f).read().splitlines()
    hdr = [l for l in lines if l.startswith('# per p')][0]
    H = [l.split() for l in lines if l.startswith('H ')]
    other = [l for l in lines if l and not l.startswith('#') and not l.startswith('H ')]
    assert not other, other
    assert all(len(x) == 11 for x in H)
    cnt = Counter(int(x[7]) for x in H)
    hp = {int(k): (int(s), int(e)) for k, s, e in re.findall(r'p(\d+)=(\d+)/(\d+)', hdr)}
    hdr_ok[seed] = all(hp[p][0] + hp[p][1] == cnt.get(p, 0) for p in hp) and set(cnt) <= set(hp)
    dup[seed] = len(H) - len(set(map(tuple, H)))
    cells[seed] = cnt.get(18, 0)
    per_p[seed] = {p: cnt[p] for p in sorted(cnt)}
    if seed == 209249:
        rows = [(i + 1 + sum(1 for l in lines[:0])) for i in range(0)]
        p18 = [(n + 1, l.split()) for n, l in enumerate(lines) if l.startswith('H ') and l.split()[7] == '18']
        cfg = Counter(tuple(x[2:7]) for _, x in p18)
        pi0 = Counter(x[10].split(',')[0] for _, x in p18)
        tail = Counter(tuple(x[8:10]) for _, x in p18)
        # families: orders (same config) linked when they differ by a permutation of <=3 positions
        fam = []
        bycfg = defaultdict(list)
        for n, x in p18: bycfg[tuple(x[2:7])].append((n, tuple(map(int, x[10].split(',')))))
        for c, items in bycfg.items():
            par = list(range(len(items)))
            def fd(i):
                while par[i] != i: par[i] = par[par[i]]; i = par[i]
                return i
            for i, j in itertools.combinations(range(len(items)), 2):
                if sum(a != b for a, b in zip(items[i][1], items[j][1])) <= 3: par[fd(i)] = fd(j)
            g = defaultdict(list)
            for i in range(len(items)): g[fd(i)].append(items[i])
            for mem in g.values():
                orders = [o for _, o in mem]
                fixed = [k for k in range(11) if len({o[k] for o in orders}) == 1]
                mov = [k for k in range(11) if k not in fixed]
                fam.append({'config_fields_3_7': list(c), 'n': len(mem), 'file_lines': [n for n, _ in mem],
                            'fixed_positions': {k: orders[0][k] for k in fixed},
                            'moving_positions': mov,
                            'moving_values': sorted({o[k] for o in orders for k in mov})})
        fam.sort(key=lambda d: (d['config_fields_3_7'], d['file_lines'][0]))
        breakdown = {'n_p18': len(p18), 'file_lines': [n for n, _ in p18],
                     'by_config_fields_3_7': {' '.join(k): v for k, v in sorted(cfg.items())},
                     'by_pi0': dict(sorted(pi0.items())), 'fields_9_10': {' '.join(k): v for k, v in tail.items()},
                     'families': fam}
res = {'inputs_sha256_verified': ver, 'header_crosscheck_ok': hdr_ok, 'duplicate_H_lines': dup,
       'p18_cells_by_seed': cells, 'all_hits_by_seed_and_p': per_p}
json.dump(res, open(os.path.join(out, 'counts.json'), 'w'), indent=1, sort_keys=True)
json.dump(breakdown, open(os.path.join(out, 'breakdown_null209249_p18.json'), 'w'), indent=1)
print(json.dumps(cells)); print('header ok', hdr_ok); print('dups', dup)
