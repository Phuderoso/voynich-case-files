#!/usr/bin/env python3
"""C047 (F-PAIR step 2): is the same-line pair excess E (C046) larger in Currier A pages than in Currier B pages?
Page-label permutation test; gates on natural texts with contiguous pseudo-language splits (catches drift along a
book) and a planted B-side weakening. Pre-registered in case-file/C047-pair-currier-split.md. Seed 4747.
Run: timeout 600 python3 tools/c047_pair_currier_split.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c046_line_pair_recurrence import Text, blocks, cap

SEED, NS, NPERM, NPERM_G, NG, NTOK = 4747, 5, 200, 40, 20, 34000
C = 'data/corpora/'

def ivtff_pages_lang(path):
    out, lang, sect = [], {}, {}
    for line in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', line)
        if h:
            m = re.search(r'\$L=(\w)', h.group(2)); lang[h.group(1)] = m.group(1) if m else None
            m = re.search(r'\$I=(\w)', h.group(2)); sect[h.group(1)] = m.group(1) if m else None; continue
        m = re.match(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        if len(ws) < 3 or not all(re.fullmatch(r'[a-z]+', w) for w in ws): continue
        out.append((m.group(1), ws))
    return out, lang, sect

def E(pl, rng):
    if not pl: return float('nan')
    t = Text(pl); return t.rec(t.w) / np.mean([t.rec(t.shuffle(rng)) for _ in range(NS)]) - 1

def diff(pl, A, rng):
    return E([x for x in pl if x[0] in A], rng) - E([x for x in pl if x[0] not in A], rng)

def perm_test(pl, A, rng, nperm):
    pages = list(dict.fromkeys(p for p, _ in pl)); k = len([p for p in pages if p in A]); obs = diff(pl, A, rng); nl = []
    for _ in range(nperm):
        nl.append(diff(pl, set(rng.choice(pages, k, replace=False)), rng))
    nl = np.array(nl); return dict(obs=float(obs), null_mean=float(nl.mean()), null_sd=float(nl.std()),
                                   p=float((1 + (nl >= obs).sum()) / (nperm + 1)))

def contiguous_A(pl, rng, frac=0.4):
    pages = list(dict.fromkeys(p for p, _ in pl)); k = int(frac * len(pages)); s = int(rng.integers(len(pages)))
    return set(pages[(s + i) % len(pages)] for i in range(k))

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED, NS=NS, NPERM=NPERM)
    nat = {'Italian_Dante': blocks(T.gutenberg(C + 'pg1012.txt')), 'Spanish_Cervantes': blocks(T.gutenberg(C + 'pg2000.txt'))}
    def window(pl):
        s = int(rng.integers(0, max(1, len(pl) - 4000))); return cap([(p, l) for p, l in pl[s:]], NTOK)
    # ---- gates (natural only, before any Voynich number)
    fp = 0
    for g in range(NG):
        pl = window(nat[list(nat)[g % 2]]); fp += perm_test(pl, contiguous_A(pl, rng), rng, NPERM_G)['p'] < 0.05
        print(' fpr trial', g, fp, round(time.time() - t0, 1), flush=True)
    pw = 0
    for g in range(NG):
        pl = window(nat['Italian_Dante']); A = contiguous_A(pl, rng)
        # plant: in non-A pages, 60% of lines get their words re-shuffled among those lines within the page
        t = Text(pl); w = t.w.copy(); pid = np.array([pl[i][0] not in A for i in t.lid])
        sel = pid & np.isin(t.lid, np.nonzero(rng.random(t.lid.max() + 1) < 0.6)[0]); idx = np.nonzero(sel)[0]
        o = idx[np.lexsort((rng.random(len(idx)), t.page[idx]))]; w[idx] = t.w[o]
        inv = {}; [inv.setdefault(int(v), x) for v, x in zip(t.w, [x for _, l in pl for x in l])]
        it = iter(w.tolist()); pl2 = [(p, [inv[next(it)] for _ in l]) for p, l in pl]
        pw += perm_test(pl2, A, rng, NPERM_G)['p'] < 0.05
        print(' power trial', g, pw, round(time.time() - t0, 1), flush=True)
    ok = fp <= 2 and pw >= 16
    R['gates'] = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=ok); print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)
    # ---- Voynich
    V = {}
    for k, f in [('Voynich_ZL3b', 'data/ZL3b-n.txt'), ('Voynich_IT2a', 'data/IT2a-n.txt')]:
        pl, lang, sect = ivtff_pages_lang(f); pl = [x for x in pl if lang.get(x[0]) in ('A', 'B')]
        A = {p for p, _ in pl if lang[p] == 'A'}
        r = perm_test(pl, A, rng, NPERM)
        r.update(E_A=E([x for x in pl if x[0] in A], rng), E_B=E([x for x in pl if x[0] not in A], rng),
                 pages_A=len(A), pages_B=len({p for p, _ in pl} - A), tokens_A=sum(len(l) for p, l in pl if p in A),
                 tokens_B=sum(len(l) for p, l in pl if p not in A))
        # descriptive: herbal-only A vs B (section held fixed)
        ph = [x for x in pl if sect.get(x[0]) == 'H']; AH = {p for p, _ in ph if lang[p] == 'A'}
        r['herbal_only'] = dict(E_A=E([x for x in ph if x[0] in AH], rng), E_B=E([x for x in ph if x[0] not in AH], rng),
                                pages_A=len(AH), pages_B=len({p for p, _ in ph} - AH), tokens_B=sum(len(l) for p, l in ph if p not in AH))
        V[k] = r; print(k, r, round(time.time() - t0, 1), 's', flush=True)
    z, i2 = V['Voynich_ZL3b'], V['Voynich_IT2a']; s = lambda r: r['p'] < 0.05
    R['voynich'] = V
    R['verdict'] = 'NOT TESTABLE' if not ok else ('A > B (pair excess larger in Currier A)' if s(z) and s(i2) else ('NO DIFFERENCE SHOWN' if not s(z) and not s(i2) else 'SPLIT'))
    R['runtime_s'] = round(time.time() - t0, 1); json.dump(R, open('analysis/C047_results.json', 'w'), indent=1, default=float)
    print(R['verdict'], R['runtime_s'])

if __name__ == '__main__': main()
