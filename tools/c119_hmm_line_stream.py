#!/usr/bin/env python3
"""C119 (F-HMM step 8): does word order inside lines give a boundary transition B more likelihood than N-LINE shuffles do?
Registered in case-file/C119-hmm-line-stream.md (sections 3-10) and its run amendments (section 'Run amendments'), before any run.
Instrument (frozen v4 fitter, imported from tools/c119_precheck_v4.py, helpers from c119_precheck_s.py / c119_precheck_v3.py):
  step 1  C117 word-reset 2-state HMM (C111/C117 EM, relative TOL 1e-6, cap NITER1 = 500), R1 restarts, on the OBSERVED text once;
          reused for every N-LINE replicate and every plant of that text (it depends only on the word multiset, C118 Amendment 1).
  step 2  A, pi, emissions frozen; B (2x2, last glyph of word k -> first glyph of word k+1, same line) fitted by L-BFGS-B in
          probability space, exact bounds [0, 1], exact gradient, two-criterion convergence (KKT projected gradient < 1e-8 OR
          |dl| < 1e-9 over the last 5 iterations) with at most 20 warm restarts; RB Dirichlet starts.
  S = (l(B fitted) - l(B rows = pi)) / n_within_line_word_boundaries.
Null N-LINE (C118): middle words of each line with L >= 5 permuted uniformly, first and last fixed, L <= 4 fixed (A2 asserted).
Texts: CAE_DV_W1, CAE_DV_W2, CAE_V, HEB_ABJ, GPOW (state-aligned plant q 0.10 on W1, SeedSequence([11802, 0]));
       ZL_A, ZL_B1, ZL_B2 (primary, Holm m = 3); IT_A, IT_B1, IT_B2 and HASH_W1 (descriptive, observed only).
       NNULL = 79 per registered text: 8 x 80 = 640 jobs.
Stages (run from the repo root):
  anchor   controls only, before calib: A0 (control part), W2 disjoint from W1, A1 identity at random parameters, A2 on 3 replicates.
  calib    controls only (seed 11803): R1 / CONV_TOL1 / RB / CONV_TOLB by the section 7 rule -> analysis/C119_frozen.json (never overwritten).
  run      resumable (analysis/C119_checkpoint.jsonl, soft stop 520 s): A0 manuscript part, step-1 restarts, then B jobs.
  gates    controls only: gate 1 (G-CONV, G-CANFAIL, G-FPR), P-NOISE, gate 3 (G-POW), secondary controls, BORDERLINE extension.
  verdict  only after gates are decided: primary strata, p / mid-p / p_cons / p_lib, Holm (BH printed), verdict label.
  desc     descriptive only, after the verdict: hash plant vs W1 nulls, twin plant observed S, descriptive T and tied T.
  status   counts only.
Seeds: 11802 run (per job SeedSequence([11802, hash_name(text), rep]); step-1 restart i: [11802, hash_name(text), 1000, i]);
       11803 calib/anchor; 11804 bootstrap; 11805 extension reps 80-159. Next free Voynich seed 11809 (11808 reserve).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, hashlib
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c119_precheck_s as V2
from c119_precheck_s import nline as nline_raw, fit_word, word_ll, word_mats, line_arrays, line_ll_and_counts, flat, pad, devowel_lines, NTOK
from c119_precheck_v3 import aligned_plant, hash_plant, hclass, init_post, grid_check as grid_logit
from c119_precheck_v4 import fit_one, Bp, GTOL, DLTOL
from c113_hmm_switch_slot_null import hash_name
from c115_hmm_switch_currier import strata, twin
import c003_position_rigidity as T
import c049_context_spelling as E
from c108_sukhotin_alternation import chars

SEED, SEED_CAL, SEED_BOOT, SEED_EXT, K = 11802, 11803, 11804, 11805, 2
NNULL, NNULL_EXT, ALPHA, SOFT_S, NPROC, Q_POW, Q_HASH, Q_TWIN = 79, 159, 0.05, 520, 8, 0.10, 0.10, 0.10
CAL_R1, CAL_R1_GRID, CAL_TOL1_GRID, CAL_RB, CAL_RB_GRID, CAL_TOLB_GRID, CAL_NREP, CONV_MIN = 30, (10, 15, 20, 30), (1.0, 2.0, 5.0), 10, (5, 10), (0.001, 0.01, 0.1), 3, 3
MAX_UNCONV, MIN_EFFN, MIN_DISTINCT, TIE, NBOOT, NITERB_EM, TOLB_EM = 0.10, 40, 0.20, 1e-9, 10000, 1000, 1e-7
assert V2.NITER1 == 500
FROZEN, CKPT, CAL_CKPT = 'analysis/C119_frozen.json', 'analysis/C119_checkpoint.jsonl', 'analysis/C119_calib_checkpoint.jsonl'
GATES_F, RESULTS_F, EXT_F, ANCHOR_F, DESC_F = 'analysis/C119_gates.json', 'analysis/C119_results.json', 'analysis/C119_extend.json', 'analysis/C119_anchor.json', 'analysis/C119_desc.json'
MAIN_CTRL, SEC_CTRL, GPOW, PRIMARY, DESC_OBS = ('CAE_DV_W1', 'CAE_DV_W2'), ('CAE_V', 'HEB_ABJ'), 'GPOW', ('ZL_A', 'ZL_B1', 'ZL_B2'), ('IT_A', 'IT_B1', 'IT_B2', 'HASH_W1')
CONTROLS = MAIN_CTRL + SEC_CTRL + (GPOW,)
REGISTERED = CONTROLS + PRIMARY                      # 8 texts x 80 = 640 jobs
STEP1_OF = {'GPOW': 'CAE_DV_W1', 'HASH_W1': 'CAE_DV_W1'}  # plants reuse W1's step 1 (same word multiset, section 3)
STEP1_TEXTS = ('CAE_DV_W1', 'CAE_DV_W2', 'CAE_V', 'HEB_ABJ') + PRIMARY + ('IT_A', 'IT_B1', 'IT_B2')
W1_SHA = ('29df436a', '2a2eeb')
ZL_SHA16, IT_SHA16, ZL_COUNTS = 'bf5b6d4ac1e3a51b', '7f27a8b0feed8f6d', dict(A=10005, B1=10007, B2=10004)

# ---------------------------------------------------------------- texts
def text_sha(lines): return hashlib.sha256('\n'.join(' '.join(''.join(w) for w in l) for l in lines).encode()).hexdigest()

def file_sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

_NAT = None
def _nat():
    global _NAT
    if _NAT is None:
        from c051_context_spelling_ab import nat_texts
        _NAT = nat_texts()
    return _NAT

def _caesar_dv(): return [l for l in T.devowel(_nat()['Latin_Caesar']) if len(l) >= 3]

_BASE = {}
def base_lines(name, manuscript_ok=False):
    """observed lines of a base text (tuples of glyph units). Manuscript texts load only when manuscript_ok (run stage, after freeze)."""
    if name in _BASE: return _BASE[name]
    if name == 'CAE_DV_W1': L = devowel_lines('Latin_Caesar', NTOK)
    elif name == 'CAE_DV_W2': L = [chars(l) for l in E.take(_caesar_dv(), NTOK, NTOK)]
    elif name == 'CAE_V': L = [chars(l) for l in E.take(_nat()['Latin_Caesar'], 0, NTOK)]
    elif name == 'HEB_ABJ': L = [chars(l) for l in E.take(_nat()['Hebrew_Genesis'], 0, NTOK)]
    elif name[:3] in ('ZL_', 'IT_'):
        assert manuscript_ok, 'manuscript text requested outside the run stage'
        path = 'data/ZL3b-n.txt' if name.startswith('ZL_') else 'data/IT2a-n.txt'
        toks, _, L3 = strata(path, with_lines=True)
        for k in L3:
            _BASE[name[:3] + k] = [list(l) for l in L3[k]]
            assert flat(_BASE[name[:3] + k]) == toks[k]          # A0: same stream as C115/C117 strata()
        return _BASE[name]
    else: raise KeyError(name)
    _BASE[name] = [list(l) for l in L]; return _BASE[name]

def symbols(lines): w = flat(lines); syms = sorted({u for x in w for u in x}); return syms, {u: i for i, u in enumerate(syms)}

def XM(lines, sid):
    obs = flat(lines); ids = np.array([sid[u] for w in obs for u in w]); wid = np.array([k for k, w in enumerate(obs) for _ in w])
    return pad(ids, wid)

def nline(lines, rng):
    sh = nline_raw(lines, rng)
    for a, b in zip(sh, lines):                                    # A2
        assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1] and (len(b) >= 5 or list(a) == list(b))
    return sh

def planted_lines(name, P, seed=SEED):
    """GPOW / HASH_W1 from W1 under the given W1 step-1 parameters P (dict pi, A, Em, sid)"""
    W1 = base_lines('CAE_DV_W1')
    if name == 'GPOW':
        pl, n = aligned_plant(W1, Q_POW, np.random.default_rng(np.random.SeedSequence([seed, 0])), P['sid'], P['pi'], P['A'], P['Em'])
    elif name == 'HASH_W1':
        pl, n = hash_plant(W1, Q_HASH, np.random.default_rng(np.random.SeedSequence([seed, 1])))
    else: raise KeyError(name)
    for a, b in zip(pl, W1): assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1]
    return [list(l) for l in pl], n

def nb_of(lines): return sum(len(l) - 1 for l in lines)

def line_desc(lines):
    mov = [l for l in lines if len(l) >= 5]; nw = len(flat(lines))
    return dict(word_tokens=nw, lines=len(lines), glyph_tokens=sum(len(w) for w in flat(lines)), boundaries=nb_of(lines),
                boundaries_movable_lines=nb_of(mov), boundaries_per_line=nb_of(lines) / len(lines), mean_line_length=nw / len(lines),
                movable_lines=len(mov), movable_line_share=len(mov) / len(lines), movable_token_share=sum(len(l) - 2 for l in mov) / nw)

# ---------------------------------------------------------------- fitting helpers
def params_of(rec):
    return dict(pi=np.array(rec['pi']), A=np.array(rec['A']), Em=np.array(rec['Em']))

def step1_restart(lines, sid, ss):
    X, M = XM(lines, sid); f = fit_word(X, M, len(sid), np.random.default_rng(ss))
    return dict(ll=f['ll'], iters=f['iters'], hit_cap=f['hit_cap'], pi=f['pi'].tolist(), A=f['A'].tolist(), Em=f['Em'].tolist())

def B_fits(arr, pi, B0s):
    return [fit_one(np.array([b[0, 1], b[1, 0]]), arr, pi) for b in B0s]

def em_crosscheck(arr, pi, B0s):
    """v2 B-EM from the same starts (cap 1000, stop when the gain < 1e-7 nats); printed only"""
    out = []
    for B in B0s:
        B = B.copy(); last = -np.inf
        for it in range(NITERB_EM):
            ll, xi = line_ll_and_counts(*arr, pi, B)
            if ll - last < TOLB_EM: break
            last = ll; B = xi / xi.sum(1, keepdims=True)
        out.append(dict(ll=ll, iters=it + 1, hit_cap=bool(it + 1 == NITERB_EM)))
    return out

def grid_lin(arr, pi):
    xs = np.linspace(0, 1, 41); return max(line_ll_and_counts(*arr, pi, Bp((a, b)))[0] for a in xs for b in xs)

def entropy_table(lines, sid, pi, Em):
    H = lambda p: float(-(p * np.log2(np.clip(p, 1e-300, 1))).sum()); obs = flat(lines)
    gl = sorted({w[0] for w in obs})
    return dict(token_mean_all_words=float(np.mean([H(init_post(w[0], sid, pi, Em)) for w in obs])),
                token_mean_words_after_boundary=float(np.mean([H(init_post(w[0], sid, pi, Em)) for l in lines for w in l[1:]])),
                type_mean_first_glyphs=float(np.mean([H(init_post(g, sid, pi, Em)) for g in gl])),
                per_first_glyph={''.join(g): [round(float(x), 6) for x in init_post(g, sid, pi, Em)] for g in gl})

def class_balance(lines):
    obs = flat(lines); types = sorted(set(map(tuple, obs)))
    ct = [sum(hclass(w) == c for w in types) for c in (0, 1)]; ck = [sum(hclass(w) == c for w in obs) for c in (0, 1)]
    return dict(types=dict(class0=ct[0], class1=ct[1], share1=ct[1] / len(types)), tokens=dict(class0=ck[0], class1=ck[1], share1=ck[1] / len(obs)))

def s_conv(rec, tolb):
    lls = [s['ll'] for s in rec['starts']]; b = max(lls)
    return sum(s['converged'] and s['ll'] >= b - tolb for s in rec['starts']) >= CONV_MIN

def step1_conv(lls, tol1): b = max(lls); return sum(l >= b - tol1 for l in lls) >= CONV_MIN

def pool_run(fn, jobs, path, t0, tag):
    from multiprocessing import Pool
    n = 0; P = Pool(NPROC)
    with open(path, 'a') as f:
        try:
            for rec in P.imap_unordered(fn, jobs):
                f.write(json.dumps(rec, default=float) + '\n'); f.flush(); n += 1
                if time.time() - t0 > SOFT_S: print(tag, 'soft stop', flush=True); break
        finally: P.terminate(); P.join()
    return n

def load(path):
    D = []
    if os.path.exists(path):
        for line in open(path):
            if line.strip(): D.append(json.loads(line))
    return D

# ---------------------------------------------------------------- anchor (controls only)
def anchor():
    t0 = time.time(); R = dict(stage='anchor', controls_only=True, manuscript_loaded=False, tool_sha256=file_sha(os.path.abspath(__file__)))
    W1 = base_lines('CAE_DV_W1'); W2 = base_lines('CAE_DV_W2'); sh = text_sha(W1)
    R['A0_W1'] = dict(text_sha256=sh, registered=f'{W1_SHA[0]}…{W1_SHA[1]}', PASS=bool(sh.startswith(W1_SHA[0]) and sh.endswith(W1_SHA[1])),
                      **line_desc(W1))
    assert R['A0_W1']['PASS'] and R['A0_W1']['word_tokens'] == 10008 and R['A0_W1']['lines'] == 1040
    assert R['A0_W1']['glyph_tokens'] == 32824 and R['A0_W1']['boundaries'] == 8968
    dv = [chars(l) for l in _caesar_dv()]; n1 = len(W1)
    assert [list(l) for l in dv[:n1]] == W1                       # W1 = the first n1 lines of the source
    off = next(i for i in range(len(dv)) if [list(l) for l in dv[i:i + len(W2)]] == W2)
    R['W2_disjoint'] = dict(W2_first_line_index=off, W1_last_line_index=n1 - 1, PASS=bool(off >= n1),
                            W2_lines_textually_equal_to_a_W1_line=sum(tuple(map(tuple, l)) in {tuple(map(tuple, x)) for x in W1} for l in W2))
    assert R['W2_disjoint']['PASS']
    rng = np.random.default_rng(np.random.SeedSequence([SEED_CAL, 0])); R['texts'] = {}
    for name in MAIN_CTRL + SEC_CTRL:
        L = base_lines(name); syms, sid = symbols(L); X, M = XM(L, sid)
        pi = rng.dirichlet([1, 1]); A = rng.dirichlet([1, 1], 2); Em = rng.dirichlet(np.ones(len(syms)), 2)   # A1 is an identity: any parameters
        cache = word_mats({tuple(w) for w in flat(L)}, sid, A, Em)
        ll0 = line_ll_and_counts(*line_arrays([[tuple(w) for w in l] for l in L], cache), pi, np.tile(pi, (2, 1)))[0]; llw = word_ll(X, M, pi, A, Em)
        for _ in range(3): nline(L, rng)                            # A2 asserted inside nline
        R['texts'][name] = dict(text_sha256=text_sha(L), symbols=len(syms), A1_random_params=dict(ll_line_reset=ll0, ll_word_rows=llw,
                                abs_diff=abs(ll0 - llw), PASS=bool(abs(ll0 - llw) < 1e-6)), A2_3_replicates='PASS', **line_desc(L))
        assert R['texts'][name]['A1_random_params']['PASS']
        print(name, json.dumps({k: v for k, v in R['texts'][name].items()}), flush=True)
    R['seconds'] = round(time.time() - t0, 1); json.dump(R, open(ANCHOR_F, 'w'), indent=1, default=float)
    print('anchor PASS', R['seconds'], 's', flush=True)

# ---------------------------------------------------------------- calib (controls only, seed 11803)
def _tuplify(L): return [[tuple(w) for w in l] for l in L]

def _cal_text(name, rep, P_w1=None):
    if name == 'GPOW': L, _ = planted_lines('GPOW', P_w1)
    else: L = base_lines(name)
    if rep > 0: L = nline(L, np.random.default_rng(np.random.SeedSequence([SEED_CAL, hash_name(name), rep])))
    return L

def _cal_s1(job):
    name, rep, i, P_w1 = job; L = _cal_text(name, rep, P_w1); syms, sid = symbols(base_lines('CAE_DV_W1') if name == 'GPOW' else L)
    r = step1_restart(L, sid, np.random.SeedSequence([SEED_CAL, hash_name(name), rep, 1, i]))
    return dict(kind='c1', name=name, rep=rep, i=i, ll=r['ll'], iters=r['iters'], hit_cap=r['hit_cap'],
                **({'pi': r['pi'], 'A': r['A'], 'Em': r['Em']} if rep == 0 else {}))

def _cal_s2(job):
    name, rep, P, P_w1 = job; L = _cal_text(name, rep, P_w1); base = 'CAE_DV_W1' if name == 'GPOW' else name
    syms, sid = symbols(base_lines(base)); pi, A, Em = P['pi'], P['A'], P['Em']
    arr = line_arrays(_tuplify(L), word_mats({tuple(w) for w in flat(L)}, sid, A, Em)); ll0 = line_ll_and_counts(*arr, pi, np.tile(pi, (2, 1)))[0]
    rng = np.random.default_rng(np.random.SeedSequence([SEED_CAL, hash_name(name), rep, 2])); B0s = [rng.dirichlet([1, 1], 2) for _ in range(CAL_RB)]
    F = B_fits(arr, pi, B0s); rec = dict(kind='c2', name=name, rep=rep, ll_reset=ll0, nb=nb_of(L),
        starts=[dict(ll=f['ll'], converged=f['converged'], conv_kkt=f['conv_kkt'], conv_dl=f['conv_dl'], kkt=f['kkt_proj_grad'],
                     nit=f['nit'], warm=f['warm_restarts'], x=f['x']) for f in F])
    if rep == 0:
        b = max(f['ll'] for f in F); g = grid_logit(arr, pi, b); G = grid_lin(arr, pi)
        rec['grid_logit'] = g; rec['grid_lin'] = dict(grid_max_ll=G, fit_minus_grid=b - G)
    return rec

def _w1_cal_params(D):
    rs = [r for r in D if r['kind'] == 'c1' and r['name'] == 'CAE_DV_W1' and r['rep'] == 0]
    if len(rs) < CAL_R1: return None
    b = max(rs, key=lambda r: r['ll']); P = params_of(b); P['sid'] = symbols(base_lines('CAE_DV_W1'))[1]; return P

def calib():
    assert not os.path.exists(FROZEN), 'analysis/C119_frozen.json exists: calib never overwrites it'
    t0 = time.time(); base4 = MAIN_CTRL + SEC_CTRL; D = load(CAL_CKPT)
    done1 = {(r['name'], r['rep'], r['i']) for r in D if r['kind'] == 'c1'}; done2 = {(r['name'], r['rep']) for r in D if r['kind'] == 'c2'}
    J1 = [(n, rep, i, None) for i in range(CAL_R1) for n in base4 for rep in range(CAL_NREP + 1) if (n, rep, i) not in done1]
    print('calib phase A (step-1 of the 4 base controls): todo', len(J1), flush=True)
    if J1: pool_run(_cal_s1, J1, CAL_CKPT, t0, 'calib-A')
    D = load(CAL_CKPT); Pw1 = _w1_cal_params(D); done1 = {(r['name'], r['rep'], r['i']) for r in D if r['kind'] == 'c1'}
    if any((n, rep, i) not in done1 for i in range(CAL_R1) for n in base4 for rep in range(CAL_NREP + 1)) or time.time() - t0 > SOFT_S:
        print('calib: resume needed (phase A incomplete)'); return
    best = {}
    for n in base4:
        rs = [r for r in D if r['kind'] == 'c1' and r['name'] == n and r['rep'] == 0]
        if len(rs) == CAL_R1: best[n] = params_of(max(rs, key=lambda r: r['ll']))
    best['GPOW'] = Pw1
    J2 = [('GPOW', rep, i, Pw1) for i in range(CAL_R1) for rep in range(CAL_NREP + 1) if ('GPOW', rep, i) not in done1]
    J3 = [(n, rep, best[n], Pw1) for n in base4 + ('GPOW',) for rep in range(CAL_NREP + 1) if (n, rep) not in done2]
    print('calib phase B: GPOW step-1 todo', len(J2), '; step-2 todo', len(J3), flush=True)
    if J3: pool_run(_cal_s2, J3, CAL_CKPT, t0, 'calib-B2')
    if J2 and time.time() - t0 <= SOFT_S: pool_run(_cal_s1, J2, CAL_CKPT, t0, 'calib-B1')
    D = load(CAL_CKPT)
    c1 = {}; c2 = {}
    for r in D:
        if r['kind'] == 'c1': c1.setdefault((r['name'], r['rep']), {})[r['i']] = r
        else: c2[(r['name'], r['rep'])] = r
    keys = [(n, rep) for n in CONTROLS for rep in range(CAL_NREP + 1)]
    if any(len(c1.get(k, {})) < CAL_R1 for k in keys) or any(k not in c2 for k in keys): print('calib: resume needed'); return
    s1 = {k: [c1[k][i]['ll'] for i in range(CAL_R1)] for k in keys}
    tab1, ch1 = {}, None
    for R1 in CAL_R1_GRID:
        for tol in CAL_TOL1_GRID:
            ok = [sum(l >= max(s1[k]) - tol for l in s1[k][:R1]) >= CONV_MIN for k in keys]
            tab1[f'R1={R1} tol={tol}'] = f'{sum(ok)}/{len(ok)}'
            if ch1 is None and all(ok): ch1 = (R1, tol)
    flag1 = ch1 is None; ch1 = ch1 or (30, 5.0)
    tab2, ch2 = {}, None
    for RB in CAL_RB_GRID:
        for tol in CAL_TOLB_GRID:
            ok = []
            for k in keys:
                st = c2[k]['starts']; b = max(s['ll'] for s in st)
                ok.append(sum(s['converged'] and s['ll'] >= b - tol for s in st[:RB]) >= CONV_MIN)
            tab2[f'RB={RB} tol={tol}'] = f'{sum(ok)}/{len(ok)}'
            if ch2 is None and all(ok): ch2 = (RB, tol)
    flag2 = ch2 is None; ch2 = ch2 or (10, 0.1)
    grid = {n: dict(logit_PASS=c2[(n, 0)]['grid_logit']['PASS'], fit_minus_logit_grid=c2[(n, 0)]['grid_logit']['lbfgs_minus_grid'],
                    fit_minus_lin_grid=c2[(n, 0)]['grid_lin']['fit_minus_grid']) for n in CONTROLS}
    desc = {f'{n}#{rep}': dict(step1_best=max(s1[(n, rep)]), step1_hit_cap=sum(c1[(n, rep)][i]['hit_cap'] for i in range(CAL_R1)),
                               S_best=(max(s['ll'] for s in c2[(n, rep)]['starts']) - c2[(n, rep)]['ll_reset']) / c2[(n, rep)]['nb'],
                               B_starts_converged=sum(s['converged'] for s in c2[(n, rep)]['starts']),
                               B_warm_restarts_max=max(s['warm'] for s in c2[(n, rep)]['starts'])) for n, rep in keys}
    out = dict(R1=ch1[0], CONV_TOL1=ch1[1], flag_step1=flag1, RB=ch2[0], CONV_TOLB=ch2[1], flag_step2=flag2,
               grid_check_observed_controls=grid, all_control_grids_PASS=all(g['logit_PASS'] for g in grid.values()),
               table_step1=tab1, table_step2=tab2, controls_descriptive=desc, seed=SEED_CAL, controls_only=True, manuscript_loaded=False,
               tool_sha256=file_sha(os.path.abspath(__file__)), seconds_last_call=round(time.time() - t0, 1))
    json.dump(out, open(FROZEN, 'x'), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k != 'controls_descriptive'}, indent=1, default=float))

def frozen(): return json.load(open(FROZEN))

# ---------------------------------------------------------------- run
def joblist():
    nn = {k: NNULL for k in REGISTERED}
    ext = json.load(open(EXT_F))['extend'] if os.path.exists(EXT_F) else []
    for k in ext: nn[k] = NNULL_EXT
    J = [(k, 0) for k in REGISTERED + DESC_OBS] + [(k, r) for r in range(1, NNULL + 1) for k in REGISTERED]
    J += [(k, r) for k in ext for r in range(NNULL + 1, NNULL_EXT + 1)]
    return J, nn

_CACHE = {}
def _s1_job(job):
    name, i = job; L = base_lines(name, manuscript_ok=True); syms, sid = symbols(L)
    r = step1_restart(L, sid, np.random.SeedSequence([SEED, hash_name(name), 1000, i]))
    return dict(kind='s1', name=name, i=i, **r)

def _b_job(job):
    name, rep, P, Fz = job; base = STEP1_OF.get(name, name); BL = base_lines(base, manuscript_ok=True); syms, sid = symbols(BL)
    P = dict(pi=np.array(P['pi']), A=np.array(P['A']), Em=np.array(P['Em']), sid=sid)
    if name not in _CACHE:
        L0 = planted_lines(name, P)[0] if name in STEP1_OF else BL
        _CACHE[name] = (L0, word_mats({tuple(w) for w in flat(L0)}, sid, P['A'], P['Em']))
    L0, cache = _CACHE[name]
    s0 = SEED_EXT if rep > NNULL else SEED
    rng = np.random.default_rng(np.random.SeedSequence([s0, hash_name(name), rep]))
    L = nline(L0, rng) if rep > 0 else L0
    B0s = [rng.dirichlet([1, 1], 2) for _ in range(Fz['RB'])]
    arr = line_arrays(_tuplify(L), cache); pi = P['pi']; ll0 = line_ll_and_counts(*arr, pi, np.tile(pi, (2, 1)))[0]; nb = nb_of(L)
    F = B_fits(arr, pi, B0s); lls = [f['ll'] for f in F]; b = int(np.argmax(lls)); Bb = Bp(F[b]['x']); Ss = [(l - ll0) / nb for l in lls]
    rec = dict(kind='b', name=name, rep=rep, ll_reset=ll0, nb=nb, S_best=Ss[b], S_starts=Ss, SD_S_starts=float(np.std(Ss, ddof=1)),
               B_best=Bb.tolist(), B_11=float(Bb[0, 0]), B_22=float(Bb[1, 1]), rows_on_bound_best=F[b]['rows_on_bound'], text_sha16=text_sha(L)[:16],
               tokens_moved=sum(a != c for a, c in zip(flat(L), flat(L0))),
               starts=[dict(ll=f['ll'], converged=f['converged'], conv_kkt=f['conv_kkt'], conv_dl=f['conv_dl'], kkt=f['kkt_proj_grad'],
                            nit=f['nit'], warm=f['warm_restarts'], rows_on_bound=f['rows_on_bound'], message=f['message']) for f in F])
    if rep == 0:
        X, M = XM(L, sid); llw = word_ll(X, M, pi, P['A'], P['Em'])
        rec['A1'] = dict(ll_line_reset=ll0, ll_word_rows=llw, abs_diff=abs(ll0 - llw), PASS=bool(abs(ll0 - llw) < 1e-6)); assert rec['A1']['PASS'], rec['A1']
        rec['lines'] = line_desc(L); rec['entropy_bits'] = entropy_table(L, sid, pi, P['Em']); rec['hash_class_balance'] = class_balance(L)
        rec['text_sha256'] = text_sha(L)
        if name in STEP1_OF: rec['lines_planted'] = planted_lines(name, P)[1]
        em = em_crosscheck(arr, pi, B0s); rec['EM_crosscheck'] = dict(EM_best_minus_lbfgs=max(e['ll'] for e in em) - lls[b], EM_iters=[e['iters'] for e in em],
                                                                     EM_hit_cap=sum(e['hit_cap'] for e in em))
        if name in CONTROLS:
            g = grid_logit(arr, pi, lls[b]); G = grid_lin(arr, pi)
            rec['grid_logit'] = g; rec['grid_lin'] = dict(grid_max_ll=G, fit_minus_grid=lls[b] - G); rec['FIT_NOT_GLOBAL'] = not g['PASS']
    return rec

def step1_table(D, Fz):
    out = {}
    for n in STEP1_TEXTS:
        rs = sorted([r for r in D if r['kind'] == 's1' and r['name'] == n], key=lambda r: r['i'])
        if len(rs) < Fz['R1']: continue
        rs = rs[:Fz['R1']]; lls = [r['ll'] for r in rs]; bi = int(np.argmax(lls))
        out[n] = dict(best=rs[bi], lls=lls, converged=step1_conv(lls, Fz['CONV_TOL1']), hit_cap=sum(r['hit_cap'] for r in rs),
                      iters=[r['iters'] for r in rs])
    return out

def anchor_manuscript():
    zs, its = file_sha('data/ZL3b-n.txt'), file_sha('data/IT2a-n.txt')
    R = dict(ZL3b_sha16=zs[:16], IT2a_sha16=its[:16], PASS_files=bool(zs.startswith(ZL_SHA16) and its.startswith(IT_SHA16)))
    for k in PRIMARY + DESC_OBS[:3]:
        L = base_lines(k, manuscript_ok=True); R[k] = dict(text_sha256=text_sha(L), words=len(flat(L)), lines=len(L))
    R['PASS_counts'] = all(R['ZL_' + k]['words'] == v for k, v in ZL_COUNTS.items())
    R['A0_stream_equals_C115_C117_strata'] = True                   # asserted in base_lines
    assert R['PASS_files'] and R['PASS_counts'], R
    return R

def run():
    Fz = frozen(); t0 = time.time()
    if not os.path.exists('analysis/C119_anchor_manuscript.json'):
        R = anchor_manuscript(); json.dump(R, open('analysis/C119_anchor_manuscript.json', 'w'), indent=1); print('A0 manuscript PASS', json.dumps(R), flush=True)
    D = load(CKPT); d1 = {(r['name'], r['i']) for r in D if r['kind'] == 's1'}
    J1 = [(n, i) for i in range(Fz['R1']) for n in STEP1_TEXTS if (n, i) not in d1]
    print('step-1 restarts todo', len(J1), flush=True)
    if J1: pool_run(_s1_job, J1, CKPT, t0, 'run-s1')
    if time.time() - t0 > SOFT_S: print('soft stop after step 1; resume'); return
    D = load(CKPT); S1 = step1_table(D, Fz); J, _ = joblist(); db = {(r['name'], r['rep']) for r in D if r['kind'] == 'b'}
    todo = [(k, r, {x: S1[STEP1_OF.get(k, k)]['best'][x] for x in ('pi', 'A', 'Em')}, Fz) for k, r in J if (k, r) not in db and STEP1_OF.get(k, k) in S1]
    print('B jobs', len(J), 'done', len(db), 'todo', len(todo), flush=True)
    n = pool_run(_b_job, todo, CKPT, t0, 'run-b') if todo else 0
    D = load(CKPT); db = {(r['name'], r['rep']) for r in D if r['kind'] == 'b'}
    reg = [j for j in J if j[0] in REGISTERED]
    print('wrote', n, 'in', round(time.time() - t0, 1), 's; registered jobs done', sum(j in db for j in reg), '/', len(reg),
          '; descriptive', sum(j in db for j in J if j[0] in DESC_OBS), '/', len(DESC_OBS), flush=True)

def status():
    J, _ = joblist(); D = load(CKPT); db = {(r['name'], r['rep']) for r in D if r['kind'] == 'b'}
    print('frozen', os.path.exists(FROZEN), '; step-1 restarts', sum(r['kind'] == 's1' for r in D),
          '; registered B jobs done', sum(j in db for j in J if j[0] in REGISTERED), '/', sum(j[0] in REGISTERED for j in J))

# ---------------------------------------------------------------- statistics
def boot_ci(x, fn, ss):
    x = np.asarray(x); rng = np.random.default_rng(ss); idx = rng.integers(0, len(x), (NBOOT, len(x)))
    v = np.array([fn(x[i]) for i in idx]); return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]

def rank_of(obs, cn):
    cn = np.asarray(cn); ties = int((np.abs(cn - obs) <= TIE).sum()); return float(((cn < obs - TIE).sum() + 0.5 * ties) / len(cn))

QS = (0.05, 0.10, 0.25, 0.75, 0.90, 0.95)

def text_stats(name, D, Fz, S1, nn):
    recs = {r['rep']: r for r in D if r['kind'] == 'b' and r['name'] == name}; base = STEP1_OF.get(name, name)
    o = recs[0]; s1ok = S1[base]['converged']; nul = [recs[r] for r in range(1, nn + 1)]
    oc = bool(s1ok and s_conv(o, Fz['CONV_TOLB'])); conv = [bool(s1ok and s_conv(r, Fz['CONV_TOLB'])) for r in nul]
    cn = np.array([r['S_best'] for r, c in zip(nul, conv) if c]); unc = int(sum(not c for c in conv)); S = o['S_best']; h = hash_name(name)
    rec = dict(obs_S=S, obs_converged=oc, step1_converged=s1ok, step1_best_ll=S1[base]['best']['ll'], step1_hit_cap=S1[base]['hit_cap'],
               obs_B_11=o['B_11'], obs_B_22=o['B_22'], obs_rows_on_bound=o['rows_on_bound_best'], obs_SD_S_starts=o['SD_S_starts'],
               obs_starts_converged=sum(s['converged'] for s in o['starts']), obs_A1_abs_diff=o['A1']['abs_diff'], delta_ll_B_obs=S * o['nb'],
               n_boundaries=o['nb'], lines=o['lines'], entropy_bits={k: v for k, v in o['entropy_bits'].items() if k != 'per_first_glyph'},
               hash_class_balance=o['hash_class_balance'], EM_crosscheck=o['EM_crosscheck'], n_null=nn, unconverged=unc,
               conv_rate=1 - unc / nn, effective_N=int(len(cn)), FIT_NOT_GLOBAL=o.get('FIT_NOT_GLOBAL'),
               grid_logit_fit_minus_grid=o.get('grid_logit', {}).get('lbfgs_minus_grid'), grid_lin_fit_minus_grid=o.get('grid_lin', {}).get('fit_minus_grid'),
               distinct_null_texts=len({r['text_sha16'] for r in nul}), lines_planted=o.get('lines_planted'))
    allst = [s for r in nul for s in r['starts']]
    rec['null_optimiser'] = dict(starts=len(allst), conv_kkt_share=float(np.mean([s['conv_kkt'] for s in allst])),
                                 conv_dl_share=float(np.mean([s['conv_dl'] for s in allst])), unconverged_starts=int(sum(not s['converged'] for s in allst)),
                                 warm_restarts_mean=float(np.mean([s['warm'] for s in allst])), warm_restarts_max=int(max(s['warm'] for s in allst)),
                                 rows_on_bound_best_share=float(np.mean([r['rows_on_bound_best'] >= 1 for r in nul])))
    if len(cn):
        ge = int((cn >= S - TIE).sum()); ties = int((np.abs(cn - S) <= TIE).sum()); gt = int((cn > S + TIE).sum())
        sdn = float(cn.std(ddof=1)) if len(cn) > 1 else 0.0
        rec.update(p=(1 + ge) / (1 + len(cn)), mid_p=(gt + 0.5 * ties + 0.5) / (1 + len(cn)), p_cons=(1 + ge + unc) / (1 + nn), p_lib=(1 + ge) / (1 + nn),
                   ties=ties, rank=rank_of(S, cn), rank_CI95=boot_ci(cn, lambda x: rank_of(S, x), np.random.SeedSequence([SEED_BOOT, h, 1])),
                   null_mean=float(cn.mean()), null_SD=sdn, null_min=float(cn.min()), null_max=float(cn.max()),
                   null_quantiles={str(q): float(np.quantile(cn, q)) for q in QS},
                   null_quantiles_CI95={str(q): boot_ci(cn, lambda x, q=q: float(np.quantile(x, q)), np.random.SeedSequence([SEED_BOOT, h, 2, int(q * 100)])) for q in QS},
                   distinct_frac=len(np.unique(np.round(cn, 9))) / len(cn), PNOISE_ratio=(sdn / o['SD_S_starts']) if o['SD_S_starts'] > 0 else None,
                   PNOISE_pass=bool(sdn > o['SD_S_starts']), z=(S - float(cn.mean())) / sdn if sdn > 0 else None)
    else: rec.update(p=None, rank=None, distinct_frac=0.0, PNOISE_pass=False)
    rec['testable_basic'] = bool(oc and unc <= MAX_UNCONV * nn and len(cn) >= MIN_EFFN)
    return rec, cn

def _ready(names, nn):
    D = load(CKPT); db = {(r['name'], r['rep']) for r in D if r['kind'] == 'b'}
    miss = [(k, r) for k in names for r in range(nn[k] + 1) if (k, r) not in db]
    return D, miss

def gates():
    Fz = frozen(); J, nn = joblist(); D, miss = _ready(CONTROLS, nn); assert not miss, f'{len(miss)} control jobs missing'
    S1 = step1_table(D, Fz); st = {}; cns = {}
    for k in CONTROLS: st[k], cns[k] = text_stats(k, D, Fz, S1, nn[k])
    bar = ALPHA / 3; G = dict(frozen=Fz, per_text=st, NNULL_used={k: nn[k] for k in CONTROLS})
    g1 = {}
    for k in MAIN_CTRL:
        s = st[k]; g1[k] = dict(converges=s['obs_converged'], conv_rate=s['conv_rate'], effective_N=s['effective_N'], distinct_frac=s['distinct_frac'],
                               not_FIT_NOT_GLOBAL=not s['FIT_NOT_GLOBAL'], p=s['p'], rank=s['rank'], rank_CI95=s.get('rank_CI95'),
                               PASS_window=bool(s['testable_basic'] and s['conv_rate'] >= 1 - MAX_UNCONV and s['distinct_frac'] >= MIN_DISTINCT
                                                and not s['FIT_NOT_GLOBAL'] and s['p'] is not None and s['p'] > bar + 1e-12))
    ranks = [st[k]['rank'] for k in MAIN_CTRL]
    mean_rank = float(np.mean(ranks)) if None not in ranks else None
    if mean_rank is not None:
        r1, r2 = np.random.default_rng(np.random.SeedSequence([SEED_BOOT, 0])), None
        a, b = cns[MAIN_CTRL[0]], cns[MAIN_CTRL[1]]; S_a, S_b = st[MAIN_CTRL[0]]['obs_S'], st[MAIN_CTRL[1]]['obs_S']
        ia = r1.integers(0, len(a), (NBOOT, len(a))); ib = r1.integers(0, len(b), (NBOOT, len(b)))
        mv = np.array([(rank_of(S_a, a[i]) + rank_of(S_b, b[j])) / 2 for i, j in zip(ia, ib)]); mci = [float(np.quantile(mv, 0.025)), float(np.quantile(mv, 0.975))]
    else: mci = None
    GFPR = bool(mean_rank is not None and 0.10 <= mean_rank <= 0.90 and all(g1[k]['p'] is not None and g1[k]['p'] > bar + 1e-12 for k in MAIN_CTRL))
    G['gate1'] = dict(windows=g1, mean_rank=mean_rank, mean_rank_CI95=mci, G_FPR=GFPR, PASS=bool(GFPR and all(g1[k]['PASS_window'] for k in MAIN_CTRL)))
    G['PNOISE'] = dict({k: dict(SD_null=st[k].get('null_SD'), SD_starts=st[k]['obs_SD_S_starts'], ratio=st[k].get('PNOISE_ratio'), PASS=st[k]['PNOISE_pass'])
                        for k in MAIN_CTRL}, PASS=all(st[k]['PNOISE_pass'] for k in MAIN_CTRL))
    gp = st[GPOW]
    G['gate3'] = dict(p=gp['p'], p_cons=gp.get('p_cons'), rank=gp['rank'], z=gp.get('z'), lines_planted=gp['lines_planted'], testable=bool(gp['testable_basic'] and gp['PNOISE_pass'] and not gp['FIT_NOT_GLOBAL']),
                      distinct_frac_printed=gp['distinct_frac'], PASS=bool(gp['testable_basic'] and gp['PNOISE_pass'] and not gp['FIT_NOT_GLOBAL'] and gp['p'] is not None and gp['p'] <= bar + 1e-12))
    sec = {}
    for k in SEC_CTRL:
        s = st[k]; sec[k] = dict(rank=s['rank'], rank_CI95=s.get('rank_CI95'), p=s['p'],
                                PASS=bool(s['testable_basic'] and s['distinct_frac'] >= MIN_DISTINCT and not s['FIT_NOT_GLOBAL'] and s['rank'] is not None and 0.05 <= s['rank'] <= 0.95))
    G['secondary'] = sec
    # BORDERLINE (one extension, controls only)
    ext_done = json.load(open(EXT_F))['extend'] if os.path.exists(EXT_F) else None
    need = []
    if mci and (mci[0] <= 0.10 <= mci[1] or mci[0] <= 0.90 <= mci[1]): need += list(MAIN_CTRL)
    for k in SEC_CTRL:
        ci = st[k].get('rank_CI95')
        if ci and (ci[0] <= 0.05 <= ci[1] or ci[0] <= 0.95 <= ci[1]): need.append(k)
    G['borderline'] = dict(needs_extension=need, extension_file=ext_done)
    if need and ext_done is None:
        json.dump(dict(extend=need, reason='BORDERLINE: bootstrap 95% interval contains a gate edge (section 9)'), open(EXT_F, 'x'), indent=1)
        G['decided'] = False; json.dump(G, open('analysis/C119_gates_79draw.json', 'w'), indent=1, default=float)
        print('BORDERLINE: extension reps 80-159 (seed 11805) for', need, '; run `run` again, then `gates`', flush=True); return
    if ext_done is not None and os.path.exists('analysis/C119_gates_79draw.json'): G['reading_79_draws'] = json.load(open('analysis/C119_gates_79draw.json'))
    G['decided'] = True; G['all_blocking_PASS'] = bool(G['gate1']['PASS'] and G['PNOISE']['PASS'] and G['gate3']['PASS'])
    json.dump(G, open(GATES_F, 'w'), indent=1, default=float)
    print(json.dumps({k: G[k] for k in ('gate1', 'PNOISE', 'gate3', 'secondary', 'borderline', 'all_blocking_PASS')}, indent=1, default=float))

def holm(ps):
    order = sorted(ps, key=lambda k: ps[k]); out, ok = {}, True
    for i, k in enumerate(order):
        bar = ALPHA / (len(ps) - i); ok = ok and ps[k] <= bar + 1e-12; out[k] = dict(p=ps[k], bar=round(bar, 5), pass_=ok)
    return out

def bh(ps):
    order = sorted(ps, key=lambda k: ps[k]); m = len(ps); kmax = 0
    for i, k in enumerate(order):
        if ps[k] <= ALPHA * (i + 1) / m + 1e-12: kmax = i + 1
    return {k: dict(p=ps[k], pass_=order.index(k) < kmax) for k in ps}

def verdict():
    Fz = frozen(); G = json.load(open(GATES_F)); assert G['decided'], 'gates not decided'
    J, nn = joblist(); D, miss = _ready(PRIMARY, nn); assert not miss, f'{len(miss)} primary jobs missing'
    S1 = step1_table(D, Fz); st = {}
    for k in PRIMARY:
        st[k], _ = text_stats(k, D, Fz, S1, nn[k])
        st[k]['testable'] = bool(st[k]['testable_basic'] and st[k]['distinct_frac'] >= MIN_DISTINCT)
        st[k]['movable_token_share_below_50pct'] = st[k]['lines']['movable_token_share'] < 0.5
    pv = lambda f: {k: (st[k][f] if st[k]['testable'] else 1.0) for k in PRIMARY}
    H, Hc, Hl, BH = holm(pv('p')), holm(pv('p_cons')), holm(pv('p_lib')), bh(pv('p'))
    cs = [k for k in PRIMARY if st[k]['testable'] and Hc[k]['pass_'] != Hl[k]['pass_']]
    passed = [k for k in PRIMARY if H[k]['pass_'] and st[k]['testable'] and k not in cs]
    untest = [k for k in PRIMARY if not st[k]['testable']]
    if not G['all_blocking_PASS']:
        failed = [g for g, ok in (('gate 1', G['gate1']['PASS']), ('P-NOISE', G['PNOISE']['PASS']), ('gate 3 (G-POW)', G['gate3']['PASS'])) if not ok]
        lab = 'NOT TESTABLE (' + ', '.join(failed) + ' failed)'
    elif len(untest) == 3: lab = 'NOT TESTABLE (all three primary strata not testable)'
    elif passed: lab = 'BOUNDARY STATE IN WORD ORDER in ' + '+'.join(passed)
    else: lab = 'NOT SUPPORTED' + (f' (not testable: {"+".join(untest)})' if untest else '')
    if cs: lab += ' (CONVERGENCE-SENSITIVE: ' + '+'.join(cs) + ', no pass)'
    D2 = load(CKPT); desc = {}
    for k in DESC_OBS:
        r = next((x for x in D2 if x['kind'] == 'b' and x['name'] == k and x['rep'] == 0), None)
        if r: desc[k] = dict(S=r['S_best'], B_11=r['B_11'], B_22=r['B_22'], n_boundaries=r['nb'], SD_S_starts=r['SD_S_starts'],
                             starts_converged=sum(s['converged'] for s in r['starts']), S_converged=s_conv(r, Fz['CONV_TOLB']),
                             entropy_bits={a: b for a, b in r['entropy_bits'].items() if a != 'per_first_glyph'}, lines=r['lines'])
    R = dict(frozen=Fz, gates={k: G[k] for k in ('gate1', 'PNOISE', 'gate3', 'secondary', 'borderline', 'all_blocking_PASS')}, primary=st,
             holm=H, holm_cons=Hc, holm_lib=Hl, BH_printed=BH, convergence_sensitive=cs, verdict=lab, descriptive_observed=desc,
             step1={k: dict(best_ll=v['best']['ll'], converged=v['converged'], hit_cap=v['hit_cap'], lls=v['lls'], A=v['best']['A'], pi=v['best']['pi']) for k, v in S1.items()},
             tool_sha256=file_sha(os.path.abspath(__file__)))
    json.dump(R, open(RESULTS_F, 'w'), indent=1, default=float)
    print(json.dumps(dict(verdict=lab, holm=H, BH=BH, primary={k: {x: st[k].get(x) for x in ('obs_S', 'p', 'mid_p', 'p_cons', 'p_lib', 'rank', 'effective_N', 'conv_rate', 'testable')} for k in PRIMARY}), indent=1, default=float))

# ---------------------------------------------------------------- descriptive (after the verdict; decides nothing)
def desc():
    assert os.path.exists(RESULTS_F), 'desc runs only after the verdict'
    import c119_precheck as C1
    C1.NITER = 500
    Fz = frozen(); D = load(CKPT); S1 = step1_table(D, Fz); out = dict(label='DESCRIPTIVE ONLY (decides nothing)')
    W1 = base_lines('CAE_DV_W1'); syms, sid = symbols(W1)
    w1n = np.array([r['S_best'] for r in D if r['kind'] == 'b' and r['name'] == 'CAE_DV_W1' and r['rep'] > 0 and s_conv(r, Fz['CONV_TOLB'])])
    hr = next(r for r in D if r['kind'] == 'b' and r['name'] == 'HASH_W1' and r['rep'] == 0)
    out['hash_plant_vs_W1_nulls'] = dict(S=hr['S_best'], lines_planted=hr.get('lines_planted'), rank=rank_of(hr['S_best'], w1n),
                                         p=float((1 + (w1n >= hr['S_best'] - TIE).sum()) / (1 + len(w1n))), effective_N=len(w1n))
    tw = [[tuple(w) for w in l] for l in W1]; rg = np.random.default_rng(np.random.SeedSequence([SEED, 2]))
    tw = [twin(l, rg, Q_TWIN) for l in tw]; ts, tsid = symbols(tw)
    F = [step1_restart(tw, tsid, np.random.SeedSequence([SEED, hash_name('TWIN_W1'), 1000, i])) for i in range(Fz['R1'])]
    P = params_of(max(F, key=lambda r: r['ll'])); cache = word_mats({tuple(w) for w in flat(tw)}, tsid, P['A'], P['Em'])
    arr = line_arrays(tw, cache); ll0 = line_ll_and_counts(*arr, P['pi'], np.tile(P['pi'], (2, 1)))[0]
    rng = np.random.default_rng(np.random.SeedSequence([SEED, hash_name('TWIN_W1'), 0])); B0s = [rng.dirichlet([1, 1], 2) for _ in range(Fz['RB'])]
    Fb = B_fits(arr, P['pi'], B0s); out['twin_plant_q0.1_observed'] = dict(S=(max(f['ll'] for f in Fb) - ll0) / nb_of(tw), step1_lls=[f['ll'] for f in F],
        note='cannot be seen by construction: the twin alphabet changes step 1 identically in the text and every N-LINE replicate')
    out['T'] = {}
    for k in ('CAE_DV_W1', 'CAE_DV_W2', 'CAE_V', 'HEB_ABJ') + PRIMARY:
        L = base_lines(k, manuscript_ok=True); sy, _ = symbols(L); h = hash_name(k)
        P_ = C1.fams(L, sy, np.random.SeedSequence([SEED, h, 2000])); Tt = C1.fams(L, sy, np.random.SeedSequence([SEED, h, 2001]), tied=True)
        out['T'][k] = dict(T=P_['T'], T_tied=Tt['T'], cap_hits=sum(i == 500 for i in P_['iters_free'] + P_['iters_con']),
                           cap_hits_tied=sum(i == 500 for i in Tt['iters_free'] + Tt['iters_con']), fits=len(P_['iters_free']) * 2)
        print('T', k, json.dumps(out['T'][k]), flush=True)
    json.dump(out, open(DESC_F, 'w'), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k != 'T'}, indent=1, default=float))

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'anchor': anchor, 'calib': calib, 'run': run, 'gates': gates, 'verdict': verdict, 'desc': desc}.get(a, status)()
