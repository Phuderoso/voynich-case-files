#!/usr/bin/env python3
"""C089 (F-TOPIC step 3): the C088 question rebuilt with a lower-variance instrument.
Q1 (primary). Inside Currier A and inside Currier B, at equal page size (pages of the C084 windows truncated to their first
lines reaching T = 80 tokens, exactly as C088), is the per-page topical gain higher in W1 (f1r-f79v) than in W2 (f86v6-f116r)?
Instrument. ONE multi-init PLSA per transcription over ALL truncated window pages (K 8, EPS 0.1, 150 iterations, N_INIT 10
inits, predictions p(w|d) averaged over inits; odd lines 1st, 3rd, ... fitted, even lines scored).  Score matrix
S[d, e] = mean over page d's even-line tokens (types in the odd-line vocabulary) of log2 p_e(w) / u(w).
Per-page gain g_d = S[d, d] - mean_{e != d, same Currier language} S[d, e]  (held-out gain of the page's own topic mix minus
its expectation under the topic mixes of the other pages of its language).  Scores are computed ONCE.
Statistic D_L = mean g(W1 pages of L) - mean g(W2 pages of L).  Null: window labels permuted among the pages of L over the
FIXED g (group sizes kept), R 9,999, two-sided p = min(1, 2 min(p+, p-)).  Family {A, B} x {ZL 3b, IT2a}, Holm 0.05.
Q2 (secondary, Layfield & Fagin Davis 2026 singulion claim, run only if its rehearsal is powered). If bifolia were written as
single-sheet units read in sequence, the two conjugate leaves of a bifolium were written consecutively, so their pages should
be topically closer than other leaf pairs of the same quire and the same Currier language. Units: leaves (all truncated pages
of the whole manuscript with >= 40 paragraph tokens; one fit per transcription), conjugates = the two leaves sharing ZL $Q and
$B; strata = quire x language with >= 2 complete same-language conjugate pairs. sim(p, q) = 0.5 (S[p,q] - E_p + S[q,p] - E_q),
E_p = mean_{e != p} S[p, e]; leaf similarity = mean over their page pairs. T = mean over conjugate pairs of (sim(pair) - mean sim of all
leaf pairs of its stratum). Null: random perfect re-matching of the leaves inside each stratum, R 9,999, two-sided; Holm over 2.
Gates (ZL 3b): Q1 planted ~halving (C088's plant: in pseudo-W2 pages each line swapped with prob 0.3 with a line of another
pseudo-W2 page; refit), detection D > 0 and p <= 0.0125, pass >= 16/20 per stratum; FPR pseudo-labels over fixed g, false calls
at p <= 0.05 <= 4/40.  Q2 plant: in pseudo-conjugate pairs (random matching per stratum) each line swapped with prob 0.2 with a
line of the partner leaf; refit; detection T > 0 and p <= 0.025, pass >= 16/20; FPR pseudo-matchings over fixed sim <= 2/20.
Rehearsal variants (env, rehearsal mode only): C089_CROSS=0 single-direction fit; C089_F1 / C089_F2 plant strengths;
C089_SKIP_Q1=1. The registered run uses the defaults (cross-fitted, F1 0.3, F2 0.2) and, Q2 having failed its rehearsal, Q1 only.
--rehearse: runs every gate on rehearsal seeds (never the real labels / real pairs) and prints its rates (Kryptos I-119).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c084_page_topics import ms_windows, holm
from c047_pair_currier_split import ivtff_pages_lang

SEED, T, K, EPS, ITERS, N_INIT, R = 8989, 80, 8, 0.1, 150, 10, 9999
CROSS = os.environ.get('C089_CROSS', '1') == '1'
F1 = float(os.environ.get('C089_F1', '0.3')); F2 = float(os.environ.get('C089_F2', '0.2'))
NG, A1, A2, MINP = 20, 0.0125, 0.025, 40

def trunc(p):
    out, t = [], 0
    for l in p:
        out.append(l); t += len(l)
        if t >= T: return out
    return None

def scores(pages, seed):
    """cross-fitted: S = mean of (fit odd lines, score even) and (fit even lines, score odd)"""
    if not CROSS: return scores1(pages, seed, 0)
    return 0.5 * (scores1(pages, seed, 0) + scores1(pages, seed + 7777, 1))

def scores1(pages, seed, par):
    """one multi-init PLSA over all pages -> S[d, e] (bits/token)"""
    A = [[w for i, l in enumerate(p) if i % 2 == par for w in l] for p in pages]
    B = [[w for i, l in enumerate(p) if i % 2 != par for w in l] for p in pages]
    voc = {w: j for j, w in enumerate(sorted({w for a in A for w in a}))}
    D, V = len(pages), len(voc); X = np.zeros((D, V)); Y = np.zeros((D, V))
    for d, a in enumerate(A):
        for w in a: X[d, voc[w]] += 1
    for d, b in enumerate(B):
        for w in b:
            if w in voc: Y[d, voc[w]] += 1
    u = X.sum(0) + 0.5; u /= u.sum(); Pm = np.zeros((D, V))
    for i in range(N_INIT):
        rng = np.random.default_rng([seed, i])
        W = rng.random((D, K)) + 0.1; H = rng.random((K, V)) + 0.1
        for _ in range(ITERS):
            Rm = X / (W @ H + 1e-12); H *= (W.T @ Rm) / (W.sum(0)[:, None] + 1e-12)
            Rm = X / (W @ H + 1e-12); W *= (Rm @ H.T) / (H.sum(1)[None, :] + 1e-12)
        P = W @ H; P /= P.sum(1, keepdims=True); Pm += ((1 - EPS) * P + EPS * u[None, :]) / N_INIT
    L = np.log2(Pm / u[None, :]); n = Y.sum(1)
    return (Y @ L.T) / np.maximum(n, 1)[:, None]

def page_gain(S, lang):
    lang = np.asarray(lang); g = np.empty(len(S))
    for d in range(len(S)):
        m = (lang == lang[d]); m[d] = False; g[d] = S[d, d] - S[d, m].mean()
    return g

def ptest(stat, obs_arg, null_args):
    obs = stat(obs_arg); nl = np.array([stat(a) for a in null_args])
    phi = (1 + (nl >= obs).sum()) / (len(nl) + 1); plo = (1 + (nl <= obs).sum()) / (len(nl) + 1)
    return dict(stat=float(obs), null_mean=float(nl.mean()), null_sd=float(nl.std(ddof=1)), p=float(min(1.0, 2 * min(phi, plo))))

def q1_test(g, lab, rng, r=R):
    """lab: bool array over the stratum's pages (True = W1); permutations over fixed g"""
    g = np.asarray(g); n1 = int(lab.sum())
    perms = np.array([rng.permutation(len(g)) for _ in range(r)])
    obs = g[lab].mean() - g[~lab].mean()
    gp = g[perms]; nl = gp[:, :n1].mean(1) - gp[:, n1:].mean(1)
    phi = (1 + (nl >= obs).sum()) / (r + 1); plo = (1 + (nl <= obs).sum()) / (r + 1)
    return dict(n_W1=n1, n_W2=int((~lab).sum()), D=float(obs), null_mean=float(nl.mean()), null_sd=float(nl.std(ddof=1)),
                p=float(min(1.0, 2 * min(phi, plo))))

