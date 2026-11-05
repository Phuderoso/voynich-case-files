"""C016 shared code: parsing label loci and running text from IVTFF files, glyph units, single-word features,
same-page null draws and planted shifts. Used by c016_power_design.py (design step) and c016_label_features.py
(counted run). Pre-registered in case-file/C016-label-features-power-first.md."""
import re, random
from collections import Counter, defaultdict
import numpy as np

UNITS = ['cth', 'ckh', 'cph', 'cfh', 'ch', 'sh']          # C003 glyph units
GALLOWS = {'k', 't', 'p', 'f', 'cth', 'ckh', 'cph', 'cfh'}
C015_TYPES = ('Ln', 'Lt', 'Lz', 'Ls', 'La', 'Lc', 'Lf', 'Lp')
EXCL_MARGIN_COLUMNS = ('f49v', 'f66r')                      # columns of isolated glyphs in the margin, not drawing labels

# dataset name -> (file, label predicate(locus_type, page))
DATASETS = {
    # D1: ZL label loci never analysed in C001-C015 (C015 counted only the C015 types + L0 on fRos). Lx (marginal
    # writing, 3 loci) was dropped after the first design run because its text was seen while locating it.
    'D1_ZL_heldout': ('data/ZL3b-n.txt', lambda lt, pg: lt == 'L0' and pg not in ('fRos',) + EXCL_MARGIN_COLUMNS),
    # D2: Takahashi's independent reading of the C015 label loci (no fRos in this file)
    'D2_IT_C015loci': ('data/IT2a-n.txt', lambda lt, pg: lt in C015_TYPES or (lt == 'L0' and pg == 'fRos')),
    # D0: re-analysis of the very labels where the lead was seen (reported, not counted)
    'D0_ZL_C015loci': ('data/ZL3b-n.txt', lambda lt, pg: lt in C015_TYPES or (lt == 'L0' and pg == 'fRos')),
}
FEATURES = ['o_init', 'len', 'y_fin', 'q_init', 'gallows']

def units(w):
    out, i = [], 0
    while i < len(w):
        for u in UNITS:
            if w.startswith(u, i): out.append(u); i += len(u); break
        else: out.append(w[i]); i += 1
    return out

def clean(t):
    """C003/C015 cleaning: drop <...> tags and @nnn; codes, first alternative of [a:b], uncertain spaces split."""
    t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
    t = re.sub(r'\[([^:\]]*):([^\]]*)\]', lambda m: m.group(1).split(':')[0], t)
    t = t.replace('{', '').replace('}', '').replace("'", '')
    return [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]

