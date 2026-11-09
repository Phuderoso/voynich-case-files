#!/usr/bin/env python3
"""C093 (NEW FAMILY F-NET, step 1): the GLOBAL one-glyph edit graph of word types, size-matched by prefix sampling.
Nodes = the first K distinct word types met in token order (all lengths; K = 4,000, reached by every reference text and both
transcriptions). Edge = one unit changed, inserted or deleted (Levenshtein 1), the "near" of Zhang & Sheng (arXiv 2610.34499,
Table 12). Units: Voynich = C003 glyph units (EVA with ch, sh, cth, ckh, cph, cfh as single glyphs, the Zhang & Sheng
convention); natural texts = letters; generator = C003 units. Frequency = token count inside the same prefix.
Statistics:  RHO = Spearman correlation of type frequency and degree (Zhang & Sheng's "neighbours and frequency",
             full-text ZL 0.587 / IT 0.577; natural texts in invented scripts at most 0.533).
             GIANT = share of the K types in the largest connected component.
References: the 9 natural texts (C077 set) and 10 fresh default Timm-Schinner generator runs, seeds 11474-11483 (8,000 lines;
next generator seed 11484). Two-sided predictive-t, t = (x - mean)/(sd*sqrt(1+1/n)), df n-1.
Cells: H1 RHO vs natural, H2 GIANT vs natural, H3 RHO vs generator, H4 GIANT vs generator; x ZL 3b, IT2a -> Holm over the
cells that pass their gates, alpha 0.05; a call needs both transcriptions.
Gates per cell (rehearsed BEFORE the pre-registration push on references only; manuscript untouched):
 G0 reach >= n-1 references reach K types. G1 false calls, leave-one-out at raw p < 0.05: <= 1/n.
 G2 power: each reference with extra one-edit copying planted (a share F of tokens replaced by a copy of one of the previous
    10 tokens with one random unit changed/inserted/deleted, units drawn from the text's own unit frequencies; F = 0.25 for
    naturals, 0.10 for the generator), cut at K, vs the other references unplanted: detected >= n-1.
 DOA (dead-on-arrival line): the effect of interest must exceed MDE80 -> RHO cells: Zhang & Sheng's gap 0.587 - 0.533 = 0.054;
    GIANT cells: 0.10 (smallest effect of interest, fixed before the rehearsal).
 A cell failing any gate is declared NOT RUN and LOW-POWER (NOT TESTABLE); it is not run on the manuscript.
Descriptive (no test): full-text RHO and near-neighbour share with the whole-text parse (all loci), to check Zhang & Sheng's
0.587 / 0.577 and 0.892 / 0.891 reproduce with our parse.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D
import c003_position_rigidity as T
D.N = 10 ** 9  # no token cap: prefix sampling by type count instead

SEED, K, LINES, ALPHA = 9393, 4000, 8000, 0.05
FN, FG = 0.25, 0.10
LEAD = {'RHO': 0.054, 'GIANT': 0.10}
GSEEDS = list(range(11474, 11484))
VPATH = {'ZL3b': 'data/ZL3b-n.txt', 'IT2a': 'data/IT2a-n.txt'}

def prefix(words, K):
    seen, cnt = [], Counter()
    for w in words:
        t = tuple(w)
        if t not in cnt:
            if len(seen) == K: break
            seen.append(t)
        cnt[t] += 1
    return seen, cnt

def graph_stats(types):
    idx = {t: i for i, t in enumerate(types)}; n = len(types)
    adj = [set() for _ in range(n)]; grp = defaultdict(list)
    for i, t in enumerate(types):
        for p in range(len(t)):
            grp[(p, t[:p] + t[p + 1:])].append(i)          # substitution groups
            j = idx.get(t[:p] + t[p + 1:])                  # deletion / insertion
            if j is not None and j != i: adj[i].add(j); adj[j].add(i)
    for g in grp.values():
        if len(g) > 1:
            for a in g:
                for b in g:
                    if a != b: adj[a].add(b)
    deg = np.array([len(a) for a in adj]); seen = np.zeros(n, bool); best = 0
    for s in range(n):
        if seen[s]: continue
        st, c = [s], 0; seen[s] = True
        while st:
            u = st.pop(); c += 1
            for v in adj[u]:
                if not seen[v]: seen[v] = True; st.append(v)
        best = max(best, c)
    return deg, best / n

def measure(words, K=K):
    types, cnt = prefix(words, K)
    if len(types) < K: return None
    deg, giant = graph_stats(types)
    rho = float(stats.spearmanr([cnt[t] for t in types], deg).correlation)
    return dict(RHO=rho, GIANT=float(giant), near_share=float((deg > 0).mean()), mean_deg=float(deg.mean()),
                tokens=int(sum(cnt.values())))

def plant(words, rng, F):
    u = Counter(x for w in words for x in w); syms = list(u); p = np.array([u[s] for s in syms], float); p /= p.sum()
    out = []
    for j, w in enumerate(words):
        w = list(w)
        if j >= 1 and rng.random() < F:
            src = list(out[j - 1 - rng.integers(min(10, j))]); op = rng.integers(3)
            if op == 2 and len(src) < 2: op = 0
            pos = int(rng.integers(len(src) + (op == 1)))
            if op == 0: src[pos] = syms[rng.choice(len(syms), p=p)]
            elif op == 1: src.insert(pos, syms[rng.choice(len(syms), p=p)])
            else: del src[pos]
            w = src
        out.append(tuple(w))
    return out

def job(spec):
    kind, name, s = spec; rng = np.random.default_rng([SEED, s])
    if kind == 'nat': ws = D.seqs_nat(*D.NAT[name]); F = FN
    else:
        import c004_generator_sweep as G
        Lg = G.generate({'text.lines_to_create': LINES}, s); ws = [tuple(D.T.units(w)) for l in (Lg or []) for w in l]; F = FG
    return kind, name, dict(ntokens=len(ws), ref=measure(ws), plant=measure(plant(ws, rng, F)))

def pt(x, ref):
    ref = np.asarray(ref, float); n = len(ref); t = (x - ref.mean()) / (ref.std(ddof=1) * math.sqrt(1 + 1 / n))
    return float(2 * stats.t.sf(abs(t), n - 1))

def mde(ref):
    ref = np.asarray(ref, float); n = len(ref); s = ref.std(ddof=1) * math.sqrt(1 + 1 / n)
    return float((stats.t.ppf(1 - ALPHA / 2, n - 1) + stats.norm.ppf(0.8)) * s)

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def gate(R, names, stat):
    n = len(names); ok_names = [m for m in names if R[m]['ref'] is not None]
    if len(ok_names) < n - 1: return dict(reached=len(ok_names), ok=False, why='G0')
    x = {m: R[m]['ref'][stat] for m in ok_names}
    xp = {m: R[m]['plant'][stat] for m in ok_names if R[m]['plant'] is not None}
    fpr = sum(pt(x[m], [x[o] for o in ok_names if o != m]) < ALPHA for m in ok_names)
    pw = sum(pt(xp[m], [x[o] for o in ok_names if o != m]) < ALPHA for m in xp)
    md = mde(list(x.values())); sh = float(np.mean([xp[m] - x[m] for m in xp]))
    why = 'G1' if fpr > 1 else 'G2' if pw < n - 1 else 'DOA' if LEAD[stat] <= md else ''
    return dict(reached=f'{len(ok_names)}/{n}', FPR=f'{fpr}/{len(ok_names)}', POW=f'{pw}/{len(xp)}', MDE80=md,
                plant_shift=sh, shift_over_MDE=sh / md, lead=LEAD[stat], lead_over_MDE=LEAD[stat] / md,
                mean=float(np.mean(list(x.values()))), sd=float(np.std(list(x.values()), ddof=1)),
                lo=min(x.values()), hi=max(x.values()), ok=why == '', why=why)

def main(mode):
    t0 = time.time()
    specs = [('nat', n, 100 + i) for i, n in enumerate(D.NAT)] + [('gen', f'gen_{s}', s) for s in GSEEDS]
    with Pool(8) as p: R = {n: o for k, n, o in p.map(job, specs)}
    nat = list(D.NAT); gen = [f'gen_{s}' for s in GSEEDS]
    cells = {'H1': (nat, 'RHO'), 'H2': (nat, 'GIANT'), 'H3': (gen, 'RHO'), 'H4': (gen, 'GIANT')}
    gates = {h: gate(R, refs, st) for h, (refs, st) in cells.items()}
    out = dict(seed=SEED, mode=mode, K=K, lines=LINES, FN=FN, FG=FG, gseeds=GSEEDS, refs=R, gates=gates)
    if mode == 'run':
        V = {tn: measure([tuple(w) for w in D.seqs_voy(p)]) for tn, p in VPATH.items()}
        full = {}
        for tn, p in VPATH.items():
            ws = [tuple(T.units(w)) for l in T.voynich(p) for w in l]; cnt = Counter(ws); ty = list(cnt)
            deg, giant = graph_stats(ty)
            full[tn] = dict(tokens=len(ws), types=len(ty), RHO=float(stats.spearmanr([cnt[t] for t in ty], deg).correlation),
                            near_share=float((deg > 0).mean()), mean_deg=float(deg.mean()), GIANT=float(giant))
        tests = []
        for h, (refs, st) in cells.items():
            ref = [R[m]['ref'][st] for m in refs if R[m]['ref'] is not None]
            for tn in VPATH:
                if not gates[h]['ok']: tests.append(dict(cell=f'{h}_{tn}', status='NOT RUN, LOW-POWER', why=gates[h]['why'])); continue
                x = V[tn][st]
                tests.append(dict(cell=f'{h}_{tn}', status='run', x=x, p=pt(x, ref), z=float((x - np.mean(ref)) / np.std(ref, ddof=1)),
                                  above_all=bool(x > max(ref)), below_all=bool(x < min(ref))))
        run = [t for t in tests if t['status'] == 'run']
        for t, a in zip(run, holm([t['p'] for t in run])): t['p_holm'] = a
        out.update(voynich=V, full_text_descriptive=full, tests=tests)
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    o = main(sys.argv[1]); json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    for m, v in o['refs'].items():
        f = lambda d: {k: round(x, 4) for k, x in d.items()} if d else None
        print(m, v['ntokens'], 'ref', f(v['ref']), 'plant', f(v['plant']))
    for h, g in o['gates'].items(): print(h, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items()})
    if o['mode'] == 'run':
        print('voynich', o['voynich']); print('full-text', o['full_text_descriptive'])
        for t in o['tests']: print(t)
    print('elapsed', round(o['elapsed_s'], 1))
