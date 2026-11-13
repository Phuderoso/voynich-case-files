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
AMENDMENT 2026-11-13 (Kryptos review, before any C115 count; case file section 'Amendment 2026-11-13'):
(A) G-SIZE only decides what a NON-pass means: all 3 primary strata enter Holm (m = 3 fixed); a Holm pass is a pass whatever its
G-SIZE; fail Holm AND fail G-SIZE -> that stratum is LOW-POWER (not evidence of absence); NOT LOCALISED needs every non-passing
stratum to pass G-SIZE, else 'NOT LOCALISED (LOW-POWER)'. The old 'NOT TESTABLE if no stratum passes G-SIZE' rule is removed.
(1) Descriptive only (no decision role): line-mix plant curve on devowelled Latin Caesar, whole lines replaced with probability
f in {0.1, 0.2, 0.3, 0.5} from two sticky sources (twin-alphabet rewrite of the line; devowelled Italian Dante lines), NREP_LM = 10
slot-null replicates each, seed 11782; and a line bootstrap (B_BOOT = 100, seed 11783) of the observed side of each primary
stratum: obs-side sd printed next to null sd, flag 'shift model off' if the ratio is > 2 or < 1/2.
(3) NNULL = 159 (floor 0.00625); checkpoint is resumable (per-job seeds, so a resumed run is identical); timeout 900 per call,
at most 2 calls. min attainable p and the first Holm step are printed.
Run: timeout 900 python3 tools/c115_hmm_switch_currier.py   (if exit 124, run the same command once more; it resumes)   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
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

SEED, SEED_SMOKE, NTOK, NSEC, NNULL, NNULL_SEC, ALPHA = 11780, 11781, 10000, 6000, 159, 20, 0.05   # NNULL 79 -> 159 by amendment 2026-11-13
SEED_LM, SEED_BOOT, LM_F, NREP_LM, B_BOOT, SD_RATIO_FLAG = 11782, 11783, (0.1, 0.2, 0.3, 0.5), 10, 100, 2.0   # amendment (1), descriptive
CKPT = 'analysis/C115_checkpoint.jsonl'
QSTAR = 0.20          # C114's twin-alphabet share; the smoke showed the plant is all-or-nothing (q <= 0.04: D ~ 0; q 0.07: D -0.42),
                      # so G-POW certifies validity only and the C113-size check is G-SIZE (shift check on each stratum's own null)
SHIFT, SHIFT_HALF = 0.07, 0.035
SECT = [('herbal_A', 'A', 'H'), ('bio_B', 'B', 'B'), ('stars_B', 'B', 'S')]

def twin(words, rng, q): return [tuple('#' + u for u in w) if rng.random() < q else w for w in words]

def lines_by(pl, lang, sect, L=None, S=None):
    return [l for p, l in pl if (L is None or lang.get(p) == L) and (S is None or sect.get(p) == S)]

def strata(path, with_lines=False):
    pl, lang, sect = ivtff_pages_lang(path); u = lambda ls: [tuple(T.units(w)) for w in flat(ls)]
    A, Bl = lines_by(pl, lang, sect, 'A'), lines_by(pl, lang, sect, 'B')
    L = dict(A=E.take(A, 0, NTOK), B1=E.take(Bl, 0, NTOK), B2=E.take(Bl, NTOK, NTOK))
    out = {k: u(v) for k, v in L.items()}
    sec = {n: u(E.take(lines_by(pl, lang, sect, L_, S), 0, NSEC)) for n, L_, S in SECT}
    if with_lines: return out, sec, {k: [[tuple(T.units(w)) for w in l] for l in v] for k, v in L.items()}
    return out, sec

def devowel_lines(name, n):
    nat = B.nat_texts(); ls = [l for l in T.devowel(nat[name]) if len(l) >= 3]
    return [chars(l) for l in E.take(ls, 0, n)]

def devowel_tokens(name, n): return flat(devowel_lines(name, n))

def line_mix(base, other, rng, f, src):
    """amendment (1), descriptive: each base line is replaced, with probability f, by a whole line from a sticky source:
    src 'twin' = the same line rewritten in the twin alphabet; src 'dante' = the next unused devowelled Italian Dante line"""
    out, j = [], 0
    for l in base:
        if rng.random() < f:
            if src == 'twin': out.append([tuple('#' + u for u in w) for w in l])
            else: out.append(other[j % len(other)]); j += 1
        else: out.append(l)
    return flat(out)

