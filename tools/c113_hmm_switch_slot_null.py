#!/usr/bin/env python3
"""C113 (F-HMM step 2): is the manuscript's 'sticky' two-state HMM (C111, post hoc) more than word-position slots?
Statistic SW (switch rate) of the best-of-NRESTART 2-state HMM (C111 fit_hmm, words as separate sequences):
  SW = sum_i occ_i * (1 - A_ii), occ_i = share of token posterior mass in state i. Alphabetic texts alternate (SW high);
  a front/back word gives SW low. T = mean SW over the text's 15,000-token halves.
Null N-SLOT (C109 shuffle_slot): every glyph unit permuted only among tokens with the same (word length, position), each half
independently; the HMM is RE-FITTED on every replicate with the same procedure (NRESTART starts). NNULL replicates.
  p_low = (1 + #{T_null <= T}) / (1 + NNULL)  (stickier than slots);  p_high = (1 + #{T_null >= T}) / (1 + NNULL).
Two-sided alpha 0.05 -> each direction at 0.025; floor 1/(1+NNULL) printed. Calibration is exact by exchangeability (the
observed text under H0 is one more slot draw); a leave-one-out rank check on the null replicates is printed.
Gate G-PLANT (power, two-sided): plant A = Latin Caesar half 1 with only 30 % of words intact and 70 % replaced by their
slot-shuffled version (a diluted departure from slots); it must give min(p_low, p_high) < 0.025. Plant B (sensitivity, printed,
decides nothing) = Latin Descartes half 1 (amendment v2: Caesar has only one half) with 50 % of words re-ordered front/back (units of class F first, then class K, order kept
inside each class; classes = alternate frequency ranks), a structure whose switch point follows word content, not position.
Smoke disclosed (controls only): Latin h1 SW 0.81 vs two slot replicates 0.39/0.40; front/back q 0.5 SW 0.176 vs 0.154/0.153.
Pre-registered in case-file/C113-hmm-switch-slot-null.md. Seed 11775 (main); next free 11776.
Run: timeout 600 python3 tools/c113_hmm_switch_slot_null.py   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c108_sukhotin_alternation import encode, flat, chars, halves
from c109_sukhotin_slot_null import slot_keys, shuffle_slot
from c111_hmm_sukhotin_convergence import pad, fit_hmm

SEED, NRESTART, ALPHA = 11775, 3, 0.05
NNULL = dict(ZL3b=60, plantA=40, plantB=40, IT2a=0)
QA, QB = 0.30, 0.50   # A: share of Latin words kept intact (rest slot-shuffled); B: front/back share

def sw_of(ids, wid, S, rng):
    X, M = pad(ids, wid); best = None
    for _ in range(NRESTART):
        ll, G, A, it = fit_hmm(X, M, S, rng)
        if best is None or ll > best[0]: best = (ll, G, A)
    ll, G, A = best; occ = G.sum(0) / G.sum()
    return float((occ * (1 - np.diag(A))).sum()), round(ll, 1), np.round(A, 3).tolist()

def plant(words, rng, q):
    cnt = {}
    for w in words:
        for u in w: cnt[u] = cnt.get(u, 0) + 1
    rank = {u: i for i, u in enumerate(sorted(cnt, key=lambda u: -cnt[u]))}; F = {u for u in rank if rank[u] % 2 == 0}
    out = []
    for w in words:
        if rng.random() < q: w = tuple([u for u in w if u in F] + [u for u in w if u not in F])
        out.append(w)
    return out

def dilute(words, rng, q):
    ids, wid, inv = encode(words); sh = shuffle_slot(ids, slot_keys(words), rng); out = []; pos = 0
    for w in words:
        out.append(w if rng.random() < q else tuple(inv[j] for j in sh[pos:pos + len(w)])); pos += len(w)
    return out

def _job(job):
    name, rep, h, words = job
    ids, wid, inv = encode(words); rng = np.random.default_rng(np.random.SeedSequence([SEED, hash_name(name), rep, h]))
    if rep > 0: ids = shuffle_slot(ids, slot_keys(words), rng)
    return name, rep, h, sw_of(ids, wid, len(inv), rng)

def hash_name(n): return sum((i + 1) * ord(c) for i, c in enumerate(n))

def main():
    from multiprocessing import Pool
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts(); texts = {}
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, lang, _ = ivtff_pages_lang(f); lines = [l for p, l in pl]
        texts[k] = [[tuple(T.units(w)) for w in flat(L)] for L in halves(lines)]
    Hc = halves(nat['Latin_Caesar'])
    texts['plantA'] = [dilute(chars(flat(Hc[0])), rng, QA)]; texts['plantB'] = [plant(chars(flat(halves(nat['Latin_Descartes'])[0])), rng, QB)]   # amendment v2: Caesar has one half
    jobs = [(k, r, h, w) for k in ('plantA', 'plantB', 'ZL3b', 'IT2a') for r in range(NNULL[k] + 1) for h, w in enumerate(texts[k])]
    print('jobs', len(jobs), round(time.time() - t0, 1), flush=True)
    res = {}; ck = 'analysis/C113_checkpoint.jsonl'; fck = open(ck, 'w')
    with Pool(8) as P:
        for name, rep, h, (sw, ll, A) in P.imap_unordered(_job, jobs):
            res[(name, rep, h)] = (sw, ll, A); fck.write(json.dumps([name, rep, h, sw, ll, A]) + '\n'); fck.flush()
            if rep == 0: print('obs', name, h, round(sw, 4), ll, A, round(time.time() - t0, 1), flush=True)
    R = dict(seed=SEED, NRESTART=NRESTART, NNULL=NNULL, alpha=ALPHA, qA=QA, qB=QB, texts={})
    for k in texts:
        nh = len(texts[k]); Tobs = float(np.mean([res[(k, 0, h)][0] for h in range(nh)]))
        d = dict(T=round(Tobs, 4), halves=[dict(SW=round(res[(k, 0, h)][0], 4), ll=res[(k, 0, h)][1], A=res[(k, 0, h)][2]) for h in range(nh)])
        n = NNULL[k]
        if n:
            Tn = np.array([np.mean([res[(k, r, h)][0] for h in range(nh)]) for r in range(1, n + 1)])
            d.update(null_mean=round(float(Tn.mean()), 4), null_sd=round(float(Tn.std(ddof=1)), 4), null_min=round(float(Tn.min()), 4),
                     null_max=round(float(Tn.max()), 4), z=round(float((Tobs - Tn.mean()) / Tn.std(ddof=1)), 2),
                     p_low=(1 + int((Tn <= Tobs).sum())) / (1 + n), p_high=(1 + int((Tn >= Tobs).sum())) / (1 + n), floor=1 / (1 + n),
                     loo_reject=f'{sum(((1 + (np.delete(Tn, i) <= Tn[i]).sum()) / n < ALPHA / 2) or ((1 + (np.delete(Tn, i) >= Tn[i]).sum()) / n < ALPHA / 2) for i in range(n))}/{n}')
        R['texts'][k] = d; print(k, {x: y for x, y in d.items() if x != 'halves'}, flush=True)
    a = R['texts']['plantA']; G = dict(plantA_p_low=a['p_low'], plantB_p_low=R['texts']['plantB']['p_low'], plantA_p_high=a['p_high'], ok=bool(min(a['p_low'], a['p_high']) < ALPHA / 2))
    R['gates'] = G; z = R['texts']['ZL3b']
    if not G['ok']: V = 'NOT TESTABLE'
    elif z['p_low'] < ALPHA / 2: V = 'STICKIER THAN SLOTS'
    elif z['p_high'] < ALPHA / 2: V = 'LESS STICKY THAN SLOTS'
    else: V = 'SLOT-EXPLAINED'
    R['verdict'] = dict(H1=V, IT2a_T_descriptive=R['texts']['IT2a']['T'], ZL_null_range=[z.get('null_min'), z.get('null_max')])
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C113_results.json', 'w'), indent=1, default=float); print(R['gates'], R['verdict'], R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke':
        rng = np.random.default_rng(1); nat = B.nat_texts(); w = chars(flat(halves(nat['Latin_Caesar'])[0])); t0 = time.time()
        for q in (0.0, QA):
            pw = plant(w, rng, q); ids, wid, inv = encode(pw)
            print('smoke q', q, 'obs', sw_of(ids, wid, len(inv), rng)[:2], round(time.time() - t0, 1), flush=True)
            for r in range(2): print('  slot', sw_of(shuffle_slot(ids, slot_keys(pw), rng), wid, len(inv), rng)[:2], round(time.time() - t0, 1), flush=True)
    else: main()
