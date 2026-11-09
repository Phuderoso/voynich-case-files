#!/usr/bin/env python3
"""LA001 - calibrated KU-RO totals (Linear A expedition).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.

Input: ins.json, a JSON dump of mwenge/lineara.xyz LinearAInscriptions.js at commit 9c81beb
(sha256 of the .js: 9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e), made with
  node -e 'eval(fs.readFileSync("LinearAInscriptions.js","utf8")+";global.I=inscriptions");...'
Modes:  --inventory  label-free decision-set inventory (no sum is compared with any total)
        --run        pre-registered tests H1, H2 with gates
"""
import json, re, sys, numpy as np

SEED = 1001
WORD = re.compile(r'^[A-Z*][A-Z0-9*₂₃+\-]*')
DIG = re.compile(r'^\d+$')
SEP = {'\n', '𐄁', '—'}  # '—' (blank/filler in lineara.xyz) treated as a separator, declared
TOTALS = {'KU-RO', 'KI-RO'}

def sections(words):
    """Yield (entries, total, flags) for each KU-RO in a document side.
    entries = list of integer entries (each entry = sum of consecutive integer numerals after a word);
    section = tokens after the previous KU-RO/KI-RO total (or document start) up to this KU-RO."""
    out = []; start = 0
    i = 0
    while i < len(words):
        w = words[i]
        if w in TOTALS:
            # total = tokens after w until newline or next word
            j = i + 1; tot = []; bad_tot = False
            while j < len(words) and words[j] == '𐄁': j += 1
            if j < len(words) and WORD.match(words[j]) and j + 1 < len(words) and DIG.match(words[j + 1]):
                j += 1  # one commodity logogram between KU-RO and its number (KU-RO GRA 100)
            while j < len(words) and words[j] != '\n' and not WORD.match(words[j]):
                if words[j] == '𐄁': j += 1; continue
                tot.append(words[j]); j += 1
            if w == 'KU-RO':
                sec = words[start:i]
                flags = []
                entries = []; cur = None
                for t in sec:
                    if any(c in t for c in '[]?'): flags.append('damage')
                    if DIG.match(t):
                        cur = (cur or 0) + int(t)
                    else:
                        if cur is not None: entries.append(cur); cur = None
                        if t in SEP or WORD.match(t):
                            pass
                        else:
                            flags.append('nonint:' + t)
                if cur is not None: entries.append(cur)
                if not tot: flags.append('no_total')
                elif not all(DIG.match(t) for t in tot): flags.append('total_nonint')
                if any(any(c in t for c in '[]?') for t in tot): flags.append('total_damage')
                T = sum(int(t) for t in tot) if tot and all(DIG.match(t) for t in tot) else None
                out.append(dict(entries=entries, total=T, flags=sorted(set(flags)), total_tokens=tot))
            start = j; i = j; continue
        i += 1
    return out

def build(path='ins.json'):
    ins = json.load(open(path))
    allsec = []
    for k in sorted(ins):
        ws = ins[k].get('transliteratedWords') or []
        if 'KU-RO' not in ws: continue
        for n, s in enumerate(sections(ws)):
            s['doc'] = k; s['idx'] = n; allsec.append(s)
    dec = [s for s in allsec if not s['flags'] and s['total'] is not None and len(s['entries']) >= 2]
    return allsec, dec

def stratum(T):
    return 0 if T < 10 else (1 if T < 100 else 2)

def stats(S, T):
    d = S - T
    E = int(np.sum(d == 0))
    sh = np.mean([np.sum(d == k) for k in (-5,-4,-3,-2,-1,1,2,3,4,5)])
    return E, E - sh

def perm_test(S, T, strata, rng, B):
    E0, C0 = stats(S, T)
    geE = 1; geC = 1
    idx = [np.where(strata == s)[0] for s in np.unique(strata)]
    for _ in range(B):
        Tp = T.copy()
        for ix in idx: Tp[ix] = T[rng.permutation(ix)]
        e, c = stats(S, Tp)
        geE += e >= E0; geC += c >= C0
    return E0, C0, geE / (B + 1), geC / (B + 1)

def holm(ps, a=0.05):
    o = np.argsort(ps); rej = [False]*len(ps)
    for r, i in enumerate(o):
        if ps[i] <= a / (len(ps) - r): rej[i] = True
        else: break
    return rej

def main():
    allsec, dec = build()
    if '--inventory' in sys.argv:
        inv = dict(source='mwenge/lineara.xyz@9c81beb LinearAInscriptions.js',
                   js_sha256='9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e',
                   kuro_sections=len(allsec), decision_set=len(dec),
                   excluded=[dict(doc=s['doc'], idx=s['idx'], flags=s['flags'], n_entries=len(s['entries'])) for s in allsec if s not in dec],
                   decision=[dict(doc=s['doc'], idx=s['idx'], n_entries=len(s['entries']), total_stratum=stratum(s['total'])) for s in dec])
        json.dump(inv, open('la001_inventory.json', 'w'), indent=1, ensure_ascii=False)
        print(len(allsec), len(dec)); return
    rng = np.random.default_rng(SEED)
    S = np.array([sum(s['entries']) for s in dec]); T = np.array([s['total'] for s in dec])
    st = np.array([stratum(t) for t in T]); n = len(T)
    # FPR gate: totals globally permuted (pairing destroyed), 200 datasets, inner B=2000
    fpr = [0, 0]
    for _ in range(200):
        Tn = T[rng.permutation(n)]
        _, _, pe, pc = perm_test(S, Tn, np.array([stratum(t) for t in Tn]), rng, 2000)
        fpr[0] += pe <= 0.05; fpr[1] += pc <= 0.05
    # power gate: on round(0.25 n) random tablets of a pairing-destroyed set, set total := sum
    pw = [0, 0]; k = int(round(0.25 * n))
    for _ in range(200):
        Tn = T[rng.permutation(n)].copy()
        pick = rng.choice(n, k, replace=False); Tn[pick] = S[pick]
        _, _, pe, pc = perm_test(S, Tn, np.array([stratum(t) for t in Tn]), rng, 2000)
        pw[0] += pe <= 0.05; pw[1] += pc <= 0.05
    E, C, pE, pC = perm_test(S, T, st, rng, 20000)
    gates_ok = [fpr[i] / 200 <= 0.08 and pw[i] / 200 >= 0.80 for i in range(2)]
    rej = holm([pE, pC])
    verdict = []
    for i in range(2):
        verdict.append('NOT TESTABLE' if not gates_ok[i] else ('DETECTED' if rej[i] else 'NOT DETECTED'))
    d = (S - T).tolist()
    res = dict(n=n, plant_k=k, exact=E, contrast=C, p_H1=pE, p_H2=pC, fpr=[f/200 for f in fpr], power=[p/200 for p in pw],
               holm_reject=rej, verdict=dict(H1=verdict[0], H2=verdict[1]),
               rows=[dict(doc=s['doc'], idx=s['idx'], entries=s['entries'], sum=int(a), total=int(b), diff=int(a-b)) for s, a, b in zip(dec, S, T)],
               diff_hist={str(x): d.count(x) for x in sorted(set(d))})
    json.dump(res, open('la001_results.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k not in ('rows',)}, indent=1))

if __name__ == '__main__':
    main()
