#!/usr/bin/env python3
"""C043 (F-ENT step 3): gated pair/predecessor decomposition of the ~0.70-bit h2 deficit.
Is the deficit concentrated in fixed set S={y,i,n,a,d,r,ch,l,q} from C042 Look 3, and does
neutralizing S close >=50% of the gap vs natural? Concentration C5 vs natural + vowelless.
Pre-registered in case-file/C043-pair-decomposition.md. Seed 4343.
Run: timeout 600 python3 tools/c043_pair_decomposition.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, math
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L
import c041_conditional_entropy as C41

SEED, N, NGATE, PCOPY = 4343, 50000, 40, 0.6
SP = C41.SP
C = 'data/corpora/'
# Fixed set from C042 Look 3 (exploratory -> confirmatory, disclosed)
S_GLYPHS = frozenset(['y', 'i', 'n', 'a', 'd', 'r', 'ch', 'l', 'q'])
OUT = 'analysis/C043_results.json'
CKPT = 'analysis/C043_results.partial.json'

def stream(words, tok, space=True, n=N):
    return C41.stream(words, tok, space, n)

def encode(s):
    return C41.encode(s)

def wshuffle(a, wid, rng):
    return C41.wshuffle(a, wid, rng)

def plant_copy(a, wid, rng, p=PCOPY):
    return C41.plant_copy(a, wid, rng, p)

def H_from_counts(cnt):
    if isinstance(cnt, Counter):
        vals = np.fromiter(cnt.values(), dtype=float)
    else:
        vals = np.asarray(cnt, dtype=float)
        vals = vals[vals > 0]
    if vals.size == 0:
        return 0.0
    p = vals / vals.sum()
    return float(-(p * np.log2(p)).sum())

def prep_full(words, tok, space=True, n=N):
    """Like C41.prep but also returns the string list and voc for glyph names."""
    s, wid = stream(words, tok, space, n=n)
    s, wid = s[:n], np.array(wid[:n], dtype=np.int64)
    a, voc = encode(s)
    return a, wid, voc, s

def inv_from_voc(voc):
    return {v: k for k, v in voc.items()}

def decompose(a, inv_voc):
    """Per-predecessor contributions; I, C5, h2, h1_next, rows sorted by contrib."""
    a = np.asarray(a, dtype=np.int64)
    A = int(a.max()) + 1
    bc = np.bincount(a[:-1] * A + a[1:], minlength=A * A).reshape(A, A)
    row = bc.sum(1)
    col = bc.sum(0)
    tot = float(row.sum())
    if tot <= 0:
        return dict(h1=0.0, h2=0.0, I=0.0, C5=0.0, rows=[], A=0)
    Hn = H_from_counts(col)          # H(next)
    Hp = H_from_counts(row)          # H(prev)
    Hpair = H_from_counts(bc.ravel())
    h2 = Hpair - Hp                  # H(next|prev)
    rows = []
    for i in range(A):
        if row[i] == 0:
            continue
        Hcond = H_from_counts(bc[i])
        I_a = Hn - Hcond
        pa = row[i] / tot
        glyph = inv_voc.get(i, str(i))
        rows.append(dict(glyph=glyph, code=int(i), P=float(pa), I=float(I_a),
                         contrib=float(pa * I_a), H_next_given=float(Hcond),
                         count=int(row[i])))
    rows.sort(key=lambda r: -r['contrib'])
    I_total = float(sum(r['contrib'] for r in rows))
    top5 = float(sum(r['contrib'] for r in rows[:5]))
    C5 = (top5 / I_total) if I_total > 0 else 0.0
    top9 = float(sum(r['contrib'] for r in rows[:9]))
    f_top9 = (top9 / I_total) if I_total > 0 else 0.0
    alph = int((np.bincount(a, minlength=A) > 0).sum())
    return dict(h1=float(Hp), h1_next=float(Hn), h2=float(h2), I=I_total,
                C5=float(C5), f_top9=float(f_top9), top5_sum=top5, rows=rows,
                A=alph, n_pairs=int(tot))

def contrib_of_set(decomp, S):
    """Sum c(a) for glyphs in S (string match on EVA/letter labels)."""
    return float(sum(r['contrib'] for r in decomp['rows'] if r['glyph'] in S))

def c5_only(a):
    """Fast C5 without glyph names (gates)."""
    a = np.asarray(a, dtype=np.int64)
    A = int(a.max()) + 1
    bc = np.bincount(a[:-1] * A + a[1:], minlength=A * A).reshape(A, A)
    row = bc.sum(1)
    col = bc.sum(0)
    tot = float(row.sum())
    if tot <= 0:
        return 0.0
    Hn = H_from_counts(col)
    contribs = []
    for i in range(A):
        if row[i] == 0:
            continue
        Hcond = H_from_counts(bc[i])
        contribs.append((row[i] / tot) * (Hn - Hcond))
    if not contribs:
        return 0.0
    contribs.sort(reverse=True)
    I = float(sum(contribs))
    return float(sum(contribs[:5]) / I) if I > 0 else 0.0

def save(R, path=OUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(R, open(path, 'w'), indent=1, default=float)

def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    R = dict(N=N, seed=SEED, log='log2 (bits)',
             S=sorted(S_GLYPHS),
             S_note='fixed from C042 Look 3 (exploratory->confirmatory, disclosed)',
             primary_tokenization='EVA glyph units (c003.units: cth ckh cph cfh ch sh single), '
             'commas as spaces (c030.ivtff_paragraphs), one space token after every word',
             texts={}, vowelless={}, gates={}, verdicts={},
             checkpoint='start')
    save(R, CKPT)

    # ---- load corpora ----
    gens = {'Generator_base': [w for ws, _ in L.generator() for w in ws]}
    c005_note = None
    try:
        import c004_generator_sweep as G
        cfg = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'],
                   **{'text.lines_to_create': 2400})
        raw = G.generate(cfg, SEED)
        gens['Generator_C005matched'] = [w for l in (raw or []) for w in l]
    except Exception as e:
        c005_note = f'skipped: {e}'
        print('C005 generator unavailable:', e, flush=True)
    R['generator_C005_note'] = c005_note

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

    def measure(label, words, use_tok, space=True, n=N):
        a, wid, voc, _ = prep_full(words, use_tok, space, n=n)
        inv = inv_from_voc(voc)
        d = decompose(a, inv)
        out = dict(h1=d['h1'], h1_next=d['h1_next'], h2=d['h2'], I=d['I'],
                   C5=d['C5'], f_top9=d['f_top9'], A=d['A'], n=int(len(a)),
                   n_pairs=d['n_pairs'],
                   top9=[{k: r[k] for k in ('glyph', 'P', 'I', 'contrib', 'H_next_given', 'count')}
                         for r in d['rows'][:9]],
                   top5_glyphs=[r['glyph'] for r in d['rows'][:5]])
        # S-localization (meaningful for Voynich / generator EVA alphabets)
        cs = contrib_of_set(d, S_GLYPHS)
        out['contrib_S'] = cs
        out['f_S'] = (cs / d['I']) if d['I'] > 0 else 0.0
        out['h2_abl_S'] = d['h2'] + cs
        out['_decomp_rows'] = d['rows']  # kept briefly; stripped before save if huge
        print(label, {k: (round(v, 4) if isinstance(v, float) else v)
                      for k, v in out.items() if k not in ('top9', '_decomp_rows')},
              round(time.time() - t0, 1), 's', flush=True)
        return out, a, wid, voc

    # ---- 1. natural texts first (for nat_min and C5 max) ----
    R['checkpoint'] = 'natural'
    for k, w in nat.items():
        m, _, _, _ = measure(k, w, None)
        # strip heavy rows before storing
        m.pop('_decomp_rows', None)
        R['texts'][k] = m
    nat_h2 = {k: R['texts'][k]['h2'] for k in nat}
    nat_C5 = {k: R['texts'][k]['C5'] for k in nat}
    nat_min_h2 = min(nat_h2.values())
    nat_max_C5 = max(nat_C5.values())
    R['natural_range'] = dict(h2=[min(nat_h2.values()), max(nat_h2.values())],
                              C5=[min(nat_C5.values()), max(nat_C5.values())],
                              nat_min_h2=nat_min_h2, nat_max_C5=nat_max_C5)
    # leave-one-out: is any natural C5 above all other six?
    R['natural_loo_C5_above_others'] = {
        k: bool(R['texts'][k]['C5'] > max(R['texts'][j]['C5'] for j in nat if j != k))
        for k in nat
    }
    save(R, CKPT)
    print('natural_range', R['natural_range'], flush=True)

    # ---- 2. gates on Caesar BEFORE any Voynich / vowelless / generator ----
    R['checkpoint'] = 'gates'
    ca_full, cwid_full, _, _ = prep_full(nat['Latin_Caesar'], None, n=10 ** 9)
    fp = pw = 0
    c5_base_list, c5_sh_list, c5_pl_list = [], [], []
    # optional H2 size check (cheap: no bootstrap): shuffle closed vs nat_min on Caesar window
    # closed_sh = contrib_top? We use: for shuffled Caesar, D = nat_min_h2 - h2_sh;
    # "false half-localized" if D>0 and (some proxy). Skip if we stick to C5 — but try cheap:
    # For each shuffle: compute h2_sh; if h2_sh < nat_min and (nat_min - h2_sh) would need
    # contrib; without S on Latin this is N/A. Disclose skip of S-closed FPR on Latin.
    h2_closed_size_skipped = ('H2 size-check on Caesar skipped: fixed EVA set S has no '
                              'Latin-letter analogue; C5 gates remain the concentration gates. '
                              'H2 relies on C041/C042 h2 FPR/power already established.')
    for g in range(NGATE):
        s0 = int(rng.integers(0, len(ca_full) - N))
        a = ca_full[s0:s0 + N].copy()
        wid = cwid_full[s0:s0 + N].copy()
        c5_base = c5_only(a)
        c5_base_list.append(c5_base)
        sh = wshuffle(a, wid, rng)
        c5_sh = c5_only(sh)
        c5_sh_list.append(c5_sh)
        if c5_sh > c5_base:
            fp += 1
        pl = plant_copy(a, wid, rng)
        c5_pl = c5_only(pl)
        c5_pl_list.append(c5_pl)
        if c5_pl > c5_base:
            pw += 1
        if (g + 1) % 10 == 0:
            print(f'  gate {g+1}/{NGATE} fp={fp} pw={pw}', round(time.time() - t0, 1), 's', flush=True)
        # checkpoint every 10
        if (g + 1) % 10 == 0:
            R['gates'] = dict(fpr=f'{fp}/{g+1}', power=f'{pw}/{g+1}', partial=True)
            save(R, CKPT)
    gate_ok = fp <= 4 and pw >= 32
    R['gates'] = dict(
        fpr=f'{fp}/{NGATE}', power=f'{pw}/{NGATE}', ok=gate_ok,
        fpr_rule='shuffled C5 > unshuffled Caesar-window C5',
        power_rule='plant_copy C5 > unshuffled Caesar-window C5',
        mean_C5_base=float(np.mean(c5_base_list)),
        mean_C5_shuffle=float(np.mean(c5_sh_list)),
        mean_C5_plant=float(np.mean(c5_pl_list)),
        caesar_symbols=int(len(ca_full)),
        h2_closed_size_check=h2_closed_size_skipped,
    )
    print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)
    save(R, CKPT)

    # ---- 3. vowelless controls (after gates; before deciding H1 but after gates) ----
    # Spec: gates BEFORE any Voynich number. Vowelless are controls for Look 1 bar — measure now.
    R['checkpoint'] = 'vowelless'
    for lab, fname in [('Latin_Caesar_vowelless', 'pg218.txt'),
                       ('Italian_Dante_vowelless', 'pg1012.txt')]:
        words = [x for l in T.devowel(T.gutenberg(C + fname)) for x in l]
        m, _, _, _ = measure(lab, words, None)
        m.pop('_decomp_rows', None)
        R['vowelless'][lab] = m
    vow_max_C5 = max(R['vowelless'][k]['C5'] for k in R['vowelless'])
    R['vowelless_max_C5'] = vow_max_C5
    save(R, CKPT)

    # ---- 4. Voynich + generators ----
    R['checkpoint'] = 'voynich'
    for k, w in {**voy, **gens}.items():
        if len(w) < 1000:
            R['texts'][k] = dict(error='missing', n_words=len(w))
            continue
        m, _, _, _ = measure(k, w, tok.get(k))
        m.pop('_decomp_rows', None)
        # closed fraction vs nat_min
        D = nat_min_h2 - m['h2']
        m['D_vs_nat_min'] = float(D)
        m['closed'] = float(m['contrib_S'] / D) if D > 0 else None
        R['texts'][k] = m
    save(R, CKPT)

    # ---- 5. verdicts ----
    def h1_bucket(c5):
        if c5 <= nat_max_C5:
            return 'INSIDE'
        if c5 <= vow_max_C5:
            return 'VOWELLESS-LIKE'
        return 'CONCENTRATED'

    def h2_bucket(closed):
        if closed is None:
            return 'UNDEFINED (D<=0)'
        if closed >= 1.0:
            return 'GAP-CLOSED'
        if closed >= 0.5:
            return 'HALF-LOCALIZED'
        return 'DISTRIBUTED'

    z = R['texts'].get('Voynich_ZL3b', {})
    i2 = R['texts'].get('Voynich_IT2a', {})
    if not gate_ok:
        H1 = 'NOT TESTABLE'
        z_h1 = i_h1 = 'NOT TESTABLE'
    else:
        z_h1 = h1_bucket(z.get('C5', 0))
        i_h1 = h1_bucket(i2.get('C5', 0))
        if z_h1 != i_h1:
            H1 = 'SPLIT'
        else:
            H1 = z_h1

    z_h2 = h2_bucket(z.get('closed'))
    i_h2 = h2_bucket(i2.get('closed'))
    if z_h2 != i_h2:
        H2 = 'SPLIT'
    else:
        H2 = z_h2

    gen_notes = {}
    for gk in gens:
        t = R['texts'].get(gk, {})
        if 'C5' in t:
            gen_notes[gk] = dict(C5=t['C5'], h2=t['h2'], contrib_S=t.get('contrib_S'),
                                 closed=t.get('closed'), h1_bucket=h1_bucket(t['C5']),
                                 h2_bucket=h2_bucket(t.get('closed')))

    R['verdicts'] = dict(
        H1=H1, H2=H2,
        ZL_H1=z_h1 if gate_ok else 'NOT TESTABLE',
        IT2a_H1=i_h1 if gate_ok else 'NOT TESTABLE',
        ZL_H2=z_h2, IT2a_H2=i_h2,
        ZL_C5=z.get('C5'), IT2a_C5=i2.get('C5'),
        nat_max_C5=nat_max_C5, vow_max_C5=vow_max_C5,
        ZL_closed=z.get('closed'), IT2a_closed=i2.get('closed'),
        ZL_contrib_S=z.get('contrib_S'), IT2a_contrib_S=i2.get('contrib_S'),
        ZL_h2=z.get('h2'), IT2a_h2=i2.get('h2'),
        ZL_h2_abl_S=z.get('h2_abl_S'), IT2a_h2_abl_S=i2.get('h2_abl_S'),
        nat_min_h2=nat_min_h2,
        generators=gen_notes,
        gate_ok=gate_ok,
    )
    R['checkpoint'] = 'done'
    R['runtime_s'] = round(time.time() - t0, 1)
    save(R, OUT)
    # also drop partial now that final exists
    try:
        if os.path.exists(CKPT):
            os.remove(CKPT)
    except OSError:
        pass
    print(json.dumps(R['verdicts'], indent=2, default=float))
    print('runtime', R['runtime_s'])

if __name__ == '__main__':
    main()
