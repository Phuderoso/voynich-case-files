#!/usr/bin/env python3
"""C084 (NEW FAMILY F-TOPIC, page-level topic models): does a page-level topic model fitted on half of each page's lines
predict the OTHER half of the same page better than a page-blind unigram model, by more than a calibrated
line-reassignment null allows; and is that topical gain inside natural language and inside the surface-matched
Timm-Schinner generator (C005 configuration)?
Model: PLSA (= KL-NMF, multiplicative EM updates, K = 8 topics, 150 iterations, fixed init seed) on the page x type count
matrix of the A lines (odd lines of every page: 1st, 3rd, ...). Prediction for page d: p(w|d) = (1-EPS) [W H]_d / sum
+ EPS u(w), EPS = 0.1, u = add-0.5 unigram of all A lines over the A vocabulary. Baseline = u.
G = mean over B-line tokens (even lines) whose type is in the A vocabulary of log2 p(w|d) / u(w)   (bits per token).
Null (structure-preserving): lines reassigned to pages at random (each page keeps its number of lines; lines intact),
then the same A/B split and fit.  X = G_obs - mean(G_null)  (bits/token);  p = (1 + #{G_null >= G_obs}) / (R + 1).
Samples: manuscript windows W1 = pages in file order from the start until >= 15,000 tokens, W2 = pages from the end
backwards until >= 15,000 tokens (pages with >= 40 paragraph tokens; ZL 3b and IT2a -> 4 measurements).
Comparators get pseudo-pages of contiguous lines cut to the SAME page-size sequence as the window (ZL sizes).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'  # 8 workers, 1 BLAS thread each
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c051_context_spelling_ab import nat_texts
import c004_generator_sweep as G
import c005_targeted_search as C5

SEED, K, EPS, ITERS, NTOK, MINP = 8484, 8, 0.1, 150, 15000, 40
R_MS, R_CMP = 99, 19
REF, HOLD, DEF = range(11286, 11306), range(11306, 11316), range(11316, 11321)
NPLANT_TOPICS, PLANT_TYPES = 8, 25
PLANT_F = float(os.environ.get('PLANT_F', '0.20'))

def plsa_gain(pages, rng, k=K):
    """pages: list of pages, each a list of lines (lists of tokens). Returns G (bits/token)."""
    A = [[w for i, l in enumerate(p) if i % 2 == 0 for w in l] for p in pages]
    B = [[w for i, l in enumerate(p) if i % 2 == 1 for w in l] for p in pages]
    voc = {w: j for j, w in enumerate(sorted({w for a in A for w in a}))}
    D, V = len(pages), len(voc); X = np.zeros((D, V))
    for d, a in enumerate(A):
        for w in a: X[d, voc[w]] += 1
    u = X.sum(0) + 0.5; u /= u.sum()
    W = rng.random((D, k)) + 0.1; H = rng.random((k, V)) + 0.1
    for _ in range(ITERS):
        Rm = X / (W @ H + 1e-12); H *= (W.T @ Rm) / (W.sum(0)[:, None] + 1e-12)
        Rm = X / (W @ H + 1e-12); W *= (Rm @ H.T) / (H.sum(1)[None, :] + 1e-12)
    P = W @ H; P /= P.sum(1, keepdims=True); P = (1 - EPS) * P + EPS * u[None, :]
    tot, n = 0.0, 0
    for d, b in enumerate(B):
        idx = [voc[w] for w in b if w in voc]
        if idx: tot += float(np.sum(np.log2(P[d, idx] / u[idx]))); n += len(idx)
    return tot / n if n else float('nan')

def reassign(pages, rng):
    lines = [l for p in pages for l in p]; sizes = [len(p) for p in pages]; perm = rng.permutation(len(lines))
    out, a = [], 0
    for s in sizes: out.append([lines[i] for i in perm[a:a + s]]); a += s
    return out

def test(args):
    name, pages, R, seed = args
    rng = np.random.default_rng(seed)
    g = plsa_gain(pages, np.random.default_rng([seed, 0]))
    nl = np.array([plsa_gain(reassign(pages, rng), np.random.default_rng([seed, i + 1])) for i in range(R)])
    return name, dict(G=g, null_mean=float(nl.mean()), null_sd=float(nl.std(ddof=1)), X=float(g - nl.mean()),
                      p=float((1 + (nl >= g).sum()) / (R + 1)), R=R, n_pages=len(pages),
                      n_tokens=sum(len(l) for p in pages for l in p))

def ms_windows(path):
    pl, lang, sect = ivtff_pages_lang(path); pages = {}
    for p, ws in pl: pages.setdefault(p, []).append(ws)
    order = [p for p in dict.fromkeys(p for p, _ in pl) if sum(map(len, pages[p])) >= MINP]
    def take(seq):
        out, t = [], 0
        for p in seq:
            if t >= NTOK: break
            out.append(p); t += sum(map(len, pages[p]))
        return out
    w1 = take(order); w2 = take(order[::-1])[::-1]
    assert not set(w1) & set(w2)
    return {'W1': w1, 'W2': w2}, pages, lang, sect

def cut(lines, sizes):
    """contiguous lines into pages with the given token-size sequence (a page closes when it reaches its size)"""
    out, cur, t, i = [], [], 0, 0
    for l in lines:
        if i >= len(sizes): break
        cur.append(l); t += len(l)
        if t >= sizes[i]: out.append(cur); cur, t = [], 0; i += 1
    return out if i == len(sizes) else None

def plant(pages, rng, f):
    """line-shuffled host (no page structure) + planted page topics: each page gets one of 8 topics (25 random types
    of frequency 5-50); a fraction f of its tokens is replaced by uniform draws from its topic"""
    host = reassign(pages, rng); c = Counter(w for p in host for l in p for w in l)
    mid = sorted(w for w, n in c.items() if 5 <= n <= 50)
    topics = [list(rng.choice(mid, PLANT_TYPES, replace=False)) for _ in range(NPLANT_TOPICS)]
    out = []
    for p in host:
        tp = topics[rng.integers(NPLANT_TOPICS)]
        out.append([[tp[rng.integers(len(tp))] if rng.random() < f else w for w in l] for l in p])
    return out

def gen_lines(cfg, s):
    c = dict(cfg); c['text.lines_to_create'] = 3600
    if 'text.initial_line' in c: c['text.initial_line'] = C5.LINES[c['text.initial_line']]
    return s, G.generate(c, s)

def call(x, sd, lo, hi):
    if x - 2 * sd > hi: return 'ABOVE'
    if x + 2 * sd < lo: return 'BELOW'
    if lo <= x <= hi: return 'INSIDE'
    return 'NOT CALLED'

def holm(ps, a=0.05):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for r, i in enumerate(o):
        if ps[i] <= a / (len(ps) - r): rej[i] = True
        else: break
    return rej

def main(design=False):
    t0 = time.time(); out = dict(seed=SEED, K=K, EPS=EPS, NTOK=NTOK, plant_f=PLANT_F)
    win, pagesZ, lang, sect = ms_windows('data/ZL3b-n.txt')
    winI, pagesI, _, _ = ms_windows('data/IT2a-n.txt')
    sizes = {w: [sum(map(len, pagesZ[p])) for p in win[w]] for w in win}
    out['windows'] = {w: dict(first=win[w][0], last=win[w][-1], n_pages=len(win[w]), n_tokens=sum(sizes[w]),
                              currier=dict(Counter(lang.get(p) for p in win[w])), sections=dict(Counter(sect.get(p) for p in win[w])))
                      for w in win}
    out['windows_IT2a'] = {w: dict(first=winI[w][0], last=winI[w][-1], n_pages=len(winI[w])) for w in winI}
    nat = nat_texts()
    with Pool(8) as pool:
        if design:
            jobs = [(f'plant_{w}_{i}', plant([pagesZ[p] for p in win[w]], np.random.default_rng([SEED, 99, i, len(w)]), PLANT_F), R_CMP, SEED * 7 + i)
                    for w in win for i in range(5)]
            jobs += [(f'shuf_ZL_{w}_{i}', reassign([pagesZ[p] for p in win[w]], np.random.default_rng([SEED, 98, i])), R_CMP, SEED * 9 + i)
                     for w in win for i in range(3)]
            for n, r in pool.map(test, jobs, chunksize=1): print(n, round(r['G'], 4), round(r['X'], 4), r['p'], flush=True)
            print('design runtime', round(time.time() - t0, 1)); return
        c5 = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
        gj = pool.starmap_async(gen_lines, [(c5, s) for s in list(REF) + list(HOLD)] + [({}, s) for s in DEF])
        jobs = []
        for w in win:
            jobs.append((f'Voynich_ZL3b_{w}', [pagesZ[p] for p in win[w]], R_MS, SEED + 1 + len(jobs)))
            jobs.append((f'Voynich_IT2a_{w}', [pagesI[p] for p in winI[w]], R_MS, SEED + 1 + len(jobs)))
            for n, L in nat.items():
                pg = cut(L, sizes[w]); jobs.append((f'nat_{n}_{w}', pg, R_CMP, SEED + 1 + len(jobs)))
            for i, n in enumerate(nat):  # FPR hosts: natural lines shuffled globally before paging
                L = [nat[n][j] for j in np.random.default_rng([SEED, 1, i]).permutation(len(nat[n]))]
                jobs.append((f'fpr_{n}_{w}', cut(L, sizes[w]), R_CMP, SEED + 1 + len(jobs)))
            jobs.append((f'fpr_ZL_{w}', reassign([pagesZ[p] for p in win[w]], np.random.default_rng([SEED, 2, len(w), int(w[1])])), R_CMP, SEED + 1 + len(jobs)))
            for i in range(5):
                jobs.append((f'plant_{w}_{i}', plant([pagesZ[p] for p in win[w]], np.random.default_rng([SEED, 3, int(w[1]), i]), PLANT_F), R_CMP, SEED + 1 + len(jobs)))
        GL = dict(gj.get()); print('generator done', round(time.time() - t0, 1), flush=True)
        miss = []
        for s, L in GL.items():
            kind = 'ref' if s in REF else 'hold' if s in HOLD else 'def'
            for w in win:
                pg = cut(L or [], sizes[w])
                if pg is None: miss.append((s, w)); continue
                jobs.append((f'gen_{kind}_{s}_{w}', pg, R_CMP, SEED + 1 + len(jobs)))
        assert all(j[1] for j in jobs), [j[0] for j in jobs if not j[1]]
        res = dict(pool.map(test, jobs, chunksize=1))
    out['generator_missing'] = miss; out['runs'] = res
    ms = [f'Voynich_{t}_{w}' for w in win for t in ('ZL3b', 'IT2a')]
    rej = holm([res[m]['p'] for m in ms])
    fpr = [n for n in res if n.startswith('fpr_')]; fp = sum(res[n]['p'] <= 0.05 for n in fpr)
    pl = [n for n in res if n.startswith('plant_')]; pw = sum(res[n]['p'] <= 0.05 for n in pl)
    g_fpr, g_pow = fp <= 2 and len(fpr) == 20, pw >= 8 and len(pl) == 10
    H = {}
    for w in win:
        natX = {n: res[f'nat_{n}_{w}']['X'] for n in nat}
        ref = [res[n]['X'] for n in res if n.startswith('gen_ref_') and n.endswith(w)]
        loo = {n: call(natX[n], res[f'nat_{n}_{w}']['null_sd'], min(v for m, v in natX.items() if m != n),
                       max(v for m, v in natX.items() if m != n)) for n in nat}
        hold = {n: call(res[n]['X'], res[n]['null_sd'], min(ref), max(ref)) for n in res if n.startswith('gen_hold_') and n.endswith(w)}
        H[w] = dict(nat_range=[min(natX.values()), max(natX.values())], nat_X=natX, gen_ref_range=[min(ref), max(ref)],
                    gen_ref_mean=float(np.mean(ref)), gen_ref_sd=float(np.std(ref, ddof=1)), n_ref=len(ref),
                    loo_calls=loo, loo_out=sum(c in ('ABOVE', 'BELOW') for c in loo.values()),
                    hold_calls=hold, hold_out=sum(c in ('ABOVE', 'BELOW') for c in hold.values()),
                    gen_default_X=[res[n]['X'] for n in res if n.startswith('gen_def_') and n.endswith(w)])
    g_loo = all(H[w]['loo_out'] <= 1 for w in win); g_hold = all(H[w]['hold_out'] <= 2 and len(H[w]['hold_calls']) == 10 for w in win)
    g_ref = all(H[w]['n_ref'] >= 18 for w in win)
    calls = {}
    for m in ms:
        w = m[-2:]; r = res[m]
        calls[m] = dict(X=r['X'], G=r['G'], p=r['p'], holm_reject=rej[ms.index(m)],
                        H2=call(r['X'], r['null_sd'], *H[w]['nat_range']), H3=call(r['X'], r['null_sd'], *H[w]['gen_ref_range']))
    if not (g_fpr and g_pow): H1 = 'NOT TESTABLE (gate)'
    elif all(rej): H1 = 'DETECTED'
    elif not any(rej): H1 = 'NOT DETECTED'
    else: H1 = 'SPLIT'
    def agg(key, gate):
        if not (g_fpr and g_pow and gate): return 'NOT TESTABLE (gate)'
        cs = {calls[m][key] for m in ms}
        return cs.pop() if len(cs) == 1 else 'MIXED (' + ', '.join(f"{m[8:]}:{calls[m][key]}" for m in ms) + ')'
    out.update(H=H, calls=calls, gates=dict(FPR=f'{fp}/{len(fpr)}', FPR_pass=g_fpr, power=f'{pw}/{len(pl)}', power_pass=g_pow,
               LOO_natural={w: H[w]['loo_out'] for w in win}, LOO_pass=g_loo, holdout_gen={w: H[w]['hold_out'] for w in win},
               holdout_pass=g_hold, ref_pass=g_ref),
               H1=H1, H2=agg('H2', g_loo), H3=agg('H3', g_hold and g_ref), runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C084_results.json', 'w'), indent=1)
    for m in ms: print(m, json.dumps(calls[m]))
    for w in win: print(w, 'nat', [round(x, 4) for x in H[w]['nat_range']], 'gen', [round(x, 4) for x in H[w]['gen_ref_range']],
                        'def', [round(x, 4) for x in H[w]['gen_default_X']], 'loo', H[w]['loo_out'], 'hold', H[w]['hold_out'])
    print('gates', out['gates']); print('H1', H1, '| H2', out['H2'], '| H3', out['H3']); print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main(design='--design' in sys.argv)