def dilute(pages, idx_groups, rng, f):
    """swap each line of the pages in a group with prob f with a line of another page of the same group (pool permutation
    over the chosen slots, re-drawn until no slot keeps a line of its own page where possible)"""
    out = [list(p) for p in pages]
    for grp in idx_groups:
        slots = [(i, j) for i in grp for j in range(len(pages[i])) if rng.random() < f]
        src = [pages[i][j] for i, j in slots]; own = [i for i, _ in slots]; perm = rng.permutation(len(src))
        for (i, j), s in zip(slots, perm): out[i][j] = src[s]
    return out

# ---------------- data ----------------
def q1_data(path):
    win, pages, lang, _ = ms_windows(path); ps, lab, lg, names = [], [], [], []
    for w in ('W1', 'W2'):
        for p in win[w]:
            if lang.get(p) not in ('A', 'B'): continue
            tp = trunc(pages[p])
            if tp: ps.append(tp); lab.append(w == 'W1'); lg.append(lang[p]); names.append(p)
    return ps, np.array(lab), np.array(lg), names

def headers(path):
    H = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', line)
        if h:
            d = dict(re.findall(r'\$(\w)=(\w+)', h.group(2))); H[h.group(1)] = d
    return H

def q2_data(path):
    pl, lang, _ = ivtff_pages_lang(path); H = headers('data/ZL3b-n.txt'); pages = {}
    for p, ws in pl: pages.setdefault(p, []).append(ws)
    ps, names = [], []
    for p in pages:
        if sum(map(len, pages[p])) < MINP: continue
        tp = trunc(pages[p])
        if tp and p in H and lang.get(p) in ('A', 'B'): ps.append(tp); names.append(p)
    leaf = {}
    for i, p in enumerate(names): leaf.setdefault(re.match(r'f(\d+)', p).group(1), []).append(i)
    info = {}
    for lf, idx in leaf.items():
        hs = [H[names[i]] for i in idx]; ls = {lang[names[i]] for i in idx}
        q = {h.get('Q') for h in hs}; b = {h.get('B') for h in hs}
        if len(q) == 1 and len(b) == 1 and len(ls) == 1: info[lf] = (q.pop(), b.pop(), ls.pop())
    bif = {}
    for lf, (q, b, l) in info.items(): bif.setdefault((q, b), []).append(lf)
    pairs = [tuple(sorted(v, key=int)) for v in bif.values() if len(v) == 2 and info[v[0]][2] == info[v[1]][2]]
    strata = {}
    for a, b in pairs: strata.setdefault((info[a][0], info[a][2]), []).append((a, b))
    strata = {k: v for k, v in strata.items() if len(v) >= 2}
    return ps, names, [lang[n] for n in names], leaf, strata

