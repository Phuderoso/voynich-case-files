#!/usr/bin/env python3
"""C003: glyph-position rigidity R = I(G;P)/H(P) (P = initial/medial/final) for Voynich vs natural-language,
vowelless, Hebrew and self-citation-generator controls. Equal 6000-word block-bootstrap samples, 99% intervals.
Usage: python3 tools/c003_position_rigidity.py   (writes analysis/C003_results.json; seeds fixed)"""
import re, json, math, random, unicodedata, os, sys
from collections import Counter
import numpy as np

NW, BLOCK, NBOOT, CI = 6000, 20, 300, (0.5, 99.5)
UNITS = ['cth', 'ckh', 'cph', 'cfh', 'ch', 'sh']

def units(w, raw=False):
    if raw: return list(w)
    out, i = [], 0
    while i < len(w):
        for u in UNITS:
            if w.startswith(u, i): out.append(u); i += len(u); break
        else: out.append(w[i]); i += 1
    return out

def voynich(path='data/ZL3b-n.txt', split_commas=True, lang=None):
    lines, curL = [], None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m: curL = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))).get('L'); continue
        m = re.match(r'<(f\w+)\.[^>]*>\s*(.*)', line)
        if not m: continue
        if lang and curL != lang: continue
        t = re.sub(r'<[^>]*>', '', m.group(2)); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        if not split_commas: t = t.replace(',', '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]
        if ws: lines.append(ws)
    return lines

def gutenberg(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    a = s.find('*** START'); b = s.find('*** END')
    s = s[s.find('\n', a) + 1:b] if a >= 0 and b > a else s
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return [re.findall(r'[a-z]+', l) for l in s.split('\n') if re.findall(r'[a-z]+', l)]

FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
def hebrew(path, merge_finals=False):
    s = open(path, encoding='utf-8').read(); lines = []
    for verse in re.findall(r'<verse[^>]*>(.*?)</verse>', s, re.S):
        ws = []
        for w in re.findall(r'<w [^>]*>([^<]*)</w>', verse):
            w = ''.join(c for c in unicodedata.normalize('NFD', w) if '\u05d0' <= c <= '\u05ea')
            if merge_finals: w = ''.join(FINALS.get(c, c) for c in w)
            if w: ws.append(w)
        if ws: lines.append(ws)
    return lines

def devowel(lines):
    out = [[re.sub('[aeiou]', '', w) for w in l] for l in lines]
    return [[w for w in l if w] for l in out if any(l)]

def plant_finals(lines):
    m = {'s': 'S', 'm': 'M', 't': 'T'}
    return [[w[:-1] + m[w[-1]] if len(w) > 1 and w[-1] in m else w for w in l] for l in lines]

def rigidity(words, raw=False, tok=None):
    tok = tok or (lambda w: units(w, raw))
    c = Counter()
    for w in words:
        u = tok(w)
        if len(u) < 2: continue
        for i, g in enumerate(u): c[(g, 0 if i == 0 else 2 if i == len(u) - 1 else 1)] += 1
    n = sum(c.values()); pg, pp = Counter(), Counter()
    for (g, p), k in c.items(): pg[g] += k; pp[p] += k
    hp = -sum(k / n * math.log2(k / n) for k in pp.values())
    mi = sum(k / n * math.log2((k / n) / (pg[g] / n * pp[p] / n)) for (g, p), k in c.items())
    rig = sum(pg[g] for g in pg if max(c[(g, p)] for p in range(3)) >= 0.9 * pg[g]) / n
    return mi / hp, rig

def boot(lines, rng, raw=False, tok=None, nboot=NBOOT):
    flat = [w for l in lines for w in l]
    blocks = [flat[i:i + BLOCK] for i in range(0, len(flat) - BLOCK + 1, BLOCK)]
    R, M = [], []
    for _ in range(nboot):
        s = []
        while len(s) < NW: s.extend(blocks[rng.randrange(len(blocks))])
        r, m = rigidity(s[:NW], raw, tok); R.append(r); M.append(m)
    return {'R_mean': float(np.mean(R)), 'R_lo': float(np.percentile(R, CI[0])), 'R_hi': float(np.percentile(R, CI[1])),
            'M2_mean': float(np.mean(M)), 'M2_lo': float(np.percentile(M, CI[0])), 'M2_hi': float(np.percentile(M, CI[1])),
            'n_words': len(flat)}

# --- self-citation generator (re-implementation from the published description; not Timm & Schinner's code)
GROUPS = [['o', 'a', 'y'], ['ch', 'sh'], ['k', 't'], ['p', 'f'], ['l', 'r'], ['d', 's']]
PREF = ['q', 'o', 'y', 'ch']
def mutate(u, rng, pool):
    u = list(u); op = rng.random()
    if op < 0.5 and u:
        i = rng.randrange(len(u)); g = u[i]
        if g == 'e' and rng.random() < 0.5: u.insert(i, 'e')
        else:
            for G in GROUPS:
                if g in G: u[i] = rng.choice([x for x in G if x != g]); break
    elif op < 0.7:
        if u and u[0] in PREF and len(u) > 1: u = u[1:]
        else: u = [rng.choice(PREF)] + u
    elif op < 0.85 and len(u) > 2: u = u[:-1]
    else: u = u + [rng.choice(pool)]
    return u

def generator(seed_lines, rng, n_words=40000, pool=None):
    lines = [[units(w) for w in l] for l in seed_lines]
    pool = pool or [g for l in lines for w in l for g in w]
    total = 0
    while total < n_words:
        src = [w for l in lines[-3:] for w in l]; new = []
        for _ in range(max(4, int(rng.gauss(10, 2)))):
            w = list(rng.choice(src))
            for _ in range(rng.choice([0, 1, 1, 2])): w = mutate(w, rng, pool)
            if rng.random() < 0.03: w = w + list(rng.choice(src))
            if not w: w = list(rng.choice(src))
            w = w[:12]  # cap word length (uncapped joins grow without bound)
            new.append(w)
        lines.append(new); total += len(new)
    return [[''.join(w) for w in l] for l in lines[len(seed_lines):]]

def mutate_b(u, rng, finals):
    u = list(u); op = rng.random()
    if op < 0.5 and u:
        i = rng.randrange(len(u)); g = u[i]
        if g == 'e' and u.count('e') < 3 and rng.random() < 0.5: u.insert(i, 'e')
        else:
            for G in GROUPS:
                if g in G: u[i] = rng.choice([x for x in G if x != g]); break
    elif op < 0.7:
        if u and u[0] in PREF and len(u) > 1: u = u[1:]
        elif not u or u[0] not in PREF: u = [rng.choice(PREF)] + u
    elif op < 0.85 and len(u) > 2: u = u[:-1]
    else: u = u[:-1] + [rng.choice(finals)] if u else u
    return u

def generator_b(seed_lines, rng, n_words=40000):
    """G1b (amended after smoke test): source = any of the last 30 lines plus the seed; e-runs capped at 3;
    final-glyph changes draw from glyphs seen word-finally in the seed."""
    seed = [[units(w) for w in l] for l in seed_lines]
    finals = [w[-1] for l in seed for w in l]
    lines, total = [], 0
    while total < n_words:
        src = [w for l in (seed + lines[-30:]) for w in l]; new = []
        for _ in range(max(4, int(rng.gauss(10, 2)))):
            w = list(rng.choice(src))
            for _ in range(rng.choice([0, 1, 1, 2])): w = mutate_b(w, rng, finals)
            if rng.random() < 0.03: w = w + list(rng.choice(src))
            w = w[:12] or list(rng.choice(src))
            new.append(w)
        lines.append(new); total += len(new)
    return [[''.join(w) for w in l] for l in lines]

def gen_tok(w):  # generator output is EVA-like; re-tokenise the same way as Voynich
    return units(w)

def main():
    rng = random.Random(20261104); out = {'params': {'NW': NW, 'BLOCK': BLOCK, 'NBOOT': NBOOT, 'CI': CI}, 'texts': {}}
    C = 'data/corpora/'
    V = voynich(); Vj = voynich(split_commas=False)
    texts = {'V': V, "V'": Vj, 'V_A': voynich(lang='A'), 'V_B': voynich(lang='B'),
             'LA_caesar': gutenberg(C + 'pg218.txt'), 'LA_descartes': gutenberg(C + 'pg23306.txt'),
             'IT_dante': gutenberg(C + 'pg1012.txt'), 'ES_quijote': gutenberg(C + 'pg2000.txt'),
             'HE': hebrew(C + 'Gen.xml'), 'HEm': hebrew(C + 'Gen.xml', True)}
    texts['LAv'] = devowel(texts['LA_caesar']); texts['ITv'] = devowel(texts['IT_dante'])
    texts['PLANT_caesar_finals'] = plant_finals(texts['LA_caesar'])
    texts['NEG_V_shuffled'] = [[''.join(rng.sample(units(w), len(units(w)))) for w in l] for l in V]
    for k, L in texts.items():
        tok = (lambda w: list(w)) if not k.startswith(('V', 'NEG')) else None
        if k == 'NEG_V_shuffled': tok = None
        out['texts'][k] = boot(L, rng, tok=tok); out['texts'][k]['alphabet'] = len({g for l in L for w in l for g in (units(w) if tok is None else tok(w))})
        print(k, {a: round(b, 3) if isinstance(b, float) else b for a, b in out['texts'][k].items()}, flush=True)
    out['texts']['V_rawEVA'] = boot(V, rng, raw=True); print('V_rawEVA', out['texts']['V_rawEVA'], flush=True)
    json.dump(out, open('analysis/C003_results.json', 'w'), indent=1)  # checkpoint
    # generators
    seed = V[:3]; G1, G2, G1b = [], [], []
    freq = Counter(g for l in V for w in l for g in units(w)); glyphs, wts = zip(*freq.items())
    for s in range(10):
        g = random.Random(1000 + s)
        G1.append(boot(generator(seed, g), rng, tok=gen_tok, nboot=100))
        G1b.append(boot(generator_b(seed, random.Random(2000 + s)), rng, tok=gen_tok, nboot=100))
        rs = [[''.join(g.choices(glyphs, wts, k=max(2, int(g.gauss(5, 1.5))))) for _ in range(9)] for _ in range(3)]
        G2.append(boot(generator(rs, g, pool=list(g.choices(glyphs, wts, k=500))), rng, tok=gen_tok, nboot=100))
    out['G1'] = G1; out['G2'] = G2; out['G1b'] = G1b; print('G1b R means', [round(x['R_mean'], 3) for x in G1b])
    print('G1 R means', [round(x['R_mean'], 3) for x in G1]); print('G2 R means', [round(x['R_mean'], 3) for x in G2], flush=True)
    json.dump(out, open('analysis/C003_results.json', 'w'), indent=1)  # checkpoint
    # false-positive calibration of the D1 rule (halves of the same text)
    fp, tot = 0, 0
    for k in ['LA_caesar', 'LA_descartes', 'IT_dante', 'ES_quijote', 'HE']:
        flat = [w for l in texts[k] for w in l]
        blocks = [flat[i:i + BLOCK] for i in range(0, len(flat) - BLOCK + 1, BLOCK)]
        for r in range(40):
            gg = random.Random(r); A, B = [], []
            for b in blocks: (A if gg.random() < 0.5 else B).append(b)
            a = boot(A, rng, tok=lambda w: list(w), nboot=60); b_ = boot(B, rng, tok=lambda w: list(w), nboot=60)
            tot += 1; fp += (a['R_lo'] > b_['R_hi']) or (b_['R_lo'] > a['R_hi'])
    out['calibration'] = {'splits': tot, 'false_positives': fp, 'rate': fp / tot}
    print('calibration', out['calibration'])
    json.dump(out, open('analysis/C003_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
