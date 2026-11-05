"""C019: repair of C018 and re-gate of the one-to-one (INJ) free reader, power first.

Changes from C018 (both fixed before any counted run):
  1. Latin-only filter for positives: a Descartes passage enters the bank only if (a) its letters are all in the
     lexicon alphabet and (b) at least 35 % of its tokens are Caesar-lexicon words under the TRUE text (oracle).
     The filter reads the plaintext only, never a reader output.
  2. Stronger one-to-one search: simulated annealing (16 restarts x 20 000 proposals, T 2.0 -> 0.05 linear,
     best state kept) instead of greedy hill climbing.
Only the INJ reader is run (STRICT and LENIENT were excluded as discriminating methods in C018).
Usage: python3 tools/c019_inj_regate.py --design | --counted
"""
import sys, os, json, random, hashlib, time, math
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3
import c018_free_reader_bar as C18

RESTARTS, ITERS, T0, T1 = 16, 20000, 2.0, 0.05
NW = 100; NITEM = 10; MINCOV = 0.35
LEX = C18.LEX

def fit(args):
    words, seed = args
    lex, sig, letters = LEX
    tl = list(Counter(tuple(w) for w in words).items())
    glyphs = sorted(set(g for t, _ in tl for g in t))
    if len(glyphs) > len(letters): return {'cmr': None, 'sample': 'NA'}
    rng = random.Random(seed); best = (-1, None)
    def total(key): return sum(n for t, n in tl if len(t) >= 2 and ''.join(key[g] for g in t) in lex)
    for r in range(RESTARTS):
        key = dict(zip(glyphs, rng.sample(letters, len(glyphs)))); inv = {v: k for k, v in key.items()}
        s = total(key); bs, bk = s, dict(key)
        for it in range(ITERS):
            T = T0 + (T1 - T0) * it / ITERS
            g = rng.choice(glyphs); new = rng.choice(letters); old = key[g]
            if new == old: continue
            h = inv.get(new)
            key[g] = new
            if h is not None: key[h] = old
            s2 = total(key)
            if s2 >= s or rng.random() < math.exp((s2 - s) / T):
                s = s2; inv.pop(old, None); inv[new] = g
                if h is not None: inv[old] = h
                if s > bs: bs, bk = s, dict(key)
            else:
                key[g] = old
                if h is not None: key[h] = new
        if bs > best[0]: best = (bs, bk)
    s, key = best
    return {'cmr': s / len(words), 'sample': ' '.join(''.join(key[g] for g in w) for w in words[:12])}

def build(seed):
    rng = random.Random(seed); lex, _, letters = LEX; items = []
    de = C18.flat(c3.gutenberg('data/corpora/pg23306.txt'))
    starts = list(range(0, len(de) - NW, NW)); rng.shuffle(starts); n_rej = 0
    for s0 in starts:
        p = de[s0:s0 + NW]
        cov = sum(len(w) >= 2 and w in lex for w in p) / NW
        if set(''.join(p)) <= set(letters) and cov >= MINCOV:
            alpha = sorted(set(''.join(p))); sym = list(range(len(alpha))); rng.shuffle(sym); k = dict(zip(alpha, sym))
            items.append({'cls': 'P1', 'words': [[k[c] for c in w] for w in p], 'answer': ' '.join(p), 'oracle': cov})
            if sum(i['cls'] == 'P1' for i in items) == NITEM: break
        else: n_rej += 1
    from c014_abjad_solver import voynich_words_with_section
    vw = voynich_words_with_section(); pages = {}
    for w, f, _ in vw: pages.setdefault(f, []).append(w)
    big = sorted(f for f, ws in pages.items() if len(ws) >= NW)
    vf = rng.sample(big, 2 * NITEM); vpass = []
    for f in vf:
        ws = pages[f]; s = rng.randrange(0, len(ws) - NW + 1); vpass.append((f, ws[s:s + NW]))
    for f, p in vpass[:NITEM]: items.append({'cls': 'V', 'folio': f, 'words': [c3.units(w) for w in p]})
    for f, p in vpass[NITEM:]:
        u = [c3.units(w) for w in p]; pool = [g for w in u for g in w]; rng.shuffle(pool); out, i = [], 0
        for w in u: out.append(pool[i:i + len(w)]); i += len(w)
        items.append({'cls': 'N3', 'folio': f, 'words': out})
    ts = [w for l in open('data/corpora/ts_generated_text.txt', encoding='utf-8') if not l.startswith('#')
          for w in l.split() if w.isalpha()]
    for s in rng.sample(range(0, len(ts) - NW, NW), NITEM):
        items.append({'cls': 'N1', 'words': [c3.units(w) for w in ts[s:s + NW]]})
    allu = [c3.units(w) for w, _, _ in vw]; g = Counter(x for w in allu for x in w); L = [len(w) for w in allu]
    gk, gw = list(g), list(g.values())
    for _ in range(NITEM):
        items.append({'cls': 'N2', 'words': [rng.choices(gk, gw, k=rng.choice(L)) for _ in range(NW)]})
    return items, n_rej

