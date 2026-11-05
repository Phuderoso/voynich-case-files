#!/usr/bin/env python3
"""C016 counted run. Do label words differ from the running text of their own pages in single glyph features?
Pre-registered in case-file/C016-label-features-power-first.md (design step: tools/c016_power_design.py).
Counted looks: 5 features x 2 datasets (D1 = ZL held-out label loci, D2 = Takahashi IT2a reading of the C015 loci),
two-sided, Bonferroni alpha = 0.005. Statistic: mean feature value over label tokens vs R = 9999 same-page
running-text draws. Gate per look: planted shift of the pre-registered size delta* detected (p <= alpha, right
direction) in >= 90 of 100 fresh replicates in BOTH directions. FPR per look: 1000 unplanted pseudo-label draws,
must be <= 0.08 at 0.05 and <= 0.015 at alpha.
Not counted: D0 (ZL reading of the C015 loci, where the lead was seen = re-analysis), first-word-per-locus
sensitivity, line-initial-word baseline, ZL vs IT per-locus agreement on the first glyph.
Usage: python3 tools/c016_label_features.py   (writes analysis/C016_results.json after every stage)"""
import json, time, sys, re
from collections import Counter
import numpy as np
sys.path.insert(0, 'tools')
from c016_common import DATASETS, FEATURES, parse, Sampler, Planter, pval, feat, units

ALPHA = 0.005; R = 9999; GATE_REPS = 100; FPR_REPS = 1000
DELTA_STAR = {'D1_ZL_heldout': {'o_init': 0.2, 'len': 0.6, 'y_fin': 0.2, 'q_init': 0.1, 'gallows': 0.2},
              'D2_IT_C015loci': {'o_init': 0.1, 'len': 0.4, 'y_fin': 0.1, 'q_init': 0.05, 'gallows': 0.1}}
OUT = 'analysis/C016_results.json'

