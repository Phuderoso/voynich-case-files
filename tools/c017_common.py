"""C017 shared code: label-TYPE contrast with a page-level permutation null.
Units are (page, label class) blocks. A unit's excess for a feature = mean feature of its label tokens minus the mean
feature of the running text of the same page (pooled running text of all counted label pages if the page has fewer
than 2k running tokens, k = the page's counted label tokens; as C015/C016).
Classes: drawing-element labels BIO (Ln, Lt), ROS (L0 on fRos), AZ (Lz, Ls, La), PP (Lc, Lf, Lp) = group A;
free-standing labels FREE (L0 not on fRos and not on the marginal glyph columns f49v, f66r) = group B.
Pre-registered in case-file/C017-label-genre-contrast.md. Reuses C016 cleaning, glyph units, features and planter."""
import re
from collections import Counter, defaultdict
import numpy as np
from c016_common import clean, units, feat, Planter, FEATURES

SUBCLASS = {'Ln': 'BIO', 'Lt': 'BIO', 'Lz': 'AZ', 'Ls': 'AZ', 'La': 'AZ', 'Lc': 'PP', 'Lf': 'PP', 'Lp': 'PP'}
A_CLASSES = ('BIO', 'ROS', 'AZ', 'PP')
EXCL = ('f49v', 'f66r')
FILES = {'ZL': 'data/ZL3b-n.txt', 'IT': 'data/IT2a-n.txt'}

def label_class(lt, pg):
    if lt in SUBCLASS: return SUBCLASS[lt]
    if lt == 'L0':
        if pg == 'fRos': return 'ROS'
        if pg in EXCL: return None
        return 'FREE'
    return None

def parse(src):
    """labels: list of (page, class, word); running: page -> list of words (non-label loci P, C, R)."""
    labels, running = [], defaultdict(list)
    for line in open(src, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)\.(\d+[a-z]?),.(\w\w)>\s*(.*)', line.rstrip('\n'))
        if not m: continue
        pg, lt, ws = m.group(1), m.group(3), clean(m.group(4))
        if lt[0] != 'L': running[pg].extend(ws); continue
        c = label_class(lt, pg)
        if c: labels.extend((pg, c, w) for w in ws)
    return labels, running

class Design:
    """Unit inventory + same-page pseudo-label sampler + permutation matrices."""
    def __init__(self, src, R, perm_seed):
        self.labels, self.running = parse(src)
        uc = Counter((p, c) for p, c, _ in self.labels)
        self.units = sorted(uc); self.k = np.array([uc[u] for u in self.units], float)
        self.cls = [c for _, c in self.units]
        self.g = np.array([c != 'FREE' for c in self.cls], float)            # 1 = drawing-element (A)
        pc = Counter(p for p, _, _ in self.labels); self.pc = pc
        self.pool = [w for p in sorted(pc) for w in self.running[p]]
        self.src = {p: (self.running[p] if len(self.running[p]) >= 2 * k else self.pool) for p, k in pc.items()}
        self.pooled_pages = sorted(p for p, k in pc.items() if len(self.running[p]) < 2 * k)
        self.mu = {f: {p: float(np.mean([feat(w, f) for w in self.src[p]])) for p in pc} for f in FEATURES}
        rng = np.random.default_rng(perm_seed)
        self.Gperm = np.array([rng.permutation(self.g) for _ in range(R)])
        self.aidx = np.where(self.g == 1)[0]
        self.acls = np.array([A_CLASSES.index(self.cls[i]) for i in self.aidx])
        self.present = sorted(set(self.acls.tolist()))
        self.Hperm = np.array([rng.permutation(self.acls) for _ in range(R)])
    def inventory(self):
        return {'units': len(self.units), 'A_units': int(self.g.sum()), 'B_units': int((1 - self.g).sum()),
                'tokens_by_class': dict(Counter(self.cls[i] for i in range(len(self.units)) for _ in range(int(self.k[i])))),
                'units_by_class': dict(Counter(self.cls)), 'pages_pooled': self.pooled_pages,
                'B_units_list': {f'{p}': int(k) for (p, c), k in zip(self.units, self.k) if c == 'FREE'}}
    def real_words(self):
        d = defaultdict(list)
        for p, c, w in self.labels: d[(p, c)].append(w)
        return [d[u] for u in self.units]
    def pseudo(self, rng):
        """Same-page draw without replacement for every page; split into the page's units in fixed order."""
        out = []
        drawn = {}
        for p in sorted(self.pc):
            s = self.src[p]; drawn[p] = [s[i] for i in rng.choice(len(s), size=self.pc[p], replace=False)]
        pos = Counter()
        for (p, c), k in zip(self.units, self.k):
            k = int(k); out.append(drawn[p][pos[p]:pos[p] + k]); pos[p] += k
        return out
    def excess(self, unit_words, f):
        return np.array([np.mean([feat(w, f) for w in ws]) - self.mu[f][p] for ws, (p, _) in zip(unit_words, self.units)])
    # --- statistics ---
    def contrast(self, e, G):
        w = self.k; we = w * e
        return (G @ we) / (G @ w) - ((1 - G) @ we) / ((1 - G) @ w)
    def contrast_test(self, e):
        obs = float(self.contrast(e, self.g[None, :])[0]); null = self.contrast(e, self.Gperm)
        n = len(null); hi = (1 + (null >= obs - 1e-12).sum()) / (n + 1); lo = (1 + (null <= obs + 1e-12).sum()) / (n + 1)
        return obs, min(1.0, 2 * min(hi, lo)), ('A>B' if hi <= lo else 'A<B')
    def hetero(self, e, L):
        w = self.k[self.aidx]; ea = e[self.aidx]; W = w.sum(); Eb = (w * ea).sum() / W
        L = np.atleast_2d(L); s = np.zeros(L.shape[0])
        for c in self.present:
            M = (L == c).astype(float); Wc = M @ w; Sc = M @ (w * ea)
            s += np.where(Wc > 0, Wc * (Sc / np.maximum(Wc, 1e-12) - Eb) ** 2, 0) / W
        return s
    def hetero_test(self, e):
        obs = float(self.hetero(e, self.acls)[0]); null = self.hetero(e, self.Hperm)
        return obs, float((1 + (null >= obs - 1e-12).sum()) / (len(null) + 1))
    def resid_sd(self, e):
        """Token-weighted SD of unit excesses around their group (A / B) means: between-unit heterogeneity."""
        w = self.k; r = np.empty_like(e)
        for gv in (0, 1):
            m = self.g == gv; r[m] = e[m] - (w[m] * e[m]).sum() / w[m].sum()
        return float(np.sqrt((w * r ** 2).sum() / w.sum()))