def main():
    mode = 'design' if '--design' in sys.argv else 'counted'
    seed = 19019 + (500 if mode == 'design' else 0)
    t0 = time.time(); items, n_rej = build(seed)
    order = list(range(len(items))); random.Random(seed + 1).shuffle(order)
    with Pool(8) as P: res = P.map(fit, [(items[i]['words'], seed + 11 * i) for i in order], chunksize=1)
    out = [{'id': f'B{j:02d}', 'cls': items[i]['cls'], 'folio': items[i].get('folio'), 'oracle': items[i].get('oracle'), **res[j]}
           for j, i in enumerate(order)]
    by = {c: sorted(o['cmr'] for o in out if o['cls'] == c and o['cmr'] is not None) for c in ('P1', 'N1', 'N2', 'N3', 'V')}
    na = Counter(o['cls'] for o in out if o['cmr'] is None)
    neg = sorted(by['N1'] + by['N2'] + by['N3']); nmax = neg[-1]
    gate = sum(1 for o in out if o['cls'] == 'P1' and o['cmr'] is not None and o['cmr'] > nmax)
    vab = sum(x > nmax for x in by['V'])
    stall = [(round(o['cmr'], 2), o['oracle']) for o in out if o['cls'] == 'P1' and o['cmr'] is not None and o['cmr'] < o['oracle'] - 1e-9]
    summ = {'by_class': by, 'na': dict(na), 'neg_p95': neg[int(0.95 * (len(neg) - 1) + 0.5)], 'neg_max': nmax,
            'gate_hits': gate, 'gate_pass': gate >= 9, 'voynich_above_negmax': vab,
            'verdict_V': ('not testable' if gate < 9 else ('Latin-like signal under INJ' if vab >= 3 else 'no reading above the bar')),
            'p1_oracle': sorted(o['oracle'] for o in out if o['cls'] == 'P1'), 'p1_below_oracle': stall,
            'positives_rejected_by_filter': n_rej}
    salt = hashlib.sha256(f'c019-{seed}'.encode()).hexdigest()[:16]
    R = {'mode': mode, 'seed': seed, 'RESTARTS': RESTARTS, 'ITERS': ITERS, 'MINCOV': MINCOV, 'salt': salt,
         'seconds': round(time.time() - t0, 1), 'summary': summ, 'items': out}
    json.dump(R, open(f'analysis/C019_{mode}.json', 'w'), indent=1)
    if mode == 'counted':
        bank = [{'id': f'B{j:02d}', 'glyphs': [' '.join(map(str, w)) for w in items[i]['words']],
                 'answer_sha256': hashlib.sha256((salt + items[i].get('answer', 'NONE')).encode()).hexdigest()}
                for j, i in enumerate(order)]
        json.dump({'salt_revealed_after_scoring': salt, 'bank': bank}, open('analysis/C019_blind_bank.json', 'w'))
    print(mode, 'gate', gate, 'PASS' if gate >= 9 else 'FAIL', 'negP95 %.2f negMax %.2f' % (summ['neg_p95'], nmax),
          'V>max', vab, summ['verdict_V'], 'NA', dict(na), 'rejected', n_rej)
    for c, v in by.items(): print('  ', c, ' '.join('%.2f' % x for x in v))
    print('  oracle', summ['p1_oracle'], 'below-oracle', stall, 'seconds', R['seconds'])

if __name__ == '__main__': main()
