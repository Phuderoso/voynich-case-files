#!/usr/bin/env python3
"""C123 (F-MID step 4): copying or drift? Two nulls beyond N-PAGE for the C120/C121/C122 statistic.
Instrument imported UNCHANGED: c120_mi_distance.Stream / recut / holm / LAGS / FILES, c121_mi_calibrated.plant / controls,
 c070_word2_sh.parse (retention filters). M = sum_d plug-in MI(d), d in (16,24,32,48,64,96,128,192,256), pairs inside a page.
New here ONLY: paragraph ids (rule below), block ids, the two permutations N-PARA and N-BLOCK, their pseudo replicates,
 the per-(stratum, null, transcription) calibration / gates / H1 / descriptives, the decision rule. See
 case-file/C123-mi-para-block.md (the pre-registration) for the full rule; this docstring is a summary.
PARAGRAPH RULE (frozen). Walk every P-locus line of a page in file order, retained by the C070 filters or not. State
 open_new starts True at each page. A line whose text contains '<%>' (anywhere: it may follow a '<!..>' comment) sets open_new. A RETAINED line first closes the
 state: if open_new it gets a new paragraph id (open_new <- False), else it joins the current paragraph. After the line (retained
 or dropped, '<->' lines included) a '<$>' anywhere in its text sets open_new. So '<$>' closes a paragraph and the next
 retained line opens a new one whether or not it carries '<%>'; dropped lines carry their marks. Non-P loci are ignored.
BLOCK RULE (frozen). Retained lines of a page, in order. Offset o (0 main, 2 descriptive D-OFF): lines [0,o) are fixed head;
 then consecutive FULL blocks of 4 lines; the remaining 0-3 lines are a fixed tail. N-BLOCK permutes the full blocks of a page
 among their own slots; head and tail stay in place. Blocks ignore paragraph boundaries.
N-PARA: words permuted inside each paragraph (unit lengths, multiset of each paragraph kept).
Run: python3 tools/c123_mi_para_block.py run   (resumable, checkpoints in analysis/c123_ckpt/)
     python3 tools/c123_mi_para_block.py struct   (STRUCTURE ONLY: paragraph / block counts, no statistic)
     C123_DRY=1 python3 tools/c123_mi_para_block.py dry   (self-test: manuscript replaced by Latin Caesar recut, tiny R)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, re, json, time, hashlib
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c120_mi_distance import Stream, recut, holm, LAGS, FILES
from c121_mi_calibrated import plant, controls
from c070_word2_sh import parse
from c003_position_rigidity import units

CSEED, GSEED, SEED, ISEED, DSEED, RESERVED = 11827, 11828, 11829, 11830, 11831, 11832
ALPHA, NT = 0.05, 8
AG = ALPHA / NT                      # 0.00625; with R_c = R_g = 200 the p floor is 1/201 = 0.004975 (needs 0 null >= M)
R, RG, RC, RD, NG, NC = 2000, 200, 200, 1000, 20, 8
EB = {'S': 0.0070, 'CB': 0.0071}     # public mean over the two transcriptions of the N-PAGE E (C121/C122)
LADDER = sorted([(1.0, 2), (1.0, 3), (0.75, 4), (0.75, 5), (1.0, 4), (1.0, 5), (1.0, 6), (1.0, 8), (1.0, 10)],
                key=lambda r: (r[0] * r[1], r[1]))
NULLS = ('PARA', 'BLOCK')
TRANS = ('ZL3b', 'IT2a')
PRIMARY = ('S', 'CB')
SECONDARY = ('BIO', 'H', 'T', 'CBmS')
SECCODE = {'S': 'S', 'BIO': 'B', 'H': 'H', 'T': 'T'}      # ZL3b $I codes
STRATA = PRIMARY + SECONDARY
DRY = os.environ.get('C123_DRY') == '1'
if DRY: STRATA = PRIMARY
if DRY: R, RG, RC, RD, NG, NC = 20, 10, 10, 10, 2, 1
CK = 'analysis/c123_ckpt/' if not DRY else '/tmp/c123_dry_ckpt/'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

# ---------------------------------------------------------------- parsing with paragraph ids (structure only)
def parse_para(path):
    meta, out, cur, open_new, pid, reason = {}, [], None, True, 0, 'page'
    cnt = dict(retained=0, new_by_own_start_mark=0, new_by_dropped_line_start_mark=0, new_by_end_mark_no_start=0,
               new_by_page_start_no_mark=0, retained_continue=0, dropped=0, dropped_with_start=0, dropped_with_end=0,
               start_mark_after_comment=0, end_mark_not_at_line_end=0)
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m or not m.group(4).startswith('P'): continue
        page, t = m.group(1), m.group(5)
        if page != cur: cur, open_new, pid, reason = page, True, 0, 'page'
        starts = '<%>' in t; ends = '<$>' in t
        if starts and not t.lstrip().startswith('<%>'): cnt['start_mark_after_comment'] += 1
        if ends and not t.rstrip().endswith('<$>'): cnt['end_mark_not_at_line_end'] += 1
        if starts: open_new = True
        keep = False
        if '<->' not in t:
            tt = re.sub(r'<[^>]*>', '', t); tt = re.sub(r'@\d+;', '', tt)
            tt = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', tt).replace('{', '').replace('}', '').replace("'", '')
            ws = [w for w in re.split(r'[.,\s]+', tt) if w]
            keep = len(ws) >= 5 and all(re.fullmatch(r'[a-z]+', w) for w in ws)
        if keep:
            cnt['retained'] += 1
            if open_new:
                pid += 1
                if starts: cnt['new_by_own_start_mark'] += 1
                elif reason == 'start': cnt['new_by_dropped_line_start_mark'] += 1
                elif reason == 'end': cnt['new_by_end_mark_no_start'] += 1
                else: cnt['new_by_page_start_no_mark'] += 1
                open_new = False
            else: cnt['retained_continue'] += 1
            d = meta.get(page, {}); out.append(dict(page=page, Q=d.get('Q'), L=d.get('L'), words=ws, pid=pid))
        else:
            cnt['dropped'] += 1; cnt['dropped_with_start'] += starts; cnt['dropped_with_end'] += ends
            if starts: reason = 'start'
        if ends:
            if not open_new: reason = 'end'
            open_new = True
    return out, cnt

def check_retention(path):
    a = [l['words'] for l in parse_para(path)[0]]; b = [l['words'] for l in parse(path)]
    assert a == b, 'retained lines differ from C070 parse()'

def headers(path):
    meta = {}
    for raw in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2)))
    return meta
ZMAP = {p: d.get('I') for p, d in headers(dict(FILES)['ZL3b']).items()}

def pages_of(path, stratum):
    """list of pages; page = (lines, pids). Section map from ZL3b $I for both transcriptions (as C122)."""
    lines, _ = parse_para(path); own = headers(path); pg, order = {}, []
    for l in lines:
        if l['L'] != 'B': continue
        sec = ZMAP.get(l['page']) or own.get(l['page'], {}).get('I')
        if stratum == 'CB': ok = True
        elif stratum == 'CBmS': ok = sec != 'S'
        else: ok = sec == SECCODE[stratum]
        if not ok: continue
        if l['page'] not in pg: pg[l['page']] = ([], []); order.append(l['page'])
        pg[l['page']][0].append(l['words']); pg[l['page']][1].append(l['pid'])
    return [pg[k] for k in order]

def nwords(pages): return sum(len(l) for p, _ in pages for l in p)

# ---------------------------------------------------------------- structure: paragraphs and blocks
def blocks_of(n, off):
    """(head_end, [block start lines], tail_start) for a page with n retained lines."""
    nb = max(0, (n - off) // 4) if n > off else 0
    return off, [off + 4 * j for j in range(nb)], off + 4 * nb

def struct_counts(pages, off=0):
    paras = nb = multi = 0
    ln = []
    for lines, pids in pages:
        paras += len(set(pids)); _, bs, _ = blocks_of(len(lines), off); nb += len(bs); multi += len(bs) >= 2
        c = {}
        for p in pids: c[p] = c.get(p, 0) + 1
        ln += list(c.values())
    return dict(pages=len(pages), lines=sum(len(l) for l, _ in pages), paragraphs=paras, full_blocks=nb, pages_ge2_blocks=multi,
                para_lines_median=float(np.median(ln)), para_lines_mean=float(np.mean(ln)), para_le4=sum(x <= 4 for x in ln),
                para_ge8=sum(x >= 8 for x in ln), words=nwords(pages))

# ---------------------------------------------------------------- stream with the two new nulls
class PStream(Stream):
    def __init__(self, pages, pids, tok=units):
        super().__init__(pages, tok)
        gid, g = [], 0
        self.segs = {0: [], 2: []}      # per offset: list over pages of (fixed_words_head, [block word arrays], tail_words)
        w0 = 0
        for k, (p, ids) in enumerate(zip(pages, pids)):
            last = None
            starts = []; wi = w0
            for li, l in enumerate(p):
                if ids[li] != last: g += 1; last = ids[li]
                gid += [g] * len(l); starts.append(wi); wi += len(l)
            starts.append(wi)
            for off in (0, 2):
                h, bs, t = blocks_of(len(p), off)
                head = np.arange(starts[0], starts[min(h, len(p))]) if h else np.arange(0)
                blks = [np.arange(starts[b], starts[b + 4]) for b in bs]
                tail = np.arange(starts[t], starts[len(p)]) if t < len(p) else np.arange(0)
                self.segs[off].append((head, blks, tail))
            w0 = wi
        self.gid = np.array(gid)
    def _reindex(self, o):
        Lo = self.L[o]; ns = np.r_[0, np.cumsum(Lo)[:-1]]
        idx = np.arange(self.n) - np.repeat(ns, Lo) + np.repeat(self.S[o], Lo)
        return self.x[idx]
    def nperm(self, null, rng):
        if null == 'PAGE': return self.perm(rng)
        return self._reindex(self.norder(null, rng))
    def norder(self, null, rng):
        if null == 'PARA':
            return np.lexsort((rng.random(self.nw), self.gid))
        off = 0 if null == 'BLOCK' else 2
        parts = []
        for head, blks, tail in self.segs[off]:
            parts.append(head)
            if len(blks) >= 2:
                for j in rng.permutation(len(blks)): parts.append(blks[j])
            else: parts += blks
            parts.append(tail)
        return np.concatenate(parts)
    def ntest(self, null, rng, r):
        m = self.mi(self.x); nul = np.array([self.mi(self.nperm(null, rng)) for _ in range(r)])
        M, Ms = m.sum(), nul.sum(1); sh = [i for i, d in enumerate(LAGS) if d <= 64]; lo = [i for i, d in enumerate(LAGS) if d >= 96]
        def split(ix):
            a, b = m[ix].sum(), nul[:, ix].sum(1); s = b.std(ddof=1)
            return dict(E=float(a - b.mean()), z=float((a - b.mean()) / s) if s > 0 else None, p=float((1 + (b >= a).sum()) / (r + 1)))
        return dict(M=float(M), null_mean=float(Ms.mean()), null_sd=float(Ms.std(ddof=1)), E=float(M - Ms.mean()),
                    z=float((M - Ms.mean()) / Ms.std(ddof=1)), p=float((1 + (Ms >= M).sum()) / (r + 1)), effective_N=int(r),
                    E_lag={str(d): float(m[i] - nul[:, i].mean()) for i, d in enumerate(LAGS)},
                    short_le64=split(sh), long_ge96=split(lo), units=int(self.n), words=int(self.nw), pages=len(self.pages),
                    paragraphs=int(len(set(self.gid))))

def pair_fractions(pages, pids):
    """STRUCTURE ONLY: per lag, share of in-page unit pairs inside one paragraph (membership kept by N-PARA) and inside one
    full block (arrangement kept exactly by N-BLOCK, offset 0)."""
    S = PStream(pages, pids, tok=list)
    ug = np.repeat(S.gid, S.L); out = {}
    ub = np.full(S.n, -1); b = 0; wpos = 0
    # block id per unit
    wstart = S.S
    for head, blks, tail in S.segs[0]:
        for bl in blks:
            lo, hi = wstart[bl[0]], wstart[bl[-1]] + S.L[bl[-1]]; ub[lo:hi] = b; b += 1
    for d in LAGS:
        a = S.masks[d]
        out[str(d)] = dict(pairs=int(len(a)), same_para=float(np.mean(ug[a] == ug[a + d])) if len(a) else None,
                           same_block=float(np.mean((ub[a] == ub[a + d]) & (ub[a] >= 0))) if len(a) else None)
    return out

# ---------------------------------------------------------------- pseudo replicates under each null (words level)
def pseudo_para(pages, pids, rng):
    out = []
    for lines, ids in zip(pages, pids):
        new = [None] * len(lines); i = 0
        while i < len(lines):
            j = i
            while j < len(lines) and ids[j] == ids[i]: j += 1
            w = [x for l in lines[i:j] for x in l]; w = [w[t] for t in rng.permutation(len(w))]; c = 0
            for t in range(i, j): new[t] = w[c:c + len(lines[t])]; c += len(lines[t])
            i = j
        out.append(new)
    return out

def pseudo_block(pages, pids, rng, off=0):
    out = []
    for lines, _ in zip(pages, pids):
        h, bs, t = blocks_of(len(lines), off); blks = [lines[b:b + 4] for b in bs]
        order = list(rng.permutation(len(blks))) if len(blks) >= 2 else list(range(len(blks)))
        new = list(lines[:h])
        for j in order: new += blks[j]
        out.append(new + list(lines[t:]))
    return out

def pseudo_of(null, pages, pids, rng): return pseudo_para(pages, pids, rng) if null == 'PARA' else pseudo_block(pages, pids, rng)

def plant_in_para(pages, pids, rng, q, k):
    """declared VARIANT of C121's plant: a line copies the previous line only if both are in the same paragraph."""
    out = []
    for lines, ids in zip(pages, pids):
        new = [list(lines[0])]
        for li in range(1, len(lines)):
            l = list(lines[li])
            if ids[li] == ids[li - 1] and rng.random() < q:
                kk = min(k, len(l)); j = int(rng.integers(len(l) - kk + 1)); prev = new[-1]
                for i in range(kk): l[j + i] = prev[min(j + i, len(prev) - 1)]
            new.append(l)
        out.append(new)
    return out