def plant(D, P, unit_words, f, target_mask, delta, tau, rng):
    """Shift delta on target units plus a unit-level random effect N(0, tau) on every unit (page heterogeneity)."""
    out = []
    for i, ws in enumerate(unit_words):
        d = (delta if target_mask[i] else 0.0) + (rng.normal(0, tau) if tau > 0 else 0.0)
        out.append(P.apply(ws, f, d, rng) if abs(d) > 1e-9 else list(ws))
    return out

# ---- studentized contrast (adopted in design run 3: the raw token-weighted contrast was miscalibrated under page
# heterogeneity, design runs 1-2). t = (E_A - E_B) / sqrt(V_A + V_B), V_g = sum w^2 (e - E_g)^2 / (sum w)^2
# (cluster-robust variance of a weighted mean, units = clusters). Studentized permutation tests stay valid under
# unequal unit variances (Janssen 1997; Chung & Romano 2013), approximately for few units.
def _tstat(self, e, G):
    w = self.k; G = np.atleast_2d(G); H = 1 - G
    def mv(M):
        W = M @ w; m = (M @ (w * e)) / W
        v = (M * (w[None, :] ** 2) * (e[None, :] - m[:, None]) ** 2).sum(1) / W ** 2
        return m, v
    mA, vA = mv(G); mB, vB = mv(H)
    return (mA - mB) / np.sqrt(vA + vB + 1e-12)
def _ttest(self, e):
    obs = float(_tstat(self, e, self.g)[0]); null = _tstat(self, e, self.Gperm)
    n = len(null); hi = (1 + (null >= obs - 1e-12).sum()) / (n + 1); lo = (1 + (null <= obs + 1e-12).sum()) / (n + 1)
    return obs, min(1.0, 2 * min(hi, lo)), ('A>B' if hi <= lo else 'A<B')
Design.tstat = _tstat; Design.t_test = _ttest

# ---- size-blocked permutation (adopted in design run 3, as C002's size-blocked null): group labels are permuted
# only among units of similar label-token count k, so units with very different sampling variance are never swapped.
SIZE_EDGES = (1, 4, 8, 13, 20, 30, 10**9)      # blocks k in [1,3], [4,7], [8,12], [13,19], [20,29], [30,+)
def size_blocks(k):
    return np.searchsorted(np.array(SIZE_EDGES), k, side='right') - 1
def blocked_perms(g, k, R, seed):
    rng = np.random.default_rng(seed); b = size_blocks(k); out = np.empty((R, len(g)))
    for r in range(R):
        x = g.copy()
        for bb in np.unique(b):
            idx = np.where(b == bb)[0]; x[idx] = rng.permutation(g[idx])
        out[r] = x
    return out
def use_blocked(D, R, seed):
    D.Gperm = blocked_perms(D.g, D.k, R, seed); return D
