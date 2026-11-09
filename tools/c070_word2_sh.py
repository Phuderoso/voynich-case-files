#!/usr/bin/env python3
"""C070 (F-LINE step 5; external claim test): is the second word of a paragraph line unusually often sh-initial?
Claim under test: N. Pelling, Cipher Mysteries, 2026-11-08, 'The mysterious Word 2 sh-initial boost' (Quire 20, Takahashi:
top lines 21.2% vs 9.9% mid-line; other lines 16.7% vs 6.8%).
Lines: paragraph loci (P*), no drawing break '<->', every word [a-z]+ after markup removal (C068 parser rules), >= 5 words.
Top line = text starts a paragraph ('<%>'). Positions 1-indexed; word 1 and the last two words are excluded from the test.
Statistic D = share of sh-initial words at position 2 - share at positions 3..n-2 (pooled over lines).
Null: within every line, words at positions 2..n-2 are permuted (word 1 and last two fixed); R = 4000; p = (1+#D*>=D)/(R+1).
Tests (Holm over 6): {Q20 ($Q=T), Currier A, Currier B outside Q20} x {IT2a, ZL3b}.
Gates per test (20 pseudo replicates from the subset's own lines with positions 2..n-2 shuffled, seed 7070):
 FPR p<=0.05 in <=2/20; power: same pseudo lines, with probability 0.10 per line, if word 2 is not sh-initial and an
 sh-initial word sits at 3..n-2, swap them -> p<=0.05 in >=16/20. A failed gate -> that test NOT TESTABLE.
Verdict per subset: REPLICATED if both transcriptions reject; PARTIAL if one; NOT DETECTED if none (gates pass).
Generator family (separate, alpha 0.05): manuscript Currier-B (all B incl. Q20, IT2a) D vs 40 default Timm-Schinner runs
(fresh seeds 10301-10345, first 40 valid, 1,500 lines, lines >= 5 words); rank p = (1+#gen D >= V)/41.
Gates: 20 held-out runs (10401-10425): FPR <= 2/20; power (same plant, q 0.10) >= 16/20.
Descriptive: shares by position (1..6, mid, last-1, last) for top/other lines; D for other initial glyph groups in B.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c004_generator_sweep import generate

SEED, R, NG, Q, ALPHA = 7070, 4000, 20, 0.10, 0.05
FILES = (('IT2a', 'data/IT2a-n.txt'), ('ZL3b', 'data/ZL3b-n.txt'))
INIT = ('sh', 'ch', 'q', 'o', 'd', 'y', 's', 'k', 't', 'p', 'a', 'l', 'c')

def parse(path):
    meta, out = {}, []
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m or not m.group(4).startswith('P'): continue
        page, t = m.group(1), m.group(5)
        if '<->' in t: continue
        top = t.lstrip().startswith('<%>')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        if len(ws) < 5 or not all(re.fullmatch(r'[a-z]+', w) for w in ws): continue
        d = meta.get(page, {}); out.append(dict(page=page, Q=d.get('Q'), L=d.get('L'), top=top, words=ws))
    return out

def is_sh(w): return w.startswith('sh')

def flags(lines, f=is_sh): return [np.array([f(w) for w in l['words']], bool) for l in lines]

def stat(F):
    a = sum(int(x[1]) for x in F); b = sum(int(x[2:-2].sum()) for x in F); nb = sum(len(x) - 4 for x in F)
    return a / len(F) - b / max(nb, 1)

def perm_test(F, rng):
    obs = stat(F); n = np.array([len(x) - 3 for x in F]); k = np.array([int(x[1:-2].sum()) for x in F])
    nb = (n - 1).sum(); null = np.empty(R)
    # under permutation, word 2 is sh with prob k/n; mid sum = k - word2
    for r in range(R):
        w2 = rng.random(len(F)) < k / n; null[r] = w2.mean() - (k - w2).sum() / nb
    return obs, float((1 + (null >= obs).sum()) / (R + 1))

def shuffled(F, rng):
    out = []
    for x in F:
        y = x.copy(); mid = y[1:-2].copy(); rng.shuffle(mid); y[1:-2] = mid; out.append(y)
    return out

def plant(F, rng, q=Q):
    out = []
    for x in F:
        y = x.copy()
        if not y[1] and rng.random() < q:
            c = np.flatnonzero(y[2:-2])
            if len(c): j = 2 + int(c[rng.integers(len(c))]); y[1], y[j] = True, False
        out.append(y)
    return out

def gate(F, seed):
    fp = pw = 0
    for i in range(NG):
        rng = np.random.default_rng(seed * 100 + i); S = shuffled(F, rng)
        fp += perm_test(S, rng)[1] <= ALPHA; pw += perm_test(plant(S, rng), rng)[1] <= ALPHA
    return int(fp), int(pw)

def subsets(lines):
    return {'Q20': [l for l in lines if l['Q'] == 'T'], 'A': [l for l in lines if l['L'] == 'A'],
            'B_noQ20': [l for l in lines if l['L'] == 'B' and l['Q'] != 'T'], 'B_all': [l for l in lines if l['L'] == 'B']}

def test_job(a):
    k, sub = a; lines = subsets(parse(dict(FILES)[k]))[sub]; F = flags(lines)
    d, p = perm_test(F, np.random.default_rng(SEED)); fp, pw = gate(F, SEED + {'Q20': 1, 'A': 2, 'B_noQ20': 3}[sub] + (0 if k == 'IT2a' else 50))
    return k, sub, dict(n_lines=len(F), D=d, p=p, fpr=fp, power=pw, gate=fp <= 2 and pw >= 16,
                        share2=sum(int(x[1]) for x in F) / len(F), share_mid=sum(int(x[2:-2].sum()) for x in F) / sum(len(x) - 4 for x in F))

def gen_job(s):
    Lg = generate({'text.lines_to_create': 1500}, s)
    if not Lg: return s, None
    F = flags([dict(words=l) for l in Lg if len(l) >= 5])
    if len(F) < 1000: return s, None
    rng = np.random.default_rng(SEED * 10 + s)
    return s, dict(D=stat(F), D_plant=stat(plant(F, rng)), n=len(F))

def profile(lines, f=is_sh):
    P = {}
    for grp, sel in (('top', [l for l in lines if l['top']]), ('other', [l for l in lines if not l['top']])):
        F = flags(sel, f); row = {}
        for i in range(6): row[f'w{i + 1}'] = float(np.mean([x[i] for x in F if len(x) > i + 2]))
        row['mid3..n-2'] = sum(int(x[2:-2].sum()) for x in F) / sum(len(x) - 4 for x in F)
        row['last-1'] = float(np.mean([x[-2] for x in F])); row['last'] = float(np.mean([x[-1] for x in F])); row['n'] = len(F)
        P[grp] = row
    return P

def main():
    t0 = time.time()
    with Pool(8) as pool:
        tj = pool.map_async(test_job, [(k, s) for k, _ in FILES for s in ('Q20', 'A', 'B_noQ20')])
        gj = pool.map_async(gen_job, list(range(10301, 10346)) + list(range(10401, 10426)))
        L = {k: parse(f) for k, f in FILES}
        V = {k: stat(flags(subsets(L[k])['B_all'])) for k in L}; print('B_all D', V, flush=True)
        T = {f'{k}_{s}': r for k, s, r in tj.get()}; print('tests', json.dumps(T), flush=True)
        G = dict(gj.get())
    names = [t for t in T if T[t]['gate']]; ps = [T[t]['p'] for t in names]
    o = np.argsort(ps); rej = {}; stop = False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for s in ('Q20', 'A', 'B_noQ20'):
        if not all(T[f'{k}_{s}']['gate'] for k, _ in FILES): ver[s] = 'NOT TESTABLE'; continue
        m = sum(rej.get(f'{k}_{s}', False) for k, _ in FILES); ver[s] = 'REPLICATED' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    ref = [G[s]['D'] for s in range(10301, 10346) if G.get(s)][:40]
    ho = [G[s] for s in range(10401, 10426) if G.get(s)][:20]
    pr = lambda v: float((1 + sum(x >= v for x in ref)) / (len(ref) + 1))
    gg = dict(n_ref=len(ref), n_ho=len(ho), fpr=int(sum(pr(h['D']) <= ALPHA for h in ho)), power=int(sum(pr(h['D_plant']) <= ALPHA for h in ho)))
    gg['pass'] = gg['fpr'] <= 2 and gg['power'] >= 16 and len(ref) == 40 and len(ho) == 20
    gtest = dict(V=V['IT2a'], p=pr(V['IT2a']), ref_min=min(ref), ref_median=float(np.median(ref)), ref_max=max(ref), gates=gg,
                 verdict=('NOT TESTABLE' if not gg['pass'] else 'ABOVE GENERATOR' if pr(V['IT2a']) <= ALPHA else 'NOT DETECTED'),
                 ZL_descriptive=dict(V=V['ZL3b'], p=pr(V['ZL3b'])))
    prof = {k: {s: profile(subsets(L[k])[s]) for s in ('Q20', 'A', 'B_all')} for k in L}
    other = {}
    for g in INIT:
        f = (lambda w, g=g: w.startswith(g) and not (g == 's' and w.startswith('sh')) and not (g == 'c' and w.startswith('ch')))
        other[g] = {k: stat(flags(subsets(L[k])['B_all'], f)) for k in L}
    out = dict(seed=SEED, R=R, Q=Q, tests=T, holm=rej, verdict=ver, generator=gtest, profile=prof, other_initials_D_B=other,
               runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C070_results.json', 'w'), indent=1)
    for k in ('tests', 'holm', 'verdict', 'generator', 'other_initials_D_B', 'runtime_s'): print(k, json.dumps(out[k]))
    print('profile', json.dumps(prof['IT2a']))

if __name__ == '__main__':
    main()
