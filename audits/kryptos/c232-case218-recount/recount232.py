#!/usr/bin/env python3
"""recount232.py -- Voynich's blind recount of Kryptos case 218 (PREREG232), written from RULE.md only.
usage: python3 recount232.py KRYPTOS_REPO OUTDIR"""
import sys, os, re, glob, hashlib, math, json, random
import numpy as np
REPO, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
D232 = REPO + '/data/cycle232'; D229 = REPO + '/data/cycle229'
CAL = list(range(209609, 209629)); HOL = list(range(209629, 209641)); SEED_BOOT = 11860; B = 1000; ALPHA = 0.05
PAT = re.compile(r'^Y model=(\w) p=(\d+) nq=(\d+) n=(\d+) pass=(\d+) max=(\S+)\s*$')
log = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); log.append(s)
def sha(fp): return hashlib.sha256(open(fp, 'rb').read()).hexdigest()
def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'), float('nan'))
    ph = k / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)
# ---------------- integrity
for base in (D232, D229):
    bad = seen = 0
    for l in open(base + '/SHA256SUMS'):
        h, p = l.split(); p = p[2:] if p.startswith('./') else p; seen += 1
        if sha(base + '/' + p) != h: bad += 1
    P(f'SHA256SUMS {base[len(REPO)+1:]}: {seen} files, {bad} bad')
P('SHA256SUMS(232) file sha', sha(D232 + '/SHA256SUMS'))
k4 = open(REPO + '/data/cycle231/k4.txt').read().strip()
nul = {int(a): b for a, b in (l.split('\t') for l in open(D232 + '/nulls232.tsv').read().split('\n')[1:] if l)}
mm = 0
for sd, ct in nul.items():
    L = list(k4); random.Random(sd).shuffle(L); mm += ''.join(L) != ct
P(f'nulls232 regenerated: {len(nul)} texts, mismatches {mm}')
hdrbad = 0; nfiles = {}
for f in glob.glob(D232 + '/R/null*.txt'):
    sd = int(re.match(r'null(\d+)_', os.path.basename(f)).group(1)); nfiles[sd] = nfiles.get(sd, 0) + 1
    h = [l for l in open(f) if l.startswith('# text=')][0]
    if hashlib.sha256(nul[sd].encode()).hexdigest() not in h: hdrbad += 1
P(f'R null files: {sum(nfiles.values())} over {len(nfiles)} texts (files/text {sorted(set(nfiles.values()))}); input_sha256 header mismatches {hdrbad}')
# ---------------- units
def units_of(files):
    u = {}
    for f in files:
        for l in open(f):
            if not l.startswith('Y '): continue
            g = PAT.match(l); assert g, l
            nq, n = int(g.group(3)), int(g.group(4))
            if nq < 10 or n <= 0: continue
            try: mx = float(g.group(6))
            except ValueError: continue
            if not math.isfinite(mx): continue
            a = u.setdefault(nq, [0, -1e9]); a[0] += n; a[1] = max(a[1], mx)
    return u
def text_units(d, label): return units_of(sorted(glob.glob(f'{d}/R/{label}_*.txt')))
U = {sd: text_units(D232, f'null{sd}') for sd in CAL + HOL}
K4 = text_units(D229, 'k4')
c229 = sorted({int(re.match(r'null(\d+)_', os.path.basename(f)).group(1)) for f in glob.glob(D229 + '/R/null*.txt')})
U229 = {sd: text_units(D229, f'null{sd}') for sd in c229}
def singles(texts, Ud):
    return [(sd, nq, n, mx) for sd in texts for nq, (n, mx) in sorted(Ud[sd].items()) if n >= 10]
def pooled(texts, Ud, g):
    out = []
    for i in range(0, len(texts) - g + 1, g):
        grp = texts[i:i + g]; nqs = set().union(*[Ud[s].keys() for s in grp])
        for nq in sorted(nqs):
            n = sum(Ud[s][nq][0] for s in grp if nq in Ud[s]); mx = max(Ud[s][nq][1] for s in grp if nq in Ud[s])
            if n >= 10: out.append((g, nq, n, mx))
    return out