def main():
    t0 = time.time(); res = {'alpha': ALPHA, 'R': R, 'delta_star': DELTA_STAR, 'stages': {}}
    def ck(stage, obj):
        res['stages'][stage] = obj; res['elapsed_s'] = round(time.time() - t0, 1)
        json.dump(res, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
        print(f'[{time.time()-t0:6.1f}s] {stage} done', flush=True)
    parsed = {}
    for di, name in enumerate(['D1_ZL_heldout', 'D2_IT_C015loci', 'D0_ZL_C015loci']):
        src, pred = DATASETS[name]
        labels, running, li, lf = parse(src, pred); parsed[name] = (labels, running, li, lf)
        S = Sampler(labels, running); P = Planter(S.pool)
        rng = np.random.default_rng(1601 + di)
        null = S.null_matrix(rng, R, FEATURES)
        words = [w for _, _, w in labels]
        out = {'label_tokens': len(words), 'loci': len({(p, l) for p, l, _ in labels}), 'pages_pooled': S.pooled_pages,
               'counted': name != 'D0_ZL_C015loci', 'looks': {}}
        for fi, f in enumerate(FEATURES):
            obs = float(np.mean([feat(w, f) for w in words])); p, d = pval(obs, null[:, fi])
            look = {'label_mean': round(obs, 4), 'null_mean': round(float(null[:, fi].mean()), 4),
                    'null_q': [round(float(q), 4) for q in np.quantile(null[:, fi], [0.0025, 0.5, 0.9975])],
                    'diff': round(obs - float(null[:, fi].mean()), 4), 'p': round(p, 5), 'dir': d}
            if name in DELTA_STAR:
                prng = np.random.default_rng(16500 + 10 * di + fi); ds = DELTA_STAR[name][f]; gate = {}
                for sgn, lab in ((1, 'up'), (-1, 'down')):
                    hits = 0
                    for _ in range(GATE_REPS):
                        pw = P.apply(S.draw(prng), f, sgn * ds, prng)
                        pp, dd = pval(np.mean([feat(x, f) for x in pw]), null[:, fi])
                        hits += (pp <= ALPHA and dd == ('more' if sgn > 0 else 'less'))
                    gate[lab] = hits
                frng = np.random.default_rng(16700 + 10 * di + fi)
                ps = np.array([pval(np.mean([feat(w, f) for w in S.draw(frng)]), null[:, fi])[0] for _ in range(FPR_REPS)])
                fpr = {'at_0.05': float(np.mean(ps <= 0.05)), 'at_alpha': float(np.mean(ps <= ALPHA))}
                gate_ok = min(gate.values()) >= 0.9 * GATE_REPS; fpr_ok = fpr['at_0.05'] <= 0.08 and fpr['at_alpha'] <= 0.015
                if not gate_ok: verdict = 'not testable (gate failed)'
                elif not fpr_ok: verdict = 'withdrawn (FPR above limit)'
                elif p <= ALPHA: verdict = f'labels differ from own-page running text ({d})'
                else: verdict = f'no difference of {ds} or more detected'
                look.update({'delta_star': ds, 'gate_hits_of_100': gate, 'gate_ok': gate_ok, 'fpr': fpr, 'fpr_ok': fpr_ok, 'verdict': verdict})
            out['looks'][f] = look
        # sensitivity (not counted): first word of each label locus only, same null machinery
        seen, first = set(), []
        for p_, l_, w in labels:
            if (p_, l_) not in seen: seen.add((p_, l_)); first.append((p_, l_, w))
        S1 = Sampler(first, running); n1 = S1.null_matrix(np.random.default_rng(1611 + di), 1999, FEATURES)
        out['first_word_only'] = {f: dict(zip(('label_mean', 'null_mean', 'p', 'dir'), (round(float(np.mean([feat(w, f) for _, _, w in first])), 4), round(float(n1[:, i].mean()), 4), *pval(float(np.mean([feat(w, f) for _, _, w in first])), n1[:, i])))) for i, f in enumerate(FEATURES)}
        out['first_word_only']['tokens'] = len(first)
        # alternative baseline (not counted): first / last words of running-text lines on the same pages
        for key, src_d in (('line_initial_baseline', li), ('line_final_baseline', lf)):
            S2 = Sampler(labels, src_d); S2.src = {p: (src_d[p] if len(src_d[p]) >= 1 else S2.pool) for p in S2.pc}
            r2 = np.random.default_rng(1621 + di); M = np.zeros((1999, len(FEATURES))); cache = {}
            for r in range(1999):
                ws = []
                for p_, k in sorted(S2.pc.items()):
                    s = S2.src[p_]; ws.extend(s[i] for i in r2.choice(len(s), size=k, replace=True))
                M[r] = np.mean([[feat(w, f) for f in FEATURES] for w in ws], axis=0)
            out[key] = {f: {'null_mean': round(float(M[:, i].mean()), 4), 'p': pval(float(np.mean([feat(w, f) for w in words])), M[:, i])} for i, f in enumerate(FEATURES)}
        out['top_initial_units'] = Counter(units(w)[0] for w in words).most_common(6)
        out['top_words'] = Counter(words).most_common(8)
        ck(name, out)
    # ZL vs IT per-locus agreement on the first glyph unit of the first word (C015 loci present in both files)
    def first_by_locus(src, pred):
        d = {}
        for line in open(src, encoding='utf-8', errors='replace'):
            m = re.match(r'<(f\w+)\.(\d+[a-z]?),.(\w\w)>\s*(.*)', line.rstrip('\n'))
            if m and m.group(3)[0] == 'L' and pred(m.group(3), m.group(1)):
                from c016_common import clean
                ws = clean(m.group(4))
                if ws: d[(m.group(1), m.group(2), m.group(3))] = ws[0]
        return d
    zl = first_by_locus(*DATASETS['D0_ZL_C015loci']); it = first_by_locus(*DATASETS['D2_IT_C015loci'])
    common = sorted(set(zl) & set(it)); tab = Counter((units(zl[k])[0] == 'o', units(it[k])[0] == 'o') for k in common)
    ck('ZL_vs_IT_first_glyph', {'loci_in_both': len(common), 'ZLo_ITo': tab[(True, True)], 'ZLo_ITnot': tab[(True, False)],
                                'ZLnot_ITo': tab[(False, True)], 'neither': tab[(False, False)],
                                'same_first_word': sum(zl[k] == it[k] for k in common),
                                'examples_disagree': [(k, zl[k], it[k]) for k in common if (units(zl[k])[0] == 'o') != (units(it[k])[0] == 'o')][:12]})

if __name__ == '__main__':
    main()
