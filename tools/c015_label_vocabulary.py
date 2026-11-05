#!/usr/bin/env python3
"""C015 (new family: label vocabulary). Do bath (Ln/Lt), rosette (fRos L0) and astro/zodiac (Lz/Ls/La) labels differ
from plant/pharma labels (Lc/Lf/Lp) in glyph profile or word types MORE (or LESS) than the running text of the same
pages does?  Pre-registered in case-file/C015-label-vocabulary.md.

Statistics (higher = more separated):
  S_g = Jensen-Shannon divergence (bits) between the two groups' glyph-bigram distributions (C003 units, with word
        start ^ and end $ markers), tokens counted with repetition.
  S_w = 1 - |T_X & T_Y| / min(|T_X|, |T_Y|), T = set of distinct word types of a group.
Tests:
  T2 (decisive, 'beyond running text'): each label token is replaced by a token drawn without replacement from the
     running text (all non-L loci: P, C, R) of the same page (S_w: drawn from the page's distinct types). Pages with
     fewer than 2k running tokens/types (k = label tokens on the page) draw from the pooled running text of the
     group's pages instead. R = 1999 draws. Two-sided p = min(1, 2 min(p_lo, p_hi)).
  T1 ('any separation'): page-block permutation of group membership among the pair's pages (page counts kept),
     R = 1999. Only for pairs where both groups have >= 5 label pages (BIO-PP, AZ-PP); ROS is one page.
Gate: planted separation (fraction f of group-X tokens rewritten by the unit swap k<->t, ch<->sh) must be detected
  (p <= ALPHA, more-separated direction) in >= 9/10 replicates at f = 0.5 for a (pair, stat, test) to be testable.
  f = 0.25 is reported as a power point.
FPR: T2 leave-one-out over the R null draws; T1 200 random page reassignments each tested with R = 1999.
Usage: python3 tools/c015_label_vocabulary.py [--smoke]   (writes analysis/C015_results.json, checkpoints per stage)
"""
import re, sys, json, time, random, os
from collections import Counter, defaultdict
import numpy as np

SRC = 'data/ZL3b-n.txt'
OUT = 'analysis/C015_results.json'
SMOKE = '--smoke' in sys.argv
R = 199 if SMOKE else 1999
NPLANT = 3 if SMOKE else 10
NFPR1 = 10 if SMOKE else 200
ALPHA = 0.005           # Bonferroni over the 10 counted looks (6 T2 + 4 T1)
UNITS = ['cth', 'ckh', 'cph', 'cfh', 'ch', 'sh']
GROUPS = {'BIO': lambda lt, pg, I: lt in ('Ln', 'Lt'),
          'ROS': lambda lt, pg, I: lt == 'L0' and pg == 'fRos',
          'AZ':  lambda lt, pg, I: lt in ('Lz', 'Ls', 'La'),
          'PP':  lambda lt, pg, I: lt in ('Lc', 'Lf', 'Lp')}
PAIRS = [('BIO', 'PP'), ('ROS', 'PP'), ('AZ', 'PP')]
T1_PAIRS = [('BIO', 'PP'), ('AZ', 'PP')]
SWAP = {'k': 't', 't': 'k', 'ch': 'sh', 'sh': 'ch'}

def units(w):
    out, i = [], 0
    while i < len(w):
        for u in UNITS:
            if w.startswith(u, i): out.append(u); i += len(u); break
        else: out.append(w[i]); i += 1
    return out

def clean(t, split_commas=True, alt=0):
    t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
    t = re.sub(r'\[([^:\]]*):([^\]]*)\]', (lambda m: m.group(1 + alt).split(':')[0]), t)
    t = t.replace('{', '').replace('}', '').replace("'", '')
    if not split_commas: t = t.replace(',', '')
    return [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]

