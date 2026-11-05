#!/usr/bin/env python3
"""C030 (F-LINE, new family): do the glyphs at line edges differ from the same line's other words?
D_end   = JSD(last glyph unit of line-final words || last unit of the line's other words)
D_start = JSD(first unit of line-initial words || first unit of other words); paragraph-first lines excluded.
Null: word order shuffled within each line (the edge word becomes a uniformly random word of its line).
Gates: calibration on re-lineated text (FPR), planted moves (power). Texts: ZL 3b paragraphs, Timm-Schinner generator;
IT2a paragraphs as replication. Writes analysis/C030_results.json. Usage: python3 tools/c030_line_edge_glyphs.py"""
import re, json, sys, time
from collections import Counter
import numpy as np
sys.path.insert(0, 'tools')
from c003_position_rigidity import units

NPERM, NREP, ALPHA, PLANT_F, SEED = 1000, 40, 0.025, 0.15, 3030

def ivtff_paragraphs(path):
    """lines of paragraph loci (type P*); '<->' read as a word space; lines with unreadable words dropped.
    returns list of (words, is_paragraph_first)"""
    out = []
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        if len(ws) < 3 or not all(re.fullmatch(r'[a-z]+', w) for w in ws): continue
        out.append((ws, m.group(2) == '@'))
    return out

def generator(path='data/corpora/ts_generated_text.txt'):
    out = []
    for line in open(path, encoding='utf-8', errors='replace'):
        if line.startswith('#'): continue
        ws = line.split()
        if len(ws) >= 3 and all(re.fullmatch(r'[a-z]+', w) for w in ws): out.append((ws, False))
    return out

def encode(lines, which):
    """per line: array of edge-unit codes for every word; also mask of lines used"""
    pos = -1 if which == 'end' else 0
    keep = [(ws) for ws, pf in lines if not (which == 'start' and pf)]
    codes = [[units(w)[pos] for w in ws] for ws in keep]
    return codes

def jsd(a, b):
    a = a / a.sum(); b = b / b.sum(); m = (a + b) / 2
    def kl(x):
        nz = x > 0; return float(np.sum(x[nz] * np.log2(x[nz] / m[nz])))
    return 0.5 * kl(a) + 0.5 * kl(b)

def test(codes, which, rng, nperm=NPERM):
    alph = sorted({c for l in codes for c in l}); ix = {c: i for i, c in enumerate(alph)}
    K = len(alph); L = len(codes)
    lens = np.array([len(l) for l in codes]); off = np.concatenate([[0], np.cumsum(lens)[:-1]])
    flat = np.array([ix[c] for l in codes for c in l])
    total = np.bincount(flat, minlength=K).astype(float)
    edge_idx = off + (lens - 1 if which == 'end' else 0)
    def stat(eidx):
        e = np.bincount(flat[eidx], minlength=K).astype(float)
        return jsd(e, total - e), e
    d_obs, e_obs = stat(edge_idx)
    null = np.empty(nperm)
    for k in range(nperm):
        null[k] = stat(off + (rng.random(L) * lens).astype(int))[0]
    p = (1 + np.sum(null >= d_obs)) / (nperm + 1)
    exp = np.zeros(K)  # expected edge counts under null = sum over lines of within-line share
    for i in range(L):
        exp += np.bincount(flat[off[i]:off[i] + lens[i]], minlength=K) / lens[i]
    ratio = {alph[i]: [int(e_obs[i]), round(float(exp[i]), 1)] for i in np.argsort(-(e_obs - exp)) if e_obs[i] + exp[i] >= 20}
    return dict(D=d_obs, null_mean=float(null.mean()), null_sd=float(null.std()), z=float((d_obs - null.mean()) / null.std()),
                p=float(p), lines=L, edge_obs_vs_expected=dict(list(ratio.items())[:6] + list(ratio.items())[-4:]))

def relineate(lines, rng):
    """concatenate all words, recut with the original line-length sequence from a random offset (circular).
    paragraph-first flags are cleared (no paragraphs remain)."""
    stream = [w for ws, _ in lines for w in ws]; n = len(stream); o = int(rng.integers(1, 200))
    stream = stream[o:] + stream[:o]; out, i = [], 0
    for ws, _ in lines:
        out.append((stream[i:i + len(ws)], False)); i += len(ws)
    return out

def plant(lines, which, target, f, rng):
    out = []
    for ws, pf in lines:
        ws = list(ws)
        if rng.random() < f:
            pos = -1 if which == 'end' else 0
            cand = [j for j, w in enumerate(ws) if units(w)[pos] == target]
            if cand:
                w = ws.pop(int(rng.choice(cand)))
                ws = ws + [w] if which == 'end' else [w] + ws
        out.append((ws, pf))
    return out

def third_unit(lines, which):
    pos = -1 if which == 'end' else 0
    return Counter(units(w)[pos] for ws, _ in lines for w in ws).most_common(3)[2][0]

def gates(lines, rng):
    g = {}
    for which in ('end', 'start'):
        fp = 0; pw = 0; tgt = third_unit(lines, which)
        for r in range(NREP):
            rl = relineate(lines, rng)
            fp += test(encode(rl, which), which, rng, 200)['p'] < ALPHA
            pw += test(encode(plant(rl, which, tgt, PLANT_F, rng), which), which, rng, 200)['p'] < ALPHA
        g[which] = dict(fpr=fp / NREP, power=pw / NREP, plant_unit=tgt, passed=bool(fp <= 4 and pw >= 32))
    return g

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); res = {}
    texts = {'voynich_ZL3b': ivtff_paragraphs('data/ZL3b-n.txt'), 'ts_generator': generator(),
             'voynich_IT2a': ivtff_paragraphs('data/IT2a-n.txt')}
    for name, lines in texts.items():
        r = dict(n_lines=len(lines), n_words=sum(len(w) for w, _ in lines), gates=gates(lines, rng))
        for which in ('end', 'start'):
            r[which] = test(encode(lines, which), which, rng)
            ok = r['gates'][which]['passed']
            r[which]['verdict'] = ('DETECTED' if r[which]['p'] < ALPHA else 'NOT DETECTED') if ok else 'NOT TESTABLE'
        res[name] = r; print(name, json.dumps({k: (r[k]['D'], r[k]['p'], r[k]['verdict']) for k in ('end', 'start')}),
                             json.dumps(r['gates']), round(time.time() - t0, 1), 's', flush=True)
    res['_meta'] = dict(NPERM=NPERM, NREP=NREP, ALPHA=ALPHA, PLANT_F=PLANT_F, SEED=SEED, seconds=round(time.time() - t0, 1))
    json.dump(res, open('analysis/C030_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
