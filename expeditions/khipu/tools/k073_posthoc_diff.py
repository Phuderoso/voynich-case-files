#!/usr/bin/env python3
"""K073 post hoc (disclosed, after the registered run): why are the three new KFG pairs absent from K010?
For each khipu of a new pair: OKR level-1 values (K010 loader, R5 masked) vs KFG pendant values (K073 loader), the shared
block's position in each source, and the KFG ChangeLog rows touching those pendants. No statistic; descriptive only.
Usage: python3 tools/k073_posthoc_diff.py data/khipu.db"""
import json, re, sqlite3, sys
from collections import defaultdict
d = json.load(open('analysis/k073_results.json')); c = sqlite3.connect(sys.argv[1]); k = sqlite3.connect('/workspace/kfg/kfg_20261111.db')
kid = {r[1]: r[0] for r in c.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
def okr_vals(n):
    if n not in kid: return None
    out = []
    for (cid,) in c.execute('select CORD_ID from cord where KHIPU_ID=? and CORD_LEVEL=1 order by CORD_ORDINAL', (kid[n],)):
        out.append(sum(int(v) for (v,) in c.execute('select knot_value_type from knot where CORD_ID=?', (cid,)) if v is not None))
    return out
def kfg_vals(n):
    L = sorted((int(m[1:]), int(float(v or 0))) for m, v in k.execute('select cord_name, value from cord where khipu=?', (n,)) if re.match(r'^p\d+$', str(m)))
    return [v for _, v in L]
def find(seq, blk):
    if seq is None: return None
    for i in range(len(seq) - len(blk) + 1):
        if seq[i:i + len(blk)] == blk: return i
    return None
out = []
for r in d['new_pairs']:
    row = dict(pair=f"{r['a']}·{r['b']}", block=r['block'], p_adj=r['p_adj'])
    for n in (r['a'], r['b']):
        o, f = okr_vals(n), kfg_vals(n); pos = find(f, r['block'])
        okr_window = o[pos:pos + len(r['block'])] if (o and pos is not None and pos + len(r['block']) <= len(o)) else None
        pens = {f'p{pos + 1 + t}' for t in range(len(r['block']))} if pos is not None else set()
        cl = [list(map(str, x)) for x in k.execute('select date, what, frm, too, explanation from changelog where khipu=?', (n,))
              if any(re.search(rf'\b{p}\b', str(x[1])) for p in pens)]
        row[n] = dict(okr_n_level1=None if o is None else len(o), kfg_n_pendants=len(f), kfg_block_at_pendant=None if pos is None else pos + 1,
                      okr_values_same_window=okr_window, okr_has_exact_block=find(o, r['block']) is not None if o else False,
                      kfg_changelog_on_block_pendants=cl)
    out.append(row)
json.dump(out, open('analysis/k073_posthoc_diff.json', 'w'), indent=1); print(json.dumps(out, indent=1))