def parse(split_commas=True, alt=0):
    """labels[group] = list of (page, word); running[page] = list of words (non-L loci); also locus counts."""
    labels, running, loci, cur = defaultdict(list), defaultdict(list), Counter(), None
    for line in open(SRC, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip(): continue
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m: cur = (m.group(1), dict(re.findall(r'\$(\w)=(\S+)', m.group(2))).get('I')); continue
        m = re.match(r'<(f\w+)\.\d+[a-z]?,.(\w\w)>\s*(.*)', line)
        if not m: continue
        lt, ws = m.group(2), clean(m.group(3), split_commas, alt)
        if lt[0] != 'L': running[cur[0]].extend(ws); continue
        for g, f in GROUPS.items():
            if f(lt, cur[0], cur[1]):
                loci[g] += 1; labels[g].extend((cur[0], w) for w in ws)
    return labels, running, loci

class Feat:
    def __init__(self):
        self.idx = {}
    def vec(self, w):
        u = ['^'] + units(w) + ['$']; out = []
        for a, b in zip(u, u[1:]): out.append(self.idx.setdefault((a, b), len(self.idx)))
        return out

def swap(w):
    return ''.join(SWAP.get(u, u) for u in units(w))

def jsd_rows(P, Q):
    """JSD in bits between rows of count matrices P, Q (R x F)."""
    P = P / P.sum(-1, keepdims=True); Q = Q / Q.sum(-1, keepdims=True); M = 0.5 * (P + Q)
    def kl(A):
        with np.errstate(divide='ignore', invalid='ignore'):
            t = np.where(A > 0, A * np.log2(A / M), 0.0)
        return t.sum(-1)
    return 0.5 * kl(P) + 0.5 * kl(Q)

def s_w(tx, ty):
    tx, ty = set(tx), set(ty)
    return 1 - len(tx & ty) / min(len(tx), len(ty))

def pval(obs, null):
    null = np.asarray(null); n = len(null)
    hi = (1 + (null >= obs - 1e-12).sum()) / (n + 1); lo = (1 + (null <= obs + 1e-12).sum()) / (n + 1)
    return min(1.0, 2 * min(hi, lo)), ('more' if hi <= lo else 'less')

def main():
    t0 = time.time(); res = {'smoke': SMOKE, 'R': R, 'alpha': ALPHA, 'stages': {}}
    def ck(stage, obj):
        res['stages'][stage] = obj; res['elapsed_s'] = round(time.time() - t0, 1)
        json.dump(res, open(OUT if not SMOKE else '/tmp/C015_smoke.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
        print(f'[{time.time()-t0:7.1f}s] {stage} done', flush=True)
    labels, running, loci = parse()
    feat = Feat()
    allwords = {w for g in labels for _, w in labels[g]} | {w for p in running for w in running[p]}
    allwords |= {swap(w) for w in allwords}
    for w in sorted(allwords): feat.vec(w)
    NF = len(feat.idx); fv = {}
    def vec(w):
        if w not in fv:
            v = np.zeros(NF, np.float64)
            for i in feat.vec(w): v[i] += 1
            fv[w] = v
        return fv[w]
    # inventory
    inv = {g: {'loci': loci[g], 'tokens': len(labels[g]), 'types': len({w for _, w in labels[g]}),
               'pages': sorted({p for p, _ in labels[g]})} for g in GROUPS}
    for g in GROUPS:
        pc = Counter(p for p, _ in labels[g])
        inv[g]['page_tokens'] = dict(pc)
        inv[g]['running_tokens_on_label_pages'] = sum(len(running[p]) for p in pc)
        inv[g]['pages_pooled_tokens'] = [p for p in pc if len(running[p]) < 2 * pc[p]]
        inv[g]['pages_pooled_types'] = [p for p in pc if len(set(running[p])) < 2 * pc[p]]
    ck('inventory', inv)

    # ---------- descriptive profiles ----------
    def prof(words):
        n = len(words); fi = Counter(units(w)[0] for w in words); la = Counter(units(w)[-1] for w in words)
        return {'n': n, 'mean_units': round(float(np.mean([len(units(w)) for w in words])), 2),
                'top_initial': [(k, round(v / n, 3)) for k, v in fi.most_common(5)],
                'top_final': [(k, round(v / n, 3)) for k, v in la.most_common(5)],
                'top_words': Counter(words).most_common(8)}
    desc = {}
    for g in GROUPS:
        lw = [w for _, w in labels[g]]; rw = [w for p in inv[g]['pages'] for w in running[p]]
        desc[g] = {'labels': prof(lw), 'running_same_pages': prof(rw)}
    ck('descriptive', desc)

    # ---------- T2 machinery ----------
    def pseudo(group_tokens, g, rng, types=False):
        """one pseudo-label draw for a group: list of words."""
        pc = Counter(p for p, _ in group_tokens); out = []
        pool_all = [w for p in pc for w in running[p]]
        if types: pool_all = sorted(set(pool_all))
        for p, k in sorted(pc.items()):
            src = running[p] if not types else sorted(set(running[p]))
            if len(src) < 2 * k: src = pool_all
            idx = rng.choice(len(src), size=k, replace=False)
            out.extend(src[i] for i in idx)
        return out
    def counts(words):
        v = np.zeros(NF)
        for w in words: v += vec(w)
        return v
    def plant(words, f, rng):
        return [swap(w) if rng.random() < f else w for w in words]

    T2 = {}
    for X, Y in PAIRS:
        rng = np.random.default_rng(1501)
        lx = [w for _, w in labels[X]]; ly = [w for _, w in labels[Y]]
        obs_g = float(jsd_rows(counts(lx)[None], counts(ly)[None])[0]); obs_w = s_w(lx, ly)
        nx_g, ny_g, nx_w, ny_w, ng, nw = [], [], [], [], [], []
        for r in range(R):
            px, py = pseudo(labels[X], X, rng), pseudo(labels[Y], Y, rng)
            nx_g.append(counts(px)); ny_g.append(counts(py))
            tx, ty = pseudo(labels[X], X, rng, True), pseudo(labels[Y], Y, rng, True)
            nw.append(s_w(tx, ty))
        ng = jsd_rows(np.array(nx_g), np.array(ny_g)); nw = np.array(nw)
        pg, dg = pval(obs_g, ng); pw, dw = pval(obs_w, nw)
        # FPR: leave-one-out over null draws
        fpr = {}
        for name, arr in (('S_g', ng), ('S_w', nw)):
            ps = [pval(arr[i], np.delete(arr, i))[0] for i in range(len(arr))]
            fpr[name] = {'at_0.05': round(float(np.mean(np.array(ps) <= 0.05)), 4),
                         'at_alpha': round(float(np.mean(np.array(ps) <= ALPHA)), 4)}
        # planted gate
        gate = {}
        for f in (0.5, 0.25):
            hits_g, hits_w, sg, sw = 0, 0, [], []
            for k in range(NPLANT):
                prng = np.random.default_rng(15100 + k); rr = random.Random(15200 + k)
                px, py = pseudo(labels[X], X, prng), pseudo(labels[Y], Y, prng)
                px = plant(px, f, rr)
                s = float(jsd_rows(counts(px)[None], counts(py)[None])[0]); p, d = pval(s, ng)
                hits_g += (p <= ALPHA and d == 'more'); sg.append(round(s, 4))
                tx, ty = pseudo(labels[X], X, prng, True), pseudo(labels[Y], Y, prng, True)
                tx = plant(tx, f, rr); s = s_w(tx, ty); p, d = pval(s, nw)
                hits_w += (p <= ALPHA and d == 'more'); sw.append(round(s, 4))
            gate[str(f)] = {'S_g_hits': hits_g, 'S_w_hits': hits_w, 'n': NPLANT, 'S_g_planted': sg, 'S_w_planted': sw}
        T2[f'{X}-{Y}'] = {'S_g_obs': round(obs_g, 4), 'S_g_null_mean': round(float(ng.mean()), 4),
                          'S_g_null_q': [round(float(q), 4) for q in np.quantile(ng, [0.0025, 0.5, 0.9975])],
                          'S_g_p': round(pg, 4), 'S_g_dir': dg,
                          'S_w_obs': round(obs_w, 4), 'S_w_null_mean': round(float(nw.mean()), 4),
                          'S_w_null_q': [round(float(q), 4) for q in np.quantile(nw, [0.0025, 0.5, 0.9975])],
                          'S_w_p': round(pw, 4), 'S_w_dir': dw, 'fpr': fpr, 'gate': gate}
        ck(f'T2_{X}-{Y}', T2[f'{X}-{Y}'])

    # ---------- T1: page-block permutation ----------
    T1 = {}
    for X, Y in T1_PAIRS:
        pages = sorted(set(inv[X]['pages']) | set(inv[Y]['pages'])); nX = len(inv[X]['pages'])
        if set(inv[X]['pages']) & set(inv[Y]['pages']): raise SystemExit('page in both groups')
        def page_data(lab):
            pw = defaultdict(list)
            for g in (X, Y):
                for p, w in lab[g]: pw[p].append(w)
            Cg = np.array([counts(pw[p]) for p in pages])
            vocab = sorted({w for p in pages for w in pw[p]}); vi = {w: i for i, w in enumerate(vocab)}
            Bw = np.zeros((len(pages), len(vocab)), bool)
            for i, p in enumerate(pages):
                for w in pw[p]: Bw[i, vi[w]] = True
            return Cg, Bw
        def stats(Cg, Bw, A):
            """A: (n, pages) bool membership in X; returns S_g, S_w arrays."""
            A = A.astype(float); Bf = Bw.astype(float)
            sg = jsd_rows(A @ Cg, (1 - A) @ Cg)
            tx = (A @ Bf) > 0; ty = ((1 - A) @ Bf) > 0
            inter = (tx & ty).sum(1); mn = np.minimum(tx.sum(1), ty.sum(1))
            return sg, 1 - inter / mn
        def perms(rng, n):
            A = np.zeros((n, len(pages)), bool)
            for i in range(n): A[i, rng.choice(len(pages), nX, replace=False)] = True
            return A
        truth = np.array([[p in inv[X]['pages'] for p in pages]])
        Cg, Bw = page_data(labels)
        og, ow = stats(Cg, Bw, truth); rng = np.random.default_rng(1520)
        NA = perms(rng, R); ng, nw = stats(Cg, Bw, NA)
        pg, dg = pval(og[0], ng); pw, dw = pval(ow[0], nw)
        # FPR: random reassignment as observed, fresh permutation null each time
        f05g = f05w = fag = faw = 0
        for i in range(NFPR1):
            Ao = perms(rng, 1); sg0, sw0 = stats(Cg, Bw, Ao); N2 = perms(rng, R); g2, w2 = stats(Cg, Bw, N2)
            a, _ = pval(sg0[0], g2); b, _ = pval(sw0[0], w2)
            f05g += a <= 0.05; f05w += b <= 0.05; fag += a <= ALPHA; faw += b <= ALPHA
        fpr = {'S_g': {'at_0.05': f05g / NFPR1, 'at_alpha': fag / NFPR1}, 'S_w': {'at_0.05': f05w / NFPR1, 'at_alpha': faw / NFPR1}, 'n': NFPR1}
        gate = {}
        for f in (0.5, 0.25):
            hg = hw = 0; sgl, swl = [], []
            for k in range(NPLANT):
                prng = np.random.default_rng(15300 + k); rr = random.Random(15400 + k)
                Ao = perms(prng, 1)[0]; xs = {pages[i] for i in range(len(pages)) if Ao[i]}
                lab2 = {X: [], Y: []}
                for g in (X, Y):
                    for p, w in labels[g]:
                        if p in xs: lab2[X].append((p, swap(w) if rr.random() < f else w))
                        else: lab2[Y].append((p, w))
                C2, B2 = page_data(lab2)
                s1, s2 = stats(C2, B2, Ao[None]); N3 = perms(prng, R); g3, w3 = stats(C2, B2, N3)
                a, da = pval(s1[0], g3); b, db = pval(s2[0], w3)
                hg += (a <= ALPHA and da == 'more'); hw += (b <= ALPHA and db == 'more')
                sgl.append(round(float(s1[0]), 4)); swl.append(round(float(s2[0]), 4))
            gate[str(f)] = {'S_g_hits': hg, 'S_w_hits': hw, 'n': NPLANT, 'S_g_planted': sgl, 'S_w_planted': swl}
        T1[f'{X}-{Y}'] = {'pages': len(pages), 'pages_X': nX, 'S_g_obs': round(float(og[0]), 4), 'S_g_null_q': [round(float(q), 4) for q in np.quantile(ng, [0.0025, 0.5, 0.9975])],
                          'S_g_p': round(pg, 4), 'S_g_dir': dg, 'S_w_obs': round(float(ow[0]), 4),
                          'S_w_null_q': [round(float(q), 4) for q in np.quantile(nw, [0.0025, 0.5, 0.9975])],
                          'S_w_p': round(pw, 4), 'S_w_dir': dw, 'fpr': fpr, 'gate': gate}
        ck(f'T1_{X}-{Y}', T1[f'{X}-{Y}'])

    # ---------- transcription-choice sensitivity (descriptive, primary pair, T2 S_g/S_w obs only vs same null size) ----------
    sens = {}
    for name, kw in (('commas_joined', {'split_commas': False}), ('second_alternative', {'alt': 1})):
        lab2, run2, _ = parse(**kw)
        lx = [w for _, w in lab2['BIO']]; ly = [w for _, w in lab2['PP']]
        for w in set(lx + ly) | {w for p in run2 for w in run2[p]}: feat.vec(w)
        NF2 = len(feat.idx)
        def cnt2(ws):
            v = np.zeros(NF2)
            for w in ws:
                for i in feat.vec(w): v[i] += 1
            return v
        rng = np.random.default_rng(1501); ng2, nw2 = [], []
        global_running = running
        for r in range(min(R, 999)):
            def ps(gt, types=False):
                pc = Counter(p for p, _ in gt); out = []; pool = [w for p in pc for w in run2[p]]
                if types: pool = sorted(set(pool))
                for p, k in sorted(pc.items()):
                    src = run2[p] if not types else sorted(set(run2[p]))
                    if len(src) < 2 * k: src = pool
                    out.extend(src[i] for i in rng.choice(len(src), size=k, replace=False))
                return out
            ng2.append(float(jsd_rows(cnt2(ps(lab2['BIO']))[None], cnt2(ps(lab2['PP']))[None])[0]))
            nw2.append(s_w(ps(lab2['BIO'], True), ps(lab2['PP'], True)))
        og2 = float(jsd_rows(cnt2(lx)[None], cnt2(ly)[None])[0]); ow2 = s_w(lx, ly)
        sens[name] = {'tokens': [len(lx), len(ly)], 'S_g_obs': round(og2, 4), 'S_g_p': round(pval(og2, ng2)[0], 4), 'S_g_dir': pval(og2, ng2)[1],
                      'S_w_obs': round(ow2, 4), 'S_w_p': round(pval(ow2, nw2)[0], 4), 'S_w_dir': pval(ow2, nw2)[1], 'R': len(ng2)}
    ck('sensitivity_BIO-PP', sens)
    if not SMOKE: print(json.dumps({'T2': {k: {kk: v[kk] for kk in ('S_g_obs', 'S_g_p', 'S_g_dir', 'S_w_obs', 'S_w_p', 'S_w_dir')} for k, v in T2.items()}}, indent=1))

if __name__ == '__main__':
    main()