def parse(src, pred):
    """labels: list of (page, locus, word); running: page -> list of words (non-L loci);
    line_init / line_fin: page -> first / last word of each running-text line."""
    labels, running, li, lf, cur = [], defaultdict(list), defaultdict(list), defaultdict(list), None
    for line in open(src, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m: cur = m.group(1); continue
        m = re.match(r'<(f\w+)\.(\d+[a-z]?),.(\w\w)>\s*(.*)', line)
        if not m: continue
        pg, loc, lt, ws = m.group(1), m.group(2), m.group(3), clean(m.group(4))
        if lt[0] != 'L':
            running[pg].extend(ws)
            if ws: li[pg].append(ws[0]); lf[pg].append(ws[-1])
            continue
        if pred(lt, pg): labels.extend((pg, loc, w) for w in ws)
    return labels, running, li, lf

def feat(w, f):
    u = units(w)
    if f == 'o_init': return float(u[0] == 'o')
    if f == 'len': return float(len(u))
    if f == 'y_fin': return float(u[-1] == 'y')
    if f == 'q_init': return float(u[0] == 'q')
    if f == 'gallows': return float(any(x in GALLOWS for x in u))
    raise KeyError(f)

class Sampler:
    """Same-page null: each label token is replaced by a running-text token of the same page, drawn without
    replacement; a page with fewer than 2k running tokens (k = its label tokens) draws from the pooled running text
    of all the dataset's label pages (as C015)."""
    def __init__(self, labels, running):
        self.pc = Counter(p for p, _, _ in labels)
        self.pool = [w for p in sorted(self.pc) for w in running[p]]
        self.src = {p: (running[p] if len(running[p]) >= 2 * k else self.pool) for p, k in self.pc.items()}
        self.pooled_pages = sorted(p for p, k in self.pc.items() if len(running[p]) < 2 * k)
    def draw(self, rng):
        out = []
        for p, k in sorted(self.pc.items()):
            s = self.src[p]; out.extend(s[i] for i in rng.choice(len(s), size=k, replace=False))
        return out
    def null_matrix(self, rng, R, feats):
        """R x len(feats) matrix of mean feature values of null draws."""
        cache = {}
        def fv(w):
            if w not in cache: cache[w] = np.array([feat(w, f) for f in feats])
            return cache[w]
        M = np.zeros((R, len(feats)))
        for r in range(R): M[r] = np.mean([fv(w) for w in self.draw(rng)], axis=0)
        return M

def pval(obs, null):
    null = np.asarray(null); n = len(null)
    hi = (1 + (null >= obs - 1e-12).sum()) / (n + 1); lo = (1 + (null <= obs + 1e-12).sum()) / (n + 1)
    return min(1.0, 2 * min(hi, lo)), ('more' if hi <= lo else 'less')

class Planter:
    """Planted shifts of known size on a pseudo-label draw. Rates: +/- delta absolute (expected), by rewriting
    eligible words; length: +/- delta glyph units on average, by inserting / deleting one unit."""
    def __init__(self, running_words):
        U = Counter(u for w in running_words for u in units(w))
        self.units = list(U); self.uw = np.array([U[u] for u in self.units], float); self.uw /= self.uw.sum()
        I = Counter(units(w)[0] for w in running_words if units(w)[0] != 'o')
        self.init_non_o = list(I); self.iw = np.array([I[u] for u in self.init_non_o], float); self.iw /= self.iw.sum()
        F = Counter(units(w)[-1] for w in running_words if units(w)[-1] != 'y')
        self.fin_non_y = list(F); self.fw = np.array([F[u] for u in self.fin_non_y], float); self.fw /= self.fw.sum()
        G = Counter(u for w in running_words for u in units(w) if u in GALLOWS)
        self.gal = list(G); self.gw = np.array([G[u] for u in self.gal], float); self.gw /= self.gw.sum()
        N = Counter(u for w in running_words for u in units(w) if u not in GALLOWS)
        self.ng = list(N); self.nw = np.array([N[u] for u in self.ng], float); self.nw /= self.nw.sum()
    def pick(self, rng, items, w): return items[rng.choice(len(items), p=w)]
    def apply(self, words, f, delta, rng):
        """delta > 0 raises the feature, < 0 lowers it. Returns new list."""
        n = len(words); us = [units(w) for w in words]; up = delta > 0; d = abs(delta)
        if f == 'len':
            elig = [i for i, u in enumerate(us) if up or len(u) >= 2]
        else:
            has = [feat(w, f) > 0 for w in words]
            elig = [i for i in range(n) if has[i] != up]
        if not elig: return list(words)
        prob = min(1.0, d * n / len(elig))
        for i in elig:
            if rng.random() >= prob: continue
            u = us[i]
            if f == 'len':
                if up: j = rng.integers(0, len(u) + 1); u.insert(j, self.pick(rng, self.units, self.uw))
                else: del u[rng.integers(0, len(u))]
            elif f == 'o_init': u[0] = 'o' if up else self.pick(rng, self.init_non_o, self.iw)
            elif f == 'y_fin': u[-1] = 'y' if up else self.pick(rng, self.fin_non_y, self.fw)
            elif f == 'q_init':
                if up: u.insert(0, 'q')
                else:
                    del u[0]
                    if not u: u.append(self.pick(rng, self.units, self.uw))
            elif f == 'gallows':
                if up: u[rng.integers(0, len(u))] = self.pick(rng, self.gal, self.gw)
                else: us[i] = u = [x if x not in GALLOWS else self.pick(rng, self.ng, self.nw) for x in u]
            us[i] = u
        return [''.join(u) for u in us]
