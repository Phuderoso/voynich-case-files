"""C018 (new family F-LLM, step 0): blind control bank + the 'invented meaning' bar of a mechanical free reader.

Question: how many words does a free-reading decipherment method "read" as Latin in text that has no message
(generator output, random glyph strings, glyph-shuffled Voynich)? That number is the bar any Voynich reading by the
same method must beat. Planted positives (real Latin enciphered) must be recovered first, or the reader is
'not discriminating' and its Voynich output is 'not testable'.

Two frozen readers, each fitting a many-to-one glyph->letter key by hill climbing (4 restarts x 3000 proposals):
  STRICT  : a token reads if the decoded word is a Latin lexicon word (len >= 2).
  LENIENT : a token reads if the multiset of its decoded consonants (anagram, vowels free) equals that of some
            lexicon word, with >= 2 consonants (the classic 'abbreviation + anagram + supply the vowels' licence).
Score CMR = read tokens / all tokens (primary); type-CMR also reported.
Lexicon: Caesar, De Bello Gallico (pg218). Positive plaintexts: Descartes, Meditationes (pg23306), other author.
Pre-registered in case-file/C018-free-reader-bar.md. Usage: python3 tools/c018_free_reader_bar.py [--smoke]
"""
import sys, os, json, random, hashlib, time
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3

MODES = ('STRICT', 'LENIENT', 'INJ'); ORACLE = {}
SEED = 18018; NW = 100; NITEM = 10; RESTARTS = 8; ITERS = 12000
VOW = set('aeiouy')
def flat(ls): return [w for l in ls for w in l]

def lexicon():
    lex = set(w for w in flat(c3.gutenberg('data/corpora/pg218.txt')) if len(w) >= 2)
    sig = set()
    for w in lex:
        c = ''.join(sorted(ch for ch in w if ch not in VOW))
        if len(c) >= 2: sig.add(c)
    letters = sorted(set(''.join(lex)))
    return lex, sig, letters

def read_type(dec, mode, lex, sig):
    if mode in ('STRICT', 'INJ'): return len(dec) >= 2 and dec in lex
    c = ''.join(sorted(ch for ch in dec if ch not in VOW)); return len(c) >= 2 and c in sig

def fit(args):
    item_words, mode, seed = args
    lex, sig, letters = LEX
    types = Counter(tuple(w) for w in item_words); tl = list(types.items())
    glyphs = sorted(set(g for t, _ in tl for g in t))
    rng = random.Random(seed); best = (-1, None)
    if mode == 'INJ' and len(glyphs) > len(letters): return {'cmr': None, 'type_cmr': None, 'sample': 'NA: more glyphs than letters'}
    def total(key):
        return sum(n for t, n in tl if read_type(''.join(key[g] for g in t), mode, lex, sig))
    for r in range(RESTARTS):
        if mode == 'INJ':
            key = dict(zip(glyphs, rng.sample(letters, len(glyphs)))); s = total(key)
            for it in range(ITERS):
                g = rng.choice(glyphs); new = rng.choice(letters); old = key[g]
                h = next((x for x in glyphs if key[x] == new), None)   # swap if the letter is taken
                key[g] = new
                if h is not None and h != g: key[h] = old
                s2 = total(key)
                if s2 >= s: s = s2
                else:
                    key[g] = old
                    if h is not None and h != g: key[h] = new
        else:
            key = {g: rng.choice(letters) for g in glyphs}; s = total(key)
            for it in range(ITERS):
                g = rng.choice(glyphs); old = key[g]; key[g] = rng.choice(letters)
                s2 = total(key)
                if s2 >= s: s = s2
                else: key[g] = old
        if s > best[0]: best = (s, dict(key))
    s, key = best
    readt = sum(1 for t, _ in tl if read_type(''.join(key[g] for g in t), mode, lex, sig))
    dec = [''.join(key[g] for g in tuple(w)) for w in item_words[:12]]
    return {'cmr': s / len(item_words), 'type_cmr': readt / len(tl), 'sample': ' '.join(dec)}

