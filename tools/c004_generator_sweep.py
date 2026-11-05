#!/usr/bin/env python3
"""C004: sweep the authors' own Timm-Schinner self-citation generator (text-generator.jar) over its documented
configuration space, screen glyph-position rigidity R (C003 metric) on 6000 words, confirm the best configs on 10
held-out seeds with bootstrap intervals; plus verbose-cipher planted controls on Latin.
Needs: java on PATH or $JAVA, the jar + conf.properties in $TSGEN (default /workspace/voynich/tsgen).
Usage: python3 tools/c004_generator_sweep.py [screen|confirm|vc|all]   (resumable: analysis/C004_sweep.jsonl)"""
import os, sys, json, re, math, random, subprocess, tempfile, shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3

TSGEN = os.environ.get('TSGEN', '/workspace/voynich/tsgen')
JAVA = os.environ.get('JAVA', '/workspace/voynich/jre/bin/java')
OUT = 'analysis/C004_sweep.jsonl'
BASE = dict(l.split('=', 1) for l in open(os.path.join(TSGEN, 'conf.properties')).read().splitlines()
            if l and not l.startswith('#') and '=' in l)
NW = 6000

def generate(cfg, seed):
    conf = dict(BASE); conf.update({k: str(v) for k, v in cfg.items()})
    conf['method.random.pseudo.seed'] = str(seed); conf['save.path'] = './generate/'
    d = tempfile.mkdtemp(dir='/tmp')
    try:
        os.makedirs(d + '/generate')
        open(d + '/conf.properties', 'w').write('\n'.join(f'{k}={v}' for k, v in conf.items()) + '\n')
        shutil.copy(os.path.join(TSGEN, 'text-generator.jar'), d)
        subprocess.run([JAVA, '-jar', 'text-generator.jar'], cwd=d, capture_output=True, timeout=60)
        f = d + '/generate/' + conf['save.filename']
        if not os.path.exists(f): return None
        return [l for l in ([re.findall(r'[a-z]+', x) for x in open(f) if not x.startswith('#')]) if l]
    except subprocess.TimeoutExpired:
        return None
    finally:
        shutil.rmtree(d, ignore_errors=True)

def stats(words):
    r, _ = c3.rigidity(words)
    U = [c3.units(w) for w in words]
    mwl = float(np.mean([len(u) for u in U])); ttr = len(set(words)) / len(words)
    big = Counter((u[i - 1], u[i]) for u in U for i in range(1, len(u))); prev = Counter()
    for (a, b), k in big.items(): prev[a] += k
    n = sum(big.values())
    h2 = -sum(k / n * math.log2(k / prev[a]) for (a, b), k in big.items())
    return dict(R=r, mwl=mwl, ttr=ttr, h2=h2)

def flat(lines): return [w for l in lines for w in l]

S1 = [{'method.morph.use_word_final_substitutions': 'false'}] + \
     [{'method.canFollow': v} for v in ('statistic', 'voynich', 'none')] + \
     [{'method.sourceChooser': v} for v in ('position', 'random')] + \
     [{'method.suggestions': v} for v in ('none', 'daiin', 'random')] + \
     [{'method.morph.replace.probability': v} for v in (20, 100)] + \
     [{'method.morph.add_remove.probability': v} for v in (0, 80)] + \
     [{'method.morph.combine_split.probability': v} for v in (0, 80)] + \
     [{'method.sourceChooser.same_position_probability': v} for v in (0, 100)] + \
     [{'method.canFollow.error_rate': 10}]

def s2_configs():
    r = random.Random(404); out = []
    for _ in range(120):
        out.append({
            'text.max_repeat_count': r.randint(0, 5),
            'method.canFollow': r.choice(['curveline', 'statistic', 'voynich', 'none']),
            'method.canFollow.error_rate': r.randint(0, 10),
            'method.sourceChooser': r.choice(['page', 'position', 'random']),
            'method.sourceChooser.same_position_probability': r.randint(0, 100),
            'method.morph.add_remove.probability': r.randint(0, 80),
            'method.morph.combine_split.probability': r.randint(0, 80),
            'method.morph.replace.probability': r.randint(20, 100),
            'method.morph.reuse_last.probability': r.randint(0, 20),
            'method.morph.combined.dismiss_as_source_probability': r.randint(0, 100),
            'method.morph.use_word_final_substitutions': r.choice(['true', 'false']),
            'method.suggestions': r.choice(['top', 'daiin', 'random', 'none']),
            'method.suggestions.probability': r.randint(0, 100),
            'method.suggestions.iType_min_percentage': r.randint(0, 100),
            'method.suggestions.olType_min_percentage': r.randint(0, 100),
            'method.suggestions.dyType_min_percentage': r.randint(0, 100)})
    return out

