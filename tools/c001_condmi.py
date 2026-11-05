#!/usr/bin/env python3
"""C001: conditional MI between Voynich vocabulary and page labels, with within-stratum permutation nulls."""
import re, sys, json, random, math
from collections import Counter, defaultdict
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else 'data/ZL3b-n.txt'
NPERM = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
K = int(sys.argv[3]) if len(sys.argv) > 3 else 300
rng = random.Random(20261104)

def parse(path):
    pages, cur = {}, None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip():
            continue
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m:
            cur = m.group(1)
            vars_ = dict(re.findall(r'\$(\w)=(\S+)', m.group(2)))
            pages[cur] = {'vars': vars_, 'words': []}
            continue
        m = re.match(r'<(f\w+)\.[^>]*>\s*(.*)', line)
        if not m or cur is None:
            continue
        t = m.group(2)
        t = re.sub(r'<[^>]*>', '', t)
        t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t)
        t = t.replace('{', '').replace('}', '').replace("'", '')
        for w in re.split(r'[.,\s]+', t):
            if w and '?' not in w and '*' not in w and re.fullmatch(r'[a-z]+', w):
                pages[cur]['words'].append(w)
    return pages

def counts_matrix(page_words, vocab):
    idx = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((len(page_words), len(vocab) + 1))
    for p, ws in enumerate(page_words):
        for w in ws:
            M[p, idx.get(w, len(vocab))] += 1
    return M

def mi(table):
    n = table.sum()
    if n == 0: return 0.0
    pxy = table / n
    px = pxy.sum(1, keepdims=True); py = pxy.sum(0, keepdims=True)
    nz = pxy > 0
    return float((pxy[nz] * np.log2(pxy[nz] / (px @ py)[nz])).sum())

def cmi(M, X, Y):
    tot = M.sum(); val = 0.0
    for y in set(Y):
        rows = [i for i, v in enumerate(Y) if v == y]
        labs = sorted(set(X[i] for i in rows))
        if len(labs) < 2: continue
        T = np.zeros((len(labs), M.shape[1]))
        for i in rows: T[labs.index(X[i])] += M[i]
        val += T.sum() / tot * mi(T)
    return val

def testable(X, Y):
    return sum(1 for y in set(Y) if len(set(X[i] for i, v in enumerate(Y) if v == y)) >= 2)

def perm_within(X, Y):
    X2 = list(X); groups = defaultdict(list)
    for i, y in enumerate(Y): groups[y].append(i)
    for idxs in groups.values():
        vals = [X[i] for i in idxs]; rng.shuffle(vals)
        for i, v in zip(idxs, vals): X2[i] = v
    return X2

def run_tests(page_words, S, H, L, nperm):
    allw = Counter(w for ws in page_words for w in ws)
    vocab = [w for w, _ in allw.most_common(K)]
    M = counts_matrix(page_words, vocab)
    tests = {'T1 I(W;H|S)': (H, S), 'T2 I(W;S|H)': (S, H), 'T3 I(W;L|S)': (L, S),
             'T4 I(W;S|L)': (S, L), 'T5 I(W;H|L)': (H, L)}
    out = {}
    for name, (X, Y) in tests.items():
        ns = testable(X, Y)
        if ns < 2:
            out[name] = {'status': 'not testable', 'strata_with_variation': ns}; continue
        obs = cmi(M, X, Y)
        null = np.array([cmi(M, perm_within(X, Y), Y) for _ in range(nperm)])
        p = (1 + (null >= obs).sum()) / (1 + nperm)
        out[name] = {'obs_bits': round(obs, 5), 'null_mean': round(float(null.mean()), 5),
                     'null_sd': round(float(null.std()), 5), 'excess_bits': round(obs - float(null.mean()), 5),
                     'z': round((obs - null.mean()) / (null.std() + 1e-12), 2), 'p': round(p, 5),
                     'strata_with_variation': ns, 'verdict': 'signal' if p < 0.01 else 'no detectable extra info'}
    return out

pages = parse(SRC)
keep = [p for p, d in pages.items() if d['vars'].get('H') in list('12345') and d['vars'].get('L') in ('A', 'B')
        and d['vars'].get('I') and d['words']]
PW = [pages[p]['words'] for p in keep]
S = [pages[p]['vars']['I'] for p in keep]; H = [pages[p]['vars']['H'] for p in keep]; L = [pages[p]['vars']['L'] for p in keep]
res = {'source': SRC, 'pages': len(keep), 'tokens': sum(map(len, PW)), 'types': len(set(w for ws in PW for w in ws)),
       'nperm': NPERM, 'K': K, 'crosstab_section_hand': Counter(f'{s}/{h}' for s, h in zip(S, H)),
       'crosstab_section_currier': Counter(f'{s}/{l}' for s, l in zip(S, L)),
       'crosstab_hand_currier': Counter(f'{h}/{l}' for h, l in zip(H, L))}
# C1 destroyed-signal control
flat = [w for ws in PW for w in ws]; rng.shuffle(flat)
C1, i = [], 0
for ws in PW: C1.append(flat[i:i + len(ws)]); i += len(ws)
# C2 planted hand-2 signal
C2 = [[('qxplantq' if (h == '2' and rng.random() < 0.03) else w) for w in ws] for ws, h in zip(C1, H)]
res['C1_shuffled'] = run_tests(C1, S, H, L, NPERM // 4)
res['C2_planted_hand2'] = run_tests(C2, S, H, L, NPERM // 4)
res['voynich'] = run_tests(PW, S, H, L, NPERM)
json.dump(res, open(f'analysis/C001_results_K{K}.json' if K != 300 else 'analysis/C001_results.json', 'w'), indent=1, default=dict)
print(json.dumps(res, indent=1, default=dict))