def build_bank(seed):
    rng = random.Random(seed); items = []
    de = flat(c3.gutenberg('data/corpora/pg23306.txt'))
    def passages(words, k, n=NW):
        starts = rng.sample(range(0, len(words) - n, n), k); return [words[s:s + n] for s in starts]
    # P1 mono-substitution, P2 + alphagram (letters sorted inside each word)
    for cls, pl in (('P1', passages(de, NITEM)), ('P2', passages(de, NITEM))):
        for p in pl:
            alpha = sorted(set(''.join(p))); sym = list(range(len(alpha))); rng.shuffle(sym)
            k = dict(zip(alpha, sym))
            ws = [[k[c] for c in (sorted(w) if cls == 'P2' else w)] for w in p]
            items.append({'cls': cls, 'words': ws, 'answer': ' '.join(p)})
    # Voynich (ZL 3b), one passage per page, distinct folios (singulion rule: never across pages)
    from c014_abjad_solver import voynich_words_with_section
    vw = voynich_words_with_section(); pages = {}
    for w, f, _ in vw: pages.setdefault(f, []).append(w)
    big = sorted(f for f, ws in pages.items() if len(ws) >= NW)
    vf = rng.sample(big, 2 * NITEM); vpass = []
    for f in vf:
        ws = pages[f]; s = rng.randrange(0, len(ws) - NW + 1); vpass.append((f, ws[s:s + NW]))
    for f, p in vpass[:NITEM]:
        items.append({'cls': 'V', 'folio': f, 'words': [c3.units(w) for w in p], 'answer': None})
    # N3 glyph-shuffled Voynich (other 10 pages): word lengths and glyph counts kept, words destroyed
    for f, p in vpass[NITEM:]:
        u = [c3.units(w) for w in p]; pool = [g for w in u for g in w]; rng.shuffle(pool); out, i = [], 0
        for w in u: out.append(pool[i:i + len(w)]); i += len(w)
        items.append({'cls': 'N3', 'folio': f, 'words': out, 'answer': None})
    # N1 Timm-Schinner generator output
    ts = [w for l in open('data/corpora/ts_generated_text.txt', encoding='utf-8') if not l.startswith('#')
          for w in l.split() if w.isalpha()]
    for s in rng.sample(range(0, len(ts) - NW, NW), NITEM):
        items.append({'cls': 'N1', 'words': [c3.units(w) for w in ts[s:s + NW]], 'answer': None})
    # N2 random EVA: Voynich glyph unigram and word-length distribution, independent draws
    allu = [c3.units(w) for w, _, _ in vw]; g = Counter(x for w in allu for x in w); L = [len(w) for w in allu]
    gk, gw = list(g), list(g.values())
    for _ in range(NITEM):
        items.append({'cls': 'N2', 'words': [rng.choices(gk, gw, k=rng.choice(L)) for _ in range(NW)], 'answer': None})
    return items

def main():
    smoke = '--smoke' in sys.argv; seed = SEED + (999 if smoke else 0)
    global ITERS, NITEM
    if smoke: ITERS, NITEM = 12000, 2
    t0 = time.time(); items = build_bank(seed)
    lex, sig, _ = LEX
    for m in MODES:
        ORACLE[m] = {c: [round(sum(read_type(w, m, lex, sig) for w in it['answer'].split()) / NW, 3)
                         for it in items if it['cls'] == c] for c in ('P1', 'P2')}
    order = list(range(len(items))); random.Random(seed + 1).shuffle(order)   # blind order
    salt = hashlib.sha256(str(seed).encode()).hexdigest()[:16]
    bank = [{'id': f'B{j:02d}', 'glyphs': [' '.join(map(str, w)) for w in items[i]['words']],
             'answer_sha256': hashlib.sha256((salt + (items[i]['answer'] or 'NONE')).encode()).hexdigest()}
            for j, i in enumerate(order)]
    jobs = [(items[i]['words'], m, seed + 7 * i + MODES.index(m)) for i in order for m in MODES]
    with Pool(8) as P: res = P.map(fit, jobs, chunksize=1)
    out = []
    for j, i in enumerate(order):
        it = items[i]
        out.append({'id': f'B{j:02d}', 'cls': it['cls'], 'folio': it.get('folio'),
                    **{m: res[len(MODES) * j + k] for k, m in enumerate(MODES)}})
    summ = {}
    for m in MODES:
        by = {c: sorted(o[m]['cmr'] for o in out if o['cls'] == c and o[m]['cmr'] is not None) for c in ('P1', 'P2', 'N1', 'N2', 'N3', 'V')}
        neg = sorted(by['N1'] + by['N2'] + by['N3']); nmax = neg[-1]
        p95 = neg[int(0.95 * (len(neg) - 1) + 0.5)]
        gate_cls = 'P2' if m == 'LENIENT' else 'P1'
        gate = sum(x > nmax for x in by[gate_cls])
        vabove = sum(x > nmax for x in by['V'])
        summ[m] = {'by_class': by, 'neg_p95': p95, 'neg_max': nmax, 'gate_class': gate_cls, 'gate_hits': gate,
                   'gate_pass': gate >= (9 if not smoke else 1), 'voynich_above_negmax': vabove,
                   'n_na': sum(o[m]['cmr'] is None for o in out),
                   'oracle_P': ORACLE.get(m)}
    R = {'seed': seed, 'smoke': smoke, 'NW': NW, 'NITEM': NITEM, 'RESTARTS': RESTARTS, 'ITERS': ITERS,
         'salt': salt, 'seconds': round(time.time() - t0, 1), 'summary': summ, 'items': out}
    tag = 'smoke' if smoke else 'results'
    os.makedirs('analysis', exist_ok=True)
    json.dump(R, open(f'analysis/C018_{tag}.json', 'w'), indent=1)
    if not smoke:
        json.dump({'salt_revealed_after_scoring': salt, 'bank': bank}, open('analysis/C018_blind_bank.json', 'w'))
    for m in summ:
        s = summ[m]
        print(m, 'gate', s['gate_class'], s['gate_hits'], 'pass' if s['gate_pass'] else 'FAIL',
              'negP95 %.3f negMax %.3f' % (s['neg_p95'], s['neg_max']), 'V>max', s['voynich_above_negmax'])
        for c, v in s['by_class'].items(): print('  ', c, ' '.join('%.2f' % x for x in v))
    print('seconds', R['seconds'])

LEX = lexicon()
if __name__ == '__main__': main()