def plant_main(pages, rng, q, k): return plant(pages, rng, q, k)   # C121 verbatim: crosses '<%>' / paragraph boundaries

# ---------------------------------------------------------------- manuscript data (or the dry-run stand-in)
def load_ms():
    D = {}
    for t, f in FILES:
        for s in STRATA: D[(s, t)] = pages_of(f, s)
    return D

def split_pp(pp): return [p for p, _ in pp], [i for _, i in pp]

def caesar_words():
    from c003_position_rigidity import gutenberg
    return [x for l in gutenberg('data/corpora/pg218.txt') for x in l]

def dry_data(D):
    """DRY RUN ONLY: replace every manuscript stratum by Latin Caesar recut into that stratum's line/paragraph template."""
    w = caesar_words(); out = {}
    for k, pp in D.items():
        pages, pids = split_pp(pp); base = recut(w, pages)
        out[k] = [(p, ids) for p, ids in zip(base, pids[:len(base)])]
    return out

# ---------------------------------------------------------------- jobs
def ck(name): return CK + name + '.json'

def cal_job(a):
    si, ni, ti, ci, s, null, t, name, words, eva, tmpl = a
    f = ck(f'cal_{s}_{null}_{t}_{ci}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([CSEED, si, ni, ti, ci]); pages, pids = tmpl
    base = recut(words, pages); ids = pids[:len(base)]; tok = units if eva else list
    res = dict(s=s, null=null, t=t, control=name, words=sum(len(l) for p in base for l in p), unplanted=[], rungs={})
    for _ in range(NC):
        ps = pseudo_of(null, base, ids, rng)
        r0 = PStream(ps, ids, tok).ntest(null, rng, RC); res['unplanted'].append([r0['p'], r0['E']])
        for q, k in LADDER:
            r1 = PStream(plant_main(ps, rng, q, k), ids, tok).ntest(null, rng, RC)
            res['rungs'].setdefault(f'{q}x{k}', []).append([r1['p'], r1['E']])
    json.dump(res, open(f, 'w')); return res

def choose(rs):
    fp = sum(p <= AG for o in rs for p, _ in o['unplanted']); n = sum(len(o['unplanted']) for o in rs); tab = {}
    for q, k in LADDER:
        key = f'{q}x{k}'; ps = [x for o in rs for x in o['rungs'][key]]
        tab[key] = dict(dose=q * k, power=sum(p <= AG for p, _ in ps) / len(ps), E_mean=float(np.mean([e for _, e in ps])))
    ch = next((k for k in tab if tab[k]['power'] >= 0.90), None)
    return dict(fpr=f'{fp}/{n}', fpr_ok=bool(fp <= round(3 / 80 * n)), ladder=tab, chosen=ch, valid=bool(ch is not None and fp <= round(3 / 80 * n)))

def gate_job(a):
    gi, s, null, t, pp, rung = a
    f = ck(f'gate_{s}_{null}_{t}')
    if os.path.exists(f): return json.load(open(f))
    rng = np.random.default_rng([GSEED, gi]); pages, pids = split_pp(pp); q, k = map(float, rung.split('x')); k = int(k)
    fp = pw = pv = 0; Ep, E0 = [], []
    for _ in range(NG):
        ps = pseudo_of(null, pages, pids, rng)
        t0 = PStream(ps, pids).ntest(null, rng, RG); fp += t0['p'] <= AG; E0.append(t0['E'])
        tp = PStream(plant_main(ps, rng, q, k), pids).ntest(null, rng, RG); pw += tp['p'] <= AG; Ep.append(tp['E'])
    r = dict(key=f'{s}_{null}_{t}', rung=rung, fpr=int(fp), power=int(pw), NG=NG, E_plant_mean=float(np.mean(Ep)),
             E_unplanted_mean=float(np.mean(E0)), pass_=bool(fp <= round(2 / 20 * NG) and pw >= round(16 / 20 * NG)))
    if null == 'PARA':
        for _ in range(NG):
            ps = pseudo_of(null, pages, pids, rng)
            pv += PStream(plant_in_para(ps, pids, rng, q, k), pids).ntest(null, rng, RG)['p'] <= AG
        r['power_inpara_plant_variant'] = int(pv)
    json.dump(r, open(f, 'w')); return r

def h1_job(a):
    hi, s, null, t, pp = a
    f = ck(f'h1_{s}_{null}_{t}')
    if os.path.exists(f): return json.load(open(f))
    pages, pids = split_pp(pp); rng = np.random.default_rng([SEED, hi])
    S = PStream(pages, pids); r = S.ntest(null, rng, R); r['key'] = f'{s}_{null}_{t}'
    json.dump(r, open(f, 'w')); return r

def desc_job(a):
    di, s, t, pp = a
    f = ck(f'desc_{s}_{t}')
    if os.path.exists(f): return json.load(open(f))
    pages, pids = split_pp(pp); rng = np.random.default_rng([DSEED, di]); S = PStream(pages, pids)
    out = dict(key=f'{s}_{t}', PAGE=S.ntest('PAGE', rng, R), BLOCK_OFF2=S.ntest('BLOCK2', rng, RD),
               pair_fractions=pair_fractions(pages, pids))
    json.dump(out, open(f, 'w')); return out

def invariance(null):
    f = ck(f'inv_{null}')
    if os.path.exists(f): return json.load(open(f))
    D = load_ms(); pages_t, pids_t = split_pp(D[('S', 'ZL3b')]); w = caesar_words(); base = recut(w, pages_t); ids = pids_t[:len(base)]
    rng = np.random.default_rng([ISEED, 0 if null == 'PARA' else 1]); S = PStream(base, ids, tok=list)
    M = S.mi(S.x).sum(); nul = []; exact = True; upg = np.repeat(S.pg, S.L); ug = np.repeat(S.gid, S.L)
    for _ in range(200):
        y = S.nperm(null, rng); nul.append(S.mi(y).sum())
        if null == 'PARA':
            for g in np.unique(S.gid)[:50]:
                m = ug == g
                if not np.array_equal(np.bincount(y[m], minlength=S.K), np.bincount(S.x[m], minlength=S.K)): exact = False
        else:
            for k in range(len(S.pages)):
                m = upg == k
                if not np.array_equal(np.bincount(y[m], minlength=S.K), np.bincount(S.x[m], minlength=S.K)): exact = False
    nul = np.array(nul); Mr = S.mi(rng.permutation(S.K)[S.x]).sum()
    blk_ok = True; ge2 = float(np.mean([len(b) >= 2 for _, b, _ in S.segs[0]]))
    if null == 'BLOCK':
        for _ in range(50):
            o = S.norder('BLOCK', rng); pos = np.empty(len(o), int); pos[o] = np.arange(len(o))
            for head, blks, tail in S.segs[0]:
                for bl in blks:
                    p0 = pos[bl[0]]
                    if not np.array_equal(o[p0:p0 + len(bl)], bl): blk_ok = False
        exact = bool(exact and blk_ok)
    out = dict(null=null, M=float(M), null_sd=float(nul.std(ddof=1)), share_null_equal_obs=float(np.mean(np.isclose(nul, M, rtol=0, atol=1e-12))),
               multiset_exact=exact, relabel_delta=float(abs(Mr - M)), share_pages_ge2_blocks=ge2 if null == 'BLOCK' else None, blocks_intact=blk_ok if null == 'BLOCK' else None)
    out['pass'] = bool(exact and out['null_sd'] > 0 and out['share_null_equal_obs'] <= 0.01 and out['relabel_delta'] < 1e-9 and
                       (null == 'PARA' or ge2 >= 0.5))
    json.dump(out, open(f, 'w')); return out

def label_pair(res, s, null, G, H, rej, cal):
    ks = [f'{s}_{null}_{t}' for t in TRANS]
    if not cal[(s, null)]['valid_both']: return 'NOT TESTABLE (calibration)'
    if not all(k in G and G[k]['pass_'] for k in ks): return 'NOT TESTABLE (gate)'
    n = sum(rej[k] for k in ks)
    if n == 2: return 'RESIDUAL'
    if n == 1: return 'PARTIAL'
    ep = float(np.mean([G[k]['E_plant_mean'] for k in ks]))
    return 'ABSORVIDO' if ep <= 0.5 * EB[s] else 'NOT TESTABLE (grosso)'

TABLE = {('RESIDUAL', 'ABSORVIDO'): 'LOCAL-4L', ('RESIDUAL', 'RESIDUAL'): 'ORDEM-ALEM-DO-BLOCO',
         ('ABSORVIDO', 'RESIDUAL'): 'DERIVA-PARAGRAFO', ('ABSORVIDO', 'ABSORVIDO'): 'LEXICAL-OU-LOCAL'}

def run():
    os.makedirs(CK, exist_ok=True); D = load_ms()
    if DRY: D = dry_data(D)
    res = dict(cycle='C123', dry=DRY, seeds=dict(cal=CSEED, gates=GSEED, H1=SEED, inv=ISEED, desc=DSEED, reserved=RESERVED),
               alpha=ALPHA, alpha_g=AG, R=R, RG=RG, RC=RC, RD=RD, NG=NG, NC=NC, EB=EB, ladder=[f'{q}x{k}' for q, k in LADDER],
               tool_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
    res['structure'] = {f'{s}_{t}': struct_counts(D[(s, t)]) for s in STRATA for t in TRANS}
    log('structure', res['structure'])
    res['G_INV'] = {n: invariance(n) for n in NULLS}; log('G-INV', res['G_INV'])
    ctr = controls(); jobs = []
    for si, s in enumerate(STRATA):
        for ni, null in enumerate(NULLS):
            for ti, t in enumerate(TRANS):
                tm = split_pp(D[(s, t)])
                for ci, (n, w, e) in enumerate(ctr): jobs.append((si, ni, ti, ci, s, null, t, n, w, e, tm))
    if DRY: jobs = [j for j in jobs if j[3] == 0]
    with Pool(8) as P: out = P.map(cal_job, jobs)
    cal = {}
    for s in STRATA:
        for null in NULLS:
            per = {}
            for t in TRANS:
                rs = [o for o in out if (o['s'], o['null'], o['t']) == (s, null, t)]
                if rs: per[t] = choose(rs)
            if len(per) < 2 and not DRY: raise SystemExit('calibration incomplete')
            cal[(s, null)] = dict(per=per, valid_both=bool(per and all(v['valid'] for v in per.values())))
            for t, v in per.items(): log('cal', s, null, t, v['fpr'], 'CHOSEN RUNG', v['chosen'], {k: (round(x['power'], 3), round(x['E_mean'], 4)) for k, x in v['ladder'].items()})
    res['calibration'] = {f'{s}_{n}': v for (s, n), v in cal.items()}
    gj, hj, dj = [], [], []; gi = hi = 0
    for s in STRATA:
        for null in NULLS:
            for t in TRANS:
                c = cal.get((s, null), {}).get('per', {}).get(t)
                if c and (c['chosen'] or DRY): gj.append((gi, s, null, t, D[(s, t)], c['chosen'] or '1.0x4'))
                hj.append((hi, s, null, t, D[(s, t)])); gi += 1; hi += 1
        for t in TRANS: dj.append((len(dj), s, t, D[(s, t)]))
    with Pool(8) as P:
        G = P.map(gate_job, gj); H = P.map(h1_job, hj); Dd = P.map(desc_job, dj)
    res['gates'] = {g['key']: g for g in G}; res['H1'] = {h['key']: h for h in H}; res['DESC'] = {d['key']: d for d in Dd}
    prim = {k: v['p'] for k, v in res['H1'].items() if k.split('_')[0] in PRIMARY}
    rej = holm(prim); res['holm_over_8'] = rej
    # trio beside every p
    res['p_with_trio'] = {k: dict(p=v['p'], z=v['z'], E=v['E'], FPR=f"{res['gates'][k]['fpr']}/{NG}" if k in res['gates'] else None,
                                  POW=f"{res['gates'][k]['power']}/{NG}" if k in res['gates'] else None,
                                  E_plant=res['gates'][k]['E_plant_mean'] if k in res['gates'] else None,
                                  rung=res['gates'][k]['rung'] if k in res['gates'] else None) for k, v in res['H1'].items()}
    pairlab, strat = {}, {}
    if all(v['pass'] for v in res['G_INV'].values()) or DRY:
        for s in PRIMARY:
            for null in NULLS:
                if all(f'{s}_{null}_{t}' in res['H1'] for t in TRANS) and (s, null) in cal:
                    pairlab[f'{s}_{null}'] = label_pair(res, s, null, res['gates'], res['H1'], rej, cal)
            a, b = pairlab.get(f'{s}_PARA'), pairlab.get(f'{s}_BLOCK')
            strat[s] = TABLE.get((a, b), 'INCONCLUSIVO')
    else:
        for s in PRIMARY:
            for null in NULLS: pairlab[f'{s}_{null}'] = 'NOT TESTABLE (G-INV)'
            strat[s] = 'INCONCLUSIVO'
    # Sigma_X raw (may be < 0 or > 1)
    sig = {}
    for k, d in res['DESC'].items():
        s, t = k.split('_')
        for null in NULLS:
            h = res['H1'].get(f'{s}_{null}_{t}')
            if h: sig[f'{k}_{null}'] = (h['null_mean'] - d['PAGE']['null_mean']) / d['PAGE']['E']
    res['pair_labels'] = pairlab; res['stratum_labels'] = strat; res['sigma_X_raw'] = sig
    res['elapsed_s'] = round(time.time() - T0, 1)
    out_f = 'analysis/C123_results.json' if not DRY else '/tmp/c123_dry_results.json'
    json.dump(res, open(out_f, 'w'), indent=1, default=float); log('pair labels', pairlab, 'strata', strat)

def struct():
    """STRUCTURE ONLY: paragraph and block counts per transcription and stratum; retention check against C070 parse()."""
    out = {}
    for t, f in FILES:
        check_retention(f); lines, cnt = parse_para(f); out[t] = dict(parse_counts=cnt)
        for s in STRATA:
            out[t][s] = struct_counts(pages_of(f, s))
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    cmd = sys.argv[1]
    {'run': run, 'dry': run, 'struct': struct}[cmd]()