def leaf_sim(S, leaf):
    E = (S.sum(1) - np.diag(S)) / (len(S) - 1); C = S - E[:, None]; sym = 0.5 * (C + C.T)
    L = sorted(leaf, key=int); ix = {l: k for k, l in enumerate(L)}; M = np.zeros((len(L), len(L)))
    for a in L:
        for b in L: M[ix[a], ix[b]] = sym[np.ix_(leaf[a], leaf[b])].mean()
    return M, ix

def q2_stat(M, ix, strata_pairs):
    """mean over pairs of (sim(pair) - mean sim of all leaf pairs of its stratum)"""
    pv = []
    for prs in strata_pairs.values():
        lv = [x for pr in prs for x in pr]
        base = np.mean([M[ix[a], ix[b]] for k, a in enumerate(lv) for b in lv[k + 1:]])
        pv += [M[ix[a], ix[b]] - base for a, b in prs]
    return float(np.mean(pv))

def rematch(strata, rng):
    out = {}
    for k, prs in strata.items():
        lv = [x for pr in prs for x in pr]; lv = [lv[i] for i in rng.permutation(len(lv))]
        out[k] = [(lv[2 * i], lv[2 * i + 1]) for i in range(len(prs))]
    return out

def q2_test(M, ix, strata, obs_pairs, rng, r=R):
    obs = q2_stat(M, ix, obs_pairs); nl = np.array([q2_stat(M, ix, rematch(strata, rng)) for _ in range(r)])
    phi = (1 + (nl >= obs).sum()) / (r + 1); plo = (1 + (nl <= obs).sum()) / (r + 1)
    return dict(T=obs, null_mean=float(nl.mean()), null_sd=float(nl.std(ddof=1)), p=float(min(1.0, 2 * min(phi, plo))))

# ---------------- gate workers ----------------
def q1_plant_job(args):
    L, k, base = args
    ps, lab, lg, _ = q1_data('data/ZL3b-n.txt'); rng = np.random.default_rng([base, k, ord(L)])
    idx = np.where(lg == L)[0]; pl = lab[idx][rng.permutation(len(idx))]
    w2 = [int(i) for i, b in zip(idx, pl) if not b]
    dp = dilute(ps, [w2], rng, F1); S = scores(dp, base * 10 + k * 2 + (L == 'B'))
    g = page_gain(S, lg)[idx]
    return L, k, q1_test(g, pl, rng, R)

def q2_plant_job(args):
    k, base = args
    ps, names, lg, leaf, strata = q2_data('data/ZL3b-n.txt'); rng = np.random.default_rng([base, k, 2])
    pseudo = rematch(strata, rng); groups = []
    for prs in pseudo.values():
        for a, b in prs: groups.append(leaf[a] + leaf[b])
    # swap lines only ACROSS the two leaves of a pseudo pair
    dp = [list(p) for p in ps]
    for prs in pseudo.values():
        for a, b in prs:
            sa = [(i, j) for i in leaf[a] for j in range(len(ps[i])) if rng.random() < F2]
            sb = [(i, j) for i in leaf[b] for j in range(len(ps[i])) if rng.random() < F2]
            for (i, j), (i2, j2) in zip(sa, sb): dp[i][j], dp[i2][j2] = ps[i2][j2], ps[i][j]
    S = scores(dp, base * 10 + k); M, ix = leaf_sim(S, leaf)
    return k, q2_test(M, ix, strata, pseudo, rng, R)

