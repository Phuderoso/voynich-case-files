"""C021 (new family: codicology). Do the two leaves of one bifolium share vocabulary beyond what scribe, Currier
language and section already explain? (Codicological question: the bifolium, not the bound order, may be the
original working unit; conjugate leaves are known to share scribe and language, so raw similarity is confounded.)

Leaves = folios (all pages of folio N, recto + verso + foldout panels), metadata from ZL 3b page headers ($Q quire,
$B bifolio within quire, $H LFD hand, $L Currier language, $I illustration type; first page of the leaf).
Similarity = cosine of word-count vectors over word types with >= 5 tokens in the manuscript.
Look A (raw): S_A = mean sim(conjugate pairs) - mean sim(other leaf pairs in the same quire).
Look B (controlled): the same, using only pairs whose two leaves share hand, language and illustration type.
Null: random re-pairing of the leaves of each quire into bifolia (same number of pairs), 4000 draws; one-sided p.
Calibration (40 destroyed-signal corpora each): A: every leaf's tokens redrawn from its quire's pool; B: redrawn from
its (hand, language, illustration) pool. FPR at alpha must be <= 0.075, or the look is 'not testable'.
Power (40 planted corpora each, on the B-destroyed corpus): one leaf of each conjugate pair gets a share f = 0.2 of
its tokens redrawn from its partner's tokens. Detection rate >= 0.8 at alpha required, else 'not testable'.
alpha = 0.025 per look (Bonferroni, 2 looks).
"""
import sys, os, re, json, random, time
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))

ALPHA = 0.025; NPERM = 4000; NCAL = 40; F_PLANT = 0.2; SEED = 21021

def leaves(path='data/ZL3b-n.txt'):
    meta, words, cur = {}, defaultdict(list), None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f(\d+)\w*)>\s*<!(.*)>', line)
        if m:
            cur = int(m.group(2)); h = dict(re.findall(r'\$(\w)=(\S+)', m.group(3)))
            meta.setdefault(cur, {k: h.get(k) for k in 'QBFHLI'}); continue
        m = re.match(r'<(f\w+)\.[^>]*>\s*(.*)', line)
        if not m or cur is None: continue
        t = re.sub(r'<[^>]*>', '', m.group(2)); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        words[cur] += [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]
    keep = [f for f in sorted(meta) if len(words[f]) >= 20 and meta[f]['Q'] and meta[f]['B']]
    return keep, meta, words

def simmat(keep, words, vocab):
    ix = {w: i for i, w in enumerate(vocab)}; X = np.zeros((len(keep), len(vocab)))
    for a, f in enumerate(keep):
        for w in words[f]:
            if w in ix: X[a, ix[w]] += 1
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12; return X @ X.T

def structure(keep, meta, look):
    """per quire: list of leaf indices, true conjugate pairs; eligible-pair mask for look B"""
    q = defaultdict(list)
    for a, f in enumerate(keep): q[meta[f]['Q']].append(a)
    conj = set()
    for Q, idx in q.items():
        byb = defaultdict(list)
        for a in idx: byb[meta[keep[a]]['B']].append(a)
        for b, l in byb.items():
            if len(l) == 2: conj.add(tuple(sorted(l)))
    n = len(keep); elig = np.zeros((n, n), bool)
    for Q, idx in q.items():
        for a in idx:
            for b in idx:
                if a < b:
                    ma, mb = meta[keep[a]], meta[keep[b]]
                    elig[a, b] = look == 'A' or (ma['H'] == mb['H'] and ma['L'] == mb['L'] and ma['I'] == mb['I'])
    return q, conj, elig

def stat(S, pairs, elig):
    cm = np.zeros_like(elig); 
    for a, b in pairs: cm[a, b] = True
    c = elig & cm; o = elig & ~cm
    if c.sum() == 0 or o.sum() == 0: return np.nan
    return S[c].mean() - S[o].mean()

def random_pairs(q, conj, rng):
    npq = Counter()
    for a, b in conj:
        for Q, idx in q.items():
            if a in idx: npq[Q] += 1; break
    out = []
    for Q, idx in q.items():
        k = npq[Q]
        if k == 0: continue
        sh = list(idx); rng.shuffle(sh)
        out += [tuple(sorted(sh[2 * i:2 * i + 2])) for i in range(k)]
    return out

def test(S, q, conj, elig, rng, nperm=NPERM):
    obs = stat(S, conj, elig)
    null = np.array([stat(S, random_pairs(q, conj, rng), elig) for _ in range(nperm)]); null = null[~np.isnan(null)]
    return obs, (1 + (null >= obs).sum()) / (1 + len(null))

def redraw(keep, meta, words, key, rng):
    pool = defaultdict(list)
    for f in keep: pool[key(meta[f])] += words[f]
    return {f: rng.choices(pool[key(meta[f])], k=len(words[f])) for f in keep}

def plant(keep, words, conj, rng, f=F_PLANT):
    w = {k: list(v) for k, v in words.items()}
    for a, b in conj:
        A, B = keep[a], keep[b]
        n = int(f * len(w[B])); pos = rng.sample(range(len(w[B])), n)
        for p in pos: w[B][p] = rng.choice(words[A])
    return w

def main():
    t0 = time.time(); rng = random.Random(SEED)
    keep, meta, words = leaves()
    cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
    S = simmat(keep, words, vocab); R = {'n_leaves': len(keep), 'vocab': len(vocab)}
    for look in ('A', 'B'):
        q, conj, elig = structure(keep, meta, look)
        ncp = sum(elig[a, b] for a, b in conj)
        key = (lambda m: m['Q']) if look == 'A' else (lambda m: (m['H'], m['L'], m['I']))
        fp = []
        for r in range(NCAL):
            w2 = redraw(keep, meta, words, key, rng); fp.append(test(simmat(keep, w2, vocab), q, conj, elig, rng, 500)[1])
        fpr = float(np.mean(np.array(fp) <= ALPHA)); fpr05 = float(np.mean(np.array(fp) <= 0.05))
        pw = []
        for r in range(NCAL):
            w2 = redraw(keep, meta, words, lambda m: (m['H'], m['L'], m['I']), rng)
            w3 = plant(keep, w2, conj, rng); pw.append(test(simmat(keep, w3, vocab), q, conj, elig, rng, 500)[1])
        power = float(np.mean(np.array(pw) <= ALPHA))
        obs, p = test(S, q, conj, elig, rng)
        testable = fpr <= 0.075 and power >= 0.8
        verdict = ('not testable' if not testable else ('detected' if p <= ALPHA else 'not detected'))
        R[look] = {'n_conj_pairs_total': len(conj), 'n_conj_pairs_eligible': int(ncp), 'n_other_pairs': int(elig.sum() - ncp),
                   'S_obs': float(obs), 'p': float(p), 'fpr_at_alpha': fpr, 'fpr_at_0.05': fpr05, 'power_f0.2': power,
                   'verdict': verdict}
        print(look, R[look], round(time.time() - t0, 1), 's', flush=True)
    R['seconds'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C021_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