def _job(job):
    name, rep, words = job[:3]; kind = job[3] if len(job) > 3 else 'slot'
    if kind == 'boot':   # amendment (1): line bootstrap of the observed side; words = list of lines; no slot shuffle
        rng = np.random.default_rng(np.random.SeedSequence([SEED_BOOT, hash_name(name), rep]))
        words = flat([words[i] for i in rng.integers(0, len(words), len(words))])
        ids, wid, inv = encode(words); return name, rep, sw_of(ids, wid, len(inv), rng)
    s0 = SEED_LM if name.startswith('LM_') else SEED
    ids, wid, inv = encode(words); rng = np.random.default_rng(np.random.SeedSequence([s0, hash_name(name), rep]))
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
    zl, zsec, zlines = strata('data/ZL3b-n.txt', with_lines=True); it, _ = strata('data/IT2a-n.txt'); cae = devowel_tokens('Latin_Caesar', NTOK)
    texts = dict(GPOW=twin(cae, rng, QSTAR), GFPR=cae, **{'ZL_' + k: v for k, v in zl.items()}, **{'SEC_' + k: v for k, v in zsec.items()})
    nn = {k: (NNULL_SEC if k.startswith('SEC_') else NNULL) for k in texts}
    for k, v in it.items(): texts['IT_' + k] = v; nn['IT_' + k] = 0
    # amendment (1), descriptive: line-mix plant curve (seed 11782); built after the primary texts so the main rng stream is unchanged
    cae_l = devowel_lines('Latin_Caesar', NTOK); dan_l = devowel_lines('Italian_Dante', 2 * NTOK); rlm = np.random.default_rng(SEED_LM)
    for src in ('twin', 'dante'):
        for f in LM_F: k = f'LM_{src}_f{f}'; texts[k] = line_mix(cae_l, dan_l, rlm, f, src); nn[k] = NREP_LM
    print('built', {k: len(v) for k, v in texts.items()}, round(time.time() - t0, 1), flush=True)
    jobs = [(k, r, texts[k]) for r in range(NNULL + 1) for k in texts if r <= nn[k]]
    jobs += [('BOOT_' + k, b, zlines[k], 'boot') for b in range(1, B_BOOT + 1) for k in ('A', 'B1', 'B2')]
    cfg = dict(seed=SEED, seed_lm=SEED_LM, seed_boot=SEED_BOOT, NNULL=NNULL, NNULL_SEC=NNULL_SEC, NREP_LM=NREP_LM, B_BOOT=B_BOOT,
               n_tokens={k: len(v) for k, v in texts.items()}, n_jobs=len(jobs))
    res = {}; boot = {}
    if os.path.exists(CKPT):   # resume (amendment (3)): only a checkpoint written under the identical config is accepted
        with open(CKPT) as fh:
            head = json.loads(fh.readline()); assert head == {'config': cfg}, 'checkpoint config mismatch: refuse to resume'
            for line in fh:
                try: name, rep, sw, ll, A = json.loads(line)
                except ValueError: continue   # torn last line after a timeout
                (boot if name.startswith('BOOT_') else res)[(name, rep)] = sw
        print('resumed', len(res) + len(boot), 'of', len(jobs), flush=True); fck = open(CKPT, 'a')
    else:
        fck = open(CKPT, 'w'); fck.write(json.dumps({'config': cfg}) + '\n'); fck.flush()
    todo = [j for j in jobs if (j[0], j[1]) not in res and (j[0], j[1]) not in boot]
    with Pool(8) as P:
        for name, rep, (sw, ll, A) in P.imap_unordered(_job, todo):
            (boot if name.startswith('BOOT_') else res)[(name, rep)] = sw
            fck.write(json.dumps([name, rep, sw, ll, A]) + '\n'); fck.flush()
            if rep == 0: print('obs', name, round(sw, 4), A, round(time.time() - t0, 1), flush=True)
    fck.close()
    R = dict(seed=SEED, seed_lm=SEED_LM, seed_boot=SEED_BOOT, NTOK=NTOK, NSEC=NSEC, NNULL=NNULL, NNULL_SEC=NNULL_SEC, NREP_LM=NREP_LM,
             B_BOOT=B_BOOT, QSTAR=QSTAR, alpha=ALPHA, n_tokens={k: len(v) for k, v in texts.items()}, texts={},
             min_attainable_p=1 / (1 + NNULL), first_holm_step=ALPHA / 3)
    print(f'min attainable p = {1 / (1 + NNULL):.5f} vs first Holm step {ALPHA / 3:.4f}', flush=True)
    for k in texts:
        R['texts'][k] = summ(res[(k, 0)], [res[(k, r)] for r in range(1, nn[k] + 1)]) if nn[k] else dict(SW=round(res[(k, 0)], 4))
        if k.startswith('SEC_') or k.startswith('LM_'): R['texts'][k].pop('p_low')
        print(k, R['texts'][k], flush=True)
    lvl = ALPHA / 3; g = R['texts']
    R['gates'] = dict(GPOW_p_low=g['GPOW']['p_low'], GPOW_D=g['GPOW']['D'], GFPR_p_low=g['GFPR']['p_low'], GFPR_D=g['GFPR']['D'], level=lvl,
                      ok=bool(g['GPOW']['p_low'] <= lvl and g['GFPR']['p_low'] > lvl))
    size = {}
    for k in ('A', 'B1', 'B2'):
        t = g['ZL_' + k]; size[k] = dict(full=bool(t['null_mean'] - SHIFT < t['null_min']), half=bool(t['null_mean'] - SHIFT_HALF < t['null_min']),
                                         margin=round(t['null_min'] - t['null_mean'], 4))
    R['gates']['G_SIZE'] = size
    # amendment (A): all 3 strata enter Holm (m = 3 fixed, never shrunk); G-SIZE only qualifies a non-pass
    ps = sorted(((g['ZL_' + k]['p_low'], k) for k in ('A', 'B1', 'B2'))); sticky = set(); m = 3
    for i, (p, k) in enumerate(ps):
        if p <= ALPHA / (m - i): sticky.add(k)
        else: break
    low_power = [k for k in ('A', 'B1', 'B2') if k not in sticky and not size[k]['full']]
    if not R['gates']['ok']: lab = 'NOT TESTABLE'
    elif not sticky: lab = 'NOT LOCALISED (LOW-POWER)' if low_power else 'NOT LOCALISED'
    else:
        lab = 'A-SPECIFIC' if sticky == {'A'} else ('B-ONLY' if 'A' not in sticky else 'SHARED A+B')
        if low_power: lab += ' (' + ', '.join(low_power) + ' LOW-POWER)'
    # amendment (1), descriptive: obs-side line-bootstrap sd vs null sd per primary stratum; line-mix curve
    shift = {}
    for k in ('A', 'B1', 'B2'):
        bs = np.array([boot[('BOOT_' + k, b)] for b in range(1, B_BOOT + 1)]); bsd = float(bs.std(ddof=1)); nsd = g['ZL_' + k]['null_sd']
        ratio = bsd / nsd if nsd > 0 else float('inf')
        shift[k] = dict(boot_sd=round(bsd, 5), boot_mean=round(float(bs.mean()), 4), null_sd=nsd, ratio=round(ratio, 3),
                        shift_model_off=bool(ratio > SD_RATIO_FLAG or ratio < 1 / SD_RATIO_FLAG))
        print('shift-check', k, shift[k], flush=True)
    R['descriptive'] = dict(shift_check=shift, line_mix={k: dict(D=g[k]['D'], null_sd=g[k]['null_sd'], SW=g[k]['SW']) for k in texts if k.startswith('LM_')})
    R['verdict'] = dict(H1=lab, holm_sticky=sorted(sticky), low_power_strata=low_power, B1_vs_B2_D=[g['ZL_B1']['D'], g['ZL_B2']['D']],
                        IT_SW={k: g['IT_' + k]['SW'] for k in ('A', 'B1', 'B2')},
                        confound='Currier A is mostly herbal and B mostly biological/stars: A vs B is partly section vs section; '
                                 'this design does not separate language from section.')
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C115_results.json', 'w'), indent=1, default=float); print(R['gates'], R['verdict'], R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke': smoke()
    elif len(sys.argv) > 1 and sys.argv[1] == 'dry':   # amendment tool check: builds texts and the job list only, fits nothing on the manuscript
        zl, zsec, zlines = strata('data/ZL3b-n.txt', with_lines=True); cae_l = devowel_lines('Latin_Caesar', NTOK)
        dan_l = devowel_lines('Italian_Dante', 2 * NTOK); rlm = np.random.default_rng(SEED_LM)
        lm = {f'LM_{s}_f{f}': len(line_mix(cae_l, dan_l, rlm, f, s)) for s in ('twin', 'dante') for f in LM_F}
        nj = 2 * (NNULL + 1) + 3 * (NNULL + 1) + 3 * (NNULL_SEC + 1) + 3 + len(lm) * (NREP_LM + 1) + 3 * B_BOOT
        print('lines', {k: len(v) for k, v in zlines.items()}, 'tokens', {k: sum(map(len, v)) for k, v in zlines.items()}, 'LM', lm, 'jobs', nj)
    elif len(sys.argv) > 1 and sys.argv[1] == 'sizes':
        zl, zsec = strata('data/ZL3b-n.txt'); print({k: len(v) for k, v in {**zl, **zsec}.items()})
    else: main()
