#!/usr/bin/env python3
"""Blind recount of Kryptos case 221 (cycle 235, I-377) from PREREG235 + data/cycle235/R only.
Voynich audit, stdlib only (scipy, if installed, used ONLY as a cross-check of the MW p, recorded).
Usage: python3 recount235.py KCF_ROOT OUT_JSON
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
"""
import sys, os, re, json, math, hashlib, random, statistics as st

ROOT, OUT = sys.argv[1], sys.argv[2]
R = os.path.join(ROOT, 'data/cycle235/R')
SEEDS_A = list(range(209647, 209659)); SEEDS_B = list(range(209659, 209671))
SCOPES = ['direct', 'bank_r10', 'all_r10']
NQ = 64
BOOT_SEED = 11899; NBOOT = 10000
# crib (Sanborn): EASTNORTHEAST at 21-33, BERLINCLOCK at 63-73 (0-based) -> 24 seats
CRIB = {}
for i, c in enumerate('EASTNORTHEAST'): CRIB[21 + i] = c
for i, c in enumerate('BERLINCLOCK'): CRIB[63 + i] = c
SEATS8 = [21, 22, 23, 24, 63, 64, 65, 66]

S232 = json.load(open(os.path.join(ROOT, 'data/cycle232/summary232.json')))
BETA = S232['fit']['beta']; KTEXT = S232['bar']['k_text']
RCAL = [S232['bar']['Rcal'][k] for k in sorted(S232['bar']['Rcal'])]
def fit(nq, N, beta=BETA):
    L = math.log(N); return beta[0] + beta[1]*L + beta[2]*L*L + beta[3]*nq
def bar(nq, N): return fit(nq, N) + KTEXT
ROUND = [-6.8417, 0.0786, 0.00027, -0.0192]
def bar_round(nq, N): return fit(nq, N, ROUND) + 0.879

K4 = open(os.path.join(ROOT, 'data/k4.txt')).read().strip()
assert len(K4) == 97
def text_of(name):
    if name == 'K4': return K4
    s = list(K4); random.Random(int(name[4:])).shuffle(s); return ''.join(s)

checks = []
def chk(ok, msg):
    checks.append((bool(ok), msg))
    if not ok: print('CHECK FAIL', msg)

