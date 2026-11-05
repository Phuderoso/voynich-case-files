#!/usr/bin/env python3
"""K025 disclosed post-hoc (not pre-registered): (a) list the whole-group sums in KH0359/KH0405; (b) corpus test
without those two khipus (they were chosen because of K001, so the corpus total is partly selected)."""
import json, numpy as np
exec(open('tools/k025_whole_group_sums.py').read().split('res = dict(')[0].replace('20261111', '20261112'))
byokr = {names[k][0]: k for k in kh}; out = {'hits': {}}
for okr in ('KH0359', 'KH0405'):
    k = byokr[okr]; v = np.array([x[0] for x in kh[k]]); cl = [x[1] for x in kh[k]]; pr = prep(cl, len(v)); P = np.r_[0, np.cumsum(v)]
    out['hits'][okr] = [dict(pendant_pos=int(i) + 1, value=int(v[i]), group_cords=[int(s) + 1, int(e)], side='right' if i < s else 'left',
                             group_values=[int(x) for x in v[s:e]]) for i, s, e in pr
                        if v[i] >= 10 and v[i] == P[e] - P[s] and (v[s:e] > 0).sum() >= 2]
tot_o = 0; tot_n = np.zeros(5000, np.int64)
for k, cords in kh.items():
    if names[k][0] in ('KH0359', 'KH0405'): continue
    cl = [x[1] for x in cords]
    if len(groups_of(cl)) < 4: continue
    v = np.array([x[0] for x in cords], np.int64); pr = prep(cl, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    tot_o += int(G(v[None], pr)[0]); tot_n += G(perm(v, 5000), pr)
out['corpus_without_two'] = dict(G=tot_o, null_mean=float(tot_n.mean()), p=pv(tot_o, tot_n))
json.dump(out, open('analysis/k025_posthoc.json', 'w'), indent=1); print(json.dumps(out, indent=1))
