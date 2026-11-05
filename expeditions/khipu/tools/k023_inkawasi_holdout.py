#!/usr/bin/env python3
"""K023 - held-out Inkawasi test of the K022 'apart' pattern. Pre-registered in case-file/K023 (commit 01ff1d21).
Reuses K022's definitions (sum cords, colours, summand blocks, anchor null); population = Incahuasi minus K001 set;
one-sided (A lower than null)."""
import json, time, numpy as np
src = open('tools/k022_sum_summand_colour.py').read().split('prim = [it')[0]
exec(src.replace('SEED = 20261107', 'SEED = 20261108'))
ink = {r[0] for r in c.execute("select OKR_NUM from khipu_main where PROVENANCE='Incahuasi'")}
hold = [it for it in items if it['okr'] in ink and it['okr'] not in sigk]
def p_lo(o, nl): return float((1 + (nl <= o + 1e-12).sum()) / (1 + len(nl)))
A = sum(it['obs'] for it in hold); N = null_draw(hold, R)
fp = pw = 0
for _ in range(NC):
    pick = [it['pool'][rng.integers(len(it['pool']))] for it in hold]
    fp += p_lo(sum(p[2] for p in pick), N) <= ALPHA
    pw += p_lo(sum(planted(it, p[0], p[1], 'apart') for it, p in zip(hold, pick)), N) <= ALPHA
res = dict(seed=20261108, R=R, n_khipus=len({it['okr'] for it in hold}), khipus=sorted({it['okr'] for it in hold}),
           n_sum_cords=len(hold), A=A, A_null_mean=float(N.mean()), A_null_sd=float(N.std()), p_one_sided_apart=p_lo(A, N),
           calib_fpr=fp / NC, power_apart=pw / NC)
res['verdict'] = ('controls failed' if res['calib_fpr'] > 0.08 else 'supported' if res['p_one_sided_apart'] <= ALPHA
                  else 'not supported' if res['power_apart'] >= 0.5 else 'not testable')
pk = defaultdict(lambda: [0, 0.0, 0.0])
for it in hold:
    pk[it['okr']][0] += 1; pk[it['okr']][1] += it['obs']; pk[it['okr']][2] += float(np.mean([p[2] for p in it['pool']]))
res['per_khipu'] = [dict(okr=k, n=v[0], obs=round(v[1], 2), null_mean=round(v[2], 2)) for k, v in sorted(pk.items())]
res['runtime_s'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k023_results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
