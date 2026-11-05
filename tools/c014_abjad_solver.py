#!/usr/bin/env python3
"""C014: vowelless-Latin (abjad-style) solver that cannot collapse to 'sss'. Objective O = mean joint 4-gram log10
score (C012/C013) minus LAMBDA * KL(decoded letter frequencies || devowelled-Latin letter frequencies) (log10 units).
LAMBDA is chosen automatically on tuning plants from Caesar's second half (never the gate text), then frozen.
Gate: 10 blind planted Descartes (devowelled) ciphers, letter accuracy >= 0.80 in >= 9/10.
Bar: max W (distinct decoded dictionary words, len >= 3) over 15 meaningless texts. Manuscript: 5 samples of 1,500
words, 3 forced from herbal pages ($I=H) and 2 from the whole text (seed 14). Replication (seed 114) runs only if
the median beats the bar. Checkpointed per run in analysis/C014_cache.jsonl.
Usage: python3 tools/c014_abjad_solver.py [--smoke]"""
import os, sys, json, random, re, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5
from c013_four_tongues import lm, encode, stream, score, texts as c013_texts, NW

RESTARTS, ITERS = 20, 15000
LAMBDAS = [0.0, 0.1, 0.3, 1.0, 3.0]
CACHE = 'analysis/C014_cache.jsonl'
flat = lambda L: [w for l in L for w in l]

