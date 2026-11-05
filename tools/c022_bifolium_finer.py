"""C022 (F-COD step 2). Does C021's controlled bifolium signal survive finer strata and distance matching?
Reuses C021's leaves, cosine similarity, re-pairing null, calibration and power gates (tools/c021_bifolium_vocab.py).
Look C: only pairs whose two leaves share LFD hand, Currier language, illustration type AND Currier's hand ($C;
        missing $C is its own category).
Look D: C021 Look-B strata (hand x language x illustration), but the comparison set is restricted to pairs whose bound
        distance (|folio number difference|) equals some true conjugate pair's distance in the same quire, so
        conjugates are compared with pairs equally far apart in the bound book.
Null: random re-pairing of each quire's leaves (4000 draws). alpha = 0.025 per look (Bonferroni, 2 looks).
Gates as C021: FPR at alpha <= 0.075 on 40 destroyed corpora (leaf words redrawn from the look's stratum pool);
power >= 0.8 on 40 planted corpora (20 % of one conjugate leaf's words from its partner).
"""
import sys, os, json, random, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c021_bifolium_vocab as T
SEED = 22022

def masks(keep, meta, q, conj):
    n = len(keep); C = np.zeros((n, n), bool); D = np.zeros((n, n), bool)
    for Q, idx in q.items():
        dists = [abs(keep[a] - keep[b]) for a, b in conj if a in idx]
        for a in idx:
            for b in idx:
                if a < b:
                    ma, mb = meta[keep[a]], meta[keep[b]]
                    same = ma['H'] == mb['H'] and ma['L'] == mb['L'] and ma['I'] == mb['I']
                    C[a, b] = same and (ma.get('C') or '-') == (mb.get('C') or '-')
                    D[a, b] = same and any(abs(keep[a] - keep[b]) == d for d in dists)
    return C, D

def main():
    t0 = time.time(); rng = random.Random(SEED)
    keep, meta, words = T.leaves()
    import re
    for line in open('data/ZL3b-n.txt', encoding='utf-8', errors='replace'):
        m = re.match(r'<f(\d+)\w*>\s*<!(.*)>', line)
        if m and int(m.group(1)) in meta and 'C' not in meta[int(m.group(1))]:
            meta[int(m.group(1))]['C'] = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))).get('C')
    cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
    S = T.simmat(keep, words, vocab)
    q, conj, _ = T.structure(keep, meta, 'A'); MC, MD = masks(keep, meta, q, conj)
    keys = {'C': lambda m: (m['H'], m['L'], m['I'], m.get('C') or '-'), 'D': lambda m: (m['H'], m['L'], m['I'])}
    R = {'n_leaves': len(keep), 'vocab': len(vocab)}
    for look, elig in (('C', MC), ('D', MD)):
        ncp = int(sum(elig[a, b] for a, b in conj))
        fp = [T.test(T.simmat(keep, T.redraw(keep, meta, words, keys[look], rng), vocab), q, conj, elig, rng, 500)[1] for _ in range(T.NCAL)]
        pw = [T.test(T.simmat(keep, T.plant(keep, T.redraw(keep, meta, words, keys[look], rng), conj, rng), vocab), q, conj, elig, rng, 500)[1] for _ in range(T.NCAL)]
        fpr = float(np.mean(np.array(fp) <= T.ALPHA)); power = float(np.mean(np.array(pw) <= T.ALPHA))
        obs, p = T.test(S, q, conj, elig, rng)
        ok = fpr <= 0.075 and power >= 0.8
        R[look] = {'n_conj_pairs_eligible': ncp, 'n_other_pairs': int(elig.sum() - ncp), 'S_obs': float(obs), 'p': float(p),
                   'fpr_at_alpha': fpr, 'power_f0.2': power,
                   'verdict': 'not testable' if not ok else ('detected' if p <= T.ALPHA else 'not detected')}
        print(look, R[look], round(time.time() - t0, 1), 's', flush=True)
    R['seconds'] = round(time.time() - t0, 1); json.dump(R, open('analysis/C022_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
