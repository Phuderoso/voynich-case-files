"""C029 (F-LEN step 3): per-sample goodness of fit of word-type lengths to a binomial, parametric bootstrap with refit.
Pre-registered in case-file/C029-word-length-goodness-of-fit.md. Seed 29029.
Run: timeout 600 python3 tools/c029_word_length_gof.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, random, time
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c027_word_length_binomial import fixed

SEED = 29029; W = 10000; K = 1000; S = 100; B = 200; NMAX = 25; LMAX = 41; C = 'data/corpora/'
COMB = np.zeros((NMAX + 1, LMAX)); KK = np.arange(LMAX)
for N in range(NMAX + 1):
    for k in range(N + 1): COMB[N, k] = comb(N, k)
NS = np.arange(1, NMAX + 1)[:, None]

def tv_fit(L):
    """L: int array of lengths (>=1). Returns (TV, N, p) of the best binomial, lengths-1 ~ Bin(N, mean/N)."""
    x = np.clip(L - 1, 0, LMAX - 1); emp = np.bincount(x, minlength=LMAX) / len(x)
    p = np.clip(x.mean() / NS, 1e-9, 1 - 1e-9)
    pmf = COMB[1:] * p ** KK * (1 - p) ** np.clip(NS - KK, 0, None); pmf[KK[None, :] > NS] = 0
    tv = 0.5 * np.abs(emp - pmf).sum(1); i = int(tv.argmin())
    return tv[i], i + 1, float(p[i, 0])

def gof_p(L, nrng):
    t, N, p = tv_fit(L); sims = nrng.binomial(N, p, size=(B, len(L))) + 1
    return (1 + sum(tv_fit(s)[0] >= t for s in sims)) / (B + 1)

def rej_rate(words, lenof, rng, nrng):
    ps = []; n = len(words)
    for _ in range(S):
        s = rng.randrange(n - W); types = sorted(set(words[s:s + W]))
        pick = rng.sample(types, K) if len(types) >= K else types
        ps.append(gof_p(np.array([lenof[w] for w in pick]), nrng))
    return sum(p < 0.05 for p in ps) / S, ps

def main():
    t0 = time.time(); rng = random.Random(SEED); nrng = np.random.default_rng(SEED)
    corp = {'Voynich_ZL3b': (T.voynich(fixed('data/ZL3b-n.txt')), T.units),
            'Latin_Caesar': (T.gutenberg(C + 'pg218.txt'), None), 'Latin_Descartes': (T.gutenberg(C + 'pg23306.txt'), None),
            'Italian_Dante': (T.gutenberg(C + 'pg1012.txt'), None), 'Italian_Machiavelli': (T.gutenberg(C + 'pg56498.txt'), None),
            'Spanish_Cervantes': (T.gutenberg(C + 'pg2000.txt'), None),
            'Hebrew_Genesis': (T.hebrew(C + 'Gen.xml'), None), 'Hebrew_Exodus': (T.hebrew(C + 'Exod.xml'), None),
            'Generator_TimmSchinner': ([l for l in ([re.findall(r'[a-z]+', x) for x in open(C + 'ts_generated_text.txt') if not x.startswith('#')]) if l], T.units)}
    words, lenof, R = {}, {}, {'K': K, 'S': S, 'B': B, 'seed': SEED, 'corpora': {}, 'calibration': {}, 'power': {}}
    for k, (lines, tok) in corp.items():
        ws = [w for l in lines for w in l]; words[k] = ws
        lenof[k] = {w: (len(tok(w)) if tok else len(w)) for w in set(ws)}
    nat = [k for k in corp if k not in ('Voynich_ZL3b', 'Generator_TimmSchinner')]
    for k in nat:   # gates first
        typ = sorted(lenof[k]); L = np.array([lenof[k][w] for w in typ]); _, N, p = tv_fit(L)
        P = dict(zip(typ, (nrng.binomial(N, p, len(typ)) + 1).tolist()))
        R['calibration'][k] = rej_rate(words[k], P, rng, nrng)[0]
        m = L.mean() - 1; v = 1.5 * m; r = m * m / (v - m)            # NB: mean m, var v
        Q = dict(zip(typ, (nrng.negative_binomial(r, r / (r + m), len(typ)) + 1).tolist()))
        R['power'][k] = rej_rate(words[k], Q, rng, nrng)[0]
        print('gate', k, R['calibration'][k], R['power'][k], round(time.time() - t0), flush=True)
    cal = list(R['calibration'].values())
    ok = sum(cal) / 7 <= 0.075 and max(cal) <= 0.15 and sum(v >= 0.8 for v in R['power'].values()) >= 6
    for k in corp:
        r, ps = rej_rate(words[k], lenof[k], rng, nrng)
        R['corpora'][k] = {'reject_rate': r, 'median_p': sorted(ps)[S // 2]}
        print(k, R['corpora'][k], round(time.time() - t0), flush=True)
    rv = R['corpora']['Voynich_ZL3b']['reject_rate']; nrej = sum(R['corpora'][k]['reject_rate'] >= 0.5 for k in nat)
    R['gates_pass'] = ok
    R['verdict_voynich'] = 'NOT TESTABLE' if not ok else ('consistent with binomial' if rv <= 0.10 else 'rejected' if rv >= 0.5 else 'inconclusive')
    R['verdict_distinctive'] = 'NOT TESTABLE' if not ok else ('SUPPORTED' if rv <= 0.10 and nrej >= 6 else 'NOT SUPPORTED')
    R['controls_rejected'] = nrej; R['seconds'] = round(time.time() - t0, 1)
    print(json.dumps({k: R[k] for k in ('calibration', 'power', 'gates_pass', 'verdict_voynich', 'verdict_distinctive', 'controls_rejected', 'seconds')}, indent=1))
    json.dump(R, open('analysis/C029_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
