#!/usr/bin/env python3
"""C038 (F-MI step 2): does long-range word recurrence L survive inside a single
IVTFF illustration section ($I = H, S, B), so cross-section topic shifts cannot
explain C037's whole-text L?
Pre-registered in case-file/C038-within-section-recurrence.md. Seed 3838.
Run: timeout 600 python3 tools/c038_within_section_recurrence.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, re
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c037_long_range_recurrence import ids, p0, cprof, SL, perm_p, jack, planted

SEED, NPERM, NGATE, GPERM = 3838, 1000, 40, 200
ALPHA = 0.05 / 3  # ≈ 0.0167
C = 'data/corpora/'
PAGE_RE = re.compile(r'^<(f\w+)>\s+<!.*\$I=([A-Za-z])')
LINE_RE = re.compile(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)')


def section_streams(path):
    """Collect paragraph words per page, then concatenate pages of one $I in folio order.
    Returns dict $I -> word list, and whole-text word list in folio order."""
    sec = defaultdict(list)
    whole = []
    cur_I = None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = PAGE_RE.match(line)
        if m:
            cur_I = m.group(2)
            continue
        m = LINE_RE.match(line.rstrip('\n'))
        if not m or cur_I is None:
            continue
        if not m.group(3).startswith('P'):
            continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t)
        t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        if len(ws) < 3 or not all(re.fullmatch(r'[a-z]+', w) for w in ws):
            continue
        sec[cur_I].extend(ws)
        whole.extend(ws)
    return dict(sec), whole


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    sec, whole = section_streams('data/ZL3b-n.txt')
    lens = {k: len(sec.get(k, [])) for k in ('H', 'S', 'B')}
    for k in ('H', 'S', 'B'):
        if lens[k] < 5500:
            raise SystemExit(f'section {k} too short: {lens[k]}')
    N = min(8000, min(lens[k] for k in ('H', 'S', 'B')))
    print('section lengths', lens, 'N', N, flush=True)

    # optional IT2a
    it2a_sec, it2a_whole = section_streams('data/IT2a-n.txt')
    it2a_has_I = any(len(it2a_sec.get(k, [])) >= N for k in ('H', 'S', 'B'))

    naturals = {
        'Latin_Caesar': [w for l in T.gutenberg(C + 'pg218.txt') for w in l],
        'Latin_Descartes': [w for l in T.gutenberg(C + 'pg23306.txt') for w in l],
        'Italian_Dante': [w for l in T.gutenberg(C + 'pg1012.txt') for w in l],
        'Italian_Machiavelli': [w for l in T.gutenberg(C + 'pg56498.txt') for w in l],
        'Spanish_Cervantes': [w for l in T.gutenberg(C + 'pg2000.txt') for w in l],
        'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l],
        'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l],
    }

    R = dict(N=N, short=[1, 10], long=[50, 500], nperm=NPERM, alpha=ALPHA, seed=SEED,
             section_lengths=lens, it2a_has_I=it2a_has_I, texts={}, sections={})

    # whole ZL at N
    a_whole = ids(whole[:N])
    S_w, L_w = SL(a_whole)
    obs_w, p_w, nm_w, ns_w = perm_p(a_whole, rng, NPERM)
    se_w = jack(a_whole)
    R['texts']['Voynich_ZL3b_whole'] = dict(
        n_total=len(whole), S=S_w, L=L_w, p_L=p_w, null_mean=nm_w, null_sd=ns_w,
        z=(L_w - nm_w) / ns_w if ns_w else None,
        jack_se_S=se_w[0], jack_se_L=se_w[1], types=int(a_whole.max() + 1))
    print('whole ZL', round(S_w, 3), round(L_w, 4), p_w, round(time.time() - t0), flush=True)

    # sections H, S, B
    sec_arr = {}
    for k in ('H', 'S', 'B'):
        a = ids(sec[k][:N])
        sec_arr[k] = a
        S, Lg = SL(a)
        obs, p, nm, ns = perm_p(a, rng, NPERM)
        se = jack(a)
        R['sections'][k] = dict(
            n_total=lens[k], S=S, L=Lg, p_L=p, null_mean=nm, null_sd=ns,
            z=(Lg - nm) / ns if ns else None,
            jack_se_S=se[0], jack_se_L=se[1], types=int(a.max() + 1))
        print('section', k, round(S, 3), round(Lg, 4), p, round(time.time() - t0), flush=True)

    # naturals
    for name, ws in naturals.items():
        if len(ws) < N:
            R['texts'][name] = dict(n=len(ws), error='too short')
            print(name, 'too short', len(ws), flush=True)
            continue
        a = ids(ws[:N])
        S, Lg = SL(a)
        obs, p, nm, ns = perm_p(a, rng, NPERM)
        se = jack(a)
        R['texts'][name] = dict(
            n_total=len(ws), S=S, L=Lg, p_L=p, null_mean=nm, null_sd=ns,
            z=(Lg - nm) / ns if ns else None,
            jack_se_S=se[0], jack_se_L=se[1], types=int(a.max() + 1))
        print(name, round(S, 3), round(Lg, 4), p, round(time.time() - t0), flush=True)

    # optional IT2a sections (descriptive)
    R['it2a_sections'] = {}
    if it2a_has_I:
        for k in ('H', 'S', 'B'):
            ws = it2a_sec.get(k, [])
            if len(ws) < N:
                R['it2a_sections'][k] = dict(n_total=len(ws), error='too short')
                continue
            a = ids(ws[:N])
            S, Lg = SL(a)
            se = jack(a)
            R['it2a_sections'][k] = dict(
                n_total=len(ws), S=S, L=Lg, jack_se_S=se[0], jack_se_L=se[1],
                types=int(a.max() + 1), note='descriptive only; no H1 p-value')
            print('IT2a', k, round(S, 3), round(Lg, 4), round(time.time() - t0), flush=True)
    else:
        R['it2a_note'] = 'IT2a lacks usable $I section streams at N; ZL only for H1'

    # H3 cross-section stream
    n3 = N // 3
    cross_words = sec['H'][:n3] + sec['S'][:n3] + sec['B'][:n3]
    # pad/truncate to N if N not divisible by 3
    if len(cross_words) < N:
        # top up from remaining H tokens after the prefix (still H-only filler disclosed)
        need = N - len(cross_words)
        cross_words = cross_words + sec['H'][n3:n3 + need]
    cross_words = cross_words[:N]
    a_cross = ids(cross_words)
    S_c, L_c = SL(a_cross)
    se_c = jack(a_cross)
    mean_within_L = float(np.mean([R['sections'][k]['L'] for k in ('H', 'S', 'B')]))
    R['H3'] = dict(
        n3=n3, N=N, seams=['H|S at %d' % n3, 'S|B at %d' % (2 * n3)],
        cross_S=S_c, cross_L=L_c, cross_jack_se_L=se_c[1],
        mean_within_L=mean_within_L,
        within_Ls={k: R['sections'][k]['L'] for k in ('H', 'S', 'B')},
        note='cross stream = H[:n3]+S[:n3]+B[:n3] (+ H filler to N if needed); descriptive only')
    print('H3 cross L', round(L_c, 4), 'mean within', round(mean_within_L, 4), flush=True)

    # Gates on H
    h = sec_arr['H']
    fp = pw = 0
    for g in range(NGATE):
        if perm_p(rng.permutation(h), rng, GPERM)[1] <= ALPHA:
            fp += 1
        if perm_p(planted(h, rng), rng, GPERM)[1] <= ALPHA:
            pw += 1
        if (g + 1) % 10 == 0:
            print('gate', g + 1, 'fp', fp, 'pw', pw, round(time.time() - t0), flush=True)
    gate_ok = fp <= 4 and pw >= 36

    nat_keys = [k for k in R['texts'] if k.startswith(('Latin', 'Italian', 'Spanish', 'Hebrew')) and 'L' in R['texts'][k]]
    nat_pos = sum(R['texts'][k]['p_L'] <= ALPHA for k in nat_keys)
    rngL = [min(R['texts'][k]['L'] for k in nat_keys), max(R['texts'][k]['L'] for k in nat_keys)]
    rngS = [min(R['texts'][k]['S'] for k in nat_keys), max(R['texts'][k]['S'] for k in nat_keys)]

    def pos(x, r):
        return 'inside' if r[0] <= x <= r[1] else ('above' if x > r[1] else 'below')

    # H1 / H2 verdicts
    V = {}
    for k in ('H', 'S', 'B'):
        t = R['sections'][k]
        if not gate_ok:
            h1 = 'not testable (gates)'
        elif t['p_L'] <= ALPHA:
            h1 = 'WITHIN-SECTION LONG-RANGE RECURRENCE'
        else:
            h1 = 'NO DETECTED WITHIN-SECTION LONG-RANGE RECURRENCE'
        within_2se = abs(t['L'] - L_w) <= 2 * np.hypot(t['jack_se_L'], se_w[1])
        V[k] = dict(
            H1=h1,
            L_vs_natural=pos(t['L'], rngL),
            S_vs_natural=pos(t['S'], rngS),
            L_vs_whole=pos(t['L'], [L_w, L_w]),  # placeholder; also numeric below
            L_minus_whole=t['L'] - L_w,
            within_2jackSE_of_whole_L=bool(within_2se))
        # cleaner L_vs_whole label
        if abs(t['L'] - L_w) <= 2 * np.hypot(t['jack_se_L'], se_w[1]):
            V[k]['L_vs_whole'] = 'within_2SE'
        elif t['L'] > L_w:
            V[k]['L_vs_whole'] = 'above_whole'
        else:
            V[k]['L_vs_whole'] = 'below_whole'

    R.update(
        gates=dict(fpr=f'{fp}/{NGATE}', power=f'{pw}/{NGATE}',
                   natural_positive=f'{nat_pos}/{len(nat_keys)}', ok=gate_ok, alpha=ALPHA),
        natural_range=dict(S=rngS, L=rngL),
        verdicts=V,
        runtime_s=round(time.time() - t0))
    os.makedirs('analysis', exist_ok=True)
    json.dump(R, open('analysis/C038_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['gates']), json.dumps(V, default=str))
    print('runtime', R['runtime_s'], flush=True)


if __name__ == '__main__':
    main()
