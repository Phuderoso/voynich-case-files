#!/usr/bin/env python3
"""C104 (F-RHYTHM step 3): does the adjacent word-length persistence (C102/C103) cross the line break?
If Voynich lines were layout-only (as in ordinary prose), the rhythm should run on from the end of one line into the
start of the next. If lines are self-contained units, the carry-over should vanish at the break.
Lines: C070 filters verbatim (paragraph loci, no '<->', all words [a-z]+), here also >= 6 words; kept words = positions
3..n-1 (words 1, 2 and last dropped, exactly as C103 H2). Paragraphs: a new paragraph starts at locus indicator '@' or '*'
or a page change. A 'run' = maximal sequence of consecutive kept lines (consecutive locus numbers, no filtered line in
between) inside one paragraph. Adjacent-line pairs come only from runs. Word length = EVA glyph units (C003 units()).
H1a (word-level carry-over): r_X = Pearson over adjacent-line pairs of (len of LAST kept word of line i, len of FIRST kept
   word of line i+1). Null: kept words permuted within every line (line multisets kept, so any line-level persistence
   stays in the null); exact vectorised draw of two distinct positions per line. D_X = r_X - null mean.
H1b (line-level persistence): r_L = Pearson over adjacent-line pairs of mean kept length. Null: line order permuted within
   each run. D_L = r_L - null mean.
p two-sided = (1 + #|r*-m| >= |r-m|)/(R+1), R = 2000. Holm over 8 = {H1a,H1b} x {Currier A,B} x {IT2a,ZL3b}.
Verdict per hypothesis and language: DETECTED-PERSISTENT / -ALTERNATING if both transcriptions reject (Holm <= 0.05) with
   the same sign; PARTIAL if one; NOT DETECTED if none; NOT TESTABLE if any gate fails for that language.
Plants on pseudo replicates (H1a pseudo = kept words shuffled in every line; H1b pseudo = line order shuffled in runs):
   H1a POS: with prob q per pair, the word of line i+1 closest in length to the last kept word of line i is swapped to the
   front; NEG: the most distant one. H1b POS: with prob q per run, lines sorted by mean length; NEG: alternated long/short.
Design (seed 11693): q = smallest of (0.05, 0.10, 0.20, 0.40) with p <= 0.05 and the right sign in >= 9/10 replicates,
   both plants, all 4 subsets (RG 300), separately for H1a and H1b; none -> NOT TESTABLE. Gates (seed 11694, 20 fresh):
   FPR <= 2/20, POS and NEG power >= 16/20, broken meter: mean D under NEG < 0 < mean D under POS.
Descriptive (no verdict): D_W = within-line adjacent persistence of the same kept words (C102 statistic, R 2000) and the
   ratio D_X / D_W; the same two numbers for natural prose cut into pseudo-lines (word counts drawn from IT2a Currier B
   lines, runs of 8 lines, seed 11696), where breaks are layout-only.
Audit C103: observed r of the four H2 subsets must equal the published values exactly.
Run: timeout 600 python tools/c104_rhythm_line_breaks.py analysis/C104_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import FILES
from c003_position_rigidity import units, gutenberg
import c102_word_length_rhythm as W

DSEED, GSEED, SEED, NSEED = 11693, 11694, 11695, 11696
R, RG, NG, ALPHA, QS = 2000, 300, 20, 0.05, (0.05, 0.10, 0.20, 0.40)
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: R, RG, NG = 50, 20, 2
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def parse_runs(path):
    """returns {L: [run, ...]}, run = list of word lists (consecutive kept lines of one paragraph)."""
    meta, out, para, prev = {}, {}, 0, None
    cur = None
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m or not m.group(4).startswith('P'): continue
        page, num, ind, t = m.group(1), int(m.group(2)), m.group(3), m.group(5)
        newp = ind in '@*' or prev is None or prev[0] != page
        ok = '<->' not in t
        if ok:
            t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
            t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
            ws = [w for w in re.split(r'[.,\s]+', t) if w]
            ok = len(ws) >= 6 and all(re.fullmatch(r'[a-z]+', w) for w in ws)
        L = meta.get(page, {}).get('L')
        contiguous = prev is not None and prev[0] == page and prev[1] == num - 1 and not newp
        if not ok or not contiguous: cur = None
        if ok:
            if cur is None: cur = []; out.setdefault(L, []).append(cur)
            cur.append(ws)
        prev = (page, num)
    return {k: [r for r in v if len(r) >= 1] for k, v in out.items()}

class Runs:
    def __init__(self, runs):
        self.lines = [np.array([len(units(w)) if isinstance(w, str) else w for w in l[2:-1]] if isinstance(l[0], str) else l, float)
                      for r in runs for l in r]
        self.run = np.concatenate([np.full(len(r), i) for i, r in enumerate(runs)])
        self.n = np.array([len(x) for x in self.lines])
        self.first = np.array([x[0] for x in self.lines]); self.last = np.array([x[-1] for x in self.lines])
        self.mean = np.array([x.mean() for x in self.lines])
        self.pair = np.r_[self.run[1:] == self.run[:-1]]  # line j paired with j+1
    def rX(self, first, last): return float(np.corrcoef(last[:-1][self.pair], first[1:][self.pair])[0, 1])
    def rL(self, mean): return float(np.corrcoef(mean[:-1][self.pair], mean[1:][self.pair])[0, 1])
    def nullX(self, rng, r):
        out = np.empty(r); off = np.r_[0, np.cumsum(self.n)[:-1]]; flat = np.concatenate(self.lines)
        for k in range(r):
            i1 = np.floor(rng.random(len(self.n)) * self.n).astype(int)
            i2 = np.floor(rng.random(len(self.n)) * (self.n - 1)).astype(int); i2 += i2 >= i1
            out[k] = self.rX(flat[off + i1], flat[off + i2])
        return out
    def nullL(self, rng, r):
        out = np.empty(r)
        for k in range(r): o = np.lexsort((rng.random(len(self.run)), self.run)); out[k] = self.rL(self.mean[o])
        return out

def ptest(obs, nl):
    m = nl.mean(); p = (1 + (np.abs(nl - m) >= abs(obs - m)).sum()) / (len(nl) + 1)
    return dict(r=obs, null_mean=float(m), null_sd=float(nl.std()), D=float(obs - m), z=float((obs - m) / nl.std()), p=float(p))
def testX(S, rng, r): return ptest(S.rX(S.first, S.last), S.nullX(rng, r))
def testL(S, rng, r): return ptest(S.rL(S.mean), S.nullL(rng, r))

def split(S):
    """list of runs of length arrays from a Runs object."""
    out = []; 
    for j, x in enumerate(S.lines):
        if j == 0 or S.run[j] != S.run[j - 1]: out.append([])
        out[-1].append(x.copy())
    return out

def mk(runs): return Runs(runs)

def pseudoX(S, rng): return [[rng.permutation(x) for x in r] for r in split(S)]
def pseudoL(S, rng): return [[r[i] for i in rng.permutation(len(r))] for r in split(S)]

def plantX(runs, rng, q, kind):
    for r in runs:
        for j in range(1, len(r)):
            if rng.random() < q:
                d = np.abs(r[j] - r[j - 1][-1]); i = int(np.argmin(d) if kind == 'POS' else np.argmax(d))
                r[j][[0, i]] = r[j][[i, 0]]
    return runs

def plantL(runs, rng, q, kind):
    out = []
    for r in runs:
        if len(r) > 1 and rng.random() < q:
            o = sorted(r, key=lambda x: -x.mean())
            if kind == 'NEG':
                a, i, j = [], 0, len(o) - 1
                while i <= j:
                    a.append(o[i]); i += 1
                    if i <= j: a.append(o[j]); j -= 1
                o = a
            r = o
        out.append(r)
    return out

HYP = {'H1a': (pseudoX, plantX, testX), 'H1b': (pseudoL, plantL, testL)}

def gate(S, h, rng, q, ng):
    pseudo, plant, test = HYP[h]; fp = pos = neg = 0; dp, dn = [], []
    for _ in range(ng):
        P0 = pseudo(S, rng); t = test(mk(P0), rng, RG); fp += t['p'] <= ALPHA
        t = test(mk(plant([[x.copy() for x in r] for r in P0], rng, q, 'POS')), rng, RG); pos += t['p'] <= ALPHA and t['D'] > 0; dp.append(t['D'])
        t = test(mk(plant([[x.copy() for x in r] for r in P0], rng, q, 'NEG')), rng, RG); neg += t['p'] <= ALPHA and t['D'] < 0; dn.append(t['D'])
    return dict(FPR=int(fp), POS=int(pos), NEG=int(neg), D_pos_mean=float(np.mean(dp)), D_neg_mean=float(np.mean(dn)))

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C104_results.json'
    res = dict(cycle='C104', smoke=SMOKE, seeds=dict(design=DSEED, gates=GSEED, test=SEED, natural=NSEED), next_free_seed=11697)
    sub = {}
    for k, f in FILES:
        pr = parse_runs(f)
        for L in 'AB': sub[f'{k}|{L}'] = Runs(pr[L])
    res['n'] = {s: dict(lines=len(S.lines), runs=int(S.run.max() + 1), pairs=int(S.pair.sum())) for s, S in sub.items()}; log('n', res['n'])
    # audit C103 H2 observed r (lines >= 6 words, words[2:-1]; ordering-independent pooled within-line r)
    from c070_word2_sh import parse
    pub = json.load(open('analysis/C103_results.json'))['H2']; A = {}
    for k, f in FILES:
        P = parse(f)
        for L in 'AB':
            Lo = W.Lines([[len(units(w)) for w in l['words'][2:-1]] for l in P if l['L'] == L and len(l['words']) >= 6])
            A[f'{k}|{L}'] = dict(r=Lo.r(Lo.x), published=pub[f'{k}|{L}']['r'])
    res['audit_C103'] = dict(values=A, exact=all(abs(v['r'] - v['published']) < 1e-12 for v in A.values())); log('audit', res['audit_C103']['exact'])
    # design + gates per hypothesis
    res['design'], res['gates'] = {}, {}
    for h in HYP:
        rng = np.random.default_rng(DSEED + (0 if h == 'H1a' else 1000)); qd = None; tab = {}
        for q in QS:
            tab[q] = {s: gate(S, h, rng, q, 10 if not SMOKE else 1) for s, S in sub.items()}
            log('design', h, q, tab[q])
            if all(g['POS'] >= (9 if not SMOKE else 0) and g['NEG'] >= (9 if not SMOKE else 0) for g in tab[q].values()): qd = q; break
        res['design'][h] = dict(q=qd, table={str(k): v for k, v in tab.items()})
        rng = np.random.default_rng(GSEED + (0 if h == 'H1a' else 1000)); G = {}
        for s, S in sub.items():
            g = gate(S, h, rng, qd if qd else QS[-1], NG)
            g['ok'] = bool(qd and g['FPR'] <= 2 and g['POS'] >= 16 and g['NEG'] >= 16 and g['D_neg_mean'] < 0 < g['D_pos_mean']); G[s] = g
        res['gates'][h] = G; log('gates', h, G)
    # H1 tests
    rng = np.random.default_rng(SEED); H = {}
    for h in HYP:
        for s, S in sub.items(): H[f'{h}|{s}'] = HYP[h][2](S, rng, R)
    ph = W.holm({k: v['p'] for k, v in H.items()})
    for k in H: H[k]['p_holm'] = ph[k]
    res['H1'] = H; log('H1', H)
    ver = {}
    for h in HYP:
        for L in 'AB':
            ks = [f'{k}|{L}' for k, _ in FILES]
            if not all(res['gates'][h][k]['ok'] for k in ks): ver[f'{h}|{L}'] = 'NOT TESTABLE'; continue
            rej = [k for k in ks if H[f'{h}|{k}']['p_holm'] <= ALPHA]; sg = {np.sign(H[f'{h}|{k}']['D']) for k in rej}
            if len(rej) == 2 and len(sg) == 1: ver[f'{h}|{L}'] = 'DETECTED-' + ('ALTERNATING' if sg == {-1.0} else 'PERSISTENT')
            elif rej: ver[f'{h}|{L}'] = 'PARTIAL'
            else: ver[f'{h}|{L}'] = 'NOT DETECTED'
    res['verdict'] = ver
    # descriptive: within-line D_W on the same kept words, ratio
    rng = np.random.default_rng(SEED + 1); DW = {}
    for s, S in sub.items():
        t = W.test(W.Lines([list(x) for x in S.lines]), rng, R); DW[s] = dict(D_W=t['D'], D_X=H[f'H1a|{s}']['D'], ratio=H[f'H1a|{s}']['D'] / t['D'])
    res['descriptive_manuscript'] = DW; log('DW', DW)
    # natural prose reference
    rng = np.random.default_rng(NSEED)
    from c070_word2_sh import parse
    ll = np.array([len(l['words']) for l in parse(dict(FILES)['IT2a']) if l['L'] == 'B'])
    C = 'data/corpora/'; NL = {}
    for name, fn in (('Latin Caesar', 'pg218.txt'), ('Latin Descartes', 'pg23306.txt'), ('Italian Dante', 'pg1012.txt'),
                     ('Spanish Cervantes', 'pg2000.txt'), ('Finnish Kivi', 'pg11940.txt')):
        w = [x for l in gutenberg(C + fn) for x in l]; lines, i = [], 0
        while i < len(w) and len(lines) < 2000:
            n = int(rng.choice(ll)); lines.append(w[i:i + n]); i += n
        lines = [np.array([len(x) for x in l[2:-1]], float) for l in lines if len(l) >= 6]
        runs = [lines[j:j + 8] for j in range(0, len(lines), 8)]; S = Runs(runs)
        tx = testX(S, rng, 500); tw = W.test(W.Lines([list(x) for x in S.lines]), rng, 500)
        NL[name] = dict(D_X=tx['D'], p_X=tx['p'], D_W=tw['D'], p_W=tw['p'], ratio=tx['D'] / tw['D'] if tw['D'] else None)
    res['descriptive_natural'] = NL; log('NL', NL)
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('verdict', ver)

if __name__ == '__main__':
    main()
