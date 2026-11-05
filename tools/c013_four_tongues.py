#!/usr/bin/env python3
"""C013: C012's homophonic hill-climbing solver against four target languages (Latin, vowelless Latin, Italian,
consonantal Hebrew). Primary metric W = distinct decoded dictionary words (len >= 3). Bar = max W over 15 meaningless
texts per language; planted held-out ciphers gate each language. Resumable: per-run results cached in
analysis/C013_cache.jsonl. Usage: python3 tools/c013_four_tongues.py [--replicate]"""
import os, sys, json, random
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5

NW, RESTARTS, ITERS = 1500, 20, 15000
CACHE = 'analysis/C013_cache.jsonl'
flat = lambda L: [w for l in L for w in l]

def corpora():
    """returns {code: (train_words, dict_set, planted_words, alphabet)}"""
    la = flat(c3.gutenberg('data/corpora/pg218.txt')); de = flat(c3.gutenberg('data/corpora/pg23306.txt'))
    lav = flat(c3.devowel(c3.gutenberg('data/corpora/pg218.txt'))); dev = flat(c3.devowel(c3.gutenberg('data/corpora/pg23306.txt')))
    it = flat(c3.gutenberg('data/corpora/pg1012.txt')); ma = flat(c3.gutenberg('data/corpora/pg56498.txt'))
    ge = flat(c3.hebrew('data/corpora/Gen.xml', True)); ex = flat(c3.hebrew('data/corpora/Exod.xml', True))
    out = {}
    for code, tr, dic, pl in (('LA', la[:len(la) // 2], la, de), ('LV', lav[:len(lav) // 2], lav, dev),
                              ('IT', it, it, ma), ('HE', ge, ge, ex)):
        alpha = sorted(set(''.join(tr)) | set(''.join(pl)))
        out[code] = (tr, set(dic), pl, alpha)
    return out

def lm(train, alpha):
    A = len(alpha) + 1; ix = {c: i for i, c in enumerate(alpha)}; sp = A - 1
    s = np.array([sp] + [x for w in train for x in [ix[ch] for ch in w] + [sp]])
    q = ((s[:-3] * A + s[1:-2]) * A + s[2:-1]) * A + s[3:]
    c = np.bincount(q, minlength=A ** 4).astype(float)
    return np.log10(np.where(c > 0, c, 0.01) / c.sum())

def encode(words):
    syms = {}; out = [[syms.setdefault(u, len(syms)) for u in w] for w in words]; return out, len(syms)

def stream(words_ids):
    s = [-1]
    for w in words_ids: s += w + [-1]
    return np.array(s)

def score(st, m, T, A):
    p = np.where(st < 0, A - 1, m[np.maximum(st, 0)])
    q = ((p[:-3] * A + p[1:-2]) * A + p[2:-1]) * A + p[3:]; return T[q].mean()

def solve(args):
    key, words_ids, n, seed, T, A = args
    rng = np.random.default_rng(seed); st = stream(words_ids); best = (-1e9, None); L = A - 1
    for r in range(RESTARTS):
        m = rng.integers(0, L, n); s = score(st, m, T, A)
        for _ in range(ITERS):
            i = rng.integers(n); old = m[i]; m[i] = rng.integers(L)
            t = score(st, m, T, A)
            if t >= s: s = t
            else: m[i] = old
        if s > best[0]: best = (s, m.copy())
    return key, float(best[0]), best[1].tolist()

def texts(replicate=False):
    """shared null and manuscript texts (unit lists), identical for all languages"""
    V = flat(c3.voynich()); out = []
    if replicate:
        rng = random.Random(113)
        for k in range(5):
            s0 = rng.randrange(len(V) - NW); out.append(('Voynich-rep', s0, [c3.units(x) for x in V[s0:s0 + NW]]))
        return out
    cfg = c5.tocfg(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
    for name, c, seeds in (('G0', {}, range(11, 16)), ('G*', cfg, range(6011, 6016))):
        for sd in seeds:
            w = flat(c4.generate(c, sd))[:NW]; out.append(('null-' + name, sd, [c3.units(x) for x in w]))
    cV = Counter(u for w in V for u in c3.units(w)); us, ps = zip(*cV.items()); ps = np.array(ps) / sum(ps)
    lens = [len(c3.units(w)) for w in V]
    for sd in range(510, 515):
        r = np.random.default_rng(sd)
        ws = [list(r.choice(us, size=random.Random(sd * 7919 + i).choice(lens), p=ps)) for i in range(NW)]
        out.append(('null-iid', sd, ws))
    rng = random.Random(13)
    for k in range(5):
        s0 = rng.randrange(len(V) - NW); out.append(('Voynich', s0, [c3.units(x) for x in V[s0:s0 + NW]]))
    return out

def planted(code, pl, alpha):
    rng = random.Random(1300 + ord(code[0]) + ord(code[1])); out = []
    top8 = [c for c, _ in Counter(''.join(pl)).most_common(8)]
    for k in range(5):
        s0 = rng.randrange(len(pl) - NW); pw = pl[s0:s0 + NW]
        for kind in ('P1', 'P2'):
            sym, ids, truth = {}, [], []
            for w in pw:
                wi = []
                for ch in w:
                    key = (ch, rng.randrange(2)) if (kind == 'P2' and ch in top8) else (ch, 0)
                    wi.append(sym.setdefault(key, len(sym))); truth.append(ch)
                ids.append(wi)
            out.append((kind, k, ids, len(sym), ''.join(truth), {v: k_[0] for k_, v in sym.items()}))
    return out

def main():
    rep = '--replicate' in sys.argv
    C = corpora(); TX = texts(rep)
    done = {}
    if os.path.exists(CACHE):
        for line in open(CACHE): r = json.loads(line); done[r['key']] = r
    jobs, info = [], {}
    for code, (tr, dic, pl, alpha) in C.items():
        T = lm(tr, alpha); A = len(alpha) + 1
        items = []
        if not rep:
            for kind, k, ids, n, truth, inv in planted(code, pl, alpha): items.append((kind, k, ids, n, truth))
        for kind, k, ws in TX:
            ids, n = encode(ws); items.append((kind, k, ids, n, None))
        for j, (kind, k, ids, n, truth) in enumerate(items):
            key = f'{code}|{kind}|{k}'; info[key] = (code, kind, k, ids, truth)
            if key not in done: jobs.append((key, ids, n, 13000 + 97 * j + 7 * ord(code[0]), T, A))
    print(f'{len(jobs)} runs to do, {len(done)} cached', flush=True)
    with Pool(8) as p, open(CACHE, 'a') as f:
        for key, s, m in p.imap_unordered(solve, jobs):
            code, kind, k, ids, truth = info[key]; alpha = C[code][3]
            dec = [''.join(alpha[m[i]] for i in w) for w in ids]
            r = dict(key=key, lang=code, kind=kind, k=k, S=s, n_symbols=len(m))
            if truth is not None:
                r['accuracy'] = float(np.mean([a == b for a, b in zip(truth, ''.join(dec))]))
            hits = [d for d in dec if len(d) >= 3 and d in C[code][1]]
            r['W'] = len(set(hits)); r['tokens_in_dict'] = len(hits)
            r['top_words'] = [w for w, _ in Counter(hits).most_common(12)]
            r['excerpt'] = ' '.join(dec[:25])
            f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush(); done[key] = r
            print(key, round(s, 3), r['W'], r.get('accuracy'), flush=True)
    summary = {}
    for code, (tr, dic, pl, alpha) in C.items():
        R = [r for r in done.values() if r['lang'] == code]
        pr = [r for r in R if r['kind'] in ('P1', 'P2')]; nu = [r for r in R if r['kind'].startswith('null')]
        vo = [r for r in R if r['kind'] == 'Voynich']; vr = [r for r in R if r['kind'] == 'Voynich-rep']
        ok = sum(r['accuracy'] >= 0.8 for r in pr); bar = max(r['W'] for r in nu)
        vW = [r['W'] for r in sorted(vo, key=lambda r: r['k'])]; med = float(np.median(vW))
        T = lm(tr, alpha); A = len(alpha) + 1; ix = {c: i for i, c in enumerate(alpha)}
        ceil = float(score(stream([[ix[c] for c in w] for w in pl[:NW]]), np.arange(len(alpha)), T, A))
        s = dict(planted_ok=f'{ok}/10', planted_acc=[round(r['accuracy'], 3) for r in pr],
                 planted_W=[r['W'] for r in pr], null_W=sorted(r['W'] for r in nu), bar_W=bar,
                 voynich_W=vW, voynich_median_W=med,
                 null_S_max=max(r['S'] for r in nu), voynich_S=[r['S'] for r in sorted(vo, key=lambda r: r['k'])],
                 planted_S_range=[min(r['S'] for r in pr), max(r['S'] for r in pr)], plain_ceiling_S=ceil,
                 dict_types=len(dic), alphabet=len(alpha))
        if vr: s['replicate_W'] = [r['W'] for r in vr]; s['replicate_median_W'] = float(np.median(s['replicate_W']))
        if ok < 9: v = 'not testable'
        elif med > bar:
            v = ('provisional: needs replication' if not vr else
                 'more words than meaningless text (replicated)' if s['replicate_median_W'] > bar else
                 'not replicated: no more words than meaningless text')
        else: v = 'no more words than meaningless text under this solver'
        s['verdict'] = v; summary[code] = s
    json.dump(dict(summary=summary, runs=sorted(done.values(), key=lambda r: r['key'])),
              open('analysis/C013_results.json', 'w'), indent=1, ensure_ascii=False)
    for c, s in summary.items(): print(c, {k: v for k, v in s.items() if k not in ('planted_acc',)})

if __name__ == '__main__':
    main()
