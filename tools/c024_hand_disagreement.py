"""C024 (new family F-TRX, transcription reliability). Do two independent transcriptions (ZL 3b vs Takahashi IT2a)
disagree more on some scribes' pages than on others? A hand whose glyphs are harder to read would show a higher
glyph-level disagreement rate.
Unit = page; rate = sum over lines present in both files of Levenshtein(ZL line, IT line) / sum max(len) (word
separators and uncertain spaces removed, ZL alternatives -> first reading, extended glyph codes -> '?').
Statistic G = sum over strata s, hands h of L_sh * (rate_sh - rate_s)^2 (pooled rates, L = compared glyphs).
Look R (raw): one stratum (all pages with a hand label 1-5), null = hand labels permuted over all pages.
Look W (within): strata = Currier language x illustration type; only strata with >= 2 hands; null = hand labels
permuted within stratum. 4000 draws, one-sided, alpha = 0.025 per look.
Gates: FPR at alpha <= 0.075 on 40 destroyed data sets (page (E,L) records shuffled across the look's permutation
units); power >= 0.8 on 40 planted data sets (destroyed data, then hand-5 pages get extra edits = 0.01 * L, i.e. +1
percentage point, about half the overall rate). Failing a gate = not testable.
"""
import sys, os, json, random, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c024_common as C
SEED = 24024; ALPHA = 0.025; NPERM = 4000; NCAL = 40; DELTA = 0.01

def G(rec, strata):
    g = 0.0
    for pages in strata:
        E = sum(rec[p][0] for p in pages); L = sum(rec[p][1] for p in pages); rs = E / L
        byh = defaultdict(lambda: [0, 0])
        for p in pages: byh[rec[p][2]][0] += rec[p][0]; byh[rec[p][2]][1] += rec[p][1]
        g += sum(l * (e / l - rs) ** 2 for e, l in byh.values())
    return g

def permute(rec, strata, rng):
    out = dict(rec)
    for pages in strata:
        hs = [rec[p][2] for p in pages]; rng.shuffle(hs)
        for p, h in zip(pages, hs): out[p] = (rec[p][0], rec[p][1], h)
    return out

def destroy(rec, strata, rng):  # shuffle the (E, L) records across pages, hands stay on pages
    out = dict(rec)
    for pages in strata:
        el = [rec[p][:2] for p in pages]; rng.shuffle(el)
        for p, x in zip(pages, el): out[p] = (x[0], x[1], rec[p][2])
    return out

def plant(rec, rng):
    return {p: (e + int(round(DELTA * l)) if h == '5' else e, l, h) for p, (e, l, h) in rec.items()}

def test(rec, strata, rng, nperm=NPERM):
    obs = G(rec, strata); null = [G(permute(rec, strata, rng), strata) for _ in range(nperm)]
    return obs, (1 + sum(x >= obs for x in null)) / (1 + nperm)

def main():
    t0 = time.time(); rng = random.Random(SEED)
    meta, pr = C.page_rates()
    rec = {p: (e, l, meta[p].get('H')) for p, (e, l, n) in pr.items() if meta[p].get('H') in list('12345') and l > 0}
    sR = [sorted(rec)]
    byst = defaultdict(list)
    for p in rec: byst[(meta[p].get('L'), meta[p].get('I'))].append(p)
    sW = [sorted(v) for v in byst.values() if len({rec[p][2] for p in v}) >= 2]
    R = {'n_pages': len(rec), 'overall_rate': sum(v[0] for v in rec.values()) / sum(v[1] for v in rec.values()),
         'rate_by_hand': {h: sum(v[0] for v in rec.values() if v[2] == h) / sum(v[1] for v in rec.values() if v[2] == h) for h in '12345'},
         'W_strata': {str((meta[v[0]].get('L'), meta[v[0]].get('I'))): {h: sum(rec[p][2] == h for p in v) for h in '12345' if any(rec[p][2] == h for p in v)} for v in sW}}
    for look, strata in (('R', sR), ('W', sW)):
        fp = [test(destroy(rec, strata, rng), strata, rng, 500)[1] for _ in range(NCAL)]
        pw = [test(plant(destroy(rec, strata, rng), rng), strata, rng, 500)[1] for _ in range(NCAL)]
        fpr = float(np.mean(np.array(fp) <= ALPHA)); power = float(np.mean(np.array(pw) <= ALPHA))
        obs, p = test(rec, strata, rng); ok = fpr <= 0.075 and power >= 0.8
        R[look] = {'n_pages': sum(len(s) for s in strata), 'G_obs': obs, 'p': p, 'fpr_at_alpha': fpr, 'power_+1pp_hand5': power,
                   'verdict': 'not testable' if not ok else ('detected' if p <= ALPHA else 'not detected')}
        print(look, R[look], round(time.time() - t0, 1), 's', flush=True)
    R['seconds'] = round(time.time() - t0, 1); json.dump(R, open('analysis/C024_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
