#!/usr/bin/env python3
"""C005: (A) coordinate-ascent search of the authors' Timm-Schinner generator for maximal glyph-position rigidity R
subject to Voynich-like word length / type-token ratio / h2 (whole-manuscript reference), held-out confirmation on
seeds 6001-6010; (B) redesigned verbose-cipher planted controls (Latin, Italian).
Usage: python3 tools/c005_targeted_search.py [ref|search|confirm|vc|all]  (resumable cache analysis/C005_search.jsonl)"""
import os, sys, json, random, threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3
import c004_generator_sweep as c4

CACHE = 'analysis/C005_search.jsonl'; NW = 6000
LINES = {'default': c4.BASE['text.initial_line'],
         'f1r.1': 'fachys ykal ar ataiin shol shory cthres y kor sholdy',
         'f58r.1': 'kor cholfy shofchy otoralchy chofchol sholy otaly dal',
         'f75r.1': 'kchedykary okeey qokar shyk chedy qotar shedy',
         'f103r.1': 'pchedal shdy ytechypchy otey qoteey qotal shedy yshdal dain okal daldy'}
SPACE = {'text.initial_line': list(LINES),
         'text.max_repeat_count': [0, 1, 2, 3, 5],
         'method.canFollow': ['curveline', 'statistic', 'voynich', 'none'],
         'method.canFollow.error_rate': [0, 2, 5, 8, 10],
         'method.sourceChooser': ['page', 'position', 'random'],
         'method.sourceChooser.same_position_probability': [0, 25, 50, 75, 100],
         'method.morph.add_remove.probability': [0, 20, 40, 60, 80],
         'method.morph.combine_split.probability': [0, 20, 40, 60, 80],
         'method.morph.reuse_last.probability': [0, 5, 10, 15, 20],
         'method.morph.combined.dismiss_as_source_probability': [0, 25, 50, 75, 100],
         'method.morph.use_word_final_substitutions': ['true', 'false'],
         'method.suggestions': ['top', 'daiin', 'random', 'none'],
         'method.suggestions.probability': [0, 25, 50, 75, 100],
         'method.suggestions.iType_min_percentage': [0, 25, 50, 75, 100],
         'method.suggestions.olType_min_percentage': [0, 25, 50, 75, 100],
         'method.suggestions.dyType_min_percentage': [0, 25, 50, 75, 100]}

def ref():
    if os.path.exists('analysis/C005_reference.json'): return json.load(open('analysis/C005_reference.json'))
    flat = c4.flat(c3.voynich()); blocks = [flat[i:i + 20] for i in range(0, len(flat) - 19, 20)]
    rng = random.Random(55); S = []
    for _ in range(50):
        s = []
        while len(s) < NW: s.extend(blocks[rng.randrange(len(blocks))])
        S.append(c4.stats(s[:NW]))
    r = {k: float(np.mean([x[k] for x in S])) for k in S[0]}
    r['first6000'] = c4.stats(flat[:NW]); json.dump(r, open('analysis/C005_reference.json', 'w'), indent=1); return r

REF = None
def like(st): return all(abs(st[k] - REF[k]) <= 0.15 * REF[k] for k in ('mwl', 'ttr', 'h2'))
def tocfg(c):
    c = dict(c); c['text.initial_line'] = LINES[c['text.initial_line']]; return c

POOL = ThreadPoolExecutor(8); LOCK = threading.Lock(); MEMO = {}
def run(cfg, seed):
    key = json.dumps([cfg, seed], sort_keys=True)
    if key in MEMO: return MEMO[key]
    L = POOL.submit(c4.generate, tocfg(cfg), seed).result()
    d = c4.stats(c4.flat(L)[:NW]) if L and len(c4.flat(L)) >= NW else None
    with LOCK:
        MEMO[key] = d; open(CACHE, 'a').write(json.dumps({'cfg': cfg, 'seed': seed, 'st': d}) + '\n')
    return d

def evaluate(cfg, s0):
    with ThreadPoolExecutor(3) as ex: R = list(ex.map(lambda s: run(cfg, s), (s0, s0 + 1, s0 + 2)))
    if any(r is None for r in R): return None, None
    m = {k: float(np.mean([r[k] for r in R])) for k in R[0]}
    return (m['R'] if like(m) else None), m

def ascend(start, s0, log):
    cur = dict(start); best, _ = evaluate(cur, s0); n = 1
    for p in range(2):
        for k, vals in SPACE.items():
            cands = [v for v in vals if v != cur[k]]
            with ThreadPoolExecutor(len(cands)) as ex:
                res = list(ex.map(lambda v: (v, evaluate({**cur, k: v}, s0)[0]), cands))
            n += len(cands)
            for v, r in res:
                if r is not None and (best is None or r > best): best, cur = r, {**cur, k: v}
        log.append(dict(pass_=p, best=best, cfg=dict(cur)))
    return dict(start=start, s0=s0, best=best, cfg=cur, evals=n, log=log)

