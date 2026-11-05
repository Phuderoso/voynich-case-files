#!/usr/bin/env python3
"""K032 post-hoc (labelled, not pre-registered): audit of the extreme tail of the K003/K031
min-p p-value. In colrank_p the observed per-column p counts only null draws (can be 0/K),
while each null draw's own p counts itself (>= 1/K). So an observed copy that is the column
maximum in ANY of the 11 columns lands on the floor. Under exchangeability the floor should
have probability 1/(K+1). We measure the floor rate on permuted copies (true nulls) for the
current p ('asym') and for the pooled exchangeable fix ('pooled': obs ranked inside obs+nulls).
Usage: python3 tools/k032_posthoc_tail_audit.py khipu.db
"""
import sys, json
src = open('tools/k032_d5w_corpus_scan.py').read().split('# Stage 1: real scan')[0]
exec(src)


def pooled_minp(No, Nn):
    A = np.vstack([No, Nn])
    live = A.max(0) > 0
    if not live.any():
        return 1.0
    A = A[:, live]
    pa = colrank_p(A, A).min(1)
    return float((pa <= pa[0] + 1e-12).sum() / len(A))


rng = np.random.default_rng(32329)
K, COPIES = 1000, 60
sel = [d for d in data if d[0] in pop_ids]
sel = sel[::6]  # spread sample over pop (~63 khipus)
cnt = dict(asym_D5w=0, pooled_D5w=0, asym_D5=0, pooled_D5=0)
n = 0
for khid, v, gids, n4, ng in sel:
    for _ in range(COPIES):
        x = rng.permutation(v)
        Wo, Wow = scores(x[None]), scores(x[None], gids, True)
        n5, n5w = null_scores(rng, x, gids, K)
        cnt['asym_D5'] += minp(Wo, n5) <= 1 / (K + 1) + 1e-12
        cnt['asym_D5w'] += minp(Wow, n5w) <= 1 / (K + 1) + 1e-12
        cnt['pooled_D5'] += pooled_minp(Wo, n5) <= 1 / (K + 1) + 1e-12
        cnt['pooled_D5w'] += pooled_minp(Wow, n5w) <= 1 / (K + 1) + 1e-12
        n += 1
    if time.time() - t0 > 250:
        print('time cap', flush=True)
        break
res = dict(n_copies=n, n_khipus=len(sel), K=K, expected_floor_rate=1 / (K + 1),
           floor_counts={k: int(c) for k, c in cnt.items()},
           floor_rates={k: c / n for k, c in cnt.items()})
print(json.dumps(res, indent=1))
json.dump(res, open('analysis/k032_posthoc_tail_audit.json', 'w'), indent=1)