Hre = re.compile(r'^H perm=(-?\d+) dir=(\d+) ix=(\d+) X=(\d+) Y=(\d+) form=(\d+) w=(\d+) agree8=(\d+) agree24=(\d+) nc=(-?[\d.]+) pt=([A-Z]+)$')
tool_shas = set()
def read_file(name, scope):
    fn = os.path.join(R, ('k4' if name == 'K4' else name) + '_' + scope + '.txt')
    lines = open(fn).read().splitlines()
    hdr = [l for l in lines if l.startswith('#')]
    H = [l for l in lines if l.startswith('H ')]
    Y = [l for l in lines if l.startswith('Y ')]; T = [l for l in lines if l.startswith('T ')]
    other = [l for l in lines if l and l[0] not in '#HYT']
    chk(not other, f'{fn}: no unknown lines')
    chk(hdr[0] == f'# scope={scope}', f'{fn}: scope header')
    txt = text_of(name); sha = hashlib.sha256(txt.encode()).hexdigest()
    m = re.match(r'# text=(\S+) input_sha256=([0-9a-f]{64})', hdr[1])
    chk(m and m.group(1) == name and m.group(2) == sha, f'{fn}: text name + input sha recomputed from k4.txt/shuffle')
    m = re.match(r'# tool=tools/cycle235/gn235.c tool_sha256=([0-9a-f]{64})', hdr[2]); chk(m, f'{fn}: tool header')
    if m: tool_shas.add(m.group(1))
    if name == 'K4': chk(hdr[3].startswith('# seed=none args=gn235 K4'), f'{fn}: seed/args')
    else:
        s = int(name[4:]); setl = 'set A' if s in SEEDS_A else 'set B'
        chk(hdr[3].startswith(f'# seed={s} ') and setl in hdr[3] and f'args=gn235 {name} ' in hdr[3], f'{fn}: seed/set/args')
    a = hdr[3].split('args=')[1].split()
    exp_scope = {'direct': ('alpha.bin', '1'), 'bank_r10': ('bank.bin', '10'), 'all_r10': ('all.bin', '10')}[scope]
    chk(a[2] == exp_scope[0] and a[5] == exp_scope[1] and a[4] == 'keys233.bin' and a[7] == 'qg.bin', f'{fn}: args scope/stride/windows/table')
    ncs = []
    for l in H:
        mm = Hre.match(l); chk(mm, f'{fn}: H parse'); 
        if not mm: continue
        ag8, ag24, nc, pt = int(mm.group(8)), int(mm.group(9)), float(mm.group(10)), mm.group(11)
        chk(ag8 == 8, f'{fn}: agree8=8'); chk(len(pt) == 97, f'{fn}: pt len 97')
        chk(pt[21:25] == 'EAST' and pt[63:67] == 'BERL', f'{fn}: EAST@21-24 BERL@63-66 in pt')
        chk(sum(pt[i] == CRIB[i] for i in SEATS8) == 8, f'{fn}: 8/8 seats recount')
        chk(sum(pt[i] == c for i, c in CRIB.items()) == ag24, f'{fn}: agree24 recount from pt')
        ncs.append(nc)
    chk(len(Y) == 1 and len(T) == 1, f'{fn}: one Y one T')
    my = re.match(r'Y nq=(\d+) n=(\d+) max=(-?[\d.]+)', Y[0])
    chk(my and int(my.group(1)) == NQ and int(my.group(2)) == len(H), f'{fn}: Y nq=64, n == #H')
    if ncs: chk(abs(float(my.group(3)) - max(ncs)) < 1e-4, f'{fn}: Y max == max H nc')
    mt = re.search(r'hits8=(\d+) hits24ge23=(\d+)', T[0])
    chk(mt and int(mt.group(1)) == len(H), f'{fn}: T hits8 == #H')
    chk(mt and int(mt.group(2)) == 0, f'{fn}: hits24ge23 == 0')
    chk(re.search(r'windows=4172', T[0]), f'{fn}: windows=4172')
    return len(H), ncs

def unit(name):
    N = 0; allnc = []; per = {}
    for sc in SCOPES:
        n, ncs = read_file(name, sc); per[sc] = n; N += n; allnc += ncs
    mx = max(allnc) if allnc else None
    R_t = mx - fit(NQ, N) if allnc else None
    return dict(N=N, per_scope=per, max=mx, bar=bar(NQ, N) if N else None, R=R_t,
                passes=bool(N >= 10 and mx >= bar(NQ, N)), passes_rounded=bool(N >= 10 and mx >= bar_round(NQ, N)),
                margin=mx - bar(NQ, N) if N else None)

def wilson(k, n, z=1.959963984540054):
    p = k/n; d = 1 + z*z/n; c = (p + z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0.0, c-h), min(1.0, c+h)]

def mw_exact(x, y):
    # U for x; exact two-sided p via DP on rank sums (no ties assumed; ties checked)
    allv = sorted(x + y); assert len(set(allv)) == len(allv), 'ties'
    n, m = len(x), len(y)
    U = sum((xi > yj) + 0.5*(xi == yj) for xi in x for yj in y)
    # count of arrangements with U=u: f(n,m,u)
    from functools import lru_cache
    @lru_cache(None)
    def f(a, b, u):
        if u < 0: return 0
        if a == 0 or b == 0: return 1 if u == 0 else 0
        return f(a-1, b, u-b) + f(a, b-1, u)
    tot = math.comb(n+m, n); mean = n*m/2
    dev = abs(U - mean)
    p = sum(f(n, m, u) for u in range(n*m+1) if abs(u - mean) >= dev - 1e-9)/tot
    sd = math.sqrt(n*m*(n+m+1)/12); zz = (abs(U-mean) - 0.5)/sd
    pn = math.erfc(zz/math.sqrt(2))
    return U, p, pn

