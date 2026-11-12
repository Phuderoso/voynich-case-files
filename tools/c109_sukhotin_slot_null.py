#!/usr/bin/env python3
"""C109 (F-VC step 2: does Sukhotin alternation survive a slot-preserving null?).
C108 found Voynich within-word alternation E 0.205-0.208 against a WITHIN-WORD shuffle null, which destroys positional slots too.
Here the null N2 keeps every slot: each glyph unit is shuffled only among tokens at the SAME (word length in units, position in
word) across the half, so every word length, every per-position unit distribution and the unit multiset are kept; only the
dependence between neighbouring units inside a word is broken. Sukhotin is RE-FITTED on every shuffle.
  A as in C108; E_slot = A - mean(A_N2); p = (1 + #{A_N2 >= A}) / (1 + NSH).
Pre-registered in case-file/C109-sukhotin-slot-null.md. Seeds 11737 (main), 11738-11741 (generator); next free 11742.
Run: timeout 600 python3 tools/c109_sukhotin_slot_null.py   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate
from c108_sukhotin_alternation import encode, alt, flat, chars, halves, VOWELS, NHALF

SEED, NSH, NG, ALPHA, PLANT_Q = 11737, 200, 20, 0.05, 0.30
GSEEDS, GLINES = [11738, 11739, 11740, 11741], 3400

def slot_keys(words):
    return np.array([len(w) * 1000 + i for w in words for i in range(len(w))], dtype=np.int64)

def shuffle_slot(ids, key, rng):
    """permute ids among positions sharing the same slot key"""
    base = np.argsort(key, kind='stable'); perm = np.lexsort((rng.random(len(ids)), key))
    out = np.empty_like(ids); out[base] = ids[perm]; return out

def test(words, rng, nsh=NSH):
    ids, wid, inv = encode(words); S = len(inv); key = slot_keys(words); A, V = alt(ids, wid, S)
    null = np.array([alt(shuffle_slot(ids, key, rng), wid, S)[0] for _ in range(nsh)])
    return dict(A=round(A, 4), null_mean=round(float(null.mean()), 4), null_sd=round(float(null.std()), 4),
                E=round(A - float(null.mean()), 4), p=(1 + int((null >= A).sum())) / (1 + nsh),
                V=sorted(inv[i] for i in np.where(V)[0]), nsym=S, nslots=int(len(set(key.tolist()))))

def decode(words, sh, inv):
    out = []; pos = 0
    for w in words: out.append(tuple(inv[j] for j in sh[pos:pos + len(w)])); pos += len(w)
    return out

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    voweled = list(VOWELS); abjad = [k for k in nat if k.startswith('Hebrew') or k.endswith('_devowel')]
    R = dict(seed=SEED, NHALF=NHALF, NSH=NSH, NG=NG, alpha=ALPHA, plant_q=PLANT_Q, gseeds=GSEEDS)
    fp = pw = 0; gl = []
    for i in range(NG):
        k = voweled[i % len(voweled)]; words = chars(flat(halves(nat[k])[0]))
        ids, wid, inv = encode(words); wsh = decode(words, shuffle_slot(ids, slot_keys(words), rng), inv)
        r1 = test(wsh, rng, 100)
        keep = rng.random(len(words)) < PLANT_Q; wpl = [w if kk else s for w, s, kk in zip(words, wsh, keep)]
        r2 = test(wpl, rng, 100)
        fp += r1['p'] < ALPHA; pw += r2['p'] < ALPHA; gl.append(dict(text=k, fpr_p=r1['p'], plant_p=r2['p'], plant_E=r2['E']))
        print('gate', i, k, fp, pw, r2['E'], round(time.time() - t0, 1), flush=True)
    G = dict(G1_fpr=f'{fp}/{NG}', G2_power=f'{pw}/{NG}', ok=bool(fp <= 2 and pw >= 16), detail=gl)
    out = {}
    for k in nat:
        out[k] = [test(chars(flat(L)), rng) for L in halves(nat[k])]
        print(k, [(y['E'], y['p'], ''.join(y['V'])) for y in out[k]], round(time.time() - t0, 1), flush=True)
    nv = [y['E'] for k in voweled for y in out[k]]; na = [y['E'] for k in abjad for y in out[k]]
    G['G4_separation'] = dict(voweled=[min(nv), max(nv)], abjad=[min(na), max(na)], ok=bool(min(nv) > max(na) or max(nv) < min(na)))
    R['gates'] = G; print({k: v for k, v in G.items() if k != 'detail'}, flush=True)
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, lang, _ = ivtff_pages_lang(f); lines = [l for p, l in pl]
        out[k] = [test([tuple(T.units(w)) for w in flat(L)], rng) for L in halves(lines)]
        print(k, [(y['E'], y['p'], y['V']) for y in out[k]], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s); n = sum(map(len, L)) if L else 0
        if not L or n < 2 * NHALF: gen[s] = dict(ok=False, n=n); continue
        gen[s] = dict(ok=True, n=n, halves=[test([tuple(T.units(w)) for w in flat(H)], rng) for H in halves(L)])
        print('gen', s, [(y['E'], y['p'], y['V']) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
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
        V = dict(H1='RESIDUAL' if all(sg) else 'NO RESIDUAL' if not any(sg) else 'SPLIT')
        if G['G4_separation']['ok']:
            V['H2'], V['voweled_range'] = place(vv, nv); V['H3'], V['abjad_range'] = place(vv, na)
        else: V['H2'] = V['H3'] = 'NOT SEPARABLE'
        V['H4'], V['generator_range'] = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
    c108 = json.load(open('analysis/C108_results.json'))
    V['voynich_E_slot'] = vv; V['voynich_E_C108'] = [y['E'] for k in ('ZL3b', 'IT2a') for y in c108['texts'][k]]
    V['slot_share_of_C108_E'] = [round(1 - a / b, 3) for a, b in zip(vv, V['voynich_E_C108'])]
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C109_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke':
        rng = np.random.default_rng(1); nat = B.nat_texts(); w = chars(flat(halves(nat['Latin_Caesar'])[0]))
        ids, wid, inv = encode(w); key = slot_keys(w); sh = shuffle_slot(ids, key, rng)
        d = decode(w, sh, inv); assert [len(x) for x in d] == [len(x) for x in w]
        for L_ in (3, 5):
            for i in range(L_):
                a = sorted(x[i] for x in w if len(x) == L_); b = sorted(x[i] for x in d if len(x) == L_); assert a == b
        print('smoke ok: slots kept', test(w, rng, 20))
    else: main()