def fitpoints(texts, Ud, gs):
    pts = [(1, nq, n, mx) for _, nq, n, mx in singles(texts, Ud)]
    for g in gs: pts += pooled(texts, Ud, g)
    return pts
def X_(nq, N):
    x = np.log(np.asarray(N, float)); return np.stack([np.ones_like(x), x, x * x, np.asarray(nq, float)], 1)
def ols(pts):
    a = np.array([(nq, n, mx) for _, nq, n, mx in pts], float)
    beta = np.linalg.lstsq(X_(a[:, 0], a[:, 1]), a[:, 2], rcond=None)[0]; return beta
def fit(beta, nq, N): return X_(np.atleast_1d(nq), np.atleast_1d(N)) @ beta
CG = [2, 5, 10, 20]
pts = fitpoints(CAL, U, CG); beta = ols(pts)
a_ = np.array([(g, nq, n, mx) for g, nq, n, mx in pts], float)
res_all = a_[:, 3] - fit(beta, a_[:, 1], a_[:, 2]); sst = ((a_[:, 3] - a_[:, 3].mean()) ** 2).sum()
P(f'FIT points {len(pts)} (singles {int((a_[:,0]==1).sum())}), N range {a_[:,2].min():.0f} .. {a_[:,2].max():.0f}, R2 {1 - (res_all**2).sum()/sst:.4f}')
P(f'FIT a {beta[0]:.4f}  b1 {beta[1]:.4f}  b2 {beta[2]:.5f}  c {beta[3]:.4f}')
for g in [1] + CG:
    m = a_[:, 0] == g; P(f'  mean residual pooling g={g}: {res_all[m].mean():+.4f} (n {m.sum()})')
NS = [10, 1e3, 1e5, 1e6]
def bN(beta): return [beta[1] + 2 * beta[2] * math.log(N) for N in NS]
rng = np.random.default_rng(SEED_BOOT); boots = []
for i in range(B):
    pick = rng.choice(len(CAL), len(CAL), replace=True)
    lab = [f'b{i}_{j}' for j in range(len(CAL))]; Ud = {lab[j]: U[CAL[k]] for j, k in enumerate(pick)}
    bb = ols(fitpoints(lab, Ud, CG)); boots.append(list(bb) + bN(bb))
boots = np.array(boots); ci = lambda j: (np.percentile(boots[:, j], 2.5), np.percentile(boots[:, j], 97.5))
for j, nm in enumerate(['a', 'b1', 'b2', 'c']): P(f'  boot95 {nm}: [{ci(j)[0]:.5f}, {ci(j)[1]:.5f}]')
lo, hi = ci(2); P(f'  curvature detected (b2 CI excludes 0): {not (lo <= 0 <= hi)}')
for j, N in enumerate(NS): P(f'  local slope b(N={N:g}) = {bN(beta)[j]:.4f}  boot95 [{ci(4+j)[0]:.4f}, {ci(4+j)[1]:.4f}]')
def Rt(sd, Ud): 
    s = singles([sd], Ud)
    if not s: return float('-inf'), None
    r = [(mx - fit(beta, nq, n)[0], nq, n, mx) for _, nq, n, mx in s]; return max(r)