def jobs():
    J = [('S0', {}, s) for s in range(1, 51)]
    J += [(f'S1.{i}', c, s) for i, c in enumerate(S1) for s in range(1, 11)]
    J += [(f'S2.{i}', c, 1001 + i) for i, c in enumerate(s2_configs())]
    return J

def run_job(j):
    tag, cfg, seed = j
    L = generate(cfg, seed)
    if not L or len(flat(L)) < NW: return dict(tag=tag, cfg=cfg, seed=seed, ok=False, n=len(flat(L)) if L else 0)
    return dict(tag=tag, cfg=cfg, seed=seed, ok=True, n=len(flat(L)), **stats(flat(L)[:NW]))

def screen():
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT): d = json.loads(l); done.add((d['tag'], d['seed']))
    todo = [j for j in jobs() if (j[0], j[2]) not in done]
    with ThreadPoolExecutor(int(os.environ.get('NPAR', '8'))) as ex, open(OUT, 'a') as f:
        for d in ex.map(run_job, todo): f.write(json.dumps(d) + '\n'); f.flush()

def load():
    return [json.loads(l) for l in open(OUT)]

def confirm():
    V = stats(flat(c3.voynich())[:NW]); rows = [d for d in load() if d['ok']]
    like = lambda d: all(abs(d[k] - V[k]) <= 0.15 * V[k] for k in ('mwl', 'ttr', 'h2'))
    best = max(rows, key=lambda d: d['R']); likes = [d for d in rows if like(d)]
    bestlike = max(likes, key=lambda d: d['R']) if likes else None
    res = {'voynich_screen_stats': V, 'n_ok': len(rows), 'n_failed': sum(1 for d in load() if not d['ok']),
           'n_voynich_like': len(likes)}
    s0 = sorted(d['R'] for d in rows if d['tag'] == 'S0')
    res['S0'] = dict(n=len(s0), min=s0[0], max=s0[-1], median=float(np.median(s0)),
                     pct_below_0418=float(np.mean(np.array(s0) < 0.418)))
    for name, d in (('D1', best), ('D2', bestlike)):
        if d is None: res[name] = 'not testable: no Voynich-like config'; continue
        reps = []
        for s in range(5001, 5011):
            L = generate(d['cfg'], s)
            if L and len(flat(L)) >= NW:
                b = c3.boot(L, random.Random(s)); reps.append(dict(seed=s, **b, **stats(flat(L)[:NW])))
        m = float(np.mean([r['R_mean'] for r in reps])) if reps else None
        res[name] = dict(selected=d, confirm=reps, mean_R=m,
                         verdict=None if m is None else ('reaches' if m >= 0.470 else 'does not reach'))
        if name == 'D1' and reps:
            L = generate(d['cfg'], 5001); rng = random.Random(7)
            # shuffle glyph units within each word, keeping them as units
            shu = [[tuple(rng.sample(c3.units(w), len(c3.units(w)))) for w in l] for l in L]
            res['neg_control_R'] = c3.rigidity([w for l in shu for w in l], tok=list)[0]
    G0 = [l for l in ([re.findall(r'[a-z]+', x) for x in open('data/corpora/ts_generated_text.txt') if not x.startswith('#')]) if l]
    res['remeasure_G0'] = c3.boot(G0, random.Random(19))
    json.dump(res, open('analysis/C004_confirm.json', 'w'), indent=1)
    return res

def vc():
    lat = c3.gutenberg('data/corpora/pg218.txt'); r = random.Random(4004)
    syms = [chr(0x41 + i) for i in range(12)]; letters = 'abcdefghijklmnopqrstuvwxyz'
    code = lambda pool: pool[r.randrange(len(pool))] + pool[r.randrange(len(pool))]
    N = {c: code(syms) for c in letters}
    P = {c: [code(syms) for _ in range(3)] for c in letters}
    D = {c: [code(syms[0:4]), code(syms[4:8]), code(syms[8:12])] for c in letters}
    def enc(w, m, pos):
        if not pos: return ''.join(m[c] for c in w)
        return ''.join(m[c][0 if i == 0 else 2 if i == len(w) - 1 else 1] for i, c in enumerate(w))
    tok = list
    res = {}
    for name, m, pos in (('VC-N', N, False), ('VC-P', P, True), ('VC-D', D, True)):
        L = [[enc(w, m, pos) for w in l] for l in lat]
        res[name] = c3.boot(L, random.Random(1), tok=tok)
    res['caesar_plain'] = c3.boot(lat, random.Random(1))
    json.dump(res, open('analysis/C004_verbose_cipher.json', 'w'), indent=1)
    return res

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if a in ('screen', 'all'): screen()
    if a in ('confirm', 'all'): print(json.dumps(confirm(), indent=1)[:3000])
    if a in ('vc', 'all'): print(json.dumps(vc(), indent=1))
