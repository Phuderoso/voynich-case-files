#!/usr/bin/env python3
"""C002: calibration audit of C001's page-permutation null (N0) vs a size-blocked null (N1), then Voynich re-run.
Usage: python3 tools/c002_null_audit.py [stage]   stages: calib, power, voynich (default: all). Resumable via analysis/C002_*.json"""
import sys, json, os, random
from collections import Counter, defaultdict
import numpy as np
src = open('tools/c001_condmi.py').read().split('\npages = parse(SRC)')[0]   # reuse C001 parser only
_argv = sys.argv; sys.argv = [_argv[0]]
ns = {}; exec(compile(src.replace("sys.argv[1] if len(sys.argv) > 1 else ", ""), 'c001', 'exec'), ns)
parse = ns['parse']; sys.argv = _argv

pages = parse('data/ZL3b-n.txt')
keep = [p for p, d in pages.items() if d['vars'].get('H') in list('12345') and d['vars'].get('L') in ('A', 'B')
        and d['vars'].get('I') and d['words']]
PW = [pages[p]['words'] for p in keep]
S = [pages[p]['vars']['I'] for p in keep]; H = [pages[p]['vars']['H'] for p in keep]; L = [pages[p]['vars']['L'] for p in keep]
SL = [s + l for s, l in zip(S, L)]
SIZES = np.array([len(w) for w in PW])
TESTS = {'T1 I(W;H|S)': (H, S), 'T2 I(W;S|H)': (S, H), 'T3 I(W;L|S)': (L, S), 'T4 I(W;S|L)': (S, L),
         'T5 I(W;H|L)': (H, L), 'T6 I(W;H|SxL)': (H, SL)}

def matrix(pw, K):
    allw = Counter(w for ws in pw for w in ws); vocab = {w: i for i, (w, _) in enumerate(allw.most_common(K))}
    M = np.zeros((len(pw), K + 1))
    for p, ws in enumerate(pw):
        for w in ws: M[p, vocab.get(w, K)] += 1
    return M

def mi(T):
    n = T.sum(); P = T / n; px = P.sum(1, keepdims=True); py = P.sum(0, keepdims=True); nz = P > 0
    return float((P[nz] * np.log2(P[nz] / (px @ py)[nz])).sum())

class Test:
    def __init__(self, X, Y):
        self.strata = []
        for y in sorted(set(Y)):
            rows = np.array([i for i, v in enumerate(Y) if v == y])
            labs = sorted(set(X[i] for i in rows))
            if len(labs) < 2: continue
            code = np.array([labs.index(X[i]) for i in rows])
            order = rows[np.argsort(SIZES[rows], kind='stable')]
            blocks = [order[i:i + 4] for i in range(0, len(order), 4)]
            if len(blocks) > 1 and len(blocks[-1]) < 4: blocks[-2] = np.concatenate([blocks[-2], blocks[-1]]); blocks.pop()
            pos = {r: k for k, r in enumerate(rows)}
            self.strata.append((rows, code, len(labs), [np.array([pos[r] for r in b]) for b in blocks]))
        self.testable = len(self.strata) >= 2
    def stat(self, M, codes=None):
        tot = M.sum(); v = 0.0
        for k, (rows, code, nl, _) in enumerate(self.strata):
            c = code if codes is None else codes[k]
            T = np.zeros((nl, M.shape[1])); np.add.at(T, c, M[rows]); v += T.sum() / tot * mi(T)
        return v
    def perm(self, rng, null):
        out = []
        for rows, code, nl, blocks in self.strata:
            c = code.copy()
            if null == 'N0': c = rng.permutation(c)
            else:
                for b in blocks: c[b] = c[rng.permutation(b)]
            out.append(c)
        return out
    def pval(self, M, rng, null, nperm):
        obs = self.stat(M); nl = np.array([self.stat(M, self.perm(rng, null)) for _ in range(nperm)])
        return obs, nl, (1 + (nl >= obs).sum()) / (1 + nperm)

def c1(seed):
    r = random.Random(seed); flat = [w for ws in PW for w in ws]; r.shuffle(flat); out, i = [], 0
    for ws in PW: out.append(flat[i:i + len(ws)]); i += len(ws)
    return out

def save(name, obj): json.dump(obj, open(f'analysis/C002_{name}.json', 'w'), indent=1)
def load(name):
    f = f'analysis/C002_{name}.json'; return json.load(open(f)) if os.path.exists(f) else None

stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
T5only = {k: Test(*v) for k, v in TESTS.items() if k != 'T6 I(W;H|SxL)'}
if stage in ('calib', 'all'):
    res = load('calib') or {}
    for seed in range(1, 41):
        if str(seed) in res: continue
        txt = c1(seed); rng = np.random.default_rng(seed); res[str(seed)] = {}
        for K in (300, 1000):
            M = matrix(txt, K)
            for null in ('N0', 'N1'):
                res[str(seed)][f'K{K}_{null}'] = {t: round(T.pval(M, rng, null, 200)[2], 4) for t, T in T5only.items()}
        save('calib', res); print('calib seed', seed, flush=True)
if stage in ('power', 'all'):
    res = load('power') or {}
    T1 = Test(H, S)
    for seed in range(101, 121):
        if str(seed) in res: continue
        r = random.Random(seed)
        txt = [[('qxplantq' if (h == '2' and r.random() < 0.03) else w) for w in ws] for ws, h in zip(c1(seed), H)]
        rng = np.random.default_rng(seed); res[str(seed)] = {}
        for K in (300, 1000):
            M = matrix(txt, K)
            for null in ('N0', 'N1'): res[str(seed)][f'K{K}_{null}'] = round(T1.pval(M, rng, null, 200)[2], 4)
        save('power', res); print('power seed', seed, flush=True)
if stage in ('voynich', 'all'):
    null = sys.argv[2] if len(sys.argv) > 2 else 'N1'
    res = load(f'voynich_{null}') or {}
    rng = np.random.default_rng(20261105)
    for K in (300, 1000):
        M = matrix(PW, K)
        for t, args in TESTS.items():
            key = f'K{K} {t}'
            if key in res: continue
            T = Test(*args)
            if not T.testable: res[key] = {'status': 'not testable'}; continue
            obs, nl, p = T.pval(M, rng, null, 2000)
            res[key] = {'obs_bits': round(obs, 5), 'null_mean': round(float(nl.mean()), 5), 'null_sd': round(float(nl.std()), 5),
                        'excess_bits': round(obs - float(nl.mean()), 5), 'z': round(float((obs - nl.mean()) / (nl.std() + 1e-12)), 2),
                        'p': round(float(p), 5), 'strata': len(T.strata)}
            save(f'voynich_{null}', res); print(key, res[key], flush=True)
