#!/usr/bin/env python3
"""C015 post-hoc, exploratory (NOT a verdict): after every pre-registered gate failed, how large must a planted
separation be before the T2 test (labels vs same-page running text) sees it? Two plant kinds on fresh pseudo-label
draws of group X: 'swap' (k<->t, ch<->sh in a fraction f of tokens, the pre-registered plant) and 'q-initial'
(prefix 'q' to a fraction f of tokens: a large first-glyph shift, since labels almost never start with q).
Same null construction, seeds and alpha as tools/c015_label_vocabulary.py. Writes analysis/C015_power_explore.json."""
import json, random, time
import numpy as np
import c015_label_vocabulary as C

def main():
    t0 = time.time(); labels, running, _ = C.parse(); feat = C.Feat()
    words = {w for g in labels for _, w in labels[g]} | {w for p in running for w in running[p]}
    words |= {C.swap(w) for w in words} | {'q' + w for w in words}
    for w in sorted(words): feat.vec(w)
    NF = len(feat.idx)
    def counts(ws):
        v = np.zeros(NF)
        for w in ws:
            for i in feat.vec(w): v[i] += 1
        return v
    def pseudo(gt, rng, types=False):
        from collections import Counter
        pc = Counter(p for p, _ in gt); out = []; pool = [w for p in pc for w in running[p]]
        if types: pool = sorted(set(pool))
        for p, k in sorted(pc.items()):
            src = running[p] if not types else sorted(set(running[p]))
            if len(src) < 2 * k: src = pool
            out.extend(src[i] for i in rng.choice(len(src), size=k, replace=False))
        return out
    plants = {'swap': C.swap, 'q-initial': lambda w: 'q' + w}
    grid = {'swap': [0.5, 1.0], 'q-initial': [0.1, 0.25, 0.5]}
    out = {}
    for X, Y in C.PAIRS:
        rng = np.random.default_rng(1501); ng, nw = [], []
        for r in range(C.R):   # identical null construction and seed as the counted run
            px, py = pseudo(labels[X], rng), pseudo(labels[Y], rng)
            ng.append((counts(px), counts(py)))
            nw.append(C.s_w(pseudo(labels[X], rng, True), pseudo(labels[Y], rng, True)))
        ng = C.jsd_rows(np.array([a for a, _ in ng]), np.array([b for _, b in ng])); nw = np.array(nw)
        res = {}
        for kind, fs in grid.items():
            for f in fs:
                hg = hw = 0; sg = []; sw = []
                for k in range(10):
                    prng = np.random.default_rng(15100 + k); rr = random.Random(15200 + k)
                    px, py = pseudo(labels[X], prng), pseudo(labels[Y], prng)
                    px = [plants[kind](w) if rr.random() < f else w for w in px]
                    s = float(C.jsd_rows(counts(px)[None], counts(py)[None])[0]); p, d = C.pval(s, ng)
                    hg += (p <= C.ALPHA and d == 'more'); sg.append(s)
                    tx, ty = pseudo(labels[X], prng, True), pseudo(labels[Y], prng, True)
                    tx = [plants[kind](w) if rr.random() < f else w for w in tx]
                    s = C.s_w(tx, ty); p, d = C.pval(s, nw); hw += (p <= C.ALPHA and d == 'more'); sw.append(s)
                res[f'{kind}@{f}'] = {'S_g_hits': int(hg), 'S_w_hits': int(hw), 'S_g_planted_mean': round(float(np.mean(sg)), 4),
                                      'S_w_planted_mean': round(float(np.mean(sw)), 4)}
        out[f'{X}-{Y}'] = {'S_g_null_mean': round(float(ng.mean()), 4), 'S_g_null_q99.75': round(float(np.quantile(ng, 0.9975)), 4),
                           'S_w_null_mean': round(float(nw.mean()), 4), 'S_w_null_q99.75': round(float(np.quantile(nw, 0.9975)), 4), 'plants': res}
        json.dump(out, open('analysis/C015_power_explore.json', 'w'), indent=1)
        print(f'[{time.time()-t0:6.1f}s] {X}-{Y}', json.dumps(out[f'{X}-{Y}']), flush=True)

if __name__ == '__main__':
    import os, sys; sys.path.insert(0, os.path.dirname(__file__)); main()
