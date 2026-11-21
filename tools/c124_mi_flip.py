#!/usr/bin/env python3
"""C124 (F-MID step 5): adjacency or drift? A neighbour-keeping block null (N-FLIP) and a BOUNDARY-PAIR statistic.
REVISION 2 (after Kryptos's blind review of draft 92ca537; see case-file/C124-mi-flip.md section 13).
Instrument imported UNCHANGED: c120 Stream/recut/holm/LAGS, c121 plant/controls, c123 PStream/pages_of/blocks_of/paragraph rule,
 plant_in_para, struct. Global M = sum_d plug-in MI(d), d in (16..256), pairs inside a page (as C120-C123): now DESCRIPTIVE under N-FLIP.
CONFIRMATORY statistic M_B (new): Sigma over lags d in (16,24,32,48,64) of the plug-in MI of the unit pairs (a, a+d) with a in the
 LAST line of a block slot s and a+d in the FIRST line of slot s+1 of the SAME page, for INTERNAL slot boundaries only
 (1 <= s <= nb-3; pages with nb >= 4 full blocks; the first and the last block-block boundary of a page are excluded because under
 N-FLIP they are kept adjacent-in-order with p 1/2, not 3/8; head/tail/edge boundaries are descriptive classes A_edge / A_tail).
 The pair set is defined on the ARRANGEMENT (slot geometry), so every null replicate is scored on its own slot boundaries; the number
 of pairs can differ slightly between the observed text and a replicate: n_pairs obs and null mean are printed beside every p.
N-FLIP: per page, full 4-line blocks (offset 0, head/tail fixed as C123) are grouped in consecutive PAIRS with a random phase
 phi in {0,1} drawn per page and replicate (phi=1 leaves block 0 alone); each pair is swapped with prob 1/2; an unpaired last
 block stays. Every block moves at most one slot (page-scale vocabulary drift is kept), block interiors are intact. Exact
 keep-adjacent-in-order probability of the boundary j|j+1: 3/8 for 1 <= j <= nb-3, 1/2 for the first and last boundary (nb >= 3), 3/4 if nb = 2.
Drift plant DR(lam) (specificity ruler): per page, every word TYPE gets u ~ U(0,1), every token v ~ U(0,1); tokens are laid back
 into the page's own word slots in order of key = lam*u + (1-lam)*v. Pure smooth vocabulary drift, no local order.
Copy plant: C121 plant verbatim (ruler of power); declared variant plant_in_para (C123) printed beside it.
Descriptive classes (observed only, pair-count matched by subsampling to n_A): A boundary pairs, I internal adjacent-line pairs
 (line r -> r+1 inside a block), C one block apart (last line of slot s -> first line of slot s+2; lags >= 128 only exist).
See case-file/C124-mi-flip.md for the frozen rule.
Run: python3 tools/c124_mi_flip.py run (resumable, analysis/c124_ckpt/); C124_DRY=1 ... dry (Caesar stand-in, tiny R);
     python3 tools/c124_mi_flip.py struct (STRUCTURE ONLY: boundary / pair counts and shares preserved by N-FLIP, no statistic)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json, time, hashlib
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c120_mi_distance import recut, holm, LAGS, FILES
from c121_mi_calibrated import plant, controls
from c003_position_rigidity import units
import c123_mi_para_block as C3

CSEED, GSEED, SEED, ISEED, DSEED, LSEED, XSEED, RESERVED = 11840, 11841, 11842, 11843, 11844, 11845, 11846, 11847
ALPHA, NT = 0.05, 2                   # family: CB x {ZL3b, IT2a} under N-FLIP
AG = ALPHA / NT                       # 0.025 for calibration / gates
R, RG, RC, RD, NG, NC = 2000, 200, 200, 1000, 20, 8
EBLK = {'ZL3b': 0.00192, 'IT2a': 0.00254}   # public C123 CB N-BLOCK residual E of the GLOBAL statistic, per transcription
SCALE = 0.66                          # E under N-FLIP / E under N-BLOCK expected if the residual were all adjacency (0.582/0.877)
BLAGS = tuple(d for d in LAGS if d <= 64)
LADDER = sorted([(0.25, 2), (0.5, 2), (0.5, 3), (1.0, 2), (1.0, 3), (0.75, 4), (0.75, 5), (1.0, 4), (1.0, 5), (1.0, 6),
                 (1.0, 8), (1.0, 10), (1.0, 99)], key=lambda r: (r[0] * r[1], r[1]))
LAMS = (0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0)               # detection ruler (as draft)
LAMS_FINE = (0.02, 0.035, 0.05, 0.075, 0.1, 0.15, 0.2, 0.275, 0.35, 0.5, 0.75, 1.0)   # for the E-matched lambda
TRANS = ('ZL3b', 'IT2a')
PRIMARY = ('CB',)
SECONDARY = ('S', 'CBmS', 'BIO')
STRATA = PRIMARY + SECONDARY
DRY = os.environ.get('C124_DRY') == '1'
if DRY: STRATA = PRIMARY + ('S',); R, RG, RC, RD, NG, NC = 20, 10, 10, 10, 2, 1
CK = 'analysis/c124_ckpt/' if not DRY else '/tmp/c124_dry_ckpt/'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def wilson(k, n, z=1.96):
    if not n: return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(float((c - h) / d), 3), round(float((c + h) / d), 3))

def flip_order(nb, rng):
    """slot order of nb full blocks under N-FLIP."""
    o = list(range(nb))
    if nb < 2: return o
    phi = int(rng.integers(2)); j = phi
    while j + 1 < nb:
        if rng.random() < 0.5: o[j], o[j + 1] = o[j + 1], o[j]
        j += 2
    return o

def cmask(name, ra, rb, sa, sb, la, lb, nba):
    """pair classes on an ARRANGEMENT: role r = line index inside its block (0..3, -1 head/tail line), s = block slot in the page,
    l = line sequence number, nb = number of full blocks of the page."""
    if name == 'A_int': return (ra == 3) & (rb == 0) & (sb == sa + 1) & (sa >= 1) & (sa <= nba - 3)     # CONFIRMATORY (p_keep 3/8)
    if name == 'A_edge': return (ra == 3) & (rb == 0) & (sb == sa + 1) & ((sa == 0) | (sa == nba - 2))  # first / last block-block boundary
    if name == 'A_tail': return (ra == 3) & (rb == -1) & (lb == la + 1)                               # last block | tail line
    if name == 'I_adj': return (ra >= 0) & (ra <= 2) & (rb == ra + 1) & (sb == sa)                    # inside a block (descriptive)
    if name == 'C_gap': return (ra == 3) & (rb == 0) & (sb == sa + 2)                                 # one block apart (descriptive)
    raise ValueError(name)

class FStream(C3.PStream):
    def __init__(self, pages, pids, tok=units):
        super().__init__(pages, pids, tok)
        wl, wr, wb, wn = [], [], [], []; gl = gb = 0
        for p in self.pages:
            nb = len(C3.blocks_of(len(p), 0)[1])
            for li, l in enumerate(p):
                full = li < 4 * nb
                for _ in l: wl.append(gl + li); wr.append(li % 4 if full else -1); wb.append(gb + li // 4 if full else -1); wn.append(nb)
            gl += len(p); gb += nb
        self.w_line, self.w_role, self.w_blk, self.w_nb = (np.array(v) for v in (wl, wr, wb, wn))
        self.pfirst = np.r_[0, np.nonzero(self.pg[1:] != self.pg[:-1])[0] + 1]
        self.pidx = np.repeat(np.arange(len(self.pfirst)), np.diff(np.r_[self.pfirst, self.nw]))
        self.u_nb = np.repeat(self.w_nb, self.L)
    def norder(self, null, rng):
        if null != 'FLIP': return super().norder(null, rng)
        parts = []
        for head, blks, tail in self.segs[0]:
            parts.append(head)
            for j in flip_order(len(blks), rng): parts.append(blks[j])
            parts.append(tail)
        return np.concatenate(parts)
    def geom(self, o):
        wl = self.w_line[o]; wr = self.w_role[o]; wb = self.w_blk[o]
        lid = np.cumsum(np.r_[True, wl[1:] != wl[:-1]]); isb = wb >= 0
        cb = np.cumsum(isb & np.r_[True, wb[1:] != wb[:-1]]); base = np.r_[0, cb][self.pfirst]
        slot = np.where(isb, cb - base[self.pidx] - 1, -1); Lo = self.L[o]
        return [np.repeat(a, Lo) for a in (wr, slot, lid)]
    def mi_pairs(self, xa, xb):
        if len(xa) == 0: return 0.0
        c = np.bincount(xa * self.K + xb, minlength=self.K * self.K).reshape(self.K, self.K).astype(float)
        n = c.sum(); px = c.sum(1) / n; py = c.sum(0) / n; nz = c > 0; pj = c[nz] / n
        return float((pj * np.log2(pj / np.outer(px, py)[nz])).sum())
    def class_pairs(self, name, x, geo, lags):
        R_, S_, L_ = geo; out = []
        for d in lags:
            a = self.masks[d]; m = cmask(name, R_[a], R_[a + d], S_[a], S_[a + d], L_[a], L_[a + d], self.u_nb[a])
            out.append((x[a][m], x[a + d][m]))
        return out
    def class_stats(self, x, geo, classes):
        out = {}
        for c in classes:
            ps = self.class_pairs(c, x, geo, BLAGS)
            out[c] = (np.array([self.mi_pairs(xa, xb) for xa, xb in ps]), np.array([len(xa) for xa, _ in ps]))
        return out
    def ntest2(self, null, rng, r, classes=('A_int',)):
        """G = global M statistic (as C120-C123), cls[c] = boundary-class statistics; same replicates for both."""
        o0 = np.arange(self.nw); m = self.mi(self.x)
        c0 = self.class_stats(self.x, self.geom(o0), classes) if classes else {}
        gn = []; cn = {c: [] for c in classes}; nn = {c: [] for c in classes}
        for _ in range(r):
            o = self.norder(null, rng); x = self._reindex(o); gn.append(self.mi(x))
            if classes:
                cs = self.class_stats(x, self.geom(o), classes)
                for c in classes: cn[c].append(cs[c][0]); nn[c].append(cs[c][1])
        gn = np.array(gn); Ms = gn.sum(1); M = m.sum()
        sh = [i for i, d in enumerate(LAGS) if d <= 64]; lo = [i for i, d in enumerate(LAGS) if d >= 96]
        def split(ix):
            a, b = m[ix].sum(), gn[:, ix].sum(1); s = b.std(ddof=1)
            return dict(E=float(a - b.mean()), z=float((a - b.mean()) / s) if s > 0 else None, p=float((1 + (b >= a).sum()) / (r + 1)))
        G = dict(M=float(M), null_mean=float(Ms.mean()), null_sd=float(Ms.std(ddof=1)), E=float(M - Ms.mean()),
                 z=float((M - Ms.mean()) / Ms.std(ddof=1)), p=float((1 + (Ms >= M).sum()) / (r + 1)), effective_N=int(r),
                 E_lag={str(d): float(m[i] - gn[:, i].mean()) for i, d in enumerate(LAGS)}, short_le64=split(sh), long_ge96=split(lo),
                 units=int(self.n), words=int(self.nw), pages=len(self.pages), paragraphs=int(len(set(self.gid))))
        C = {}
        for c in classes:
            mo, no = c0[c]; mn = np.array(cn[c]); sn = mn.sum(1); M_ = mo.sum(); sd = sn.std(ddof=1)
            C[c] = dict(M=float(M_), null_mean=float(sn.mean()), null_sd=float(sd), E=float(M_ - sn.mean()),
                        z=float((M_ - sn.mean()) / sd) if sd > 0 else None, p=float((1 + (sn >= M_).sum()) / (r + 1)),
                        E_lag={str(d): float(mo[i] - mn[:, i].mean()) for i, d in enumerate(BLAGS)},
                        n_pairs_obs=int(no.sum()), n_pairs_null_mean=float(np.mean(np.array(nn[c]).sum(1))))
        return dict(G=G, cls=C, B=C.get('A_int'))

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

# ------------------------------------------------------------------ descriptive contrast of pair classes (observed text only)
def contrast(S, rng, nsub=200):
    """A boundary pairs (internal, lags <= 64), I internal adjacent-line pairs (lags <= 64), C one block apart (lags >= 128, the only
    lags that reach 5 lines). Plug-in MI of the pooled pairs, subsampled to the common pair count so the plug-in bias is equal."""
    geo = S.geom(np.arange(S.nw)); P = {}
    for nm, cl, lags in (('A', 'A_int', BLAGS), ('I', 'I_adj', BLAGS), ('C', 'C_gap', tuple(d for d in LAGS if d >= 128))):
        ps = S.class_pairs(cl, S.x, geo, lags)
        P[nm] = (np.concatenate([a for a, _ in ps]), np.concatenate([b for _, b in ps]))
    n = min(len(v[0]) for v in P.values()); out = dict(n_pairs={k: int(len(v[0])) for k, v in P.items()}, n_common=int(n))
    out['M_full'] = {k: S.mi_pairs(*v) for k, v in P.items()}
    if n < 20: out['note'] = 'too few pairs'; return out
    for k, v in P.items():
        vals = [S.mi_pairs(v[0][ix], v[1][ix]) for ix in (rng.choice(len(v[0]), n, replace=False) for _ in range(nsub))]
        out[f'M_sub_{k}'] = dict(mean=float(np.mean(vals)), sd=float(np.std(vals, ddof=1)))
    return out

# ------------------------------------------------------------------ structure only
def boundary_share(pages, rng, n=2000):
    """STRUCTURE ONLY: mean share of original block-to-block boundaries that stay adjacent and in order under N-FLIP and N-BLOCK,
    by position class (first, internal 1<=j<=nb-3, last) and the number of internal boundaries."""
    tot = sum(max(0, len(C3.blocks_of(len(p), 0)[1]) - 1) for p, _ in pages); kf = kb = 0
    cls = {'first': [0, 0], 'internal': [0, 0], 'last': [0, 0]}; ninternal = 0; pages4 = 0
    for p, _ in pages:
        nb = len(C3.blocks_of(len(p), 0)[1]); pages4 += nb >= 4; ninternal += max(0, nb - 3)
    for _ in range(n):
        for p, _ in pages:
            nb = len(C3.blocks_of(len(p), 0)[1])
            if nb < 2: continue
            for o, which in ((flip_order(nb, rng), 'f'), (list(rng.permutation(nb)), 'b')):
                kept = [b == a + 1 for a, b in zip(o, o[1:])]
                if which == 'f':
                    kf += sum(kept)
                    for j, k in enumerate(kept):
                        c = 'first' if j == 0 else ('last' if j == nb - 2 else 'internal'); cls[c][0] += k; cls[c][1] += 1
                else: kb += sum(kept)
    return dict(boundaries=int(tot), internal_boundaries=int(ninternal), pages_ge4_blocks=int(pages4),
                kept_FLIP=kf / (n * tot) if tot else None, kept_BLOCK=kb / (n * tot) if tot else None,
                kept_FLIP_by_class={c: (v[0] / v[1] if v[1] else None) for c, v in cls.items()})

def pair_counts(pp, rng, n=50):
    """STRUCTURE ONLY: number of class-A_int unit pairs (counts of positions, no glyph value used) observed vs mean under N-FLIP / N-BLOCK."""
    pages, pids = C3.split_pp(pp); S = FStream(pages, pids); out = {}
    for null in (None, 'FLIP', 'BLOCK'):
        v = []
        for _ in range(1 if null is None else n):
            o = np.arange(S.nw) if null is None else S.norder(null, rng); x = S.x if null is None else S._reindex(o)
            geo = S.geom(o); v.append(sum(len(a) for a, _ in S.class_pairs('A_int', x, geo, BLAGS)))
        out[null or 'obs'] = float(np.mean(v))
    return out

def struct():
    D = load_ms(); rng = np.random.default_rng(0); out = {}
    for (s, t), pp in D.items():
        out[f'{s}_{t}'] = dict(C3.struct_counts(pp), **boundary_share(pp, rng, 300), n_pairs_A_int=pair_counts(pp, rng))
    print(json.dumps(out, indent=1))

# ------------------------------------------------------------------ jobs
SLICE = 2   # reps per calibration job (finer checkpoints for 'timeout 470' loops)
def cal_job(a):
    ti, ci, sl, t, name, words, eva, tmpl = a
    f = ck(f'cal_CB_FLIP_{t}_{ci}_{sl}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([CSEED, ti, ci, sl]); pages, pids = tmpl
    base = recut(words, pages); ids = pids[:len(base)]; tok = units if eva else list
    res = dict(t=t, control=name, unplanted=[], rungs={})
    for _ in range(min(SLICE, NC - sl * SLICE)):
        ps = pseudo_flip(base, rng)
        r0 = FStream(ps, ids, tok).ntest2('FLIP', rng, RC); res['unplanted'].append([r0['B']['p'], r0['B']['E']])
        for q, k in LADDER:
            r1 = FStream(plant(ps, rng, q, k), ids, tok).ntest2('FLIP', rng, RC)
            res['rungs'].setdefault(f'{q}x{k}', []).append([r1['B']['p'], r1['B']['E'], r1['G']['E']])
    json.dump(res, open(f, 'w')); return res

def choose(rs):
    fp = sum(p <= AG for o in rs for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs); tab = {}
    for q, k in LADDER:
        key = f'{q}x{k}'; ps = [x for o in rs for x in o['rungs'][key]]
        tab[key] = dict(dose=q * k, power=sum(x[0] <= AG for x in ps) / len(ps), E_B_mean=float(np.mean([x[1] for x in ps])),
                        E_global_FLIP_mean=float(np.mean([x[2] for x in ps])))
    ks = list(tab); ch = next((k for k in ks if tab[k]['power'] >= 0.90), None); ok = fp <= round(3 / 80 * n)
    interp = None   # descriptive only: linear interpolation of dose and global E at power 0.90 between the two bracketing rungs
    if ch is not None and ks.index(ch) > 0:
        a_, b_ = tab[ks[ks.index(ch) - 1]], tab[ch]; fr = (0.90 - a_['power']) / (b_['power'] - a_['power'])
        interp = dict(dose=a_['dose'] + fr * (b_['dose'] - a_['dose']),
                      E_global_FLIP=a_['E_global_FLIP_mean'] + fr * (b_['E_global_FLIP_mean'] - a_['E_global_FLIP_mean']))
    return dict(fpr=f'{fp}/{n}', fpr_ok=bool(ok), ladder=tab, chosen=ch, valid=bool(ch is not None and ok), interp_at_power_0_90=interp)

def drift_job(a):
    """drift ruler on the manuscript's own CB words: DR(lam) tested under N-BLOCK with the GLOBAL statistic (the C123 instrument)."""
    ti, t, li, lam, pp = a
    f = ck(f'driftcal_CB_{t}_{li}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([LSEED, ti, li]); pages, pids = C3.split_pp(pp)
    ps = [FStream(plant_drift(pages, rng, lam), pids).ntest2('BLOCK', rng, RG, classes=())['G'] for _ in range(NG)]
    r = dict(t=t, lam=lam, power_BLOCK=sum(x['p'] <= AG for x in ps), E_BLOCK_mean=float(np.mean([x['E'] for x in ps])))
    json.dump(r, open(f, 'w')); return r

def drift_pick(rows, t):
    """lam_det: smallest lam in LAMS that N-BLOCK detects in >= 18/20; lam_obs: lam in LAMS_FINE whose mean E under N-BLOCK is closest
    (log scale) to the public observed E_BLK of this transcription (the drift that would explain all of C123)."""
    rows = sorted(rows, key=lambda r: r['lam']); need = round(0.9 * NG)
    det = next((r['lam'] for r in rows if r['lam'] in LAMS and r['power_BLOCK'] >= need), None)
    pos = [r for r in rows if r['E_BLOCK_mean'] > 0]
    obs = min(pos, key=lambda r: abs(np.log(r['E_BLOCK_mean'] / EBLK[t])))['lam'] if pos else None
    reach = bool(rows and max(r['E_BLOCK_mean'] for r in rows) >= EBLK[t])
    return dict(t=t, table=rows, lam_det=det, lam_obs=obs, obs_reachable=reach, EBLK=EBLK[t])

GSL = 5     # gate replicates per job (checkpoint granularity)
def gate_main(a):
    gi, t, pp, rung, sl = a
    f = ck(f'gateM_CB_FLIP_{t}_{sl}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, gi, sl]); pages, pids = C3.split_pp(pp); q, k = rung.split('x'); q, k = float(q), int(float(k))
    r = dict(t=t, fp=0, pw=0, pv=0, n=0, Ep=[], E0=[], EpG=[], EpB=[], npairs=[])
    for _ in range(min(GSL, NG - sl * GSL)):
        ps = pseudo_flip(pages, rng)
        t0 = FStream(ps, pids).ntest2('FLIP', rng, RG)['B']; r['fp'] += int(t0['p'] <= AG); r['E0'].append(t0['E'])
        S = FStream(plant(ps, rng, q, k), pids); tp = S.ntest2('FLIP', rng, RG); r['pw'] += int(tp['B']['p'] <= AG)
        r['Ep'].append(tp['B']['E']); r['EpG'].append(tp['G']['E'])
        r['EpB'].append(S.ntest2('BLOCK', rng, RG, classes=())['G']['E'])      # same plant under N-BLOCK, global statistic (C123 units)
        r['pv'] += int(FStream(C3.plant_in_para(ps, pids, rng, q, k), pids).ntest2('FLIP', rng, RG)['B']['p'] <= AG); r['n'] += 1
    json.dump(r, open(f, 'w')); return r

def gate_spec(a):
    gi, t, pp, nm, lam, sl = a
    f = ck(f'gateS_CB_FLIP_{t}_{nm}_{sl}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, gi, 100 + 10 * sl + ('det', 'obs', 'lam1').index(nm)]); pages, pids = C3.split_pp(pp)
    rj, Ed = 0, []
    for _ in range(min(GSL, NG - sl * GSL)):
        td = FStream(plant_drift(pages, rng, float(lam)), pids).ntest2('FLIP', rng, RG)['B']; rj += int(td['p'] <= AG); Ed.append(td['E'])
    r = dict(t=t, nm=nm, lam=float(lam), rej=rj, n=len(Ed), Ed=Ed)
    json.dump(r, open(f, 'w')); return r

def gate_combine(t, rung, lam_det, lam_obs, M, S_):
    n = sum(m['n'] for m in M); cat = lambda k: [x for m in M for x in m[k]]
    fp, pw, pv = (sum(m[k] for m in M) for k in ('fp', 'pw', 'pv')); spec = {}
    for nm, lam in (('det', lam_det), ('obs', lam_obs), ('lam1', 1.0)):
        rows = [x for x in S_ if x['nm'] == nm]
        if lam is None or not rows: spec[nm] = None; continue
        rj = sum(x['rej'] for x in rows); nn = sum(x['n'] for x in rows)
        spec[nm] = dict(lam=float(lam), rejections=int(rj), NG=nn, wilson=wilson(int(rj), nn), E_B_mean=float(np.mean([e for x in rows for e in x['Ed']])))
    ok = lambda s: bool(s is not None and s['rejections'] <= round(3 / 20 * NG))
    eg, eb = float(np.mean(cat('EpG'))), float(np.mean(cat('EpB')))
    return dict(key=f'CB_FLIP_{t}', rung=rung, fpr=int(fp), power=int(pw), power_inpara_plant_variant=int(pv), NG=n,
                E_plant_B_mean=float(np.mean(cat('Ep'))), E_plant_FLIP_global=eg, E_plant_BLOCK_global=eb,
                ratio_FLIP_over_BLOCK=eg / eb if eb else None, E_unplanted_B_mean=float(np.mean(cat('E0'))),
                g_fpr=bool(fp <= round(2 / 20 * NG)), g_pow=bool(pw >= round(16 / 20 * NG)), spec=spec,
                g_spec=bool(ok(spec['det']) and ok(spec['obs'])), thr_E_BLK_scaled=SCALE * EBLK[t])

def h1_job(a):
    hi, s, null, t, pp, r = a
    f = ck(f'h_{s}_{null}_{t}')
    if os.path.exists(f): return json.load(open(f))
    pages, pids = C3.split_pp(pp); rng = np.random.default_rng([SEED if s in PRIMARY and null == 'FLIP' else DSEED, hi])
    S = FStream(pages, pids); cl = ('A_int', 'A_edge', 'A_tail') if s in PRIMARY else ('A_int',)
    o = S.ntest2(null, rng, r, cl); o['key'] = f'{s}_{null}_{t}'
    o['p'] = o['B']['p']; o['E'] = o['B']['E']; o['z'] = o['B']['z']
    if null == 'FLIP': o['contrast'] = contrast(S, np.random.default_rng([XSEED, hi]))
    json.dump(o, open(f, 'w'), default=float); return o

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
    # preservation per position class (block order only, Caesar geometry): kept-adjacent-in-order for boundaries, and block 0 first / last block last
    cnt = {'first_boundary': [0, 0], 'internal_boundary': [0, 0], 'last_boundary': [0, 0], 'block0_stays_first': [0, 0], 'last_stays_last': [0, 0]}
    for _ in range(2000):
        for _, blks, _ in S.segs[0]:
            nb = len(blks)
            if nb < 2: continue
            o = flip_order(nb, rng)
            for j, (a_, b_) in enumerate(zip(o, o[1:])):
                c = 'first_boundary' if j == 0 else ('last_boundary' if j == nb - 2 else 'internal_boundary')
                cnt[c][0] += b_ == a_ + 1; cnt[c][1] += 1
            cnt['block0_stays_first'][0] += o[0] == 0; cnt['block0_stays_first'][1] += 1
            cnt['last_stays_last'][0] += o[-1] == nb - 1; cnt['last_stays_last'][1] += 1
    pres = {c: (v[0] / v[1] if v[1] else None) for c, v in cnt.items()}
    # statistic geometry: the confirmatory pair set must sit on 3/8 boundaries only and exist on the stand-in
    npairs = int(sum(len(a) for a, _ in S.class_pairs('A_int', S.x, S.geom(np.arange(S.nw)), BLAGS)))
    out = dict(M=float(M), null_sd=float(nul.std(ddof=1)), share_null_equal_obs=float(np.mean(np.isclose(nul, M, rtol=0, atol=1e-12))),
               multiset_exact=exact, blocks_intact=intact, moved_at_most_one_slot=moved1, relabel_delta=float(abs(Mr - M)), share_pages_ge2_blocks=ge2,
               preservation_by_position_class=pres, n_pairs_A_int_stand_in=npairs)
    out['pass'] = bool(exact and intact and moved1 and out['null_sd'] > 0 and out['share_null_equal_obs'] <= 0.01 and out['relabel_delta'] < 1e-9
                       and ge2 >= 0.5 and abs(pres['internal_boundary'] - 0.375) < 0.02 and npairs > 0)
    json.dump(out, open(f, 'w')); return out

def label(res):
    ks = [f'CB_FLIP_{t}' for t in TRANS]; note = ' [ruler from controls (copy plant + drift plant on controls / pseudo replicates), not from CB]'
    if not res['G_INV']['pass']: return 'NAO TESTAVEL (G-INV)'
    if not all(res['calibration'][t]['valid'] for t in TRANS): return 'NAO TESTAVEL (calibracao)'
    G = res['gates']
    if not all(k in G and G[k]['g_fpr'] and G[k]['g_pow'] for k in ks): return 'NAO TESTAVEL (gate)'
    if not all(G[k]['g_spec'] for k in ks): return 'NAO TESTAVEL (especificidade: N-FLIP le deriva como adjacencia)'
    n = sum(res['holm'][k] for k in ks)
    if n == 2: return 'ADJACENCIA-NA-FRONTEIRA'
    if n == 1: return 'PARCIAL'
    ep = {t: G[f'CB_FLIP_{t}']['E_plant_FLIP_global'] for t in TRANS}; thr = {t: SCALE * EBLK[t] for t in TRANS}
    if all(ep[t] <= 0.5 * thr[t] for t in TRANS): return 'DERIVA-COMPATIVEL' + note
    if all(ep[t] <= thr[t] for t in TRANS): return 'DERIVA-COMPATIVEL (fraco)' + note
    return 'NAO TESTAVEL (grosso)' + note

def run():
    os.makedirs(CK, exist_ok=True); D = load_ms()
    if DRY: D = dry_data(D)
    res = dict(cycle='C124', revision=2, dry=DRY, seeds=dict(cal=CSEED, gates=GSEED, H1=SEED, inv=ISEED, desc=DSEED, drift=LSEED, contrast=XSEED, reserved=RESERVED),
               alpha=ALPHA, alpha_g=AG, R=R, RG=RG, RC=RC, RD=RD, NG=NG, NC=NC, EBLK=EBLK, SCALE=SCALE, ladder=[f'{q}x{k}' for q, k in LADDER],
               lams=LAMS, lams_fine=LAMS_FINE, tool_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
    res['G_INV'] = invariance() if not DRY else dict(invariance(), note='dry'); log('G-INV', res['G_INV'])
    ctr = controls(); jobs = []; nsl = -(-NC // SLICE)
    for ti, t in enumerate(TRANS):
        tm = C3.split_pp(D[('CB', t)])
        for ci, (n, w, e) in enumerate(ctr):
            for sl in range(nsl): jobs.append((ti, ci, sl, t, n, w, e, tm))
    if DRY: jobs = [j for j in jobs if j[1] == 0]
    dj = [(ti, t, li, lam, D[('CB', t)]) for ti, t in enumerate(TRANS) for li, lam in enumerate(LAMS_FINE)]
    with Pool(8) as P:
        out = P.map(cal_job, jobs, chunksize=1); DR = P.map(drift_job, dj, chunksize=1)
    merged = {}
    for o in out:
        m = merged.setdefault((o['t'], o['control']), dict(t=o['t'], control=o['control'], unplanted=[], rungs={}))
        m['unplanted'] += o['unplanted']
        for k_, v in o['rungs'].items(): m['rungs'].setdefault(k_, []).extend(v)
    res['calibration'] = {t: choose([m for (tt, _), m in merged.items() if tt == t]) for t in TRANS}
    res['drift_calibration'] = {t: drift_pick([d for d in DR if d['t'] == t], t) for t in TRANS}
    for t in TRANS: log('cal', t, res['calibration'][t]['fpr'], 'RUNG', res['calibration'][t]['chosen'], 'LAM det', res['drift_calibration'][t]['lam_det'], 'obs', res['drift_calibration'][t]['lam_obs'])
    gj = [(ti, t, D[('CB', t)], res['calibration'][t]['chosen'] or ('1.0x4' if DRY else None), res['drift_calibration'][t]['lam_det'], res['drift_calibration'][t]['lam_obs'])
          for ti, t in enumerate(TRANS)]
    gj = [g for g in gj if g[3]]; nsg = -(-NG // GSL)
    gm = [(g[0], g[1], g[2], g[3], sl) for g in gj for sl in range(nsg)]
    gs = [(g[0], g[1], g[2], nm, lam, sl) for g in gj for nm, lam in (('det', g[4]), ('obs', g[5]), ('lam1', 1.0)) if lam is not None for sl in range(nsg)]
    hj, hi = [], 0
    for s in STRATA:
        for t in TRANS:
            hj.append((hi, s, 'FLIP', t, D[(s, t)], R if s in PRIMARY else RD)); hi += 1
            hj.append((hi, s, 'BLOCK', t, D[(s, t)], RD)); hi += 1
    with Pool(8) as P:
        GM = P.map(gate_main, gm, chunksize=1); GS = P.map(gate_spec, gs, chunksize=1); H = P.map(h1_job, hj, chunksize=1)
    G = [gate_combine(g[1], g[3], g[4], g[5], [m for m in GM if m['t'] == g[1]], [x for x in GS if x['t'] == g[1]]) for g in gj]
    res['gates'] = {g['key']: g for g in G}; res['tests'] = {h['key']: h for h in H}
    prim = {k: v['p'] for k, v in res['tests'].items() if k.startswith('CB_FLIP_')}
    res['holm'] = holm(prim)
    res['p_with_trio'] = {k: dict(p=v['p'], z=v['z'], E=v['E'], n_pairs_obs=v['B']['n_pairs_obs'], n_pairs_null_mean=v['B']['n_pairs_null_mean'],
                                  rung=res['gates'].get(k, {}).get('rung'), FPR=res['gates'].get(k, {}).get('fpr'), POW=res['gates'].get(k, {}).get('power'),
                                  E_plant_B=res['gates'].get(k, {}).get('E_plant_B_mean'), E_plant_FLIP_global=res['gates'].get(k, {}).get('E_plant_FLIP_global'),
                                  E_plant_BLOCK_global=res['gates'].get(k, {}).get('E_plant_BLOCK_global'), SPEC=res['gates'].get(k, {}).get('spec'))
                          for k, v in res['tests'].items() if k.startswith('CB_FLIP_')}
    res['global_M_FLIP_descriptive'] = {k: dict(E=v['G']['E'], z=v['G']['z'], p=v['G']['p']) for k, v in res['tests'].items() if '_FLIP_' in k}
    # share of the N-BLOCK residual that N-FLIP absorbs, global statistic (raw, descriptive): (mean M*_FLIP - mean M*_BLOCK) / E_BLOCK
    res['share_FLIP_of_BLOCK_raw'] = {f'{s}_{t}': (res['tests'][f'{s}_FLIP_{t}']['G']['null_mean'] - res['tests'][f'{s}_BLOCK_{t}']['G']['null_mean'])
                                      / res['tests'][f'{s}_BLOCK_{t}']['G']['E'] for s in STRATA for t in TRANS}
    res['boundary_share'] = {f'{s}_{t}': boundary_share(D[(s, t)], np.random.default_rng([DSEED, 99]), 200 if not DRY else 5)
                             for s in STRATA for t in TRANS}
    res['label_CB'] = label(res); res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open('analysis/C124_results.json' if not DRY else '/tmp/c124_dry_results.json', 'w'), indent=1, default=float)
    log('LABEL CB', res['label_CB'], res['p_with_trio'])

if __name__ == '__main__':
    {'run': run, 'dry': run, 'struct': struct}[sys.argv[1]]()
