"""C027 (new family F-LEN, word-length morphology): is the Voynich word-type length distribution closer to a binomial
than natural-language controls are (Stolfi's binomial observation, tested with controls)?
Pre-registered in case-file/C027-word-length-binomial.md. Seed 27027. Run: timeout 600 python3 tools/c027_word_length_binomial.py
Loaders reused from tools/c003_position_rigidity.py; '<->' (drawing break) read as a word space (C026 lesson).
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, random, time, tempfile
from math import comb
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T

SEED = 27027; W = 10000; B = 200; NTWIN = 40; ALPHA = 0.05; NMAX = 25
C = 'data/corpora/'

def fixed(path):
    t = tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt')
    t.write(open(path, encoding='utf-8', errors='replace').read().replace('<->', '.')); t.close(); return t.name

def stream(lines, tok=None):
    return [len(tok(w)) if tok else len(w) for l in lines for w in l], [w for l in lines for w in l]

def tv_binom(lengths):
    n = len(lengths); emp = Counter(lengths); best = (9, None)
    m = sum(lengths) / n - 1
    for N in range(1, NMAX + 1):
        p = min(max(m / N, 1e-9), 1 - 1e-9)
        pmf = {k + 1: comb(N, k) * p ** k * (1 - p) ** (N - k) for k in range(N + 1)}
        keys = set(pmf) | set(emp)
        tv = 0.5 * sum(abs(emp.get(k, 0) / n - pmf.get(k, 0)) for k in keys)
        if tv < best[0]: best = (tv, N)
    return best

def window_tvs(words, lenof, rng, nb=B):
    out = []
    for _ in range(nb):
        s = rng.randrange(len(words)); idx = [(s + i) % len(words) for i in range(W)]
        types = {words[i] for i in idx}
        out.append(tv_binom([lenof[w] for w in types])[0])
    return out

def p_closer(tv_x, tv_c):
    """one-sided: is X closer to binomial than control C? independent window draws, paired by index"""
    return (1 + sum(a >= b for a, b in zip(tv_x, tv_c))) / (1 + len(tv_x))

def holm(ps):
    order = sorted(ps, key=ps.get); out, run = {}, 0
    for i, k in enumerate(order):
        run = max(run, min(1, ps[k] * (len(ps) - i))); out[k] = run
    return out

def main():
    t0 = time.time(); rng = random.Random(SEED)
    V = T.voynich(fixed('data/ZL3b-n.txt'))
    corp = {'Voynich_ZL3b': (V, T.units),
            'Latin_Caesar': (T.gutenberg(C + 'pg218.txt'), None), 'Latin_Descartes': (T.gutenberg(C + 'pg23306.txt'), None),
            'Italian_Dante': (T.gutenberg(C + 'pg1012.txt'), None), 'Italian_Machiavelli': (T.gutenberg(C + 'pg56498.txt'), None),
            'Spanish_Cervantes': (T.gutenberg(C + 'pg2000.txt'), None),
            'Hebrew_Genesis': (T.hebrew(C + 'Gen.xml'), None), 'Hebrew_Exodus': (T.hebrew(C + 'Exod.xml'), None),
            'Generator_TimmSchinner': ([l for l in ([re.findall(r'[a-z]+', x) for x in open(C + 'ts_generated_text.txt') if not x.startswith('#')]) if l], T.units)}
    words, lenof, R = {}, {}, {'window_tokens': W, 'draws': B}
    for k, (lines, tok) in corp.items():
        ws = [w for l in lines for w in l]; words[k] = ws
        lenof[k] = {w: (len(tok(w)) if tok else len(w)) for w in set(ws)}
    tv = {k: window_tvs(words[k], lenof[k], rng) for k in corp}
    for k in corp:
        full = tv_binom([lenof[k][w] for w in set(words[k])])
        R[k] = {'tokens': len(words[k]), 'types': len(lenof[k]), 'tv_window_mean': sum(tv[k]) / B,
                'tv_window_2.5_97.5': sorted(tv[k])[int(0.025 * B)], 'tv_window_97.5': sorted(tv[k])[int(0.975 * B) - 1],
                'tv_all_types': full[0], 'best_N_all_types': full[1]}
        print(k, R[k], flush=True)
    controls = [k for k in corp if k not in ('Voynich_ZL3b',)]
    raw = {k: p_closer(tv['Voynich_ZL3b'], tv[k]) for k in controls}
    adj = holm(raw); R['p_raw'] = raw; R['p_holm'] = adj
    # gates, on Caesar: twins = Voynich token stream with each type given a random length
    cz = [lenof['Latin_Caesar'][w] for w in set(words['Latin_Caesar'])]
    vt = list(set(words['Voynich_ZL3b']))
    def twin(sample_len):
        return {w: sample_len() for w in vt}
    fp = []
    for _ in range(NTWIN):
        L = twin(lambda: rng.choice(cz)); fp.append(p_closer(window_tvs(words['Voynich_ZL3b'], L, rng, 100), tv['Latin_Caesar'][:100]))
    _, Nc = tv_binom(cz); pc = (sum(cz) / len(cz) - 1) / Nc
    def mix():
        return 1 + sum(rng.random() < pc for _ in range(Nc)) if rng.random() < 0.5 else rng.choice(cz)
    pw = []
    for _ in range(NTWIN):
        L = twin(mix); pw.append(p_closer(window_tvs(words['Voynich_ZL3b'], L, rng, 100), tv['Latin_Caesar'][:100]))
    a_min = ALPHA / len(controls)   # strictest Holm step
    R['gates'] = {'fpr_at_alpha_strict': sum(p < a_min for p in fp) / NTWIN, 'fpr_at_0.05': sum(p < 0.05 for p in fp) / NTWIN,
                  'power_at_alpha_strict': sum(p < a_min for p in pw) / NTWIN, 'alpha_strict': a_min}
    g = R['gates']; ok = g['fpr_at_0.05'] <= 0.075 and g['power_at_alpha_strict'] >= 0.8
    nat = [k for k in controls if not k.startswith('Generator')]
    R['verdict_H1'] = ('NOT TESTABLE' if not ok else
                       ('CONFIRMED' if all(adj[k] < ALPHA for k in nat) else 'NOT CONFIRMED'))
    R['verdict_generator_look'] = 'n/a' if not ok else ('Voynich closer' if adj['Generator_TimmSchinner'] < ALPHA else 'not closer')
    R['seconds'] = round(time.time() - t0, 1); print(json.dumps({k: R[k] for k in ('p_holm', 'gates', 'verdict_H1', 'verdict_generator_look', 'seconds')}), flush=True)
    json.dump(R, open('analysis/C027_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
