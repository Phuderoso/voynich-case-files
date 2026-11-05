"""C020: power map of the C019 exclusion. Which cipher classes would the one-to-one (INJ) reader have caught?

Planted Latin (Descartes, C019 Latin-only filter) in four classes, 10 items each, 100 words:
  P1  plain monoalphabetic substitution (control; must pass >= 9/10 again or the run is void)
  PH  homophonic: each of the 4 most frequent letters of the passage gets 2 symbols, chosen at random per occurrence
  PV  verbose: each vowel becomes a fixed 2-symbol sequence (vowel symbol + a shared marker symbol)
  PN  noisy copy: plain substitution, then 15 % of symbol tokens replaced by a random symbol of the item
Negatives N1/N2/N3 as C019 (generator, random EVA, glyph-shuffled Voynich), 10 each. No Voynich passage is scored.
Reader: C019 INJ (simulated annealing, 16 x 20 000). Usage: python3 tools/c020_inj_power_map.py
"""
import sys, os, json, random, time
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3
import c018_free_reader_bar as C18
import c019_inj_regate as C19

SEED = 20020; NW = 100; NITEM = 10; VOW = 'aeiouy'

def positives(rng):
    lex, _, letters = C19.LEX
    de = C18.flat(c3.gutenberg('data/corpora/pg23306.txt'))
    starts = list(range(0, len(de) - NW, NW)); rng.shuffle(starts); pas = []
    for s0 in starts:
        p = de[s0:s0 + NW]; cov = sum(len(w) >= 2 and w in lex for w in p) / NW
        if set(''.join(p)) <= set(letters) and cov >= C19.MINCOV: pas.append((p, cov))
        if len(pas) == 4 * NITEM: break
    items = []
    for j, (p, cov) in enumerate(pas):
        cls = ('P1', 'PH', 'PV', 'PN')[j // NITEM]
        alpha = sorted(set(''.join(p))); sym = list(range(len(alpha))); rng.shuffle(sym); k = dict(zip(alpha, sym))
        nxt = len(alpha)
        if cls == 'P1': ws = [[k[c] for c in w] for w in p]
        elif cls == 'PH':
            top = [c for c, _ in Counter(''.join(p)).most_common(4)]; alt = {c: nxt + i for i, c in enumerate(top)}
            ws = [[(alt[c] if c in alt and rng.random() < 0.5 else k[c]) for c in w] for w in p]
        elif cls == 'PV':
            ws = [[x for c in w for x in ((k[c], nxt) if c in VOW else (k[c],))] for w in p]
        else:
            ws = [[k[c] for c in w] for w in p]; flatpos = [(a, b) for a, w in enumerate(ws) for b in range(len(w))]
            for a, b in rng.sample(flatpos, int(0.15 * len(flatpos))): ws[a][b] = rng.randrange(len(alpha))
        items.append({'cls': cls, 'words': ws, 'oracle': cov})
    return items


def main():
    t0 = time.time(); rng = random.Random(SEED)
    items = positives(rng)
    neg, _ = C19.build(SEED + 1)               # C019 bank builder on a fresh seed; keep only its negatives
    items += [it for it in neg if it['cls'] in ('N1', 'N2', 'N3')]
    order = list(range(len(items))); random.Random(SEED + 2).shuffle(order)
    with Pool(8) as P: res = P.map(C19.fit, [(items[i]['words'], SEED + 13 * i) for i in order], chunksize=1)
    out = [{'cls': items[i]['cls'], 'oracle': items[i].get('oracle'), **res[j]} for j, i in enumerate(order)]
    by = {c: sorted(o['cmr'] for o in out if o['cls'] == c and o['cmr'] is not None) for c in ('P1', 'PH', 'PV', 'PN', 'N1', 'N2', 'N3')}
    na = dict(Counter(o['cls'] for o in out if o['cmr'] is None))
    nmax = max(by['N1'] + by['N2'] + by['N3'])
    det = {c: sum(1 for o in out if o['cls'] == c and o['cmr'] is not None and o['cmr'] > nmax) for c in ('P1', 'PH', 'PV', 'PN')}
    verdict = {c: ('covered' if det[c] >= 9 else 'not covered') for c in ('PH', 'PV', 'PN')}
    R = {'seed': SEED, 'neg_max': nmax, 'detected': det, 'control_valid': det['P1'] >= 9, 'verdict': verdict,
         'na': na, 'by_class': by, 'seconds': round(time.time() - t0, 1), 'items': out}
    json.dump(R, open('analysis/C020_results.json', 'w'), indent=1)
    print('negMax %.2f' % nmax, 'detected', det, 'control', 'VALID' if R['control_valid'] else 'VOID', verdict, 'NA', na)
    for c, v in by.items(): print('  ', c, ' '.join('%.2f' % x for x in v))
    print('seconds', R['seconds'])

if __name__ == '__main__': main()
