"""C026 (F-TRX step 3, audit): do the bifolium findings of C021 (Look B) and C023 survive a change of transcription
(Takahashi IT2a instead of ZL 3b) and the removal of the least reliable text (labels, rings, rays; see C025)?
Pre-registered in case-file/C026-transcription-replication.md. Seed 26026. Three looks, Bonferroni alpha 0.05/3.
Loader, similarity, nulls, redraw and plant reused unchanged from tools/c021_bifolium_vocab.py and
tools/c023_distance_null.py; only the input text changes. Run: timeout 600 python3 tools/c026_transcription_replication.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, random, time
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c021_bifolium_vocab as T
import c023_distance_null as D
SEED = 26026; ALPHA = 0.05 / 3; NCAL = 40

def leaves_paragraph_only(path='data/ZL3b-n.txt'):
    """Same as T.leaves but keeps only paragraph loci (locus type letter P)."""
    meta, words, cur = {}, defaultdict(list), None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f(\d+)\w*)>\s*<!(.*)>', line)
        if m:
            cur = int(m.group(2)); h = dict(re.findall(r'\$(\w)=(\S+)', m.group(3)))
            meta.setdefault(cur, {k: h.get(k) for k in 'QBFHLI'}); continue
        m = re.match(r'<(f\w+)\.\d+,.(\w)[^>]*>\s*(.*)', line)
        if not m or cur is None or m.group(2) != 'P': continue
        t = re.sub(r'<[^>]*>', '', m.group(3)); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        words[cur] += [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]
    keep = [f for f in sorted(meta) if len(words[f]) >= 20 and meta[f]['Q'] and meta[f]['B']]
    return keep, meta, words

def gates(fp, pw):
    fpr = float(np.mean(np.array(fp) <= ALPHA)); power = float(np.mean(np.array(pw) <= ALPHA))
    return fpr, power, fpr <= 0.075 and power >= 0.8

def look_c023(keep, meta, words, rng):
    cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
    cl = D.cells(keep, meta); _, conj, _ = T.structure(keep, meta, 'B')
    key = lambda m: (m['H'], m['L'], m['I'])
    fp = [D.test(T.simmat(keep, T.redraw(keep, meta, words, key, rng), vocab), cl, rng, 500)[1] for _ in range(NCAL)]
    pw = [D.test(T.simmat(keep, T.plant(keep, T.redraw(keep, meta, words, key, rng), conj, rng), vocab), cl, rng, 500)[1] for _ in range(NCAL)]
    fpr, power, ok = gates(fp, pw); obs, p = D.test(T.simmat(keep, words, vocab), cl, rng)
    return {'n_leaves': len(keep), 'vocab': len(vocab), 'n_cells': len(cl), 'n_conj': sum(len(v['conj']) for v in cl.values()),
            'S_obs': obs, 'p': p, 'fpr_at_alpha': fpr, 'power_f0.2': power,
            'verdict': 'not testable' if not ok else ('replicated' if p <= ALPHA else 'not replicated')}

def look_c021b(keep, meta, words, rng):
    cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
    q, conj, elig = T.structure(keep, meta, 'B'); key = lambda m: (m['H'], m['L'], m['I'])
    fp = [T.test(T.simmat(keep, T.redraw(keep, meta, words, key, rng), vocab), q, conj, elig, rng, 500)[1] for _ in range(NCAL)]
    pw = [T.test(T.simmat(keep, T.plant(keep, T.redraw(keep, meta, words, key, rng), conj, rng), vocab), q, conj, elig, rng, 500)[1] for _ in range(NCAL)]
    fpr, power, ok = gates(fp, pw); obs, p = T.test(T.simmat(keep, words, vocab), q, conj, elig, rng, 4000)
    return {'n_leaves': len(keep), 'vocab': len(vocab), 'n_conj_eligible': int(sum(elig[a, b] for a, b in conj)),
            'S_obs': float(obs), 'p': float(p), 'fpr_at_alpha': fpr, 'power_f0.2': power,
            'verdict': 'not testable' if not ok else ('replicated' if p <= ALPHA else 'not replicated')}

def main():
    t0 = time.time(); rng = random.Random(SEED); R = {'alpha_per_look': ALPHA}
    it = T.leaves('data/IT2a-n.txt'); zp = leaves_paragraph_only('data/ZL3b-n.txt')
    for name, fn, data in [('IT_C023', look_c023, it), ('ZLpara_C023', look_c023, zp), ('IT_C021B', look_c021b, it)]:
        R[name] = fn(*data, rng); print(name, R[name], round(time.time() - t0, 1), 's', flush=True)
    R['seconds'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C026_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
