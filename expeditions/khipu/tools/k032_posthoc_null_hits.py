#!/usr/bin/env python3
"""K032 post-hoc (labelled, not pre-registered): rebuild the three null corpora with the
same seeds (deterministic) and list which permuted khipus produced BH false discoveries.
Usage: python3 tools/k032_posthoc_null_hits.py khipu.db
"""
import sys, json
src = open('tools/k032_d5w_corpus_scan.py').read().split('# Stage 1: real scan')[0]
exec(src)
out = []
for r in range(R_NULL):
    rows = run_scan(SEEDS['null'] * 10 + r, lambda rng, v: rng.permutation(v), f'null{r}')
    g1, n1, n2, n3 = families(rows)
    rec = dict(rep=r,
               F1=[dict(okr=g1[i]['okr'], inv=g1[i]['inv'], stratum=g1[i]['stratum'], n_pend=g1[i]['n_pend'],
                        p_D5w=g1[i]['p_D5w'], p_D5=g1[i]['p_D5']) for i in np.nonzero(n1)[0]],
               F2=[dict(okr=rows[i]['okr'], inv=rows[i]['inv'], stratum=rows[i]['stratum'], n_pend=rows[i]['n_pend'],
                        p_D5=rows[i]['p_D5']) for i in np.nonzero(n2)[0]],
               F3=[dict(okr=rows[i]['okr'], stratum=rows[i]['stratum'], p_D5w=rows[i]['p_D5w']) for i in np.nonzero(n3)[0]],
               n_floor_D5w=int(sum(rr['p_D5w'] <= 1 / 10001 + 1e-12 for rr in rows)),
               n_floor_D5=int(sum(rr['p_D5'] <= 1 / 10001 + 1e-12 for rr in rows)),
               min_p_D5w=min(rr['p_D5w'] for rr in rows), min_p_D5=min(rr['p_D5'] for rr in rows))
    out.append(rec)
    print(json.dumps(rec), flush=True)
json.dump(out, open('analysis/k032_posthoc_null_hits.json', 'w'), indent=1, default=float)
