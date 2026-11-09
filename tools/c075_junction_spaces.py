#!/usr/bin/env python3
"""C075 — F-JUNC step 2: is the word-junction dependence of C074 an artefact of uncertain word spaces?
Data: ZL3b only (IT2a has no uncertain-space mark: 0 commas in paragraph lines, so it cannot answer this question).
Lines: C070 parser rules (paragraph loci, no '<->', every word [a-z]+ after markup removal, >= 5 words), but the separator
between adjacent words is kept: 'unc' if the separator run contains ',' (ZL uncertain space), else 'cert'.
Pairs: adjacent interior words (positions 2..n-1), as in C074. Classes: 8 commonest finals / 10 commonest initials + other
(fixed per language from its own interior counts, as C074). MI = plug-in mutual information (bits).
H1 (per Currier language): MI over certain-space pairs only vs page-shuffle null (interior words shuffled among interior slots
 of the same page; pair slots keep their separator label), R = 500, one-sided rank p.
 Gates (20 reps): FPR <= 2/20 on page-shuffled text; power >= 16/20 with C074's planted junction rule (q 0.05, all pairs).
H2 (per Currier language): D = MI(uncertain pairs) - mean over 20 random size-matched subsamples of MI(certain pairs).
 Null: separator labels permuted among the interior pairs of the same page (text fixed), R = 500, one-sided (D > 0).
 Gates (20 reps, base = page-shuffled text + C074 plant q 0.05 on all pairs): FPR <= 2/20 on the base;
 power >= 16/20 with an extra plant (q 0.10) on uncertain pairs only.
Holm over the gated tests among the 4 (alpha 0.05).
Generator (descriptive, pre-registered criterion): 20 default Timm-Schinner runs (fresh seeds 11001-11020, 1,500 lines,
 pseudo-pages of 29 lines, lines >= 5 words); per run, mean MI over 20 subsamples of N pairs, N = manuscript Currier-B
 certain-pair count. Manuscript Currier-B certain-pair MI is ABOVE / INSIDE / BELOW the run range.
Descriptive: share of uncertain separators in the C074 seam cells (y.q, r.a, n.ch, n.o, s.a, l.k) vs all pairs.
Seed 7575. Mode 'inventory' prints label-free counts only (no MI).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from multiprocessing import Pool
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T3
from c004_generator_sweep import generate

SEED, R, NG, NSUB, Q1, Q2, ALPHA = 7575, 500, 20, 20, 0.05, 0.10, 0.05
KF, KI = 8, 10
ZL = 'data/ZL3b-n.txt'

def parse(path=ZL):
    meta, out = {}, []
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m or not m.group(4).startswith('P'): continue
        page, t = m.group(1), m.group(5)
        if '<->' in t: continue
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        parts = re.split(r'([.,\s]+)', t.strip(' .,'))
        ws, seps = parts[0::2], parts[1::2]
        ws = [w for w in ws]
        if len(ws) < 5 or not all(re.fullmatch(r'[a-z]+', w) for w in ws): continue
        lab = [1 if ',' in s else 0 for s in seps]  # 1 = uncertain
        d = meta.get(page, {}); out.append(dict(page=page, L=d.get('L'), words=ws, unc=lab))
    return out

class Data:
    """Per page: codes (final class, initial class) of interior words; pair slots (i, i+1) with separator labels."""
    def __init__(self, pages):
        fin, ini = Counter(), Counter()
        for p in pages:
            for ws, _ in p:
                for w in ws[1:-1]:
                    u = T3.units(w); fin[u[-1]] += 1; ini[u[0]] += 1
        self.fmap = {u: i for i, (u, _) in enumerate(fin.most_common(KF))}
        self.imap = {u: i for i, (u, _) in enumerate(ini.most_common(KI))}
        self.P = []
        for p in pages:
            codes, I, L = [], [], []
            for ws, unc in p:
                s = len(codes)
                for w in ws[1:-1]:
                    u = T3.units(w); codes.append((self.fmap.get(u[-1], KF), self.imap.get(u[0], KI)))
                for k in range(1, len(ws) - 2):  # pair of interior words k, k+1 (0-indexed), separator unc[k]
                    I.append(s + k - 1); L.append(unc[k])
            if I: self.P.append((np.array(codes, int).reshape(-1, 2), np.array(I, int), np.array(L, int)))

def pairs(P, which=None):
    f, g = [], []
    for c, I, L in P:
        sel = I if which is None else I[L == which]
        f.append(c[sel, 0]); g.append(c[sel + 1, 1])
    return np.concatenate(f), np.concatenate(g)

def mi(f, g):
    tab = np.bincount(f * (KI + 1) + g, minlength=(KF + 1) * (KI + 1)).reshape(KF + 1, KI + 1).astype(float)
    n = tab.sum(); pxy = tab / n; px = pxy.sum(1, keepdims=True); py = pxy.sum(0, keepdims=True); nz = pxy > 0
    return float((pxy[nz] * np.log2(pxy[nz] / (px @ py)[nz])).sum())

def shuffle(P, rng): return [(c[rng.permutation(len(c))], I, L) for c, I, L in P]
def relabel(P, rng): return [(c, I, L[rng.permutation(len(L))]) for c, I, L in P]

def plant(P, rng, target, q, only_unc=False):
    out = []
    for c, I, L in P:
        c = c.copy()
        for i, l in zip(I, L):
            if only_unc and not l: continue
            if rng.random() < q:
                cand = np.flatnonzero(c[:, 1] == target[c[i, 0]])
                if len(cand): j = cand[rng.integers(len(cand))]; c[[i + 1, j]] = c[[j, i + 1]]
        out.append((c, I, L))
    return out

def h1(P, rng):
    obs = mi(*pairs(P, 0)); null = np.array([mi(*pairs(shuffle(P, rng), 0)) for _ in range(R)])
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (R + 1))

def dstat(P, rng):
    fu, gu = pairs(P, 1); fc, gc = pairs(P, 0); n = len(fu)
    sub = [mi(fc[s], gc[s]) for s in (rng.choice(len(fc), n, replace=False) for _ in range(NSUB))]
    return mi(fu, gu) - float(np.mean(sub)), mi(fu, gu), float(np.mean(sub))

def h2(P, rng):
    obs = dstat(P, rng)[0]; null = np.array([dstat(relabel(P, rng), rng)[0] for _ in range(R)])
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (R + 1))

def lang_pages(lang):
    by = {}
    for l in parse():
        if l['L'] == lang: by.setdefault(l['page'], []).append((l['words'], l['unc']))
    return list(by.values())

def job(a):
    lang, kind = a; D = Data(lang_pages(lang)); i = ('A', 'B').index(lang); seed = SEED * 10 + i * 2 + (kind == 'H2')
    target = np.random.default_rng(seed).integers(0, KI, KF + 1); fp = pw = 0
    if kind == 'H1':
        obs, nm, p = h1(D.P, np.random.default_rng(seed))
        for g in range(NG):
            rng = np.random.default_rng(seed * 100 + g); S = shuffle(D.P, rng)
            fp += h1(S, rng)[2] <= ALPHA; pw += h1(plant(S, rng, target, Q1), rng)[2] <= ALPHA
        return lang, kind, dict(MI_cert=obs, MI_null=nm, X=obs - nm, p=p, fpr=int(fp), power=int(pw), gate=fp <= 2 and pw >= 16)
    rng0 = np.random.default_rng(seed); obs, nm, p = h2(D.P, rng0); _, mu, mc = dstat(D.P, rng0)
    for g in range(NG):
        rng = np.random.default_rng(seed * 100 + g); B = plant(shuffle(D.P, rng), rng, target, Q1)
        fp += h2(B, rng)[2] <= ALPHA; pw += h2(plant(B, rng, target, Q2, True), rng)[2] <= ALPHA
    return lang, kind, dict(D=obs, D_null_mean=nm, MI_unc=mu, MI_cert_matched=mc, p=p, fpr=int(fp), power=int(pw), gate=fp <= 2 and pw >= 16)

def gen_job(a):
    s, N = a
    Lg = [l for l in (generate({'text.lines_to_create': 1500}, s) or []) if len(l) >= 5]
    if len(Lg) < 1000: return s, None
    D = Data([[(w, [0] * (len(w) - 1)) for w in Lg[i:i + 29]] for i in range(0, len(Lg), 29)])
    f, g = pairs(D.P, 0); rng = np.random.default_rng(s); n = min(N, len(f))
    return s, dict(n_pairs=len(f), N_used=n, MI=float(np.mean([mi(f[x], g[x]) for x in (rng.choice(len(f), n, replace=False) for _ in range(NSUB))])))

SEAMS = [('y', 'q'), ('r', 'a'), ('n', 'ch'), ('n', 'o'), ('s', 'a'), ('l', 'k')]

def descriptive(lang):
    out = {}; tot = Counter()
    for p in lang_pages(lang):
        for ws, unc in p:
            for k in range(1, len(ws) - 2):
                a, b = T3.units(ws[k])[-1], T3.units(ws[k + 1])[0]; tot[(a, b, unc[k])] += 1; tot[('*', '*', unc[k])] += 1
    for a, b in SEAMS + [('*', '*')]:
        n = tot[(a, b, 0)] + tot[(a, b, 1)]; out[f'{a}.{b}'] = dict(n=n, unc=tot[(a, b, 1)], share_unc=tot[(a, b, 1)] / max(n, 1))
    return out

def inventory():
    for lang in ('A', 'B'):
        D = Data(lang_pages(lang)); n = sum(len(I) for _, I, _ in D.P); u = sum(int(L.sum()) for _, _, L in D.P)
        print(lang, 'pages', len(D.P), 'interior pairs', n, 'uncertain', u, 'certain', n - u)

def main():
    t0 = time.time()
    with Pool(8) as pool:
        DB = Data(lang_pages('B')); NB = sum(int((L == 0).sum()) for _, _, L in DB.P)
        gj = pool.map_async(gen_job, [(s, NB) for s in range(11001, 11021)], chunksize=1)
        T = {f'{k}_{l}': r for l, k, r in pool.map(job, [(l, k) for k in ('H1', 'H2') for l in ('A', 'B')], chunksize=1)}
        print('tests', json.dumps(T), flush=True)
        G = [r for _, r in gj.get() if r]
    names = [t for t in T if T[t]['gate']]; ps = [T[t]['p'] for t in names]; rej, stop = {}, False
    for r, i in enumerate(np.argsort(ps)):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for t in T:
        if not T[t]['gate']: ver[t] = 'NOT TESTABLE'
        elif t.startswith('H1'): ver[t] = 'DETECTED' if rej[t] else 'NOT DETECTED'
        else: ver[t] = 'UNCERTAIN STRONGER' if rej[t] else 'NO DIFFERENCE SHOWN'
    mm = [g['MI'] for g in G]; v = T['H1_B']['MI_cert']
    gv = dict(n=len(G), N=NB, MI_min=min(mm), MI_max=max(mm), MI_mean=float(np.mean(mm)), manuscript_B_cert=v,
              position='ABOVE' if v > max(mm) else 'BELOW' if v < min(mm) else 'INSIDE')
    out = dict(seed=SEED, tests=T, holm=rej, verdict=ver, generator=gv, generator_runs=G,
               descriptive={l: descriptive(l) for l in ('A', 'B')}, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C075_results.json', 'w'), indent=1)
    for k in ('holm', 'verdict', 'generator', 'descriptive', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    inventory() if sys.argv[1:] == ['inventory'] else main()
