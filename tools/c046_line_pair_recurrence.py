#!/usr/bin/env python3
"""C046 (new design for the same-line word-pair question; C006/C007 lacked power): do the same word pairs keep
sharing a line more often than a within-page shuffle predicts, and is the Voynich excess weaker than every natural
text? Replication-style test of the claim in arXiv 2610.34499 ("the manuscript shows this at half the strength of
the weakest"). Pre-registered in case-file/C046-line-pair-recurrence.md. Seed 4646.
Run: timeout 600 python3 tools/c046_line_pair_recurrence.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T

SEED, NTOK, B, BG, PAGE = 4646, 15000, 200, 100, 30
C = 'data/corpora/'

def ivtff_pages(path):
    """as c030.ivtff_paragraphs (same filters) but keeps the folio/page id"""
    out = []
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        if len(ws) < 3 or not all(re.fullmatch(r'[a-z]+', w) for w in ws): continue
        out.append((m.group(1), ws))
    return out

def blocks(lines):
    """natural text: pages = consecutive blocks of PAGE lines; lines with < 3 words dropped (same as Voynich filter)"""
    ls = [l for l in lines if len(l) >= 3]; return [(i // PAGE, l) for i, l in enumerate(ls)]

def cap(pl, n=NTOK):
    out, t = [], 0
    for p, l in pl:
        if t >= n: break
        out.append((p, l)); t += len(l)
    return out

class Text:
    def __init__(self, pl):
        voc = {}; self.w = np.array([voc.setdefault(x, len(voc)) for _, l in pl for x in l], np.int64); self.V = len(voc)
        lid = np.repeat(np.arange(len(pl)), [len(l) for _, l in pl]); self.lid = lid
        pg = {}; self.page = np.array([pg.setdefault(p, len(pg)) for p, l in pl for _ in l], np.int64)
        I, J = [], []; s = 0
        for _, l in pl:
            k = len(l); a, b = np.triu_indices(k, 1); I.append(a + s); J.append(b + s); s += k
        self.I, self.J = np.concatenate(I), np.concatenate(J); self.pl = pl
    def rec(self, w):
        a, b = w[self.I], w[self.J]; keep = a != b; lo, hi = np.minimum(a, b)[keep], np.maximum(a, b)[keep]
        lineid = self.lid[self.I][keep]
        key = np.unique((lo * self.V + hi) * (self.lid.max() + 1) + lineid) // (self.lid.max() + 1)  # one per (line, pair)
        _, c = np.unique(key, return_counts=True); return int((c >= 2).sum())
    def shuffle(self, rng, w=None):
        w = self.w if w is None else w; o = np.lexsort((rng.random(len(w)), self.page)); return w[o]
    def test(self, rng, w=None, nb=B):
        w = self.w if w is None else w; obs = self.rec(w); nl = np.array([self.rec(self.shuffle(rng, w)) for _ in range(nb)])
        return dict(rec=obs, null_mean=float(nl.mean()), null_sd=float(nl.std()), E=float(obs / nl.mean() - 1),
                    p=float((1 + (nl >= obs).sum()) / (nb + 1)))

def halves(pl):
    pages = list(dict.fromkeys(p for p, _ in pl)); h = len(pages) // 2; A = set(pages[:h])
    return [x for x in pl if x[0] in A], [x for x in pl if x[0] not in A]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    nat = {'Latin_Caesar': blocks(T.gutenberg(C + 'pg218.txt')), 'Latin_Descartes': blocks(T.gutenberg(C + 'pg23306.txt')),
           'Italian_Dante': blocks(T.gutenberg(C + 'pg1012.txt')), 'Italian_Machiavelli': blocks(T.gutenberg(C + 'pg56498.txt')),
           'Spanish_Cervantes': blocks(T.gutenberg(C + 'pg2000.txt')), 'Hebrew_Genesis': blocks(T.hebrew(C + 'Gen.xml')),
           'Hebrew_Exodus': blocks(T.hebrew(C + 'Exod.xml'))}
    voy = {'Voynich_ZL3b': ivtff_pages('data/ZL3b-n.txt'), 'Voynich_IT2a': ivtff_pages('data/IT2a-n.txt')}
    R = dict(seed=SEED, NTOK=NTOK, B=B, page_lines_natural=PAGE, texts={})
    # ---- 1. gates first (natural only)
    names = list(nat); fp = 0
    for g in range(40):
        t = Text(cap(nat[names[g % 7]])); fp += t.test(rng, t.shuffle(rng), BG)['p'] < 0.05
    pw = {0.05: 0, 0.02: 0}; d = Text(cap(nat['Italian_Dante'])); fr = np.bincount(d.w); mid = np.nonzero((fr >= 5) & (fr <= 50))[0]
    for g in range(40):
        for rate in pw:
            w = d.shuffle(rng); pairs = rng.choice(mid, (30, 2))
            for li in np.nonzero(rng.random(d.lid.max() + 1) < rate)[0]:
                pos = np.nonzero(d.lid == li)[0]; i, j = rng.choice(pos, 2, replace=False); w[i], w[j] = pairs[rng.integers(30)]
            pw[rate] += d.test(rng, w, BG)['p'] < 0.05
    g1 = fp <= 4 and pw[0.05] >= 32
    R['gates_H1'] = dict(fpr=f'{fp}/40', power_5pct=f'{pw[0.05]}/40', power_2pct=f'{pw[0.02]}/40', ok=g1)
    print('gates H1', R['gates_H1'], round(time.time() - t0, 1), 's', flush=True)
    # ---- 2. natural texts: full (N tokens) and halves
    for k, pl in nat.items():
        c = cap(pl); r = Text(c).test(rng); r['halves'] = [Text(h).test(rng, nb=100)['E'] for h in halves(c)]
        R['texts'][k] = r; print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in r.items()}, round(time.time() - t0, 1), 's', flush=True)
    hmin = lambda ex=None: min(e for k in nat if k != ex for e in R['texts'][k]['halves'])
    # H2 gates: LOO FPR on natural halves; power: Dante with 75% of lines' words re-shuffled within pages
    f2 = sum(all(e < hmin(k) for e in R['texts'][k]['halves']) for k in nat)
    p2 = 0
    for g in range(10):
        c = cap(nat['Italian_Dante']); ok = True
        for h in halves(c):
            t = Text(h); w = t.w.copy(); sel = np.isin(t.lid, np.nonzero(rng.random(t.lid.max() + 1) < 0.75)[0])
            idx = np.nonzero(sel)[0]; o = idx[np.lexsort((rng.random(len(idx)), t.page[idx]))]; w[idx] = t.w[o]
            ok &= t.test(rng, w, 100)['E'] < hmin()
        p2 += ok
    g2 = f2 <= 1 and p2 >= 8
    R['gates_H2'] = dict(fpr_loo=f'{f2}/7', power=f'{p2}/10', ok=g2, natural_half_min=hmin())
    print('gates H2', R['gates_H2'], round(time.time() - t0, 1), 's', flush=True)
    # ---- 3. Voynich
    for k, pl in voy.items():
        c = cap(pl); r = Text(c).test(rng); r['halves'] = [Text(h).test(rng, nb=100)['E'] for h in halves(c)]
        r['n_lines'] = len(c); r['n_pages'] = len(set(p for p, _ in c)); R['texts'][k] = r; print(k, r, flush=True)
    z, i2 = R['texts']['Voynich_ZL3b'], R['texts']['Voynich_IT2a']
    sig = lambda t: t['p'] < 0.05 and t['E'] > 0
    H1 = 'NOT TESTABLE' if not g1 else ('PRESENT (pairs recur beyond the page shuffle)' if sig(z) and sig(i2) else ('ABSENT' if not sig(z) and not sig(i2) else 'SPLIT'))
    lo = lambda t: all(e < hmin() for e in t['halves'])
    H2 = 'NOT TESTABLE' if not g2 else ('WEAKER THAN EVERY NATURAL TEXT' if lo(z) and lo(i2) else ('NOT WEAKER' if not lo(z) and not lo(i2) else 'SPLIT'))
    R['verdicts'] = dict(H1=H1, H2=H2, natural_E_full=[min(R['texts'][k]['E'] for k in nat), max(R['texts'][k]['E'] for k in nat)])
    R['runtime_s'] = round(time.time() - t0, 1); json.dump(R, open('analysis/C046_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['verdicts'])); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
