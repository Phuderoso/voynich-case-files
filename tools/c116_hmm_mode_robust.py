#!/usr/bin/env python3
"""C116 (F-HMM step 5): a mode-robust re-test of C113's 'stickier than word-position slots', per Currier stratum.
Why: C115's line bootstrap showed the best-of-3 2-state HMM is mode-unstable (sticky SW ~0.10, slot-like ~0.20, alternating ~0.89),
so the C113/C114/C115 switch-rate SW and its D are not interpretable. Design adopted from Kryptos's review (2026-11-13 ~20:03 PT):
- per text, NRESTART = 30 EM restarts of C111 fit_hmm (unchanged); each restart gets SW_r = sum_i occ_i (1 - A_ii) (C113 sw_of formula)
  and its log-likelihood ll_r;
- modes fixed IN ADVANCE on SW: sticky SW < 0.15; slot 0.15 <= SW <= 0.5; alternating SW > 0.5 (checked on controls only, G-MODE);
- statistic DL = (max ll over sticky restarts - max ll over non-sticky restarts) / n_glyph_tokens; -inf if no sticky restart,
  +inf if no non-sticky restart; the ML SW and the sticky-restart fraction are DESCRIPTIVE only;
- convergence gate G-CONV: the best ll must be reached (within CONV_TOL = 1.0 nat) by >= 3 of 30 restarts, on the observed text and on
  every null replicate; unconverged null replicates are excluded from the null and counted; a stratum is NOT TESTABLE if its observed
  text is unconverged or more than 10 % of its null replicates are.
Null: N-SLOT (C109 shuffle_slot, same as C113/C115), all 30 restarts re-run on each replicate.
Test: one-sided toward 'sticky favoured', p = (1 + #{converged null DL >= obs DL}) / (1 + #converged null). Holm over the 3 primary
strata (ZL3b A, B1, B2 of C115, 10,000 tokens each), alpha 0.05, m = 3 fixed. NNULL 79 per primary stratum, 59 per gate text.
Gates: G-POW devowelled Latin Caesar 10,000 tokens with the C114 twin-alphabet plant q 0.20 must reach p <= 0.05/3; G-FPR the same
text unplanted must not; G-MODE: fewer than 5 % of all control restarts (G-POW + G-FPR, observed + null) may fall within 0.02 of a
mode boundary (0.15 or 0.5), else the boundaries are ill-posed and the run is NOT TESTABLE. IT2a A/B1/B2: observed only, descriptive.
Compute: ~360 jobs x 30 fits; resumable checkpoint (per-job seeds, so resumed = identical); each call runs under timeout 600 with a
soft deadline (SOFT_S) and is repeated in later cycles until all jobs are done. Verdict only when every job is in the checkpoint.
Pre-registered in case-file/C116-hmm-mode-robust.md. Seed 11787; next free 11788.
Run: timeout 600 python3 tools/c116_hmm_mode_robust.py run   (repeat until 'status' shows all done; then 'verdict')
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c108_sukhotin_alternation import encode
from c109_sukhotin_slot_null import slot_keys, shuffle_slot
from c111_hmm_sukhotin_convergence import pad, fit_hmm
from c113_hmm_switch_slot_null import hash_name
from c115_hmm_switch_currier import strata, devowel_tokens, twin, NTOK, QSTAR

SEED, NRESTART, CONV_TOL, CONV_MIN, MAX_UNCONV = 11787, 30, 1.0, 3, 0.10
STICKY, ALT, BAND, MAX_BAND = 0.15, 0.5, 0.02, 0.05
NNULL_P, NNULL_G, ALPHA, SOFT_S = 79, 59, 0.05, 520
PRIMARY, GATES, DESC = ('ZL_A', 'ZL_B1', 'ZL_B2'), ('GPOW', 'GFPR'), ('IT_A', 'IT_B1', 'IT_B2')
CKPT = 'analysis/C116_checkpoint.jsonl'

def texts():
    zl, _ = strata('data/ZL3b-n.txt'); it, _ = strata('data/IT2a-n.txt'); cae = devowel_tokens('Latin_Caesar', NTOK)
    T = dict(GPOW=twin(cae, np.random.default_rng(np.random.SeedSequence([SEED, 0])), QSTAR), GFPR=cae)
    T.update({'ZL_' + k: v for k, v in zl.items()}); T.update({'IT_' + k: v for k, v in it.items()}); return T

def joblist():
    nn = {**{k: NNULL_G for k in GATES}, **{k: NNULL_P for k in PRIMARY}, **{k: 0 for k in DESC}}
    J = [(k, r) for k in GATES for r in range(NNULL_G + 1)]          # gates first: the instrument is judged before the manuscript
    J += [(k, 0) for k in PRIMARY + DESC]
    J += [(k, r) for r in range(1, NNULL_P + 1) for k in PRIMARY]
    return J, nn

def restarts(ids, wid, S, rng):
    X, M = pad(ids, wid); out = []
    for _ in range(NRESTART):
        ll, G, A, it = fit_hmm(X, M, S, rng); occ = G.sum(0) / G.sum()
        out.append((round(float(ll), 3), round(float((occ * (1 - np.diag(A))).sum()), 5), int(it)))
    return out

_T = None
def _job(job):
    global _T
    if _T is None: _T = texts()
    name, rep = job; words = _T[name]; ids, wid, inv = encode(words)
    rng = np.random.default_rng(np.random.SeedSequence([SEED, hash_name(name), rep]))
    if rep > 0: ids = shuffle_slot(ids, slot_keys(words), rng)
    return dict(name=name, rep=rep, n=int(len(ids)), R=restarts(ids, wid, len(inv), rng))

def mode(sw): return 'sticky' if sw < STICKY else ('alt' if sw > ALT else 'slot')

def stat(rec):
    R = rec['R']; ll = np.array([r[0] for r in R]); sw = np.array([r[1] for r in R]); best = ll.max()
    st = sw < STICKY; conv = int((ll >= best - CONV_TOL).sum()) >= CONV_MIN
    if not st.any(): dl = -np.inf
    elif st.all(): dl = np.inf
    else: dl = (ll[st].max() - ll[~st].max()) / rec['n']
    return dict(DL=float(dl), conv=conv, n_best=int((ll >= best - CONV_TOL).sum()), ML_SW=float(sw[ll.argmax()]),
                sticky_frac=float(st.mean()), modes={m: int(sum(mode(s) == m for s in sw)) for m in ('sticky', 'slot', 'alt')})

def load():
    D = {}
    if os.path.exists(CKPT):
        for line in open(CKPT):
            if line.strip(): r = json.loads(line); D[(r['name'], r['rep'])] = r
    return D

def run():
    from multiprocessing import Pool
    t0 = time.time(); done = load(); J, _ = joblist(); todo = [j for j in J if j not in done]
    print('jobs', len(J), 'done', len(done), 'todo', len(todo), flush=True)
    if not todo: return
    P = Pool(8); it = P.imap(_job, todo); n = 0
    with open(CKPT, 'a') as f:
        try:
            for rec in it:
                f.write(json.dumps(rec) + '\n'); f.flush(); n += 1
                if time.time() - t0 > SOFT_S: break
        finally: P.terminate()
    print('wrote', n, 'in', round(time.time() - t0, 1), 's; done', len(done) + n, '/', len(J), flush=True)

def status():
    done = load(); J, _ = joblist(); left = [j for j in J if j not in done]
    print('done', len(J) - len(left), '/', len(J), 'next', left[:3])

def holm(ps):
    order = sorted(ps, key=lambda k: ps[k]); out, ok = {}, True
    for i, k in enumerate(order):
        bar = ALPHA / (len(ps) - i); ok = ok and ps[k] <= bar + 1e-12; out[k] = dict(p=ps[k], bar=round(bar, 5), pass_=ok)
    return out

def verdict():
    D = load(); J, nn = joblist(); missing = [j for j in J if j not in D]
    assert not missing, f'{len(missing)} jobs missing: run more calls first'
    S = {k: stat(v) for k, v in D.items()}; R = dict(per_text={}, gates={}, seed=SEED)
    for k in GATES + PRIMARY + DESC:
        o = S[(k, 0)]; nul = [S[(k, r)] for r in range(1, nn[k] + 1)]; cn = [s['DL'] for s in nul if s['conv']]
        unc = sum(not s['conv'] for s in nul)
        p = (1 + sum(d >= o['DL'] for d in cn)) / (1 + len(cn)) if nn[k] else None
        fin = [d for d in cn if np.isfinite(d)]
        R['per_text'][k] = dict(obs=o, n_null=nn[k], unconverged=unc, p=p, floor=(1 / (1 + len(cn)) if nn[k] else None),
                                testable=bool(o['conv'] and (nn[k] == 0 or unc <= MAX_UNCONV * nn[k])),
                                null_DL_finite=len(fin), null_DL_mean=(float(np.mean(fin)) if fin else None),
                                null_DL_sd=(float(np.std(fin, ddof=1)) if len(fin) > 1 else None),
                                null_neg_inf=sum(d == -np.inf for d in cn), null_pos_inf=sum(d == np.inf for d in cn),
                                null_modes={m: sum(s['modes'][m] for s in nul) for m in ('sticky', 'slot', 'alt')},
                                null_ML_SW_mean=(float(np.mean([s['ML_SW'] for s in nul])) if nul else None))
        print(k, json.dumps(R['per_text'][k], default=float), flush=True)
    sws = [r[1] for (k, rep), v in D.items() if k in GATES for r in v['R']]
    band = float(np.mean([abs(s - STICKY) <= BAND or abs(s - ALT) <= BAND for s in sws]))
    pt = R['per_text']; bar1 = ALPHA / 3
    R['gates'] = dict(G_MODE=dict(band_frac=round(band, 4), n_restarts=len(sws), pass_=band < MAX_BAND),
                      G_POW=dict(p=pt['GPOW']['p'], pass_=bool(pt['GPOW']['testable'] and pt['GPOW']['p'] <= bar1 + 1e-12)),
                      G_FPR=dict(p=pt['GFPR']['p'], pass_=bool(pt['GFPR']['testable'] and pt['GFPR']['p'] > bar1 + 1e-12)))
    gok = all(g['pass_'] for g in R['gates'].values())
    H = holm({k: (pt[k]['p'] if pt[k]['testable'] else 1.0) for k in PRIMARY})
    passed = [k for k in PRIMARY if H[k]['pass_'] and pt[k]['testable']]; untest = [k for k in PRIMARY if not pt[k]['testable']]
    if not gok: lab = 'NOT TESTABLE (gates)'
    elif passed: lab = 'STICKY FAVOURED in ' + '+'.join(passed)
    elif len(untest) == 3: lab = 'NOT TESTABLE (convergence)'
    else: lab = 'NOT SUPPORTED' + (f' (not testable: {"+".join(untest)})' if untest else '')
    R['holm'] = H; R['verdict'] = lab; print(R['gates'], H, lab)
    json.dump(R, open('analysis/C116_results.json', 'w'), indent=1, default=float)

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if a == 'run': run()
    elif a == 'verdict': verdict()
    elif a == 'dry':
        T = texts(); J, nn = joblist(); print({k: len(v) for k, v in T.items()}, 'jobs', len(J))
    else: status()