def starts():
    rows = [json.loads(l) for l in open('analysis/C004_sweep.jsonl')]
    old = rows and json.load(open('analysis/C004_confirm.json'))['voynich_screen_stats']
    likeold = lambda d: all(abs(d[k] - old[k]) <= 0.15 * old[k] for k in ('mwl', 'ttr', 'h2'))
    picks = [rows[[d['tag'] for d in rows].index('S1.5')]] + [d for d in rows if d['tag'].startswith('S2') and likeold(d)]
    out = []
    for d in picks:
        base = {k: (int(v) if str(v).lstrip('-').isdigit() else v) for k, v in c4.BASE.items() if k in SPACE}
        base['text.initial_line'] = 'default'
        for k, v in d['cfg'].items():
            if k in SPACE: base[k] = v
        out.append(base)
    return out

def search():
    if os.path.exists(CACHE):
        for l in open(CACHE):
            d = json.loads(l); MEMO[json.dumps([d['cfg'], d['seed']], sort_keys=True)] = d['st']
    S = starts()
    with ThreadPoolExecutor(len(S)) as ex:
        res = list(ex.map(lambda i: ascend(S[i], 7000 + 100 * i, []), range(len(S))))
    json.dump(res, open('analysis/C005_search_result.json', 'w'), indent=1); return res

def confirm():
    res = json.load(open('analysis/C005_search_result.json'))
    feas = [r for r in res if r['best'] is not None]
    out = {'reference': REF, 'n_starts': len(res), 'n_feasible_starts': len(feas),
           'total_evals': sum(r['evals'] for r in res)}
    if not feas: out['A'] = 'not testable: no feasible point'
    else:
        b = max(feas, key=lambda r: r['best']); reps = []
        for s in range(6001, 6011):
            L = c4.generate(tocfg(b['cfg']), s)
            if L and len(c4.flat(L)) >= NW:
                reps.append(dict(seed=s, **c3.boot(L, random.Random(s)), **c4.stats(c4.flat(L)[:NW])))
        m = {k: float(np.mean([r[k] for r in reps])) for k in ('R_mean', 'mwl', 'ttr', 'h2')}
        ok = m['R_mean'] >= 0.470 and like({'mwl': m['mwl'], 'ttr': m['ttr'], 'h2': m['h2']})
        L = c4.generate(tocfg(b['cfg']), 6001); rng = random.Random(7)
        shu = [tuple(rng.sample(c3.units(w), len(c3.units(w)))) for l in L for w in l]
        out['A'] = dict(selected=b['cfg'], search_best=b['best'], confirm=reps, means=m,
                        voynich_like=like({'mwl': m['mwl'], 'ttr': m['ttr'], 'h2': m['h2']}),
                        verdict='reaches' if ok else 'not reached by targeted search',
                        neg_control_R=c3.rigidity(shu, tok=list)[0])
    json.dump(out, open('analysis/C005_confirm.json', 'w'), indent=1); return out

def vc():
    r = random.Random(5005); base = [chr(0x41 + i) for i in range(12)]
    ini = [chr(0x61 + i) for i in range(4)]; fin = [chr(0x71 + i) for i in range(4)]
    out = {}
    for lang, path in (('latin_caesar', 'data/corpora/pg218.txt'), ('italian_dante', 'data/corpora/pg1012.txt')):
        lines = c3.gutenberg(path)
        letters = sorted({ch for l in lines for w in l for ch in w})
        N = {c: r.choice(base) + r.choice(base) for c in letters}
        F = {c: r.choice(fin) for c in letters}; I = {c: r.choice(ini) for c in letters}
        def enc(w, mode):
            if len(w) == 1 or mode == 'N': return ''.join(N[c] for c in w)
            s = []
            for i, c in enumerate(w):
                if i == len(w) - 1: s.append(N[c][0] + F[c])
                elif i == 0 and mode == 'IF': s.append(I[c] + N[c][1])
                else: s.append(N[c])
            return ''.join(s)
        res = {m: c3.boot([[enc(w, m) for w in l] for l in lines], random.Random(1), tok=list) for m in ('N', 'F', 'IF')}
        res['planted_pass'] = res['F']['R_lo'] > res['N']['R_hi'] and res['IF']['R_lo'] > res['F']['R_hi']
        hi, lo = res['IF']['R_hi'], res['IF']['R_lo']
        res['ruleB'] = 'below' if hi < 0.470 else 'reaches'
        out[lang] = res
    json.dump(out, open('analysis/C005_verbose_cipher.json', 'w'), indent=1); return out

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'all'
    REF = ref()
    if a in ('vc', 'all'): print(json.dumps({k: {m: (v[m] if not isinstance(v[m], dict) else round(v[m]['R_mean'], 3)) for m in v} for k, v in vc().items()}))
    if a in ('search', 'all'): search()
    if a in ('confirm', 'all'): print(json.dumps(confirm(), indent=1)[:2500])