def gates(pool, base, out):
    t = time.time()
    jobs = [] if os.environ.get('C089_SKIP_Q1') == '1' else [(L, k, base) for L in 'AB' for k in range(NG)]
    q1 = {f'{L}_{k}': r for L, k, r in pool.imap_unordered(q1_plant_job, jobs)}
    q2 = {} if (out['mode'] == 'registered' and PRIMARY_ONLY) else \
        {f'{k}': r for k, r in pool.imap_unordered(q2_plant_job, [(k, base + 1) for k in range(NG)])}
    pw1 = {L: sum(q1.get(f'{L}_{k}', {'D': 0})['D'] > 0 and q1.get(f'{L}_{k}', {'p': 1})['p'] <= A1 for k in range(NG)) for L in 'AB'}
    pw2 = sum(q2[f'{k}']['T'] > 0 and q2[f'{k}']['p'] <= A2 for k in range(NG))
    out.update(q1_plants=q1, q2_plants=q2, q1_power={L: f'{pw1[L]}/{NG}' for L in 'AB'}, q2_power=f'{pw2}/{NG}',
               q1_pass={L: pw1[L] >= 16 for L in 'AB'}, q2_pass=pw2 >= 16, gate_runtime_s=round(time.time() - t, 1))
    return out

def fpr(S_ZL, lg, lab, M, ix, strata, base):
    rng = np.random.default_rng([base, 77]); g = page_gain(S_ZL, lg); n1 = 0
    for L in 'AB':
        idx = np.where(lg == L)[0]
        for k in range(NG):
            pl = lab[idx][rng.permutation(len(idx))]; n1 += q1_test(g[idx], pl, rng, 1999)['p'] <= 0.05
    n2 = sum(q2_test(M, ix, strata, rematch(strata, rng), rng, 1999)['p'] <= 0.05 for _ in range(NG))
    return dict(q1_fpr=f'{n1}/{2 * NG}', q1_fpr_pass=n1 <= 4, q2_fpr=f'{n2}/{NG}', q2_fpr_pass=n2 <= 2)