RC = {sd: Rt(sd, U) for sd in CAL}; RH = {sd: Rt(sd, U) for sd in HOL}
k_text = max(v[0] for v in RC.values()); argk = max(RC, key=lambda s: RC[s][0])
sres = np.array([mx - fit(beta, nq, n)[0] for _, nq, n, mx in singles(CAL, U)]); k05 = float(np.percentile(sres, 95))
P(f'k_text {k_text:.4f} (text {argk}, unit nq {RC[argk][1]} N {RC[argk][2]} max {RC[argk][3]}); k05 {k05:.4f}; bar intercept a+k {beta[0]+k_text:.4f}')
P('  R_t calibration: ' + ' '.join(f'{s}:{v[0]:+.3f}' for s, v in RC.items()))
P('  R_t holdout    : ' + ' '.join(f'{s}:{v[0]:+.3f}' for s, v in RH.items()))
def bar(nq, N): return fit(beta, nq, N)[0] + k_text
# ---------------- gates
gates = {}
# P
K4maxN = max(n for n, _ in K4.values())
pl = [l.rstrip('\n').split('\t') for l in open(D232 + '/plants232.tsv')]; hdr = pl[0]; pl = [dict(zip(hdr, r)) for r in pl[1:]]
LP = re.compile(r'^([PH]) (\w) perm=(\d+) dir=(\d+) ix=\d+ X=(\d+) Y=(\d+) form=(\d+) p=(\d+)(.*)$')
okP = okP6 = okP56 = okLoose = 0; rows = []
for r in pl:
    pid = r['pid']; tru = (r['row'], r['dir'], r['X'], r['Y'], r['form']); p = int(r['p'])
    Pl, Hl, PlL = [], [], []
    for l in open(f'{D232}/R/plant_{pid}.txt'):
        g = LP.match(l.rstrip('\n'))
        if not g: continue
        cfg = g.group(3, 4, 5, 6, 7); pp = int(g.group(8))
        if g.group(1) == 'P' and pp == p:
            kv = dict(x.split('=', 1) for x in g.group(9).split() if '=' in x)
            if cfg == tru: Pl.append(kv)
            if cfg[:4] == tru[:4]: PlL.append(kv)
        if g.group(1) == 'H' and cfg == tru and p % pp == 0: Hl.append(pp)
    rec = bool(Pl) and bool(Hl)
    best = max(Pl, key=lambda kv: float(kv['nc'])) if Pl else None
    nq = int(best['nqnc']) if best else int(r['n_pred']); nc = float(best['nc']) if best else float('nan')
    Nref = K4[nq][0] if nq in K4 else K4maxN
    ok = rec and nc >= bar(nq, Nref); okP += ok
    okP6 += rec and nc >= bar(nq, 1e6); okP56 += rec and nc >= bar(nq, 5e6)
    bl = max(PlL, key=lambda kv: float(kv['nc'])) if PlL else None
    okLoose += bool(bl) and bool(Hl) and float(bl['nc']) >= bar(int(bl['nqnc']), K4[int(bl['nqnc'])][0] if int(bl['nqnc']) in K4 else K4maxN)
    rows.append(f'  plant {pid:>2} bad={r["bad"]:>3} rec={int(rec)} H_p={sorted(set(Hl))} nq={nq} nc={nc:.3f} Nref={Nref} bar={bar(nq,Nref):.3f} pass={int(ok)}')
for x in rows: P(x)
w = wilson(okP, 24); gates['P'] = okP >= 23
P(f'GATE P: {okP}/24 (Wilson95 {w[0]:.3f}-{w[1]:.3f}) -> {"PASS" if gates["P"] else "FAIL"}; at N 1e6 {okP6}/24, at 5e6 {okP56}/24; sensitivity form-not-required {okLoose}/24')
odd = [r for r in pl if int(r['pid']) % 2 == 1]
# H
kh = sum(v[0] >= k_text for v in RH.values()); w = wilson(kh, 12); gates['H'] = kh <= 1
P(f'GATE H: holdout per-text passes {kh}/12 (Wilson95 {w[0]:.3f}-{w[1]:.3f}) -> {"PASS" if gates["H"] else "FAIL"}')
# M
hp = fitpoints(HOL, U, [2, 4, 12]); h = np.array([(g, nq, n, mx) for g, nq, n, mx in hp], float)
hr = h[:, 3] - fit(beta, h[:, 1], h[:, 2]); dec = np.floor(np.log10(h[:, 2])).astype(int); okM = True
for d in sorted(set(dec)):
    m = dec == d; mr = hr[m].mean(); used = m.sum() >= 10; okM &= (abs(mr) <= 0.15) or not used
    P(f'  holdout decade 1e{d}: units {m.sum()} mean residual {mr:+.4f} {"(gated)" if used else "(<10 units, not gated)"}')
