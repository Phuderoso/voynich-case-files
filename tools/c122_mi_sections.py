#!/usr/bin/env python3
"""C122 (F-MID step 3): where does the Currier B echo live? The C120/C121 statistic, per illustration section of Currier B.
Instrument verbatim from C120 (imported unchanged from tools/c120_mi_distance.py): C070 parser, paragraph loci, words
 [a-z]+, lines >= 5 words; per page the EVA units of each word + separator '_'; M = sum_d plug-in MI(d),
 d in (16,24,32,48,64,96,128,192,256), pairs inside a page; null N-PAGE = words permuted within their page.
 E = M - mean(M*), z = E / sd(M*), p one-sided = (1 + #M* >= M)/(R + 1). Plant family P(q,k) = C121's multi-word copy
 (imported unchanged from tools/c121_mi_calibrated.py).
SECTIONS (fixed before any section statistic was computed). Section of a Currier-B page = its ZL3b header illustration code
 $I (H herbal, B biological/balneo, S stars/recipes, T text-only, C cosmological, ...). The SAME page->section map (from
 ZL3b) is used for IT2a; an IT2a Currier-B page absent from the ZL3b map takes its own IT2a $I. Pages keep the Currier
 language of their own transcription (as in C120/C121). MINIMUM: a section is tested only if it has >= 1,500 words in
 ZL3b (after the C070 filters); smaller sections are printed and dropped. Expected from the header count: H, B, S, T kept,
 C (~350 words) dropped.
ALPHA: Holm over all 8 tests {kept sections} x {ZL3b, IT2a} at 0.05 (fixed family even if a section is NOT TESTABLE).
 alpha_g = 0.05/8 = 0.00625 (strictest Holm step) for calibration and gates.
Stages (one command 'run', every job checkpointed in analysis/c122_ckpt/, wrapped in 'timeout 600' and resumable):
 1 G-INV (seed 11826): C121's invariance check repeated on the SMALLEST kept section template (Latin Caesar recut):
   page multisets exact over 200 null draws, null sd > 0, share of null M equal to observed <= 1 %, |dM| under symbol
   relabelling < 1e-9. Fail -> every section NOT TESTABLE.
 2 CALIBRATION on controls only (seed 11822, stream [11822, si, ci]): C121's 10 controls (7 Gutenberg naturals, Hebrew
   Gen+Exod, Timm-Schinner runs 11812, 11813), each recut into the section's ZL3b page/line word-count template; per
   control x section 8 pseudo replicates (words shuffled inside each page), each tested unplanted and with every rung
   (R_c 200). RESCALING RULE: ladder starts at the C121 Currier-B plant 0.75x4 and climbs in the same family:
   0.75x4 (dose 3), 0.75x5 (3.75), 1.0x4 (4), 1.0x5 (5), 1.0x6 (6). Chosen rung = smallest dose with pooled power
   >= 0.90 at alpha_g over the 80 planted tests; calibration valid only if FPR (unplanted p <= alpha_g) <= 3/80.
   No rung -> section NOT TESTABLE (calibration).
 3 GATES on the manuscript (seed 11823, stream [11823, i], i over strata in fixed order): per section x transcription,
   20 pseudo replicates (C120 pseudo()), R_g 200. G-FPR unplanted p <= alpha_g in <= 2/20; G-POW chosen plant
   p <= alpha_g in >= 16/20. Mean planted E printed.
 4 H1 (seed 11824, stream [11824, i]): R 1000 per stratum; printed: units, words, pages, E, null sd, z, p, effective N
   (= R, M always finite), E per lag.
 5 DESCRIPTIVE D-COL (seed 11825, R 200; never a verdict): per stratum, word-level copy from the previous line in the same
   page: COL = # word positions j with w[i][j] == w[i-1][j]; ANY = # positions with w[i][j] in line i-1 at some other
   position (and not the same column). Null: C120 pseudo() (words shuffled within page, recut into the same line lengths).
   Printed: obs, null mean, ratio obs/null, z for COL and ANY. Pre-declared reading: 'column-led' if the COL ratio
   exceeds the ANY ratio and COL z >= 3; 'anywhere-led' if the reverse; otherwise 'no clear lead'.
VERDICT per section (needs G-INV pass, valid calibration, gates pass in BOTH transcriptions; else NOT TESTABLE):
 DETECTED both transcriptions reject (Holm); PARTIAL one; EXCLUDED none AND the chosen plant's mean planted E on the
 manuscript pseudo replicates (mean of the two transcriptions) <= 0.0070 bits (C121 pooled ZL3b-B excess), i.e. an echo
 as large as the pooled Currier-B one is excluded from that section; if none rejects but that plant E > 0.0070 ->
 NOT TESTABLE (coarse: the instrument only certifies echoes larger than the pooled one there).
 Distinct tests (Kryptos lesson): 2 transcriptions of the same pages = one result seen twice; 4 distinct section results.
Run: timeout 600 python3 tools/c122_mi_sections.py run  -> analysis/C122_results.json (+ log by tee)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time, hashlib
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c120_mi_distance import Stream, pseudo, recut, holm, LAGS, FILES
from c070_word2_sh import parse
from c121_mi_calibrated import plant, controls

CSEED, GSEED, SEED, DSEED, ISEED = 11822, 11823, 11824, 11825, 11826
ALPHA, NT = 0.05, 8
AG = ALPHA / NT
R, RG, RC, RD, NG, NC, MINW, EB = 1000, 200, 200, 200, 20, 8, 1500, 0.0070
LADDER = sorted([(0.75, 4), (0.75, 5), (1.0, 4), (1.0, 5), (1.0, 6)], key=lambda r: (r[0] * r[1], r[1]))
CK = 'analysis/c122_ckpt/'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def headers(path):
    meta = {}
    for raw in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2)))
    return meta

ZMAP = {p: d.get('I') for p, d in headers(dict((t, f) for t, f in FILES)['ZL3b']).items()}

def sections(path):
    own = headers(path); pages, order = {}, []
    for l in parse(path):
        if l['L'] != 'B': continue
        sec = ZMAP.get(l['page']) or own.get(l['page'], {}).get('I')
        key = (sec, l['page'])
        if key not in pages: pages[key] = []; order.append(key)
        pages[key].append(l['words'])
    out = {}
    for k in order: out.setdefault(k[0], []).append(pages[k])
    return out

def nwords(pages): return sum(len(l) for p in pages for l in p)

def cal_job(a):
    si, ci, sec, name, words, eva = a
    f = f'{CK}cal_{sec}_{ci}.json'
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([CSEED, si, ci]); base = recut(words, TEMPL[sec])
    mk = (lambda pg: Stream(pg)) if eva else (lambda pg: Stream(pg, tok=list))
    res = dict(sec=sec, control=name, words=nwords(base), unplanted=[], rungs={})
    for _ in range(NC):
        ps = pseudo(base, rng)
        t = mk(ps).test(rng, RC); res['unplanted'].append([t['p'], t['E']])
        for q, k in LADDER:
            t = mk(plant(ps, rng, q, k)).test(rng, RC); res['rungs'].setdefault(f'{q}x{k}', []).append([t['p'], t['E']])
    json.dump(res, open(f, 'w')); return res

def gate_job(a):
    i, sec, t, pages, q, k = a
    f = f'{CK}gate_{sec}_{t}.json'
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, i]); fp = pw = 0; Ep = []; E0 = []
    for _ in range(NG):
        ps = pseudo(pages, rng)
        t0 = Stream(ps).test(rng, RG); fp += t0['p'] <= AG; E0.append(t0['E'])
        tp = Stream(plant(ps, rng, q, k)).test(rng, RG); pw += tp['p'] <= AG; Ep.append(tp['E'])
    r = dict(key=f'{sec}_{t}', plant=f'{q}x{k}', fpr=int(fp), power=int(pw), E_plant_mean=float(np.mean(Ep)),
             E_unplanted_mean=float(np.mean(E0)), pass_=bool(fp <= 2 and pw >= 16))
    json.dump(r, open(f, 'w')); return r

def h1_job(a):
    i, sec, t, pages = a
    f = f'{CK}h1_{sec}_{t}.json'
    if os.path.exists(f): return json.load(open(f))
    r = Stream(pages).test(np.random.default_rng([SEED, i]), R); r['key'] = f'{sec}_{t}'; r['effective_N'] = R
    json.dump(r, open(f, 'w')); return r

def dcol(pages):
    col = anyp = 0
    for p in pages:
        for a, b in zip(p[:-1], p[1:]):
            sa = set(a)
            for j, w in enumerate(b):
                if j < len(a) and a[j] == w: col += 1
                elif w in sa: anyp += 1
    return col, anyp

def d_job(a):
    i, sec, t, pages = a
    rng = np.random.default_rng([DSEED, i]); c, n = dcol(pages)
    nul = np.array([dcol(pseudo(pages, rng)) for _ in range(RD)], float)
    out = dict(key=f'{sec}_{t}')
    for j, (nm, o) in enumerate((('COL', c), ('ANY', n))):
        m, s = nul[:, j].mean(), nul[:, j].std(ddof=1)
        out[nm] = dict(obs=int(o), null_mean=float(m), ratio=float(o / m) if m else None, z=float((o - m) / s) if s else None)
    rc, ra = out['COL']['ratio'] or 0, out['ANY']['ratio'] or 0
    out['reading'] = ('column-led' if rc > ra and (out['COL']['z'] or 0) >= 3 else
                      'anywhere-led' if ra > rc and (out['ANY']['z'] or 0) >= 3 else 'no clear lead')
    return out

def invariance(sec):
    f = f'{CK}inv.json'
    if os.path.exists(f): return json.load(open(f))
    from c003_position_rigidity import gutenberg
    rng = np.random.default_rng(ISEED); w = [x for l in gutenberg('data/corpora/pg218.txt') for x in l]
    s = Stream(recut(w, TEMPL[sec]), tok=list); M = s.mi(s.x).sum(); exact = True; nul = []
    upg = np.repeat(s.pg, s.L)
    for _ in range(200):
        y = s.perm(rng); nul.append(s.mi(y).sum())
        for k in range(len(s.pages)):
            m = upg == k
            if not np.array_equal(np.bincount(y[m], minlength=s.K), np.bincount(s.x[m], minlength=s.K)): exact = False
    nul = np.array(nul); Mr = s.mi(rng.permutation(s.K)[s.x]).sum()
    out = dict(seed=ISEED, control=f'Latin Caesar on ZL3b-B section {sec} template', M=float(M), null_sd=float(nul.std(ddof=1)),
               share_null_equal_obs=float(np.mean(np.isclose(nul, M, rtol=0, atol=1e-12))), page_multiset_exact=exact,
               relabel_delta=float(abs(Mr - M)))
    out['pass'] = bool(exact and out['null_sd'] > 0 and out['share_null_equal_obs'] <= 0.01 and out['relabel_delta'] < 1e-9)
    json.dump(out, open(f, 'w')); return out

SEC = {t: sections(f) for t, f in FILES}
KEPT = sorted([s for s, pg in SEC['ZL3b'].items() if nwords(pg) >= MINW], key=lambda s: -nwords(SEC['ZL3b'][s]))
TEMPL = {s: SEC['ZL3b'][s] for s in KEPT}

def run():
    res = dict(cycle='C122', seeds=dict(cal=CSEED, gates=GSEED, H1=SEED, dcol=DSEED, inv=ISEED), alpha=ALPHA, alpha_g=AG,
               R=R, RG=RG, RC=RC, NC=NC, NG=NG, min_words=MINW, EB=EB, ladder=[f'{q}x{k}' for q, k in LADDER],
               tool_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
    res['strata'] = {t: {s: dict(pages=len(pg), lines=sum(len(p) for p in pg), words=nwords(pg),
                                 units=int(sum(len(x) + 1 for p in pg for l in p for x in l)), kept=s in KEPT) for s, pg in SEC[t].items()} for t in SEC}
    log('strata', res['strata'], 'kept', KEPT)
    inv = invariance(KEPT[-1]); res['G_INV'] = inv; log('G-INV', inv)
    ctr = controls()
    jobs = [(si, ci, s, n, w, e) for si, s in enumerate(KEPT) for ci, (n, w, e) in enumerate(ctr)]
    with Pool(8) as P: out = P.map(cal_job, jobs)
    cal = {}
    for s in KEPT:
        rs = [o for o in out if o['sec'] == s]
        fp = sum(p <= AG for o in rs for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs)
        tab = {}
        for q, k in LADDER:
            key = f'{q}x{k}'; ps = [x for o in rs for x in o['rungs'][key]]
            tab[key] = dict(dose=q * k, power=sum(p <= AG for p, _ in ps) / len(ps), E_mean=float(np.mean([e for _, e in ps])),
                            min_control_power=min(sum(p <= AG for p, _ in o['rungs'][key]) / NC for o in rs))
        ch = next((k for k in tab if tab[k]['power'] >= 0.90), None)
        cal[s] = dict(fpr=f'{fp}/{n}', fpr_ok=fp <= 3, ladder=tab, chosen=ch, valid=bool(fp <= 3 and ch is not None),
                      control_words=[o['words'] for o in rs])
        log('cal', s, cal[s]['fpr'], ch, {k: (round(v['power'], 3), round(v['E_mean'], 4)) for k, v in tab.items()})
    res['calibration'] = cal
    order = [(s, t) for s in KEPT for t in ('ZL3b', 'IT2a')]
    gj = []
    for i, (s, t) in enumerate(order):
        ch = cal[s]['chosen']
        if ch: q, k = ch.split('x'); gj.append((i, s, t, SEC[t][s], float(q), int(k)))
    with Pool(8) as P:
        G = P.map(gate_job, gj)
        H = P.map(h1_job, [(i, s, t, SEC[t][s]) for i, (s, t) in enumerate(order)])
        D = P.map(d_job, [(i, s, t, SEC[t][s]) for i, (s, t) in enumerate(order)])
    res['gates'] = {g['key']: g for g in G}; res['H1'] = {h['key']: h for h in H}; res['DCOL'] = {d['key']: d for d in D}
    for g in G: log('gate', g)
    for h in H: log('H1', h['key'], {k: h[k] for k in ('units', 'E', 'null_sd', 'z', 'p')})
    for d in D: log('DCOL', d)
    rej = holm({k: v['p'] for k, v in res['H1'].items()}); res['holm'] = rej; ver = {}
    for s in KEPT:
        ks = [f'{s}_ZL3b', f'{s}_IT2a']
        if not inv['pass']: ver[s] = 'NOT TESTABLE (G-INV)'; continue
        if not cal[s]['valid']: ver[s] = 'NOT TESTABLE (calibration)'; continue
        if not all(k in res['gates'] and res['gates'][k]['pass_'] for k in ks): ver[s] = 'NOT TESTABLE (gate)'; continue
        n = sum(rej[k] for k in ks)
        if n == 2: ver[s] = 'DETECTED'
        elif n == 1: ver[s] = 'PARTIAL'
        else:
            ep = float(np.mean([res['gates'][k]['E_plant_mean'] for k in ks]))
            ver[s] = 'EXCLUDED' if ep <= EB else 'NOT TESTABLE (coarse)'
    res['verdict'] = ver; res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open('analysis/C122_results.json', 'w'), indent=1, default=float); log('holm', rej); log('verdict', ver)

if __name__ == '__main__':
    os.makedirs(CK, exist_ok=True)
    {'run': run}[sys.argv[1]]()