def hl(x, y): return st.median([a - b for a in x for b in y])

names = ['K4'] + [f'null{s}' for s in SEEDS_A + SEEDS_B]
units = {nm: unit(nm) for nm in names}
nulls = [units[f'null{s}'] for s in SEEDS_A + SEEDS_B]
pA = sum(units[f'null{s}']['passes'] for s in SEEDS_A); pB = sum(units[f'null{s}']['passes'] for s in SEEDS_B)
P = pA + pB
if P >= 4: h1 = 'FAILS (too permissive)'
else: h1 = 'HOLDS' if (pA <= 2 and pB <= 2) else 'FRONTEIRA'
h1_robust = (pA <= 2 and pB <= 2) == (P <= 3)
Rn = [u['R'] for u in nulls]
U, p_exact, p_norm = mw_exact(Rn, RCAL)
shift = hl(Rn, RCAL)
rng = random.Random(BOOT_SEED); bs = []
for _ in range(NBOOT):
    xs = [rng.choice(Rn) for _ in Rn]; ys = [rng.choice(RCAL) for _ in RCAL]; bs.append(hl(xs, ys))
bs.sort(); ci = [bs[int(0.025*NBOOT)], bs[int(0.975*NBOOT)-1]]
try:
    import scipy, scipy.stats as ss
    sp = dict(version=scipy.__version__, p_exact=float(ss.mannwhitneyu(Rn, RCAL, alternative='two-sided', method='exact').pvalue),
              p_asym=float(ss.mannwhitneyu(Rn, RCAL, alternative='two-sided', method='asymptotic').pvalue))
except Exception as e: sp = dict(error=repr(e))
k4 = units['K4']
rank_p = (1 + sum(r >= k4['R'] for r in Rn))/(len(Rn) + 1)
out = dict(
    rule='PREREG235 as read; fit/bar from summary232.json full-precision beta + k_text (rounded constants as sensitivity)',
    beta=BETA, k_text=KTEXT, Rcal=RCAL,
    units=units, H1=dict(passes=P, of=24, setA=pA, setB=pB, wilson95=wilson(P, 24), verdict=h1,
                         passes_rounded=sum(u['passes_rounded'] for u in nulls), max_margin=max(u['margin'] for u in nulls)),
    H2=dict(null_R_median=st.median(Rn), cal_R_median=st.median(RCAL), U=U, n_null=len(Rn), n_cal=len(RCAL),
            mw_p_exact=p_exact, mw_p_normal_cc=p_norm, HL_shift=shift, boot_ci95=ci, boot_seed=BOOT_SEED, nboot=NBOOT,
            scipy_crosscheck=sp,
            reading='p<0.05 with negative shift => bar conservative in this family by |shift| (power note)'),
    K4=dict(N=k4['N'], per_scope=k4['per_scope'], max=k4['max'], bar=k4['bar'], R=k4['R'], passes=k4['passes'], rank_p=rank_p),
    checks=dict(n=len(checks), failed=[m for ok, m in checks if not ok], tool_shas=sorted(tool_shas)),
    gateT='NOT TESTABLE externally: qg.bin / quadgrams.json not published; NC values taken as printed',
)
json.dump(out, open(OUT, 'w'), indent=1)
print(json.dumps({k: out[k] for k in ['H1', 'H2', 'K4']}, indent=1))
print('checks', len(checks), 'failed', len(out['checks']['failed']), 'tool_shas', sorted(tool_shas))
for nm in names:
    u = units[nm]; print(nm, u['per_scope'], u['N'], round(u['max'], 4), round(u['bar'], 4), round(u['R'], 4), u['passes'])