def corpus():
    lav = flat(c3.devowel(c3.gutenberg('data/corpora/pg218.txt')))
    dev = flat(c3.devowel(c3.gutenberg('data/corpora/pg23306.txt')))
    tr, tune = lav[:len(lav) // 2], lav[len(lav) // 2:]
    alpha = sorted(set(''.join(tr)) | set(''.join(dev)) | set(''.join(tune)))
    cnt = Counter(''.join(tr)); q = np.array([cnt[c] + 0.5 for c in alpha]); q = q / q.sum()
    return tr, tune, set(lav), dev, alpha, q

def objective(st, m, T, A, symw, q, lam):
    s = score(st, m, T, A)
    if lam == 0: return s
    p = np.bincount(m, weights=symw, minlength=len(q)) / symw.sum()
    nz = p > 0
    return s - lam * float((p[nz] * np.log10(p[nz] / q[nz])).sum())

def solve(args):
    key, words_ids, n, seed, T, A, q, lam, iters, restarts = args
    rng = np.random.default_rng(seed); st = stream(words_ids); L = A - 1
    symw = np.bincount([x for w in words_ids for x in w], minlength=n).astype(float)
    best = (-1e9, None)
    for r in range(restarts):
        m = rng.integers(0, L, n); s = objective(st, m, T, A, symw, q, lam)
        for _ in range(iters):
            i = rng.integers(n); old = m[i]; m[i] = rng.integers(L)
            t = objective(st, m, T, A, symw, q, lam)
            if t >= s: s = t
            else: m[i] = old
        if s > best[0]: best = (s, m.copy())
    return key, float(best[0]), best[1].tolist()

def plants(words, seed, k_samples):
    rng = random.Random(seed); out = []
    top8 = [c for c, _ in Counter(''.join(words)).most_common(8)]
    for k in range(k_samples):
        s0 = rng.randrange(len(words) - NW); pw = words[s0:s0 + NW]
        for kind in ('P1', 'P2'):
            sym, ids, truth = {}, [], []
            for w in pw:
                wi = []
                for ch in w:
                    key = (ch, rng.randrange(2)) if (kind == 'P2' and ch in top8) else (ch, 0)
                    wi.append(sym.setdefault(key, len(sym))); truth.append(ch)
                ids.append(wi)
            out.append((kind, k, ids, len(sym), ''.join(truth)))
    return out

def voynich_words_with_section(path='data/ZL3b-n.txt'):
    """(word, folio, $I) in ZL order, same cleaning as c3.voynich (split commas)."""
    out, cur = [], (None, None)
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m: cur = (m.group(1), dict(re.findall(r'\$(\w)=(\S+)', m.group(2))).get('I')); continue
        m = re.match(r'<(f\w+)\.[^>]*>\s*(.*)', line)
        if not m: continue
        t = re.sub(r'<[^>]*>', '', m.group(2)); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        for w in re.split(r'[.,\s]+', t):
            if w and re.fullmatch(r'[a-z]+', w): out.append((w, cur[0], cur[1]))
    return out

def manuscript(seed, avoid_seed=None):
    """5 samples of NW words: 3 drawn from herbal ($I=H) words only, 2 from all words (replication: 2 and 3); no sample shares a word
    (by ZL position) with an earlier one, nor with the samples of avoid_seed (used for the replication set)."""
    V = voynich_words_with_section(); allix = list(range(len(V))); Hix = [i for i in allix if V[i][2] == 'H']
    rng = random.Random(seed); out = []; used = set()
    if avoid_seed is not None:
        for x in manuscript(avoid_seed): used |= x[5]
    nh = 3 if avoid_seed is None else 2  # herbal text is too short for 3 more disjoint herbal windows
    for k, (pool, tag) in enumerate([(Hix, 'H')] * nh + [(allix, 'all')] * (5 - nh)):
        while True:
            s0 = rng.randrange(len(pool) - NW); seg = pool[s0:s0 + NW]
            if not (set(seg) & used): break
        used |= set(seg)
        out.append((f'{tag}{k}', s0, [c3.units(V[i][0]) for i in seg], f'{V[seg[0]][1]}-{V[seg[-1]][1]}',
                    dict(Counter(V[i][2] for i in seg)), set(seg)))
    return out

def entropy(dec):
    c = Counter(''.join(dec)); n = sum(c.values()); p = np.array(list(c.values())) / n
    return float(-(p * np.log2(p)).sum())

def run_jobs(jobs, info, done, alpha, dic, f):
    with Pool(8) as p:
        for key, s, m in p.imap_unordered(solve, jobs):
            kind, ids, truth, extra = info[key]
            dec = [''.join(alpha[m[i]] for i in w) for w in ids]
            r = dict(key=key, kind=kind, O=s, n_symbols=len(m), **extra)
            if truth is not None: r['accuracy'] = float(np.mean([a == b for a, b in zip(truth, ''.join(dec))]))
            hits = [d for d in dec if len(d) >= 3 and d in dic]
            r['W'] = len(set(hits)); r['tokens_in_dict'] = len(hits); r['letter_entropy_bits'] = entropy(dec)
            r['top_letter_share'] = max(Counter(''.join(dec)).values()) / len(''.join(dec))
            r['top_words'] = [w for w, _ in Counter(hits).most_common(12)]; r['excerpt'] = ' '.join(dec[:25])
            f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush(); done[key] = r
            print(key, round(s, 3), r['W'], r.get('accuracy'), round(r['top_letter_share'], 2), flush=True)

def main():
    smoke = '--smoke' in sys.argv; t0 = time.time()
    iters, restarts = (300, 1) if smoke else (ITERS, RESTARTS)
    cache = CACHE.replace('.jsonl', '_smoke.jsonl') if smoke else CACHE
    tr, tune, dic, dev, alpha, q = corpus(); T = lm(tr, alpha); A = len(alpha) + 1
    done = {}
    if os.path.exists(cache):
        for line in open(cache): r = json.loads(line); done[r['key']] = r
    f = open(cache, 'a')
    # 1) tuning (Caesar second half, devowelled; 2 samples x P1/P2 per lambda)
    TP = plants(tune, 1401, 2 if not smoke else 1); jobs, info = [], {}
    for lam in LAMBDAS:
        for j, (kind, k, ids, n, truth) in enumerate(TP):
            key = f'tune|{lam}|{kind}|{k}'; info[key] = (kind, ids, truth, dict(stage='tune', lam=lam))
            if key not in done: jobs.append((key, ids, n, 14000 + 31 * j, T, A, q, lam, iters, restarts))
    print(len(jobs), 'tuning runs', flush=True); run_jobs(jobs, info, done, alpha, dic, f)
    tm = {lam: float(np.mean([r['accuracy'] for r in done.values() if r.get('stage') == 'tune' and r['lam'] == lam]))
          for lam in LAMBDAS}
    lam = max(LAMBDAS, key=lambda l: (round(tm[l], 3), -l)); print('tuning means', tm, 'chosen', lam, flush=True)
    # 2) gate + nulls + manuscript with frozen lambda
    jobs, info = [], {}
    items = [(kind, f'{kind}|{k}', ids, n, truth, dict(stage='gate')) for kind, k, ids, n, truth in
             plants(dev, 1300 + ord('L') + ord('V'), 5 if not smoke else 1)]
    nulls = [x for x in c013_texts() if x[0].startswith('null')]
    if smoke: nulls = nulls[:2]
    for kind, k, ws in nulls:
        ids, n = encode(ws); items.append((kind, f'{kind}|{k}', ids, n, None, dict(stage='null')))
    for tag, s0, ws, fol, sec, _ in (manuscript(14) if not smoke else manuscript(14)[:1]):
        ids, n = encode(ws); items.append(('Voynich', f'Voynich|{tag}|{s0}', ids, n, None,
                                           dict(stage='voynich', folios=fol, sections=sec)))
    for j, (kind, key, ids, n, truth, extra) in enumerate(items):
        key = f'{lam}|{key}'; info[key] = (kind, ids, truth, dict(extra, lam=lam))
        if key not in done: jobs.append((key, ids, n, 14500 + 97 * j, T, A, q, lam, iters, restarts))
    print(len(jobs), 'main runs', flush=True); run_jobs(jobs, info, done, alpha, dic, f)
    R = [r for r in done.values() if r.get('lam') == lam and r.get('stage') in ('gate', 'null', 'voynich')]
    gate = [r for r in R if r['stage'] == 'gate']; nu = [r for r in R if r['stage'] == 'null']
    vo = [r for r in R if r['stage'] == 'voynich']
    ok = sum(r['accuracy'] >= 0.8 for r in gate); bar = max(r['W'] for r in nu); med = float(np.median([r['W'] for r in vo]))
    S = dict(lambda_chosen=lam, tuning_mean_accuracy=tm, gate_ok=f'{ok}/{len(gate)}',
             gate_acc=sorted(round(r['accuracy'], 3) for r in gate), gate_W=sorted(r['W'] for r in gate),
             null_W=sorted(r['W'] for r in nu), bar_W=bar, voynich=[(r['key'], r['folios'], r['W']) for r in vo],
             voynich_median_W=med, alphabet=alpha, dict_types=len(dic))
    if ok < 9: v = 'not testable (gate failed)'
    elif med > bar:
        jobs, info = [], {}
        for j, (tag, s0, ws, fol, sec, _) in enumerate(manuscript(114, avoid_seed=14)):
            ids, n = encode(ws); key = f'{lam}|rep|{tag}|{s0}'
            info[key] = ('Voynich-rep', ids, None, dict(stage='rep', lam=lam, folios=fol, sections=sec))
            if key not in done: jobs.append((key, ids, n, 14900 + 97 * j, T, A, q, lam, iters, restarts))
        run_jobs(jobs, info, done, alpha, dic, f)
        rw = [r['W'] for r in done.values() if r.get('stage') == 'rep']; S['replicate_W'] = rw
        v = ('more vowelless-Latin words than meaningless text (replicated)' if np.median(rw) > bar
             else 'not replicated: no more words than meaningless text')
    else: v = 'no more vowelless-Latin words than meaningless text under this solver'
    S['verdict'] = v; S['elapsed_s'] = round(time.time() - t0, 1)
    if not smoke:
        json.dump(dict(summary=S, runs=sorted(done.values(), key=lambda r: r['key'])),
                  open('analysis/C014_results.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(S, ensure_ascii=False))

if __name__ == '__main__':
    main()
