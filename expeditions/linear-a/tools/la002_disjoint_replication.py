#!/usr/bin/env python3
"""LA002 - KU-RO = sum, replicated on sections LA001 did not use (erasure marks re-read, fractions valued).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
Input: ins.json from lineara.xyz@9c81beb (see data/MANIFEST.md). Modes: --inventory (label-free), --run.
"""
import json, re, sys, itertools, numpy as np
from fractions import Fraction as Fr
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import la001_kuro_totals as L1

ERASED = '\U0001076b'   # lineara.xyz 'erased' marker (stripErased() in utils.js), read as a separator
VAL = {'¹⁄₂': Fr(1, 2), '¹⁄₄': Fr(1, 4), '³⁄₄': Fr(3, 4), '¹⁄₈': Fr(1, 8), '¹⁄₃': Fr(1, 3), '¹⁄₅': Fr(1, 5),
       '³⁄₈': Fr(3, 8), '⅝': Fr(5, 8)}
SENS = {'¹⁄₁₆': Fr(1, 16), '13/20': Fr(13, 20), '≈ ¹⁄₆': Fr(1, 6)}   # uncertain: sensitivity only
WORD, DIG = L1.WORD, L1.DIG
SEP = {'\n', '𐄁', '—', ERASED}

def num(t, sens):
    if DIG.match(t): return Fr(int(t))
    if t in VAL: return VAL[t]
    if sens and t in SENS: return SENS[t]
    return None

def sections(words, sens):
    out = []; start = 0; i = 0
    while i < len(words):
        w = words[i]
        if w in L1.TOTALS:
            j = i + 1
            while j < len(words) and words[j] in ('𐄁',): j += 1
            if j < len(words) and WORD.match(words[j]) and j + 1 < len(words) and num(words[j + 1], True) is not None: j += 1
            tot = []
            while j < len(words) and words[j] != '\n' and not WORD.match(words[j]):
                if words[j] in ('𐄁', ERASED): j += 1; continue
                tot.append(words[j]); j += 1
            if w == 'KU-RO':
                flags = []; entries = []; cur = None
                for t in words[start:i]:
                    if any(c in t for c in '[]?'): flags.append('damage')
                    v = num(t, sens)
                    if v is not None: cur = (cur or 0) + v
                    else:
                        if cur is not None: entries.append(cur); cur = None
                        if not (t in SEP or WORD.match(t)): flags.append('unvalued:' + t)
                if cur is not None: entries.append(cur)
                tv = [num(t, sens) for t in tot]
                if not tot: flags.append('no_total')
                elif any(v is None for v in tv): flags.append('total_unvalued')
                if any(any(c in t for c in '[]?') for t in tot): flags.append('total_damage')
                T = sum(tv) if tot and all(v is not None for v in tv) else None
                out.append(dict(entries=entries, total=T, flags=sorted(set(flags))))
            start = j; i = j; continue
        i += 1
    return out

def build(sens=False):
    ins = json.load(open('ins.json'))
    _, dec1 = L1.build(); used = {(s['doc'], s['idx']) for s in dec1}
    allsec = []
    for k in sorted(ins):
        ws = ins[k].get('transliteratedWords') or []
        if 'KU-RO' not in ws: continue
        for n, s in enumerate(sections(ws, sens)):
            s['doc'] = k; s['idx'] = n; allsec.append(s)
    dec = [s for s in allsec if (s['doc'], s['idx']) not in used and not s['flags'] and s['total'] is not None and len(s['entries']) >= 2]
    return allsec, dec, used

def strata_of(T):
    st = np.array([L1.stratum(float(t)) for t in T])
    # pre-registered merge rule: a stratum with < 2 sections joins the next lower one (or the next higher if lowest)
    for _ in range(3):
        for g in sorted(set(st)):
            if np.sum(st == g) < 2 and len(set(st)) > 1:
                others = sorted(set(st) - {g}); tgt = max([o for o in others if o < g], default=min(others))
                st[st == g] = tgt
    return st

def exact_null(S, T, st):
    groups = [list(np.where(st == g)[0]) for g in sorted(set(st))]
    dist = {}
    for combo in itertools.product(*[list(itertools.permutations(g)) for g in groups]):
        Tp = list(T)
        for g, p in zip(groups, combo):
            for a, b in zip(g, p): Tp[a] = T[b]
        e = sum(1 for a, b in zip(S, Tp) if a == b); dist[e] = dist.get(e, 0) + 1
    return dist

def pval(dist, e):
    tot = sum(dist.values()); return sum(v for k, v in dist.items() if k >= e) / tot

def main():
    sens = '--sens' in sys.argv
    allsec, dec, used = build(sens)
    if '--inventory' in sys.argv:
        inv = dict(sensitivity=sens, kuro_sections=len(allsec), used_in_LA001=len(used), decision_set=len(dec),
                   decision=[dict(doc=s['doc'], idx=s['idx'], n_entries=len(s['entries']),
                                  has_fraction=any(e.denominator > 1 for e in s['entries']) or s['total'].denominator > 1) for s in dec],
                   excluded=[dict(doc=s['doc'], idx=s['idx'], flags=s['flags'], n_entries=len(s['entries'])) for s in allsec
                             if s not in dec and (s['doc'], s['idx']) not in used])
        json.dump(inv, open('la002_inventory%s.json' % ('_sens' if sens else ''), 'w'), indent=1, ensure_ascii=False)
        print(len(allsec), len(dec), [d['doc'] for d in inv['decision']]); return
    rng = np.random.default_rng(2020)
    S = [sum(s['entries']) for s in dec]; T = [s['total'] for s in dec]; n = len(T)
    # GATES FIRST (no observed statistic used): exact p floor and planted power curve on pairing-destroyed sets
    st0 = strata_of(T); floor = pval(exact_null(S, T, st0), n) if n else 1
    curve = {}
    for k in range(1, n + 1):
        hit = 0
        for _ in range(100):
            Tn = [T[i] for i in rng.permutation(n)]; pick = rng.choice(n, k, replace=False)
            for i in pick: Tn[i] = S[i]
            e = sum(1 for a, b in zip(S, Tn) if a == b)
            hit += pval(exact_null(S, Tn, strata_of(Tn)), e) <= 0.05
        curve[k] = hit / 100
    kstar = min([k for k in curve if curve[k] >= 0.80], default=None)
    testable = kstar is not None and kstar <= n / 2
    gates = dict(n=n, exact_p_floor_all_balance=floor, power_curve=curve, k_star=kstar, testable=testable)
    print('GATES', json.dumps(gates))
    E = sum(1 for a, b in zip(S, T) if a == b); dist = exact_null(S, T, st0); p = pval(dist, E)
    verdict = 'NOT TESTABLE' if not testable else ('DETECTED' if p <= 0.05 else 'NOT DETECTED')
    res = dict(sensitivity=sens, gates=gates, exact=E, p_exact=p, null_dist=dist, verdict=verdict,
               rows=[dict(doc=s['doc'], idx=s['idx'], entries=[str(e) for e in s['entries']], sum=str(a), total=str(b), diff=str(a - b))
                     for s, a, b in zip(dec, S, T)])
    json.dump(res, open('la002_results%s.json' % ('_sens' if sens else ''), 'w'), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, default=str))

if __name__ == '__main__':
    main()
