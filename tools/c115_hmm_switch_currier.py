#!/usr/bin/env python3
"""C115 (F-HMM step 4): where does C113's 'stickier than slots' live, Currier A, Currier B, or both?
Statistic and null unchanged from C113/C114: SW = posterior-weighted switch rate of the best-of-3 2-state HMM (C111 fit_hmm,
C113 sw_of); null N-SLOT = C109 shuffle_slot, HMM re-fitted; D = SW - null mean. Strata are taken by Currier language from the
ZL3b page headers ($L), in folio order, each exactly NTOK = 10,000 word tokens (whole lines, E.take): A = first 10,000 A tokens;
B1 = first 10,000 B tokens; B2 = next 10,000 B tokens. One-sided test toward 'stickier' (direction fixed by C113):
p_low = (1 + #{null <= obs}) / (1 + NNULL), NNULL = 79 (floor 0.0125), Holm over the 3 primary strata at alpha 0.05.
Gates: G-POW devowelled Latin Caesar, 10,000 tokens, twin-alphabet plant q 0.20 (C114) must reach p_low <= 0.05/3 (validity);
G-FPR the same text unplanted must NOT; G-SIZE per primary stratum: an observation at null_mean - 0.07 (the C113 effect) must lie
below all NNULL replicates, else that stratum is NOT TESTABLE for a C113-size effect (the smoke on devowelled Italian Dante showed
the twin plant is all-or-nothing, so it cannot certify -0.07 itself; disclosed in the case file).
Secondary, descriptive (NNULL_SEC = 20, no p): section strata herbal-A, biological-B, stars-B (first 6,000 tokens each), and
IT2a observed SW for A/B1/B2 (no null).
Pre-registered in case-file/C115-hmm-switch-currier.md. Seed 11780 (main); 11781 smoke calibration; next free 11782.
Run: timeout 600 python3 tools/c115_hmm_switch_currier.py   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
import c049_context_spelling as E
from c047_pair_currier_split import ivtff_pages_lang
from c108_sukhotin_alternation import encode, flat, chars
from c109_sukhotin_slot_null import slot_keys, shuffle_slot
from c113_hmm_switch_slot_null import sw_of, hash_name

SEED, SEED_SMOKE, NTOK, NSEC, NNULL, NNULL_SEC, ALPHA = 11780, 11781, 10000, 6000, 79, 20, 0.05
QSTAR = 0.20          # C114's twin-alphabet share; the smoke showed the plant is all-or-nothing (q <= 0.04: D ~ 0; q 0.07: D -0.42),
                      # so G-POW certifies validity only and the C113-size check is G-SIZE (shift check on each stratum's own null)
SHIFT, SHIFT_HALF = 0.07, 0.035
SECT = [('herbal_A', 'A', 'H'), ('bio_B', 'B', 'B'), ('stars_B', 'B', 'S')]

def twin(words, rng, q): return [tuple('#' + u for u in w) if rng.random() < q else w for w in words]

def lines_by(pl, lang, sect, L=None, S=None):
    return [l for p, l in pl if (L is None or lang.get(p) == L) and (S is None or sect.get(p) == S)]

def strata(path):
    pl, lang, sect = ivtff_pages_lang(path); u = lambda ls: [tuple(T.units(w)) for w in flat(ls)]
    A, Bl = lines_by(pl, lang, sect, 'A'), lines_by(pl, lang, sect, 'B')
    out = dict(A=u(E.take(A, 0, NTOK)), B1=u(E.take(Bl, 0, NTOK)), B2=u(E.take(Bl, NTOK, NTOK)))
    sec = {n: u(E.take(lines_by(pl, lang, sect, L, S), 0, NSEC)) for n, L, S in SECT}
    return out, sec

def devowel_tokens(name, n):
    nat = B.nat_texts(); ls = [l for l in T.devowel(nat[name]) if len(l) >= 3]
    return chars(flat(E.take(ls, 0, n)))

def _job(job):
    name, rep, words = job
    ids, wid, inv = encode(words); rng = np.random.default_rng(np.random.SeedSequence([SEED, hash_name(name), rep]))
    if rep > 0: ids = shuffle_slot(ids, slot_keys(words), rng)
    return name, rep, sw_of(ids, wid, len(inv), rng)

def smoke():
    """calibration on a control only (devowelled Italian Dante, 10,000 tokens): D for a few plant shares, 4 null replicates each"""
    from multiprocessing import Pool
    t0 = time.time(); base = devowel_tokens('Italian_Dante', NTOK); rng = np.random.default_rng(SEED_SMOKE); jobs = []
    for q in (0.0, 0.01, 0.02, 0.04, 0.07):
        w = twin(base, rng, q); jobs += [(f'smk_q{q}', r, w) for r in range(5)]
    res = {}
    with Pool(8) as P:
        for name, rep, (sw, ll, A) in P.imap_unordered(_job, jobs): res[(name, rep)] = sw
    for q in (0.0, 0.01, 0.02, 0.04, 0.07):
        k = f'smk_q{q}'; nl = [res[(k, r)] for r in range(1, 5)]
        print(k, 'n', len(base), 'SW', round(res[(k, 0)], 4), 'null', np.round(nl, 4).tolist(), 'D', round(res[(k, 0)] - float(np.mean(nl)), 4))
    print('smoke s', round(time.time() - t0, 1))

def summ(obs, Tn):
    Tn = np.array(Tn); sd = float(Tn.std(ddof=1))
    return dict(SW=round(obs, 4), null_mean=round(float(Tn.mean()), 4), null_sd=round(sd, 5), null_min=round(float(Tn.min()), 4),
                null_max=round(float(Tn.max()), 4), D=round(obs - float(Tn.mean()), 4), below_all=bool(obs < Tn.min()),
                p_low=(1 + int((Tn <= obs).sum())) / (1 + len(Tn)))

def main():
    from multiprocessing import Pool
    assert QSTAR is not None, 'QSTAR not fixed'
    t0 = time.time(); rng = np.random.default_rng(SEED)
    zl, zsec = strata('data/ZL3b-n.txt'); it, _ = strata('data/IT2a-n.txt'); cae = devowel_tokens('Latin_Caesar', NTOK)
    texts = dict(GPOW=twin(cae, rng, QSTAR), GFPR=cae, **{'ZL_' + k: v for k, v in zl.items()}, **{'SEC_' + k: v for k, v in zsec.items()})
    nn = {k: (NNULL_SEC if k.startswith('SEC_') else NNULL) for k in texts}
    for k, v in it.items(): texts['IT_' + k] = v; nn['IT_' + k] = 0
    print('built', {k: len(v) for k, v in texts.items()}, round(time.time() - t0, 1), flush=True)
    jobs = [(k, r, texts[k]) for r in range(NNULL + 1) for k in texts if r <= nn[k]]
    res = {}; fck = open('analysis/C115_checkpoint.jsonl', 'w')
    with Pool(8) as P:
        for name, rep, (sw, ll, A) in P.imap_unordered(_job, jobs):
            res[(name, rep)] = sw; fck.write(json.dumps([name, rep, sw, ll, A]) + '\n'); fck.flush()
            if rep == 0: print('obs', name, round(sw, 4), A, round(time.time() - t0, 1), flush=True)
    R = dict(seed=SEED, NTOK=NTOK, NSEC=NSEC, NNULL=NNULL, NNULL_SEC=NNULL_SEC, QSTAR=QSTAR, alpha=ALPHA, n_tokens={k: len(v) for k, v in texts.items()}, texts={})
    for k in texts:
        R['texts'][k] = summ(res[(k, 0)], [res[(k, r)] for r in range(1, nn[k] + 1)]) if nn[k] else dict(SW=round(res[(k, 0)], 4))
        if k.startswith('SEC_'): R['texts'][k].pop('p_low')
        print(k, R['texts'][k], flush=True)
    lvl = ALPHA / 3; g = R['texts']
    R['gates'] = dict(GPOW_p_low=g['GPOW']['p_low'], GPOW_D=g['GPOW']['D'], GFPR_p_low=g['GFPR']['p_low'], GFPR_D=g['GFPR']['D'], level=lvl,
                      ok=bool(g['GPOW']['p_low'] <= lvl and g['GFPR']['p_low'] > lvl))
    size = {}
    for k in ('A', 'B1', 'B2'):
        t = g['ZL_' + k]; size[k] = dict(full=bool(t['null_mean'] - SHIFT < t['null_min']), half=bool(t['null_mean'] - SHIFT_HALF < t['null_min']),
                                         margin=round(t['null_min'] - t['null_mean'], 4))
    R['gates']['G_SIZE'] = size; testable = [k for k in ('A', 'B1', 'B2') if size[k]['full']]
    ps = sorted(((g['ZL_' + k]['p_low'], k) for k in testable)); sticky = set(); m = 3
    for i, (p, k) in enumerate(ps):
        if p <= ALPHA / (m - i): sticky.add(k)
        else: break
    if not R['gates']['ok'] or not testable: lab = 'NOT TESTABLE'
    elif not sticky: lab = 'NOT LOCALISED'
    elif sticky == {'A'}: lab = 'A-SPECIFIC'
    elif 'A' not in sticky: lab = 'B-ONLY'
    else: lab = 'SHARED A+B'
    R['verdict'] = dict(H1=lab, holm_sticky=sorted(sticky), not_testable_strata=[k for k in ('A', 'B1', 'B2') if k not in testable], B1_vs_B2_D=[g['ZL_B1']['D'], g['ZL_B2']['D']],
                        IT_SW={k: g['IT_' + k]['SW'] for k in ('A', 'B1', 'B2')})
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C115_results.json', 'w'), indent=1, default=float); print(R['gates'], R['verdict'], R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke': smoke()
    elif len(sys.argv) > 1 and sys.argv[1] == 'sizes':
        zl, zsec = strata('data/ZL3b-n.txt'); print({k: len(v) for k, v in {**zl, **zsec}.items()})
    else: main()
