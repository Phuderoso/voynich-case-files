#!/usr/bin/env python3
"""C133 (F-DIAL step 3): does Fagin Davis's scribal hand $H carry the Currier A/B mixture, within section?
See case-file/C133-hand-stratum.md (the pre-registration); this docstring is a summary.
REUSE (credit): instrument and plants IMPORTED unchanged from tools/c131_intermediate_pages.py (sha256 259472b3...f1d3ea):
 Inst (add-0.5 leave-out A/B unigram profiles, lam-hat on {0,.01,..,1}, d = distance from own pole), N-RUN pseudo-pages
 (n consecutive tokens of the page's own (L, I) stratum, donors left out), own-page line plants (other-language whole lines).
PAGE SCORE. e_i = d_i - mean(N-RUN null d of page i), R = 400 fresh replicates (seed 11915). e removes the section/length baseline.
UNITS. Currier B pages, INFORMATIVE under the C131 rule, with a numeric hand $H (ZL3b headers for both transcriptions).
T1 (primary, hand 5). S5 = mean e over hand-5 pages. Null: hand labels permuted WITHIN SECTION $I (section composition fixed),
 EXACT enumeration; p = #{S >= S5} / #arrangements (observed arrangement included).
T2 (omnibus, all hands). W = sum over sections s, hands h of n_sh (mean e_sh - mean e_s)^2. Null: within-section label permutation,
 Monte Carlo 20000 (seed 11918), p = (1 + #{W* >= W}) / 20001.
POWER + FPR (pseudo-hand, ZL3b, seed 11916 plants / 11917 planted-page nulls): real hand-5 pages removed; a pseudo-hand with hand 5's
 section composition (3 herbal-B + 1 T page) drawn from the other-hand pages; f of each pseudo-hand page's lines replaced by
 other-language lines (C131 plant); planted e uses a null of the planted length (R 100); T1 (exact) and T2 (MC 2000) recomputed.
 f in {0, .05, ..., .5}, 200 simulations each. f = 0 is the FPR check.
Holm over {T1, T2}; IT2a concordance; drop-max (T1 without its largest page) descriptive.
Run: python3 tools/c133_hand_stratum.py struct | run
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json, time, itertools
import numpy as np
from collections import defaultdict, OrderedDict
sys.path.insert(0, os.path.dirname(__file__))
from c131_intermediate_pages import Inst, ms_pages, holm, wilson, ZH, FILES

SEED_NULL, SEED_PLANT, SEED_PNULL, SEED_PERM = 11915, 11916, 11917, 11918   # 11919 reserved; next free 11920
R, R_P, NPERM, NPERM_SIM, NSIM, ALPHA, POW, F_GATE = 400, 100, 20000, 2000, 200, 0.05, 0.80, 0.25
FGRID = [round(0.05 * k, 2) for k in range(0, 11)]
HAND = '5'
OUT = 'analysis/C133_results.json'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def null_mean(I, p, rng, ntok, reps):
    i = I.idx[p]; save = int(I.n[i]); I.n[i] = ntok; L = I.P[p]['L']; s = 0.0
    for _ in range(reps):
        t, ex = I.pseudo(p, rng); s += I.d(I.lam(t, ex), L)
    I.n[i] = save; return s / reps

def units(I):
    """informative B pages with numeric hand -> dict page -> (section, hand)"""
    U = OrderedDict()
    for p in I.names:
        h = ZH.get(p, {}).get('H')
        if I.P[p]['L'] == 'B' and I.status(p) == 'INFORMATIVE' and h and h.isdigit(): U[p] = (I.P[p]['I'], h)
    return U

def t1_exact(e, sec, lab):
    """exact within-section permutation p for the mean of the labelled set. e, sec: dict page->; lab: set of labelled pages"""
    tot = np.array([0.0]); k_all = 0; obs = np.mean([e[p] for p in lab])
    for s in sorted(set(sec[p] for p in lab)):
        pg = [p for p in e if sec[p] == s]; k = sum(p in lab for p in pg); k_all += k
        sums = np.array([sum(c) for c in itertools.combinations([e[p] for p in pg], k)])
        tot = (tot[:, None] + sums[None, :]).ravel()
    S = tot / k_all
    return float(obs), float((S >= obs - 1e-12).sum() / len(S)), int(len(S))

def t2_mc(e, sec, hand, nperm, rng):
    """vectorised within-section permutation; sections with one hand contribute 0 to W and to every W* (left out)."""
    W = 0.0; Wp = np.zeros(nperm)
    for s in sorted(set(sec.values())):
        pg = [p for p in e if sec[p] == s]; hs = sorted(set(hand[p] for p in pg))
        if len(hs) < 2: continue
        ev = np.array([e[p] for p in pg]); lab = np.array([hs.index(hand[p]) for p in pg]); mu = ev.mean()
        perms = rng.permuted(np.tile(lab, (nperm, 1)), axis=1)
        for h in range(len(hs)):
            nh = (lab == h).sum(); W += nh * (ev[lab == h].mean() - mu) ** 2
            Wp += nh * (((perms == h) @ ev) / nh - mu) ** 2
    return float(W), float((1 + (Wp >= W - 1e-12).sum()) / (nperm + 1))

def real_scores(I, U, ti):
    e, d, nm = {}, {}, {}
    for p in U:
        pi = I.names.index(p); rng = np.random.default_rng([SEED_NULL, ti, pi]); L = I.P[p]['L']
        tok = I.ids([w for ln in I.P[p]['lines'] for w in ln]); d[p] = I.d(I.lam(tok, {I.idx[p]}), L)
        nm[p] = null_mean(I, p, rng, int(I.n[I.idx[p]]), R); e[p] = d[p] - nm[p]
    return e, d, nm

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'struct'
    if mode == 'struct':
        for t, f in FILES:
            P = ms_pages(f); I = Inst(P); U = units(I); c = defaultdict(int)
            for p, (s, h) in U.items(): c[(s, h)] += 1
            print(t, 'B informative pages with hand:', len(U), dict(sorted(c.items())))
            print('  hand 5:', [(p, s) for p, (s, h) in U.items() if h == HAND])
        return
    out = dict(seeds=dict(null=SEED_NULL, plant=SEED_PLANT, planted_null=SEED_PNULL, perm=SEED_PERM, reserved=[11919], next_free=11920),
               R=R, R_P=R_P, NPERM=NPERM, NPERM_SIM=NPERM_SIM, NSIM=NSIM, FGRID=FGRID, F_GATE=F_GATE, POW=POW,
               tool_c131_sha256='259472b33a4433647f8ac1680d4a3ea92ff475e2213931fa72ddace5fef1d3ea', power={}, manuscript={})
    # ---- 1. power and FPR first (ZL3b, pseudo-hands; real hand-5 statistic not computed yet)
    P = ms_pages(FILES[0][1]); I = Inst(P); U = units(I)
    sec = {p: s for p, (s, h) in U.items()}; hand = {p: h for p, (s, h) in U.items()}
    h5 = [p for p in U if hand[p] == HAND]; comp = defaultdict(int)
    for p in h5: comp[sec[p]] += 1
    rest = [p for p in U if hand[p] != HAND]
    base_e, _, _ = real_scores(I, {p: U[p] for p in rest}, 0)
    out['power_design'] = dict(hand5_composition=dict(comp), n_rest=len(rest),
                               rest_per_section={s: sum(sec[p] == s for p in rest) for s in comp})
    for fi, f in enumerate(FGRID):
        rng = np.random.default_rng([SEED_PLANT, fi]); rngp = np.random.default_rng([SEED_PERM, 1, fi]); c1 = c2 = 0; es = []; ds = []
        for k in range(NSIM):
            pseudo = []
            for s, n in comp.items():
                cand = [p for p in rest if sec[p] == s]; pseudo += [cand[j] for j in rng.choice(len(cand), size=n, replace=False)]
            e = dict(base_e)
            for p in pseudo:
                t, ex = I.plant(p, f, rng); dp = I.d(I.lam(t, ex), 'B')
                rn = np.random.default_rng([SEED_PNULL, fi, k, I.idx[p]])
                e[p] = dp - null_mean(I, p, rn, len(t), R_P); es.append(e[p]); ds.append(dp)
            _, p1, _ = t1_exact(e, sec, set(pseudo))
            hd = {p: ('X' if p in pseudo else hand[p]) for p in rest}
            _, p2 = t2_mc(e, sec, hd, NPERM_SIM, rngp)
            c1 += p1 <= ALPHA; c2 += p2 <= ALPHA
        out['power'][str(f)] = dict(T1_rate=c1 / NSIM, T1_wilson=wilson(c1, NSIM), T2_rate=c2 / NSIM, T2_wilson=wilson(c2, NSIM),
                                    planted_e_mean=float(np.mean(es)), planted_d_mean=float(np.mean(ds)))
        log('power f', f, json.dumps(out['power'][str(f)])); json.dump(out, open(OUT, 'w'), indent=1, default=float)
    pw = out['power']
    out['gates'] = dict(G_FPR_T1=bool(pw['0.0']['T1_rate'] <= 0.10), G_FPR_T2=bool(pw['0.0']['T2_rate'] <= 0.10),
                        G_POW_T1=bool(pw[str(F_GATE)]['T1_rate'] >= POW), G_POW_T2=bool(pw[str(F_GATE)]['T2_rate'] >= POW),
                        f80_T1=next((f for f in FGRID if f > 0 and pw[str(f)]['T1_rate'] >= POW), None),
                        f80_T2=next((f for f in FGRID if f > 0 and pw[str(f)]['T2_rate'] >= POW), None))
    log('GATES', json.dumps(out['gates'])); json.dump(out, open(OUT, 'w'), indent=1, default=float)
    # ---- 2. real data, ZL3b primary then IT2a
    for ti, (t, fpath) in enumerate(FILES):
        P = ms_pages(fpath); I = Inst(P); U = units(I)
        sec = {p: s for p, (s, h) in U.items()}; hand = {p: h for p, (s, h) in U.items()}
        e, d, nm = real_scores(I, U, ti); h5 = [p for p in U if hand[p] == HAND]
        S5, p1, narr = t1_exact(e, sec, set(h5))
        W, p2 = t2_mc(e, sec, hand, NPERM, np.random.default_rng([SEED_PERM, 0, ti]))
        top = max(h5, key=lambda p: e[p]); S5d, p1d, narrd = t1_exact(e, sec, set(h5) - {top})
        hm = defaultdict(list)
        for p in U: hm[f'{sec[p]}-H{hand[p]}'].append(e[p])
        out['manuscript'][t] = dict(n_units=len(U), pages={p: dict(I=sec[p], H=hand[p], d=d[p], null_mean=nm[p], e=e[p]) for p in U},
            T1=dict(S5=S5, p=p1, n_arrangements=narr, hand5=h5), T2=dict(W=W, p=p2, nperm=NPERM),
            dropmax=dict(dropped=top, S=S5d, p=p1d, n_arrangements=narrd),
            hand_section_mean_e={k: dict(n=len(v), mean_e=float(np.mean(v))) for k, v in sorted(hm.items())})
        log(t, json.dumps({k: v for k, v in out['manuscript'][t].items() if k != 'pages'}, default=float))
        json.dump(out, open(OUT, 'w'), indent=1, default=float)
    # ---- 3. verdict
    Z, T = out['manuscript']['ZL3b'], out['manuscript']['IT2a']; G = out['gates']
    adj = holm([Z['T1']['p'], Z['T2']['p']]); V = {}
    for j, (key, nm_, fg, pg) in enumerate([('T1', 'HAND-5 EXCESS', G['G_FPR_T1'], G['G_POW_T1']), ('T2', 'HAND EFFECT WITHIN SECTION', G['G_FPR_T2'], G['G_POW_T2'])]):
        conc = T[key]['p'] <= ALPHA
        if not fg: v = 'NOT TESTABLE (G-FPR)'
        elif not pg: v = 'NOT TESTABLE (G-POW at f 0.25 < 0.80)'
        elif adj[j] <= ALPHA: v = nm_ + (' (IT2a concordant)' if conc else ' -> UNRESOLVED (IT2a discordant)')
        else: v = 'NO ' + nm_ + f' (EXCLUDED at pseudo-hand f >= {G["f80_" + key]})'
        V[key] = dict(verdict=v, p=Z[key]['p'], holm=adj[j], IT2a_p=T[key]['p'])
    out['verdict'] = V; json.dump(out, open(OUT, 'w'), indent=1, default=float); log('VERDICT', json.dumps(V))

if __name__ == '__main__': main()
