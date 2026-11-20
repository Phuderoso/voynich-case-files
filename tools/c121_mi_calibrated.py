#!/usr/bin/env python3
"""C121 (F-MID step 2): glyph mutual information at a distance with a plant CALIBRATED ON CONTROLS FIRST.
Instrument, statistic, null and strata are C120's verbatim (imported from tools/c120_mi_distance.py, unchanged):
 M = sum_d plug-in MI(d), d in (16,24,32,48,64,96,128,192,256), pairs inside a page; null N-PAGE = words permuted within page.
What is new: the plant. C120's one-word self-citation at q 0.25 was too faint (G-POW 0-3/20). Here a plant ladder is run on
CONTROL texts only (never the manuscript) and a written rule picks the plant per Currier template before any manuscript run.
Stages (each wrapped in 'timeout 600'; per-job checkpoints so a killed stage resumes):
  inv   G-INV invariance / non-degeneracy pre-check of the null on a control (lesson of C118). seed 11820.
  cal   calibration on controls only -> analysis/C121_calibration.json. seed 11817.
  run   registered test (gates on manuscript pseudo replicates with the chosen plant, then H1) -> analysis/C121_results.json.
        seeds 11818 (gates), 11819 (H1).
Plant P(q,k) 'multi-word copy': in every line after a page's first, with probability q, a start j is drawn uniformly in
 [0, len-k] and the k words at j..j+k-1 are replaced by copies of the previous (already planted) line's words at positions
 min(j+i, len(prev)-1). Line lengths are kept. Ladder: k in {1,2,3} x q in {0.25,0.5,0.75,1.0}, dose = q*k, ascending
 (ties: smaller k first).
Controls (C120 H2 panel texts, nothing new): Latin Caesar, Latin Descartes, Italian Dante, Spanish Cervantes, Italian
 Machiavelli, Finnish Kivi, Finnish Kalevala, Hebrew Gen+Exod, and Timm-Schinner runs 11812, 11813 (C120 seeds), each recut
 into the ZL3b Currier A and Currier B page/line word-count templates (only the word counts per line are borrowed; no glyph).
 Per control and template: 8 pseudo replicates (words shuffled inside each page, recut into the template lines); on each,
 one unplanted test and one test per ladder rung (R_c = 200, N-PAGE). Total per rung and template: 80 tests.
Calibration rule (fixed in this file before calibration ran), per template T in {A, B}, alpha_g = 0.0125 (= 0.05/4, the
 strictest Holm step):
  FPR_T = share of the 80 unplanted tests with p <= alpha_g. Calibration valid only if FPR_T <= 3/80.
  POW_T(rung) = share of the 80 planted tests with p <= alpha_g.
  chosen rung = smallest dose with POW_T >= 0.90 (margin over the 0.80 registered gate). None -> template NOT TESTABLE.
  Comparability (reported, and a gate for B): mean planted excess E_plant(rung) on the B template must be <= 0.0070 bits
  (the public descriptive C120 Voynich ZL3b-B excess), so the plant certifies an effect no larger than the one seen.
  If it is larger, B is flagged 'plant larger than observed' and its verdict is NOT TESTABLE.
AMENDMENT 1 (written after stage-1 calibration on controls, before any manuscript run; tool sha 46f4d07d ran stage 1):
 no stage-1 rung reached 0.90 (B best 1.0x3: 0.8625, E 0.0035; A best 1.0x3: 0.3375). Stage 'cal2' extends the ladder
 upward with the same plant family and the same rule: k in {4, 5} x q in {0.75, 1.0}, fresh seed 11821 (stream
 [11821, ti, ci]), same controls/templates/R_c/NC; its unplanted tests are added to FPR (bar <= 6/160). The chosen rung is the
 smallest dose over stage 1 + stage 2 with POW_T >= 0.90; comparability for B unchanged (E_plant <= 0.0070).
 Calibration output: analysis/C121_calibration.json (stage 1 kept in key 'stage1').
Registered test (run): per stratum {A,B}x{ZL3b,IT2a}: 20 manuscript pseudo replicates (C120 pseudo()), R_g 200,
 G-FPR unplanted p <= alpha_g in <= 2/20; G-POW chosen plant p <= alpha_g in >= 16/20. H1: R 1000, Holm over 4 at 0.05.
 Per language: DETECTED (both transcriptions reject), PARTIAL (one), EXCLUDED (none, all gates pass: an in-page echo of the
 calibrated plant's size is excluded), NOT TESTABLE (any gate fails, or G-INV fails, or no rung qualified).
 Printed beside p: null sd, effective N (finite replicates), E per lag.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, hashlib
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c120_mi_distance import Stream, strata, pseudo, recut, holm, LAGS, FILES
from c003_position_rigidity import gutenberg, hebrew

CSEED, GSEED, SEED, ISEED, CSEED2 = 11817, 11818, 11819, 11820, 11821
ALPHA, AG, R, RG, RC, NG, NC = 0.05, 0.0125, 1000, 200, 200, 20, 8
EB = 0.0070
LADDER2 = sorted([(q, k) for k in (4, 5) for q in (0.75, 1.0)], key=lambda r: (r[0] * r[1], r[1]))
LADDER = sorted([(q, k) for k in (1, 2, 3) for q in (0.25, 0.5, 0.75, 1.0)], key=lambda r: (r[0] * r[1], r[1]))
NAT = [('Latin Caesar', 'pg218.txt'), ('Latin Descartes', 'pg23306.txt'), ('Italian Dante', 'pg1012.txt'),
       ('Spanish Cervantes', 'pg2000.txt'), ('Italian Machiavelli', 'pg56498.txt'), ('Finnish Kivi', 'pg11940.txt'),
       ('Finnish Kalevala', 'pg7000.txt')]
CK = 'analysis/c121_ckpt/'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def plant(pages, rng, q, k):
    out = []
    for p in pages:
        new = [list(p[0])]
        for l in p[1:]:
            l = list(l)
            if rng.random() < q:
                kk = min(k, len(l)); j = int(rng.integers(len(l) - kk + 1)); prev = new[-1]
                for i in range(kk): l[j + i] = prev[min(j + i, len(prev) - 1)]
            new.append(l)
        out.append(new)
    return out

def controls():
    C = 'data/corpora/'; out = []
    for name, fn in NAT: out.append((name, [x for l in gutenberg(C + fn) for x in l], False))
    out.append(('Hebrew Gen+Exod', [x for l in hebrew(C + 'Gen.xml') + hebrew(C + 'Exod.xml') for x in l], False))
    from c004_generator_sweep import generate
    for s in (11812, 11813):
        g = generate({'text.lines_to_create': 4000}, s); out.append((f'TS gen {s}', [x for l in g for x in l], True))
    return out

def cal_job(a, seed=CSEED, ladder=LADDER, tag='cal'):
    ti, ci, T, name, words, eva = a
    f = f'{CK}{tag}_{T}_{ci}.json'
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([seed, ti, ci]); tmpl = TEMPL[T]
    base = recut(words, tmpl)
    mk = (lambda pg: Stream(pg)) if eva else (lambda pg: Stream(pg, tok=list))
    res = dict(T=T, control=name, words=sum(len(l) for p in base for l in p), unplanted=[], rungs={})
    for _ in range(NC):
        ps = pseudo(base, rng)
        t = mk(ps).test(rng, RC); res['unplanted'].append([t['p'], t['E']])
        for q, k in ladder:
            t = mk(plant(ps, rng, q, k)).test(rng, RC); res['rungs'].setdefault(f'{q}x{k}', []).append([t['p'], t['E']])
    json.dump(res, open(f, 'w')); return res

def calibrate():
    ctr = controls(); jobs = [(ti, ci, T, n, w, e) for ti, T in enumerate('AB') for ci, (n, w, e) in enumerate(ctr)]
    with Pool(8) as P: out = P.map(cal_job, jobs)
    cal = dict(seed=CSEED, RC=RC, NC=NC, alpha_g=AG, EB=EB, ladder=[f'{q}x{k}' for q, k in LADDER], per_control=out, choice={})
    for T in 'AB':
        rs = [o for o in out if o['T'] == T]
        fp = sum(p <= AG for o in rs for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs)
        tab = {}
        for q, k in LADDER:
            key = f'{q}x{k}'; ps = [x for o in rs for x in o['rungs'][key]]
            tab[key] = dict(dose=q * k, power=sum(p <= AG for p, _ in ps) / len(ps), E_mean=float(np.mean([e for _, e in ps])),
                            min_control_power=min(sum(p <= AG for p, _ in o['rungs'][key]) / NC for o in rs))
        ch = next((k for k in tab if tab[k]['power'] >= 0.90), None)
        ok = fp <= 3 and ch is not None
        comp = None if ch is None else tab[ch]['E_mean'] <= EB
        cal['choice'][T] = dict(fpr=f'{fp}/{n}', fpr_ok=fp <= 3, ladder=tab, chosen=ch, comparable=comp,
                                testable=bool(ok and (comp or T == 'A')))
        log('cal', T, cal['choice'][T]['fpr'], ch, comp, {k: (round(v['power'], 3), round(v['E_mean'], 4)) for k, v in tab.items()})
    json.dump(cal, open('analysis/C121_calibration.json', 'w'), indent=1); return cal

def cal2_job(a): return cal_job(a, CSEED2, LADDER2, 'cal2')

def calibrate2():
    st1 = json.load(open('analysis/C121_calibration.json'))
    st1 = st1.get('stage1', st1)
    ctr = controls(); jobs = [(ti, ci, T, n, w, e) for ti, T in enumerate('AB') for ci, (n, w, e) in enumerate(ctr)]
    with Pool(8) as P: out2 = P.map(cal2_job, jobs)
    cal = dict(stage1=st1, stage2=dict(seed=CSEED2, ladder=[f'{q}x{k}' for q, k in LADDER2], per_control=out2), choice={})
    for T in 'AB':
        rs1 = [o for o in st1['per_control'] if o['T'] == T]; rs2 = [o for o in out2 if o['T'] == T]
        fp = sum(p <= AG for o in rs1 + rs2 for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs1 + rs2)
        tab = dict(st1['choice'][T]['ladder'])
        for q, k in LADDER2:
            key = f'{q}x{k}'; ps = [x for o in rs2 for x in o['rungs'][key]]
            tab[key] = dict(dose=q * k, power=sum(p <= AG for p, _ in ps) / len(ps), E_mean=float(np.mean([e for _, e in ps])),
                            min_control_power=min(sum(p <= AG for p, _ in o['rungs'][key]) / NC for o in rs2))
        order = sorted(tab, key=lambda kk: (tab[kk]['dose'], int(kk.split('x')[1])))
        ch = next((kk for kk in order if tab[kk]['power'] >= 0.90), None)
        comp = None if ch is None else tab[ch]['E_mean'] <= EB
        cal['choice'][T] = dict(fpr=f'{fp}/{n}', fpr_ok=fp <= 6, ladder={kk: tab[kk] for kk in order}, chosen=ch, comparable=comp,
                                testable=bool(fp <= 6 and ch is not None and (comp or T == 'A')))
        log('cal2', T, cal['choice'][T]['fpr'], ch, comp, {kk: (round(tab[kk]['power'], 3), round(tab[kk]['E_mean'], 4)) for kk in order})
    json.dump(cal, open('analysis/C121_calibration.json', 'w'), indent=1); return cal

def invariance():
    rng = np.random.default_rng(ISEED); w = [x for l in gutenberg('data/corpora/pg218.txt') for x in l]
    s = Stream(recut(w, TEMPL['B']), tok=list); M = s.mi(s.x).sum()
    exact = True; nul = []
    for _ in range(200):
        y = s.perm(rng); nul.append(s.mi(y).sum())
        for k in range(len(s.pages)):
            m = np.repeat(s.pg, s.L) == k
            if not np.array_equal(np.bincount(y[m], minlength=s.K), np.bincount(s.x[m], minlength=s.K)): exact = False
    nul = np.array(nul); relab = rng.permutation(s.K); Mr = s.mi(relab[s.x]).sum()
    out = dict(seed=ISEED, control='Latin Caesar on ZL3b-B template', M=float(M), null_sd=float(nul.std(ddof=1)),
               share_null_equal_obs=float(np.mean(np.isclose(nul, M, rtol=0, atol=1e-12))), page_multiset_exact=exact,
               relabel_delta=float(abs(Mr - M)))
    out['pass'] = bool(exact and out['null_sd'] > 0 and out['share_null_equal_obs'] <= 0.01 and out['relabel_delta'] < 1e-9)
    json.dump(out, open('analysis/C121_invariance.json', 'w'), indent=1); log('G-INV', out); return out

def gate_job(a):
    i, L, t, pages, q, k = a
    f = f'{CK}gate_{L}_{t}.json'
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, i]); fp = pw = 0; Ep = []
    for _ in range(NG):
        ps = pseudo(pages, rng)
        fp += Stream(ps).test(rng, RG)['p'] <= AG
        tp = Stream(plant(ps, rng, q, k)).test(rng, RG); pw += tp['p'] <= AG; Ep.append(tp['E'])
    r = dict(key=f'{L}_{t}', plant=f'{q}x{k}', fpr=int(fp), power=int(pw), E_plant_mean=float(np.mean(Ep)),
             pass_=bool(fp <= 2 and pw >= 16))
    json.dump(r, open(f, 'w')); return r

def h1_job(a):
    i, L, t, pages = a
    f = f'{CK}h1_{L}_{t}.json'
    if os.path.exists(f): return json.load(open(f))
    r = Stream(pages).test(np.random.default_rng([SEED, i]), R); r['key'] = f'{L}_{t}'; r['effective_N'] = R
    json.dump(r, open(f, 'w')); return r

def run():
    cal = json.load(open('analysis/C121_calibration.json')); inv = json.load(open('analysis/C121_invariance.json'))
    S = {t: strata(f) for t, f in FILES}
    order = [(t, L) for t in ('ZL3b', 'IT2a') for L in ('A', 'B')]
    res = dict(cycle='C121', seeds=dict(cal=CSEED, gates=GSEED, H1=SEED, inv=ISEED), alpha_g=AG, R=R, RG=RG,
               tool_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), G_INV=inv['pass'],
               calibration={T: {k: cal['choice'][T][k] for k in ('fpr', 'chosen', 'comparable', 'testable')} for T in 'AB'})
    gj = []
    for i, (t, L) in enumerate(order):
        ch = cal['choice'][L]['chosen']
        if ch: q, k = ch.split('x'); gj.append((i, L, t, S[t][L], float(q), int(k)))
    with Pool(8) as P:
        G = P.map(gate_job, gj); H = P.map(h1_job, [(i, L, t, S[t][L]) for i, (t, L) in enumerate(order)])
    res['gates'] = {g['key']: g for g in G}; res['H1'] = {h['key']: h for h in H}
    for h in H: log('H1', h['key'], {k: h[k] for k in ('E', 'z', 'p', 'null_sd')})
    rej = holm({k: v['p'] for k, v in res['H1'].items()}); res['holm'] = rej; ver = {}
    for L in 'AB':
        ks = [f'{L}_ZL3b', f'{L}_IT2a']
        if not (inv['pass'] and cal['choice'][L]['testable'] and all(k in res['gates'] and res['gates'][k]['pass_'] for k in ks)):
            ver[L] = 'NOT TESTABLE'
        else:
            n = sum(rej[k] for k in ks); ver[L] = 'DETECTED' if n == 2 else 'PARTIAL' if n == 1 else 'EXCLUDED'
    res['verdict_H1'] = ver; res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open('analysis/C121_results.json', 'w'), indent=1, default=float); log('gates', res['gates']); log('verdict', ver)

S0 = {t: strata(f) for t, f in FILES}; TEMPL = {L: S0['ZL3b'][L] for L in 'AB'}
if __name__ == '__main__':
    os.makedirs(CK, exist_ok=True)
    {'inv': invariance, 'cal': calibrate, 'cal2': calibrate2, 'run': run}[sys.argv[1]]()
