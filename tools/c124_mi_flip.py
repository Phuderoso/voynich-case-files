#!/usr/bin/env python3
"""C124 (F-MID step 5): adjacency or drift? A neighbour-keeping block null (N-FLIP) for the C120-C123 statistic.
Instrument imported UNCHANGED: c120 Stream/recut/holm/LAGS, c121 plant/controls, c123 PStream/pages_of/blocks_of/paragraph rule,
 plant_in_para, struct. M = sum_d plug-in MI(d), d in (16..256), pairs inside a page (as C120-C123).
New here ONLY:
 N-FLIP: per page, full 4-line blocks (offset 0, head/tail fixed as C123) are grouped in consecutive PAIRS with a random phase
  phi in {0,1} drawn per page and replicate (phi=1 leaves block 0 alone); each pair is swapped with prob 1/2; an unpaired last
  block stays. Every block moves at most one slot (page-scale vocabulary drift is kept), block interiors are intact, and the line
  pairs that straddle a block boundary are broken unless both sides keep their order.
 Drift plant DR(lam) (specificity ruler): per page, every word TYPE gets u ~ U(0,1), every token v ~ U(0,1); tokens are laid back
  into the page's own word slots in order of key = lam*u + (1-lam)*v. Pure smooth vocabulary drift, no local order.
 Copy plant: C121 plant verbatim (ruler of power); declared variant plant_in_para (C123) printed beside it.
See case-file/C124-mi-flip.md for the frozen rule.
Run: python3 tools/c124_mi_flip.py run (resumable, analysis/c124_ckpt/); C124_DRY=1 ... dry (Caesar stand-in, tiny R);
     python3 tools/c124_mi_flip.py struct (STRUCTURE ONLY: boundary / pair shares preserved by N-FLIP, no statistic)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json, time, hashlib
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c120_mi_distance import recut, holm, LAGS, FILES
from c121_mi_calibrated import plant, controls
from c003_position_rigidity import units
import c123_mi_para_block as C3

CSEED, GSEED, SEED, ISEED, DSEED, LSEED, RESERVED = 11833, 11834, 11835, 11836, 11837, 11838, 11839
ALPHA, NT = 0.05, 2                   # family: CB x {ZL3b, IT2a} under N-FLIP
AG = ALPHA / NT                       # 0.025 for calibration / gates
R, RG, RC, RD, NG, NC = 2000, 200, 200, 1000, 20, 8
EBLK = 0.00223                        # public C123 CB N-BLOCK residual E, mean of ZL3b 0.00192 and IT2a 0.00254
LADDER = sorted([(0.25, 2), (0.5, 2), (0.5, 3), (1.0, 2), (1.0, 3), (0.75, 4), (0.75, 5), (1.0, 4), (1.0, 5), (1.0, 6),
                 (1.0, 8), (1.0, 10), (1.0, 99)], key=lambda r: (r[0] * r[1], r[1]))
LAMS = (0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0)
TRANS = ('ZL3b', 'IT2a')
PRIMARY = ('CB',)
SECONDARY = ('S', 'CBmS', 'BIO')
STRATA = PRIMARY + SECONDARY
DRY = os.environ.get('C124_DRY') == '1'
if DRY: STRATA = PRIMARY + ('S',); R, RG, RC, RD, NG, NC = 20, 10, 10, 10, 2, 1
CK = 'analysis/c124_ckpt/' if not DRY else '/tmp/c124_dry_ckpt/'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def flip_order(nb, rng):
    """slot order of nb full blocks under N-FLIP."""
    o = list(range(nb))
    if nb < 2: return o
    phi = int(rng.integers(2)); j = phi
    while j + 1 < nb:
        if rng.random() < 0.5: o[j], o[j + 1] = o[j + 1], o[j]
        j += 2
    return o

class FStream(C3.PStream):
    def norder(self, null, rng):
        if null != 'FLIP': return super().norder(null, rng)
        parts = []
        for head, blks, tail in self.segs[0]:
            parts.append(head)
            for j in flip_order(len(blks), rng): parts.append(blks[j])
            parts.append(tail)
        return np.concatenate(parts)

def pseudo_flip(pages, rng):
    out = []
    for lines in pages:
        h, bs, t = C3.blocks_of(len(lines), 0); blks = [lines[b:b + 4] for b in bs]; new = list(lines[:h])
        for j in flip_order(len(blks), rng): new += blks[j]
        out.append(new + list(lines[t:]))
    return out

def pseudo_of(null, pages, pids, rng):
    return pseudo_flip(pages, rng) if null == 'FLIP' else C3.pseudo_block(pages, pids, rng)

def plant_drift(pages, rng, lam):
    out = []
    for p in pages:
        w = [x for l in p for x in l]; ty = sorted(set(w)); u = dict(zip(ty, rng.random(len(ty)))); v = rng.random(len(w))
        key = np.array([lam * u[x] for x in w]) + (1 - lam) * v; o = np.argsort(key, kind='stable'); w2 = [w[i] for i in o]
        new, c = [], 0
        for l in p: new.append(w2[c:c + len(l)]); c += len(l)
        out.append(new)
    return out

def ck(name): return CK + name + '.json'
def load_ms():
    D = {}
    for t, f in FILES:
        for s in STRATA: D[(s, t)] = C3.pages_of(f, s)
    return D
def dry_data(D):
    w = C3.caesar_words(); out = {}
    for k, pp in D.items():
        pages, pids = C3.split_pp(pp); base = recut(w, pages); out[k] = [(p, i) for p, i in zip(base, pids[:len(base)])]
    return out

# ------------------------------------------------------------------ structure only
def boundary_share(pages, rng, n=2000):
    """STRUCTURE ONLY: mean share of original block-to-block boundaries (last line of block j -> first line of j+1) that stay
    adjacent and in order under N-FLIP and under N-BLOCK."""
    tot = sum(max(0, len(C3.blocks_of(len(p), 0)[1]) - 1) for p, _ in pages); kf = kb = 0
    for _ in range(n):
        for p, _ in pages:
            nb = len(C3.blocks_of(len(p), 0)[1])
            if nb < 2: continue
            for o, which in ((flip_order(nb, rng), 'f'), (list(rng.permutation(nb)), 'b')):
                kept = sum(1 for a, b in zip(o, o[1:]) if b == a + 1)
                if which == 'f': kf += kept
                else: kb += kept
    return dict(boundaries=int(tot), kept_FLIP=kf / (n * tot) if tot else None, kept_BLOCK=kb / (n * tot) if tot else None)

def struct():
    D = load_ms(); rng = np.random.default_rng(0); out = {}
    for (s, t), pp in D.items():
        out[f'{s}_{t}'] = dict(C3.struct_counts(pp), **boundary_share(pp, rng, 300))
    print(json.dumps(out, indent=1))

# ------------------------------------------------------------------ jobs
def cal_job(a):
    ti, ci, t, name, words, eva, tmpl = a
    f = ck(f'cal_CB_FLIP_{t}_{ci}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([CSEED, ti, ci]); pages, pids = tmpl
    base = recut(words, pages); ids = pids[:len(base)]; tok = units if eva else list
    res = dict(t=t, control=name, unplanted=[], rungs={})
    for _ in range(NC):
        ps = pseudo_flip(base, rng)
        r0 = FStream(ps, ids, tok).ntest('FLIP', rng, RC); res['unplanted'].append([r0['p'], r0['E']])
        for q, k in LADDER:
            r1 = FStream(plant(ps, rng, q, k), ids, tok).ntest('FLIP', rng, RC)
            res['rungs'].setdefault(f'{q}x{k}', []).append([r1['p'], r1['E']])
    json.dump(res, open(f, 'w')); return res

def choose(rs):
    fp = sum(p <= AG for o in rs for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs); tab = {}
    for q, k in LADDER:
        key = f'{q}x{k}'; ps = [x for o in rs for x in o['rungs'][key]]
        tab[key] = dict(dose=q * k, power=sum(p <= AG for p, _ in ps) / len(ps), E_mean=float(np.mean([e for _, e in ps])))
    ch = next((k for k in tab if tab[k]['power'] >= 0.90), None); ok = fp <= round(3 / 80 * n)
    return dict(fpr=f'{fp}/{n}', fpr_ok=bool(ok), ladder=tab, chosen=ch, valid=bool(ch is not None and ok))

def drift_cal_job(a):
    """drift ruler on the manuscript's own CB words: smallest lam that N-BLOCK detects in >= 18/20 (0.90)."""
    ti, t, pp = a
    f = ck(f'driftcal_CB_{t}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([LSEED, ti]); pages, pids = C3.split_pp(pp); tab = {}
    for lam in LAMS:
        ps = [FStream(plant_drift(pages, rng, lam), pids).ntest('BLOCK', rng, RG) for _ in range(NG)]
        tab[str(lam)] = dict(power_BLOCK=sum(r['p'] <= AG for r in ps), E_BLOCK_mean=float(np.mean([r['E'] for r in ps])))
        if tab[str(lam)]['power_BLOCK'] >= round(0.9 * NG): break
    ch = next((l for l in tab if tab[l]['power_BLOCK'] >= round(0.9 * NG)), None)
    r = dict(t=t, ladder=tab, chosen=ch); json.dump(r, open(f, 'w')); return r

def gate_job(a):
    gi, t, pp, rung, lam = a
    f = ck(f'gate_CB_FLIP_{t}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, gi]); pages, pids = C3.split_pp(pp); q, k = rung.split('x'); q, k = float(q), int(float(k))
    fp = pw = pv = sp = sp1 = 0; Ep, E0, Ed = [], [], []
    for _ in range(NG):
        ps = pseudo_flip(pages, rng)
        t0 = FStream(ps, pids).ntest('FLIP', rng, RG); fp += t0['p'] <= AG; E0.append(t0['E'])
        tp = FStream(plant(ps, rng, q, k), pids).ntest('FLIP', rng, RG); pw += tp['p'] <= AG; Ep.append(tp['E'])
        pv += FStream(C3.plant_in_para(ps, pids, rng, q, k), pids).ntest('FLIP', rng, RG)['p'] <= AG
    if lam is not None:
        for _ in range(NG):
            td = FStream(plant_drift(pages, rng, float(lam)), pids).ntest('FLIP', rng, RG); sp += td['p'] <= AG; Ed.append(td['E'])
            sp1 += FStream(plant_drift(pages, rng, 1.0), pids).ntest('FLIP', rng, RG)['p'] <= AG
    r = dict(key=f'CB_FLIP_{t}', rung=rung, fpr=int(fp), power=int(pw), power_inpara_plant_variant=int(pv), NG=NG,
             E_plant_mean=float(np.mean(Ep)), E_unplanted_mean=float(np.mean(E0)),
             g_fpr=bool(fp <= round(2 / 20 * NG)), g_pow=bool(pw >= round(16 / 20 * NG)),
             drift_lam=lam, spec_rejections=int(sp) if lam is not None else None, spec_rejections_lam1=int(sp1) if lam is not None else None,
             E_drift_FLIP_mean=float(np.mean(Ed)) if Ed else None, g_spec=bool(lam is not None and sp <= round(3 / 20 * NG)))
    json.dump(r, open(f, 'w')); return r

def h1_job(a):
    hi, s, null, t, pp, r = a
    f = ck(f'h_{s}_{null}_{t}')
    if os.path.exists(f): return json.load(open(f))
    pages, pids = C3.split_pp(pp); rng = np.random.default_rng([SEED if s in PRIMARY and null == 'FLIP' else DSEED, hi])
    o = FStream(pages, pids).ntest(null, rng, r); o['key'] = f'{s}_{null}_{t}'; json.dump(o, open(f, 'w')); return o

def invariance():
    f = ck('inv_FLIP')
    if os.path.exists(f): return json.load(open(f))
    D = load_ms(); pages_t, pids_t = C3.split_pp(D[('CB', 'ZL3b')]); base = recut(C3.caesar_words(), pages_t); ids = pids_t[:len(base)]
    rng = np.random.default_rng([ISEED, 0]); S = FStream(base, ids, tok=list); M = S.mi(S.x).sum(); upg = np.repeat(S.pg, S.L)
    nul, exact, intact, moved1 = [], True, True, True
    for it in range(200):
        y = S.nperm('FLIP', rng); nul.append(S.mi(y).sum())
        for k in range(len(S.pages)):
            m = upg == k
            if not np.array_equal(np.bincount(y[m], minlength=S.K), np.bincount(S.x[m], minlength=S.K)): exact = False
    for _ in range(50):
        o = S.norder('FLIP', rng); pos = np.empty(len(o), int); pos[o] = np.arange(len(o))
        for head, blks, tail in S.segs[0]:
            starts = sorted(pos[b[0]] for b in blks)
            for j, bl in enumerate(blks):
                p0 = pos[bl[0]]
                if not np.array_equal(o[p0:p0 + len(bl)], bl): intact = False
                if abs(starts.index(p0) - j) > 1: moved1 = False
    nul = np.array(nul); Mr = S.mi(rng.permutation(S.K)[S.x]).sum(); ge2 = float(np.mean([len(b) >= 2 for _, b, _ in S.segs[0]]))
    out = dict(M=float(M), null_sd=float(nul.std(ddof=1)), share_null_equal_obs=float(np.mean(np.isclose(nul, M, rtol=0, atol=1e-12))),
               multiset_exact=exact, blocks_intact=intact, moved_at_most_one_slot=moved1, relabel_delta=float(abs(Mr - M)), share_pages_ge2_blocks=ge2)
    out['pass'] = bool(exact and intact and moved1 and out['null_sd'] > 0 and out['share_null_equal_obs'] <= 0.01 and out['relabel_delta'] < 1e-9 and ge2 >= 0.5)
    json.dump(out, open(f, 'w')); return out

def label(res):
    ks = [f'CB_FLIP_{t}' for t in TRANS]
    if not res['G_INV']['pass']: return 'NAO TESTAVEL (G-INV)'
    if not all(res['calibration'][t]['valid'] for t in TRANS): return 'NAO TESTAVEL (calibracao)'
    G = res['gates']
    if not all(k in G and G[k]['g_fpr'] and G[k]['g_pow'] for k in ks): return 'NAO TESTAVEL (gate)'
    if not all(G[k]['g_spec'] for k in ks): return 'NAO TESTAVEL (especificidade: N-FLIP le deriva como adjacencia)'
    n = sum(res['holm'][k] for k in ks)
    if n == 2: return 'ADJACENCIA-NA-FRONTEIRA'
    if n == 1: return 'PARCIAL'
    ep = float(np.mean([G[k]['E_plant_mean'] for k in ks]))
    if ep <= 0.5 * EBLK: return 'DERIVA-COMPATIVEL'
    if ep <= EBLK: return 'DERIVA-COMPATIVEL (fraco)'
    return 'NAO TESTAVEL (grosso)'

def run():
    os.makedirs(CK, exist_ok=True); D = load_ms()
    if DRY: D = dry_data(D)
    res = dict(cycle='C124', dry=DRY, seeds=dict(cal=CSEED, gates=GSEED, H1=SEED, inv=ISEED, desc=DSEED, drift=LSEED, reserved=RESERVED),
               alpha=ALPHA, alpha_g=AG, R=R, RG=RG, RC=RC, RD=RD, NG=NG, NC=NC, EBLK=EBLK, ladder=[f'{q}x{k}' for q, k in LADDER],
               lams=LAMS, tool_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
    res['G_INV'] = invariance() if not DRY else dict(invariance(), note='dry'); log('G-INV', res['G_INV'])
    ctr = controls(); jobs = []
    for ti, t in enumerate(TRANS):
        tm = C3.split_pp(D[('CB', t)])
        for ci, (n, w, e) in enumerate(ctr): jobs.append((ti, ci, t, n, w, e, tm))
    if DRY: jobs = [j for j in jobs if j[1] == 0]
    dj = [(ti, t, D[('CB', t)]) for ti, t in enumerate(TRANS)]
    with Pool(8) as P:
        out = P.map(cal_job, jobs); DR = P.map(drift_cal_job, dj)
    res['calibration'] = {t: choose([o for o in out if o['t'] == t]) for t in TRANS}
    res['drift_calibration'] = {d['t']: d for d in DR}
    for t in TRANS: log('cal', t, res['calibration'][t]['fpr'], 'RUNG', res['calibration'][t]['chosen'], 'LAM', res['drift_calibration'][t]['chosen'])
    gj = [(ti, t, D[('CB', t)], res['calibration'][t]['chosen'] or ('1.0x4' if DRY else None), res['drift_calibration'][t]['chosen'])
          for ti, t in enumerate(TRANS)]
    gj = [g for g in gj if g[3]]
    hj, hi = [], 0
    for s in STRATA:
        for t in TRANS:
            hj.append((hi, s, 'FLIP', t, D[(s, t)], R if s in PRIMARY else RD)); hi += 1
            hj.append((hi, s, 'BLOCK', t, D[(s, t)], RD)); hi += 1
    with Pool(8) as P:
        G = P.map(gate_job, gj); H = P.map(h1_job, hj)
    res['gates'] = {g['key']: g for g in G}; res['tests'] = {h['key']: h for h in H}
    prim = {k: v['p'] for k, v in res['tests'].items() if k.startswith('CB_FLIP_')}
    res['holm'] = holm(prim)
    res['p_with_trio'] = {k: dict(p=v['p'], z=v['z'], E=v['E'], rung=res['gates'].get(k, {}).get('rung'),
                                  FPR=res['gates'].get(k, {}).get('fpr'), POW=res['gates'].get(k, {}).get('power'),
                                  E_plant=res['gates'].get(k, {}).get('E_plant_mean'), SPEC=res['gates'].get(k, {}).get('spec_rejections'))
                          for k, v in res['tests'].items() if '_FLIP_' in k}
    # share of the N-BLOCK residual that N-FLIP absorbs (raw, descriptive): (mean M*_FLIP - mean M*_BLOCK) / E_BLOCK
    res['share_FLIP_of_BLOCK_raw'] = {f'{s}_{t}': (res['tests'][f'{s}_FLIP_{t}']['null_mean'] - res['tests'][f'{s}_BLOCK_{t}']['null_mean'])
                                      / res['tests'][f'{s}_BLOCK_{t}']['E'] for s in STRATA for t in TRANS}
    res['boundary_share'] = {f'{s}_{t}': boundary_share(D[(s, t)], np.random.default_rng([DSEED, 99]), 200 if not DRY else 5)
                             for s in STRATA for t in TRANS}
    res['label_CB'] = label(res); res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open('analysis/C124_results.json' if not DRY else '/tmp/c124_dry_results.json', 'w'), indent=1, default=float)
    log('LABEL CB', res['label_CB'], res['p_with_trio'])

if __name__ == '__main__':
    {'run': run, 'dry': run, 'struct': struct}[sys.argv[1]]()
