#!/usr/bin/env python3
"""C108 (NEW FAMILY F-VC, step 1: vowel/consonant alternation, Sukhotin's algorithm).
Sukhotin's algorithm (B. V. Sukhotin 1962; English description J. B. M. Guy, Cryptologia 15(3), 1991, who also applied it to
Voynich f79v/f80r) splits a script's symbols into two classes so that the classes alternate as much as possible.
Statistic per text half (N = 15,000 tokens; contacts = adjacent glyph units INSIDE a word, both orders, diagonal excluded):
  A = share of within-word adjacent non-identical unit pairs whose two units fall in different Sukhotin classes.
  Null N1: units shuffled within every word (word length and unit multiset kept), Sukhotin RE-FITTED on each shuffle;
  E = A - mean(A_null); p = (1 + #{A_null >= A}) / (1 + NSH).
Pre-registered in case-file/C108-sukhotin-alternation.md. Seeds 11732 (main), 11733-11736 (generator); next free 11737.
Run: timeout 600 python3 tools/c108_sukhotin_alternation.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c049_context_spelling as E
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, NSH, NG, ALPHA = 11732, 15000, 200, 20, 0.05
GSEEDS, GLINES = [11733, 11734, 11735, 11736], 3400
PLANT_Q = 0.30          # power plant: share of words whose true order is restored inside a within-word-shuffled text
VOWELS = {'Latin_Caesar': 'aeiouy', 'Latin_Descartes': 'aeiouy', 'Italian_Dante': 'aeiou', 'Italian_Machiavelli': 'aeiou',
          'Spanish_Cervantes': 'aeiou', 'Finnish_Kalevala': 'aeiouy', 'Finnish_Kivi': 'aeiouy'}

def encode(words):
    """words: list of tuples of units -> (ids int array, wid int array, symbols list)"""
    sym = {}; ids = []; wid = []
    for k, w in enumerate(words):
        for u in w: ids.append(sym.setdefault(u, len(sym))); wid.append(k)
    inv = [None] * len(sym)
    for u, i in sym.items(): inv[i] = u
    return np.array(ids, dtype=np.int64), np.array(wid, dtype=np.int64), inv

def contacts(ids, wid, S):
    same = wid[1:] == wid[:-1]; a, b = ids[:-1][same], ids[1:][same]; keep = a != b; a, b = a[keep], b[keep]
    M = np.zeros((S, S)); np.add.at(M, (a, b), 1); M = M + M.T
    return M, a, b

def sukhotin(M):
    S = M.shape[0]; r = M.sum(1).astype(float); V = np.zeros(S, bool)
    while True:
        c = np.where(~V, r, -np.inf); v = int(np.argmax(c))
        if not np.isfinite(c[v]) or c[v] <= 0: break
        V[v] = True; r = r - 2 * M[:, v]
    return V

def alt(ids, wid, S):
    M, a, b = contacts(ids, wid, S); V = sukhotin(M)
    return (float(np.mean(V[a] != V[b])) if len(a) else np.nan), V

def shuffle_within(ids, wid, rng):
    order = np.lexsort((rng.random(len(ids)), wid)); return ids[order]

def test(words, rng, nsh=NSH):
    ids, wid, inv = encode(words); S = len(inv); A, V = alt(ids, wid, S)
    null = np.array([alt(shuffle_within(ids, wid, rng), wid, S)[0] for _ in range(nsh)])
    return dict(A=round(A, 4), null_mean=round(float(null.mean()), 4), null_sd=round(float(null.std()), 4),
                E=round(A - float(null.mean()), 4), p=(1 + int((null >= A).sum())) / (1 + nsh),
                V=sorted(inv[i] for i in np.where(V)[0]), nsym=S, npairs=int(contacts(ids, wid, S)[1].size))

def flat(lines): return [w for l in lines for w in l]
def chars(words): return [tuple(w) for w in words]
def halves(lines):
    n = sum(map(len, lines)); hs = (0, 1) if n >= 2 * NHALF else (0,)
    return [E.take(lines, h * NHALF, NHALF) for h in hs]

def token_acc(V, inv_vset, words, vowels):
    """share of letter tokens whose Sukhotin class matches the true vowel class (G3 tool check)"""
    s = set(inv_vset); tot = ok = 0
    for w in words:
        for u in w: tot += 1; ok += ((u in s) == (u in vowels))
    return ok / tot

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    voweled = [k for k in VOWELS]; abjad = [k for k in nat if k.startswith('Hebrew') or k.endswith('_devowel')]
    R = dict(seed=SEED, NHALF=NHALF, NSH=NSH, NG=NG, alpha=ALPHA, plant_q=PLANT_Q, gseeds=GSEEDS)
    # G1 FPR (null true: within-word-shuffled natural text, tested against a fresh shuffle null) and G2 power (plant)
    fp = pw = 0; gl = []
    for i in range(NG):
        k = voweled[i % len(voweled)]; L = halves(nat[k])[0]; words = chars(flat(L))
        ids, wid, inv = encode(words); sh = shuffle_within(ids, wid, rng)
        wsh = []; pos = 0
        for w in words: wsh.append(tuple(inv[j] for j in sh[pos:pos + len(w)])); pos += len(w)
        r1 = test(wsh, rng, 100)
        keep = rng.random(len(words)) < PLANT_Q; wpl = [w if kk else s for w, s, kk in zip(words, wsh, keep)]
        r2 = test(wpl, rng, 100)
        fp += r1['p'] < ALPHA; pw += r2['p'] < ALPHA; gl.append(dict(text=k, fpr_p=r1['p'], plant_p=r2['p'], plant_E=r2['E']))
        print('gate', i, k, fp, pw, r2['E'], round(time.time() - t0, 1), flush=True)
    G = dict(G1_fpr=f'{fp}/{NG}', G2_power=f'{pw}/{NG}', ok=bool(fp <= 2 and pw >= 16), detail=gl)
    out = {}; acc = {}
    for k in nat:
        out[k] = []
        for L in halves(nat[k]):
            w = chars(flat(L)); r = test(w, rng); out[k].append(r)
            if k in VOWELS: acc.setdefault(k, []).append(round(token_acc(None, r['V'], w, VOWELS[k]), 4))
        print(k, [(y['E'], y['p'], ''.join(y['V'])) for y in out[k]], acc.get(k), round(time.time() - t0, 1), flush=True)
    G['G3_token_accuracy'] = acc; G['G3_ok'] = bool(all(a >= 0.80 for v in acc.values() for a in v))
    nv = [y['E'] for k in voweled for y in out[k]]; na = [y['E'] for k in abjad for y in out[k]]
    G['G4_separation'] = dict(voweled=[min(nv), max(nv)], abjad=[min(na), max(na)], ok=bool(min(nv) > max(na) or max(nv) < min(na)))
    R['gates'] = G; print({k: v for k, v in G.items() if k != 'detail'}, flush=True)
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, lang, _ = ivtff_pages_lang(f); lines = [l for p, l in pl]
        out[k] = []; out[k + '_raw'] = []
        for L in halves(lines):
            out[k].append(test([tuple(T.units(w)) for w in flat(L)], rng))
            out[k + '_raw'].append(test(chars(flat(L)), rng))      # descriptive: raw EVA characters
        print(k, [(y['E'], y['p'], y['V']) for y in out[k]], 'raw', [(y['E'], y['V']) for y in out[k + '_raw']], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s); n = sum(map(len, L)) if L else 0
        if not L or n < 2 * NHALF: gen[s] = dict(ok=False, n=n); continue
        gen[s] = dict(ok=True, n=n, halves=[test([tuple(T.units(w)) for w in flat(H)], rng) for H in halves(L)])
        print('gen', s, [(y['E'], y['V']) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]; vv = [y['E'] for y in vo]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    genv = [y['E'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves']]
    if not G['ok']: V = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE', H4='NOT TESTABLE')
    else:
        sg = [y['p'] < ALPHA / 4 for y in vo]
        V = dict(H1='EXCESS' if all(sg) else 'NO EXCESS' if not any(sg) else 'SPLIT')
        if G['G4_separation']['ok']:
            V['H2'], V['voweled_range'] = place(vv, nv); V['H3'], V['abjad_range'] = place(vv, na)
        else: V['H2'] = V['H3'] = 'NOT SEPARABLE'
        V['H4'], V['generator_range'] = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
        V['G3_tool_valid'] = G['G3_ok']
    V['voynich_E'] = vv; R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C108_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__': main()