gates['M'] = bool(okM); P(f'GATE M: -> {"PASS" if okM else "FAIL"} (holdout units {len(hp)})')
gates['C'] = a_[:, 2].max() >= 1e6; P(f'GATE C: calibration max N {a_[:,2].max():.0f} -> {"PASS" if gates["C"] else "FAIL"}')
P('DECISION: ' + ('ADOPTED (from cycle 233, Y-line families)' if all(gates.values()) else 'NOT ADOPTED') + f'  gates {gates}')
# ---------------- K4
k4r = [(mx - fit(beta, nq, n)[0], nq, n, mx) for nq, (n, mx) in sorted(K4.items()) if n >= 10]
RK = max(k4r); nab = sum(r[0] >= k_text for r in k4r)
P(f'K4 units {len(k4r)} (N {min(r[2] for r in k4r)} .. {max(r[2] for r in k4r)}, total {sum(r[2] for r in k4r)}); R_K4 {RK[0]:+.4f} at nq {RK[1]} N {RK[2]} max {RK[3]}; units >= bar {nab}; K4 passes: {RK[0] >= k_text}')
labs = {}
for nm, RR in (('calibration', RC), ('holdout', RH), ('c229 nulls (descriptive)', {s: Rt(s, U229) for s in c229})):
    n = len(RR); ge = sum(v[0] >= RK[0] for v in RR.values()); p = (1 + ge) / (n + 1); labs[nm] = p
    P(f'  rank p {nm}: (1+{ge})/({n}+1) = {p:.4f}; distance p/alpha = {p/ALPHA:.2f}x')
rob = (labs['calibration'] / ALPHA >= 2) and labs['holdout'] > ALPHA and RK[0] < k_text
P('K4 LABEL: ' + ('NO-SIGNAL' if RK[0] < k_text else 'PASS') + (' (robust)' if rob else ' FRONTEIRA'))
# ---------------- retro c229
R229 = {s: Rt(s, U229) for s in c229}; k229 = sum(v[0] >= k_text for v in R229.values()); w = wilson(k229, len(c229))
P(f'RETRO c229 nulls: per-text passes of the new bar {k229}/{len(c229)} (Wilson95 {w[0]:.3f}-{w[1]:.3f})')
for s in c229:
    for nq, (n, mx) in sorted(U229[s].items()):
        if n >= 10 and mx >= -6.0: P(f'  c229 null {s} unit nq {nq} N {n} max {mx:.3f} >= -6.0; bar {bar(nq,n):.3f} -> {"PASS" if mx >= bar(nq,n) else "below new bar"}')
P(f'RETRO K4 c229 units with max >= -6.0 (nq>=10): ' + str([(nq, n, mx) for mx_, nq, n, mx in [(0,)+r[1:] for r in k4r] if mx >= -6.0]))
P(f'bar examples: bar(10,72)={bar(10,72):.3f} bar(10,1e6)={bar(10,1e6):.3f} bar(20,1e3)={bar(20,1e3):.3f} bar(45,1e5)={bar(45,1e5):.3f}')
open(OUT + '/summary232_voynich.txt', 'w').write('\n'.join(log) + '\n')
json.dump(dict(beta=list(beta), k_text=k_text, k05=k05, gates={k: bool(v) for k, v in gates.items()}, R_K4=RK[0], rank_p=labs,
               boot_ci={nm: ci(j) for j, nm in enumerate(['a', 'b1', 'b2', 'c', 'b10', 'b1e3', 'b1e5', 'b1e6'])}), open(OUT + '/summary232_voynich.json', 'w'), indent=1)
