"""C028 (F-LEN step 2, repair of C027): is a Voynich sample of K word types more binomial in length than
equal-sized samples of natural-language controls? Pre-registered in case-file/C028-word-length-binomial-repaired.md.
Seed 28028. Run: timeout 600 python3 tools/c028_word_length_binomial_repaired.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, random, time
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c027_word_length_binomial import fixed, tv_binom, p_closer, holm

SEED = 28028; W = 10000; K = 1000; D = 2000; ALPHA = 0.05
C = 'data/corpora/'

def samples(words, lenof, rng, nd=D):
    out = []; n = len(words)
    for _ in range(nd):
        s = rng.randrange(n - W) if n > W else 0
        types = sorted(set(words[s:s + W]))
        pick = rng.sample(types, K) if len(types) >= K else types
        out.append(tv_binom([lenof[w] for w in pick])[0])
    return out

def main():
    t0 = time.time(); rng = random.Random(SEED)
    corp = {'Voynich_ZL3b': (T.voynich(fixed('data/ZL3b-n.txt')), T.units),
            'Latin_Caesar': (T.gutenberg(C + 'pg218.txt'), None), 'Latin_Descartes': (T.gutenberg(C + 'pg23306.txt'), None),
            'Italian_Dante': (T.gutenberg(C + 'pg1012.txt'), None), 'Italian_Machiavelli': (T.gutenberg(C + 'pg56498.txt'), None),
            'Spanish_Cervantes': (T.gutenberg(C + 'pg2000.txt'), None),
            'Hebrew_Genesis': (T.hebrew(C + 'Gen.xml'), None), 'Hebrew_Exodus': (T.hebrew(C + 'Exod.xml'), None),
            'Generator_TimmSchinner': ([l for l in ([re.findall(r'[a-z]+', x) for x in open(C + 'ts_generated_text.txt') if not x.startswith('#')]) if l], T.units)}
    words, lenof, R = {}, {}, {'K_types': K, 'window_tokens': W, 'draws': D, 'seed': SEED}
    for k, (lines, tok) in corp.items():
        ws = [w for l in lines for w in l]; words[k] = ws
        lenof[k] = {w: (len(tok(w)) if tok else len(w)) for w in set(ws)}
    tv = {}
    for k in corp:
        tv[k] = samples(words[k], lenof[k], rng); st = sorted(tv[k])
        R[k] = {'tokens': len(words[k]), 'types': len(lenof[k]), 'tv_mean': sum(st) / D,
                'tv_2.5': st[int(.025 * D)], 'tv_97.5': st[int(.975 * D) - 1]}
        print(k, R[k], round(time.time() - t0), flush=True)
    nat = [k for k in corp if k not in ('Voynich_ZL3b', 'Generator_TimmSchinner')]
    a7 = ALPHA / len(nat)
    # calibration: half vs half of each control
    cal = {}
    for k in nat:
        h = len(words[k]) // 2; A, Bh = words[k][:h], words[k][h:]
        ta, tb = samples(A, lenof[k], rng), samples(Bh, lenof[k], rng)
        cal[k] = {'A_vs_B': p_closer(ta, tb), 'B_vs_A': p_closer(tb, ta)}
    fp = sum(p < a7 for d in cal.values() for p in d.values())
    # power: planted binomial lengths in each control's own stream
    pw = {}
    for k in nat:
        typ = list(lenof[k]); _, N = tv_binom([lenof[k][w] for w in typ]); p = (sum(lenof[k][w] for w in typ) / len(typ) - 1) / N
        P = {w: 1 + sum(rng.random() < p for _ in range(N)) for w in typ}
        pw[k] = p_closer(samples(words[k], P, rng), tv[k])
    hits = sum(p < a7 for p in pw.values())
    R['gates'] = {'calibration_p': cal, 'false_positives_of_14': fp, 'power_p': pw, 'power_hits_of_7': hits, 'alpha_7': a7}
    ok = fp <= 1 and hits >= 6
    raw = {k: p_closer(tv['Voynich_ZL3b'], tv[k]) for k in nat}; adj = holm(raw)
    R['p_raw'] = raw; R['p_holm'] = adj
    R['reverse_p_control_closer_than_voynich'] = {k: p_closer(tv[k], tv['Voynich_ZL3b']) for k in nat}
    R['generator_look_p'] = p_closer(tv['Voynich_ZL3b'], tv['Generator_TimmSchinner'])
    R['verdict_H1'] = 'NOT TESTABLE' if not ok else ('CONFIRMED' if all(v < ALPHA for v in adj.values()) else 'NOT CONFIRMED')
    R['seconds'] = round(time.time() - t0, 1)
    print(json.dumps({k: R[k] for k in ('gates', 'p_holm', 'reverse_p_control_closer_than_voynich', 'generator_look_p', 'verdict_H1', 'seconds')}, indent=1), flush=True)
    json.dump(R, open('analysis/C028_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
