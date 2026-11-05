#!/usr/bin/env python3
"""C042 (F-ENT step 2): conditional-entropy profile h_k for k=1..4 (bits, log2).
Does the Voynich low next-glyph uncertainty persist at h3/h4 vs 7 natural texts at matched N=50k,
and does the Timm-Schinner generator follow the same profile? Look 3: predecessor MI attribution.
Pre-registered in case-file/C042-entropy-profile-hk.md. Seed 4242.
Run: timeout 600 python3 tools/c042_entropy_profile.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, math
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L
import c041_conditional_entropy as C41

SEED, N, NBLK, NBOOT, NGATE, PCOPY = 4242, 50000, 20, 200, 40, 0.6
SP = C41.SP
C = 'data/corpora/'
KS = (1, 2, 3, 4)

def stream(words, tok, space=True, n=N):
    return C41.stream(words, tok, space, n)

def encode(s):
    return C41.encode(s)

def prep(words, tok, space=True, n=N):
    return C41.prep(words, tok, space, n)

def wshuffle(a, wid, rng):
    return C41.wshuffle(a, wid, rng)

def plant_copy(a, wid, rng, p=PCOPY):
    return C41.plant_copy(a, wid, rng, p)

def H_from_counts(cnt):
    """Entropy from a Counter or array of positive counts (log2)."""
    if isinstance(cnt, Counter):
        vals = np.fromiter(cnt.values(), dtype=float)
    else:
        vals = np.asarray(cnt, dtype=float)
        vals = vals[vals > 0]
    if vals.size == 0:
        return 0.0
    p = vals / vals.sum()
    return float(-(p * np.log2(p)).sum())

def ngram_counter(a, k):
    """Sparse Counter of overlapping k-grams encoded as int64 base-A rolls.
    For k=1 returns bincount-like Counter of symbols."""
    a = np.asarray(a, dtype=np.int64)
    if k == 1:
        return Counter(int(x) for x in a)
    A = int(a.max()) + 1
    n = len(a) - k + 1
    if n <= 0:
        return Counter()
    # Horner: c = a[i] + A*(a[i+1] + A*(...))
    c = a[k - 1:].astype(np.int64).copy()
    mul = 1
    for j in range(k - 2, -1, -1):
        mul *= A
        c += a[j:j + n] * mul
    return Counter(int(x) for x in c)

def block_ngram_counters(a, k):
    """Per-block sparse Counters for k-grams (and for k-1 if k>=2, computed separately)."""
    edges = np.linspace(0, len(a), NBLK + 1).astype(int)
    return [ngram_counter(a[edges[b]:edges[b + 1]], k) for b in range(NBLK)]

def merge_counters(blocks, idxs):
    out = Counter()
    for i in idxs:
        out.update(blocks[i])
    return out

def hk_from_counters(ck, ck1):
    """h_k = H(k-gram) - H((k-1)-gram). For k=1, ck1 unused, return H(1-gram)."""
    if ck1 is None:
        return H_from_counts(ck)
    return H_from_counts(ck) - H_from_counts(ck1)

def profile(a):
    """Point estimates h1..h4 and |A|."""
    alph = int(len(set(int(x) for x in a)))
    out = {'A': alph}
    prev = None
    for k in KS:
        ck = ngram_counter(a, k)
        out[f'h{k}'] = hk_from_counters(ck, prev)
        if k >= 2:
            out[f'h{k}_norm'] = out[f'h{k}'] / math.log2(alph) if alph > 1 else float('nan')
        prev = ck
    return out

def boot_ci_profile(a, rng, which_ks=(2, 3, 4)):
    """Block-bootstrap 95% CI for selected h_k. Returns dict k -> [lo, hi]."""
    # Precompute block counters for k=1..4
    blks = {k: block_ngram_counters(a, k) for k in KS}
    out = {k: [] for k in which_ks}
    for _ in range(NBOOT):
        idxs = rng.integers(0, NBLK, NBLK)
        # merge once per k
        merged = {k: merge_counters(blks[k], idxs) for k in KS}
        for k in which_ks:
            ck1 = merged[k - 1] if k >= 2 else None
            out[k].append(hk_from_counters(merged[k], ck1))
    return {k: np.percentile(out[k], [2.5, 97.5]).tolist() for k in which_ks}

def low_call(h, ci_hi, nat_min):
    return bool(h < nat_min and ci_hi < nat_min)

def predecessor_mi(a, inv_voc):
    """Look 3: per-predecessor I(prev=a; next) = H(next) - H(next|prev=a), weighted by P(a).
    Returns list of dicts sorted by contribution P(a)*I descending."""
    A = int(a.max()) + 1
    bc = np.bincount(a[:-1] * A + a[1:], minlength=A * A).reshape(A, A)
    row = bc.sum(1)
    tot = float(row.sum())
    Hn = H_from_counts(bc.sum(0))
    rows = []
    for i in range(A):
        if row[i] == 0:
            continue
        Hcond = H_from_counts(bc[i])
        I = Hn - Hcond
        pa = row[i] / tot
        glyph = inv_voc.get(i, str(i))
        rows.append(dict(glyph=glyph, P=float(pa), I=float(I), contrib=float(pa * I),
                         H_next_given=float(Hcond), count=int(row[i])))
    rows.sort(key=lambda r: -r['contrib'])
    return rows

def inv_from_voc(voc):
    return {v: k for k, v in voc.items()}

def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    gens = {'Generator_base': [w for ws, _ in L.generator() for w in ws]}
    try:
        import c004_generator_sweep as G
        cfg = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'],
                   **{'text.lines_to_create': 2400})
        raw = G.generate(cfg, SEED)
        gens['Generator_C005matched'] = [w for l in (raw or []) for w in l]
    except Exception as e:
        print('C005 generator unavailable:', e, flush=True)

    voy = {'Voynich_ZL3b': [w for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt') for w in ws],
           'Voynich_IT2a': [w for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt') for w in ws]}
    nat = {'Latin_Caesar': [w for l in T.gutenberg(C + 'pg218.txt') for w in l],
           'Latin_Descartes': [w for l in T.gutenberg(C + 'pg23306.txt') for w in l],
           'Italian_Dante': [w for l in T.gutenberg(C + 'pg1012.txt') for w in l],
           'Italian_Machiavelli': [w for l in T.gutenberg(C + 'pg56498.txt') for w in l],
           'Spanish_Cervantes': [w for l in T.gutenberg(C + 'pg2000.txt') for w in l],
           'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l],
           'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l]}
    tok = {k: T.units for k in list(voy) + list(gens)}

    R = dict(N=N, seed=SEED, log='log2 (bits)',
             primary_tokenization='EVA glyph units (c003.units), commas as spaces (c030), '
                                  'one space token after every word; first N=50000',
             texts={}, gates={}, natural_range={}, verdicts={}, descriptive={}, look3={})

    # ---- 1. natural texts first
    streams = {}  # keep encoded streams for later CI on min/max
    def measure(k, words, do_boot=True, which_ks=(2, 3, 4)):
        a, wid, A = prep(words, tok.get(k))
        # also need original symbols for Look 3: re-encode with voc
        s, _ = stream(words, tok.get(k)); s = s[:N]
        a2, voc = encode(s)
        assert len(a2) == len(a)
        m = profile(a)
        m['n'] = int(len(a))
        if do_boot:
            cis = boot_ci_profile(a, rng, which_ks=which_ks)
            for kk, ci in cis.items():
                m[f'h{kk}_ci95'] = ci
            # norm CIs from same point / log2|A|
            for kk in which_ks:
                lo, hi = m[f'h{kk}_ci95']
                m[f'h{kk}_norm_ci95'] = [lo / math.log2(m['A']), hi / math.log2(m['A'])]
        R['texts'][k] = m
        streams[k] = (a, wid, voc)
        brief = {x: (round(y, 4) if isinstance(y, float) else y)
                 for x, y in m.items() if not x.endswith('ci95') and not x.endswith('_norm_ci95')}
        print(k, brief, round(time.time() - t0, 1), 's', flush=True)
        return a, wid, voc

    for k, w in nat.items():
        measure(k, w, do_boot=True)

    # natural ranges per k
    nat_range = {}
    for kk in KS:
        vals = [R['texts'][k][f'h{kk}'] for k in nat]
        nat_range[f'h{kk}'] = [min(vals), max(vals)]
        if kk >= 2:
            nvals = [R['texts'][k][f'h{kk}_norm'] for k in nat]
            nat_range[f'h{kk}_norm'] = [min(nvals), max(nvals)]
    R['natural_range'] = nat_range
    print('natural_range', {k: [round(a, 4), round(b, 4)] for k, (a, b) in nat_range.items()}, flush=True)

    # leave-one-out at k=2
    R['natural_loo_low_k2'] = {}
    for k in nat:
        others_min = min(R['texts'][j]['h2'] for j in nat if j != k)
        ci_hi = R['texts'][k]['h2_ci95'][1]
        R['natural_loo_low_k2'][k] = low_call(R['texts'][k]['h2'], ci_hi, others_min)

    # ---- 2. gates on Caesar BEFORE Voynich
    ca, cwid, cvoc = streams['Latin_Caesar']
    # need longer Caesar stream for windows
    ca_full, cwid_full, cA_full = prep(nat['Latin_Caesar'], None, n=10 ** 9)
    nmin2 = nat_range['h2'][0]
    nmin3 = nat_range['h3'][0]
    qmin2 = nat_range['h2_norm'][0]
    fp2 = pw2 = fp3 = 0
    fpn = pwn = 0
    ph = []
    for g in range(NGATE):
        s0 = int(rng.integers(0, len(ca_full) - N))
        a = ca_full[s0:s0 + N]
        wid = cwid_full[s0:s0 + N]
        # FPR: within-word shuffle
        sh = wshuffle(a, wid, rng)
        msh = profile(sh)
        # cheap CI: bootstrap only h2 (and h3)
        ci_sh = boot_ci_profile(sh, rng, which_ks=(2, 3))
        fp2 += low_call(msh['h2'], ci_sh[2][1], nmin2)
        fp3 += low_call(msh['h3'], ci_sh[3][1], nmin3)
        fpn += low_call(msh['h2_norm'], ci_sh[2][1] / math.log2(msh['A']), qmin2)
        # Power: plant
        pl = plant_copy(a, wid, rng)
        mpl = profile(pl)
        ci_pl = boot_ci_profile(pl, rng, which_ks=(2,))
        ph.append(mpl['h2'])
        pw2 += low_call(mpl['h2'], ci_pl[2][1], nmin2)
        pwn += low_call(mpl['h2_norm'], ci_pl[2][1] / math.log2(mpl['A']), qmin2)
        if (g + 1) % 10 == 0:
            print(f'  gate {g+1}/{NGATE}', round(time.time() - t0, 1), 's', flush=True)
    gate_ok = fp2 <= 4 and pw2 >= 32
    gate2_ok = fpn <= 4 and pwn >= 32
    R['gates'] = dict(
        fpr_k2=f'{fp2}/{NGATE}', power_k2=f'{pw2}/{NGATE}', ok_k2=gate_ok,
        fpr_k3=f'{fp3}/{NGATE}', fpr_k3_note='descriptive size check; not a gate for H1',
        fpr_norm_k2=f'{fpn}/{NGATE}', power_norm_k2=f'{pwn}/{NGATE}', ok_norm=gate2_ok,
        plant_h2_mean=float(np.mean(ph)), caesar_symbols=int(len(ca_full)))
    print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)

    # ---- 3. Voynich + generators
    for k, w in {**voy, **gens}.items():
        if len(w) < 1000:
            R['texts'][k] = dict(error='missing')
            continue
        measure(k, w, do_boot=True)

    # classify robustly low per k
    def robust_map(text_key, use_norm=False):
        t = R['texts'].get(text_key, {})
        if 'h2' not in t:
            return {}
        out = {}
        for kk in (2, 3, 4):
            key = f'h{kk}' + ('_norm' if use_norm else '')
            nmin = nat_range[key][0]
            ci = t.get(f'h{kk}' + ('_norm' if use_norm else '') + '_ci95')
            if ci is None:
                # fall back
                ci = t.get(f'h{kk}_ci95')
                if use_norm and ci is not None:
                    ci = [ci[0] / math.log2(t['A']), ci[1] / math.log2(t['A'])]
            if ci is None:
                out[kk] = False
                continue
            out[kk] = low_call(t[key], ci[1], nmin)
        return out

    per = {}
    for k in list(voy) + list(gens):
        if 'h2' not in R['texts'].get(k, {}):
            per[k] = 'missing'
            continue
        rh = robust_map(k, False)
        rn = robust_map(k, True)
        per[k] = dict(robust_low=rh, robust_low_norm=rn,
                      profile={f'h{kk}': R['texts'][k][f'h{kk}'] for kk in KS},
                      profile_norm={f'h{kk}_norm': R['texts'][k].get(f'h{kk}_norm') for kk in (2, 3, 4)})

    def classify(rmap):
        """rmap: {2:bool, 3:bool, 4:bool}"""
        if not rmap.get(2) and not rmap.get(3) and not rmap.get(4):
            return 'INSIDE NATURAL'
        if rmap.get(2) and (rmap.get(3) or rmap.get(4)):
            return 'UNUSUALLY LOW'
        # only h2, or only one of 3/4 without h2, etc.
        return 'PARTIAL'

    z_r = per['Voynich_ZL3b']['robust_low'] if isinstance(per.get('Voynich_ZL3b'), dict) else {}
    i_r = per['Voynich_IT2a']['robust_low'] if isinstance(per.get('Voynich_IT2a'), dict) else {}
    z_n = per['Voynich_ZL3b']['robust_low_norm'] if isinstance(per.get('Voynich_ZL3b'), dict) else {}
    i_n = per['Voynich_IT2a']['robust_low_norm'] if isinstance(per.get('Voynich_IT2a'), dict) else {}

    def primary_verdict(zr, ir, gate):
        if not gate:
            return 'NOT TESTABLE'
        cz, ci = classify(zr), classify(ir)
        if zr != ir:
            # disagree on which ks are robustly low
            return 'SPLIT'
        if cz == ci:
            return cz
        return 'SPLIT'

    R['verdicts'] = dict(
        H1=primary_verdict(z_r, i_r, gate_ok),
        H2=primary_verdict(z_n, i_n, gate2_ok),
        ZL_pattern=classify(z_r), IT2a_pattern=classify(i_r),
        ZL_ks_low=z_r, IT2a_ks_low=i_r,
        ZL_norm_pattern=classify(z_n), IT2a_norm_pattern=classify(i_n),
        per_text=per)

    # generator classifications (do not decide H1)
    for gk in gens:
        if isinstance(per.get(gk), dict):
            R['verdicts'][f'{gk}_pattern'] = classify(per[gk]['robust_low'])
            R['verdicts'][f'{gk}_ks_low'] = per[gk]['robust_low']

    # ---- 4. Look 3 descriptive: predecessor MI for Voynich + natural median reference + vowelless
    look3 = {}
    for k in ['Voynich_ZL3b', 'Voynich_IT2a', 'Italian_Machiavelli', 'Latin_Caesar', 'Italian_Dante']:
        if k not in streams:
            continue
        a, wid, voc = streams[k]
        inv = inv_from_voc(voc)
        rows = predecessor_mi(a, inv)
        look3[k] = dict(top15=rows[:15], h2=R['texts'][k]['h2'],
                        total_I=float(sum(r['contrib'] for r in rows)))
    # vowelless controls
    for lab, fname in [('Latin_Caesar_vowelless', 'pg218.txt'), ('Italian_Dante_vowelless', 'pg1012.txt')]:
        words = [x for l in T.devowel(T.gutenberg(C + fname)) for x in l]
        a, wid, A = prep(words, None)
        s, _ = stream(words, None); s = s[:N]
        a2, voc = encode(s)
        m = profile(a2)
        inv = inv_from_voc(voc)
        rows = predecessor_mi(a2, inv)
        look3[lab] = dict(top15=rows[:15], h2=m['h2'], profile=m,
                          total_I=float(sum(r['contrib'] for r in rows)))
        R['descriptive'][lab] = m
    R['look3'] = look3

    # natural median h2 for attribution narrative
    nat_h2s = sorted(R['texts'][k]['h2'] for k in nat)
    R['natural_h2_median'] = float(nat_h2s[len(nat_h2s) // 2])

    R['runtime_s'] = round(time.time() - t0, 1)
    os.makedirs('analysis', exist_ok=True)
    json.dump(R, open('analysis/C042_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['verdicts'], default=str, indent=2))
    print('runtime', R['runtime_s'])

if __name__ == '__main__':
    main()