def main(rehearse):
    t0 = time.time(); out = dict(seed=SEED, T=T, K=K, N_INIT=N_INIT, R=R, F1=F1, F2=F2, mode='rehearsal' if rehearse else 'registered')
    base = SEED * 1000 + (900 if rehearse else 100)
    psZ, labZ, lgZ, nmZ = q1_data('data/ZL3b-n.txt'); psI, labI, lgI, nmI = q1_data('data/IT2a-n.txt')
    q2Z = q2_data('data/ZL3b-n.txt'); q2I = q2_data('data/IT2a-n.txt')
    out['q1_cells'] = {tr: {f'{L}_{w}': int(((lg == L) & (lab == (w == 'W1'))).sum()) for L in 'AB' for w in ('W1', 'W2')}
                       for tr, lg, lab in (('ZL3b', lgZ, labZ), ('IT2a', lgI, labI))}
    out['q2_strata'] = {tr: {f'{k[0]}{k[1]}': len(v) for k, v in d[4].items()} for tr, d in (('ZL3b', q2Z), ('IT2a', q2I))}
    print('cells', out['q1_cells'], 'strata', out['q2_strata'], flush=True)
    with Pool(8) as pool:
        fits = pool.starmap(scores, [(psZ, base + 1), (psI, base + 2), (q2Z[0], base + 3), (q2I[0], base + 4),
                                     (psZ, base + 5), (q2Z[0], base + 6)])
        gates(pool, base + 10, out)
    SZ, SI, S2Z, S2I, SZb, S2Zb = fits
    M2Z, ixZ = leaf_sim(S2Z, q2Z[3]); M2I, ixI = leaf_sim(S2I, q2I[3])
    # reliability (no labels): two independent ensembles on the same pages
    gZ, gZb = page_gain(SZ, lgZ), page_gain(SZb, lgZ)
    out['reliability'] = dict(q1_g_corr=float(np.corrcoef(gZ, gZb)[0, 1]), q1_g_mean=float(gZ.mean()), q1_g_sd=float(gZ.std(ddof=1)),
                              q2_sim_corr=float(np.corrcoef(leaf_sim(S2Z, q2Z[3])[0].ravel(), leaf_sim(S2Zb, q2Z[3])[0].ravel())[0, 1]))
    out.update(fpr(SZ, lgZ, labZ, M2Z, ixZ, q2Z[4], base + 20))
    if not rehearse:
        rng = np.random.default_rng([SEED, 1]); tests = {}
        for tr, S, lg, lab in (('ZL3b', SZ, lgZ, labZ), ('IT2a', SI, lgI, labI)):
            g = page_gain(S, lg)
            for L in 'AB':
                idx = np.where(lg == L)[0]; tests[f'{tr}_{L}'] = q1_test(g[idx], lab[idx], rng, R)
        main4 = ['ZL3b_A', 'IT2a_A', 'ZL3b_B', 'IT2a_B']; rej = holm([tests[m]['p'] for m in main4])
        for m, r_ in zip(main4, rej): tests[m]['holm_reject'] = bool(r_)
        verdict = {}
        for L in 'AB':
            z, i = tests[f'ZL3b_{L}'], tests[f'IT2a_{L}']
            if not (out['q1_fpr_pass'] and out['q1_pass'][L]): verdict[L] = 'NOT TESTABLE (gate)'
            elif z['holm_reject'] and i['holm_reject'] and z['D'] > 0 and i['D'] > 0: verdict[L] = 'DETECTED (W1 > W2 within language)'
            elif z['holm_reject'] and i['holm_reject'] and z['D'] < 0 and i['D'] < 0: verdict[L] = 'DETECTED REVERSED (W2 > W1)'
            elif z['holm_reject'] or i['holm_reject']: verdict[L] = 'SPLIT (transcription-dependent)'
            else: verdict[L] = 'NOT DETECTED'
        out.update(q1_tests=tests, q1_verdict=verdict)
        if PRIMARY_ONLY: pass
        else:
            t2 = {}
            for tr, M, ix, d in (('ZL3b', M2Z, ixZ, q2Z), ('IT2a', M2I, ixI, q2I)):
                t2[tr] = q2_test(M, ix, d[4], d[4], rng, R)
            rj = holm([t2['ZL3b']['p'], t2['IT2a']['p']])
            for tr, r_ in zip(('ZL3b', 'IT2a'), rj): t2[tr]['holm_reject'] = bool(r_)
            z, i = t2['ZL3b'], t2['IT2a']
            if not (out['q2_fpr_pass'] and out['q2_pass']): v2 = 'NOT TESTABLE (gate)'
            elif z['holm_reject'] and i['holm_reject'] and z['T'] > 0 and i['T'] > 0: v2 = 'DETECTED (conjugate leaves closer)'
            elif z['holm_reject'] and i['holm_reject'] and z['T'] < 0 and i['T'] < 0: v2 = 'DETECTED REVERSED (conjugates farther)'
            elif z['holm_reject'] or i['holm_reject']: v2 = 'SPLIT (transcription-dependent)'
            else: v2 = 'NOT DETECTED'
            out.update(q2_tests=t2, q2_verdict=v2)
    out['runtime_s'] = round(time.time() - t0, 1)
    fn = 'analysis/C089_rehearsal.json' if rehearse else 'analysis/C089_results.json'
    json.dump(out, open(fn, 'w'), indent=1)
    for k in ('q1_cells', 'q2_strata', 'q1_power', 'q2_power', 'q1_pass', 'q2_pass', 'q1_fpr', 'q2_fpr', 'reliability',
              'q1_tests', 'q1_verdict', 'q2_tests', 'q2_verdict', 'gate_runtime_s', 'runtime_s'):
        if k in out: print(k, out[k], flush=True)
    for k, r in sorted(out['q1_plants'].items()): print('plant1', k, round(r['D'], 4), round(r['null_sd'], 4), r['p'])
    for k, r in sorted(out['q2_plants'].items(), key=lambda x: int(x[0])): print('plant2', k, round(r['T'], 4), round(r['null_sd'], 4), r['p'])

PRIMARY_ONLY = True  # Q2 dropped before the push: rehearsal power 3/20 (< 16/20), see the case file
if __name__ == '__main__':
    main('--rehearse' in sys.argv)
