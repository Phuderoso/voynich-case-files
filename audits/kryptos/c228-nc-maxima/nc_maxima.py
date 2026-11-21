#!/usr/bin/env python3
"""Per RULE.md: max NC per case (205/206/211) for K4 and nulls under tie='?' and first-vote."""
import sys, glob, collections, os
import numpy as np
sys.path.insert(0, '/workspace/k209-d2-audit')
from recount209 import perm_maps, N, CRP, CRS, KA
W = '/workspace/k228-nc-maxima'
D = W + '/kryptos-main/data'
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
IDX = {'AZ': {c: i for i, c in enumerate(AZ)}, 'KA': {c: i for i, c in enumerate(KA)}}
ALPH = {'AZ': AZ, 'KA': KA}
AL = {0: ('AZ', 'AZ'), 1: ('KA', 'KA'), 2: ('KA', 'AZ'), 3: ('AZ', 'KA')}  # (plain-side, cipher-side)
qg = np.fromfile(W + '/qg.bin', dtype=np.float32)
assert qg.size == 26 ** 4
CRIB = set(CRP)
def qi(a, b, c, d): return ((a * 26 + b) * 26 + c) * 26 + d
WIN = [i for i in range(94) if not any(x in CRIB for x in range(i, i + 4))]

def load_case(c):
    texts = {}
    for l in open(f'{D}/cycle{c}/texts.tsv'):
        p = l.rstrip('\n').split('\t')
        if p[0] in ('label', 'seed'): continue
        lab = p[0] if (p[0] == 'K4' or p[0].startswith('null')) else 'null' + p[0]
        texts[lab] = p[1]
    files = {}
    if c == '219':
        files['K4'] = [f'{D}/cycle219/K4.txt']
        for f in sorted(glob.glob(f'{D}/cycle219/null*.txt')):
            b = os.path.basename(f)
            if b.startswith('nulls219'): continue
            files[b[:-4]] = [f]
    else:
        files['K4'] = [f'{D}/cycle{c}/results_k4.txt']
        for f in sorted(glob.glob(f'{D}/cycle{c}/results_null*.txt')):
            files['null' + os.path.basename(f)[len('results_null'):-4]] = [f]
    return texts, files

def parse(c, line):
    t = line.split()
    if c == '219': return tuple(map(int, t[2:11])) + (tuple(map(int, t[11:])),)
    return tuple(map(int, t[1:10])) + (tuple(map(int, t[10].split(','))),)

def decrypt(ct, hit, cache):
    w, mode, dr, al, be, model, p, e, bad, pi = hit
    if (w, pi) not in cache: cache[(w, pi)] = perm_maps(w, pi)
    sig, inv = cache[(w, pi)][mode]; S = inv if dr else sig
    pa, ca = AL[al]; ip, ic = IDX[pa], IDX[ca]
    j = [S[x] for x in CRP]
    kv = [((ic[ct[j[t]]] + ip[CRS[t]]) % 26) if be else ((ic[ct[j[t]]] - ip[CRS[t]]) % 26) for t in range(24)]
    res = [(j[t] if model else CRP[t]) % p for t in range(24)]
    cls = collections.defaultdict(collections.Counter)
    for r, v in zip(res, kv): cls[r][v] += 1
    nbad = 0
    for r, cn in cls.items():
        if len(cn) > 2 or (len(cn) == 2 and min(cn.values()) >= 2): nbad += 99
        elif len(cn) == 2: nbad += 1
    ee = 2 if nbad > 1 else nbad
    assert ee == e and ee <= 1, ('excess mismatch', hit, ee)
    out = {}
    for rule in ('Q', 'F'):
        kres = {}
        for r, cn in cls.items():
            mc = cn.most_common()
            if rule == 'F': kres[r] = mc[0][0]
            elif len(mc) == 1 or mc[0][1] > mc[1][1]: kres[r] = mc[0][0]
        P = []
        for i in range(N):
            r = (S[i] if model else i) % p
            if r in kres:
                x = ic[ct[S[i]]]; k = kres[r]
                P.append(ALPH[pa][(x - k) % 26 if be == 0 else (k - x) % 26])
            else: P.append('?')
        P = ''.join(P)
        sc = []
        for i in WIN:
            q = P[i:i + 4]
            if '?' in q: continue
            sc.append(float(qg[qi(*[ord(ch) - 65 for ch in q])]))
        n = len(sc)
        out[rule] = dict(P=P, known=N - P.count('?'), n=n, nc=(sum(sc) / n if n else None))
    return j, out

def ok(r): return r['nc'] is not None and r['nc'] >= -6.0 and r['known'] >= 49 and r['n'] >= 10

def run():
    rows = []   # one dict per hit
    inputdelta = []
    for c, case in (('219', '205'), ('220', '206'), ('225', '211')):
        texts, files = load_case(c)
        cache = {}
        for lab, fl in files.items():
            ct = texts[lab]; seen2 = set(); seen3 = set(); nh = 0; perp = collections.Counter()
            for f in fl:
                for ln in open(f):
                    if not ln.startswith('H '): continue
                    hit = parse(c, ln)
                    j, out = decrypt(ct, hit, cache)
                    w, mode, dr, al, be, model, p, e, bad, pi = hit
                    k2 = (w, mode, dr, al, be, model, p, tuple(j)); k3 = (al, be, model, p, tuple(j))
                    u2 = k2 not in seen2; seen2.add(k2); u3 = k3 not in seen3; seen3.add(k3)
                    rows.append(dict(case=case, lab=lab, cls='K4' if lab == 'K4' else 'null', p=p, e=e, al=al, u2=u2, u3=u3, **{r: out[r] for r in out}))
                    nh += 1; perp[(p, e)] += 1
            # input delta: stamped per-p strict/one-error vs H lines read
            stamp = [l for l in open(fl[0]) if l.startswith('# per p')][0]
            import re
            st = {int(a): (int(b), int(d)) for a, b, d in re.findall(r'p(\d+)=(\d+)/(\d+)', stamp)}
            for p, (s, o) in sorted(st.items()):
                got_s = perp[(p, 0)]; got_all = perp[(p, 0)] + perp[(p, 1)]
                inputdelta.append((case, lab, p, s, o, got_s, got_all))
    return rows, inputdelta

def summarize(rows):
    def stats(sel, rule):
        hs = [r for r in sel]
        el = [r[rule]['nc'] for r in hs if r[rule]['nc'] is not None and r[rule]['known'] >= 49 and r[rule]['n'] >= 10]
        n10 = [r[rule]['nc'] for r in hs if r[rule]['nc'] is not None and r[rule]['n'] >= 10]
        anyn = [r[rule]['nc'] for r in hs if r[rule]['nc'] is not None]
        ps = [r for r in hs if ok(r[rule])]
        return dict(cells=len(hs), elig=len(el), mx_el=max(el) if el else None, mx_n10=max(n10) if n10 else None, mx_any=max(anyn) if anyn else None,
                    npass=len(ps), ntexts=len({r[rule]['P'] for r in ps}), texts_pass=len({r['lab'] for r in ps}))
    f = lambda v: 'NA' if v is None else f'{v:.4f}'
    units = (('U1', lambda r: True), ('U2', lambda r: r['u2']), ('U3', lambda r: r['u3']))
    lines = []
    with open(W + '/counts_case.tsv', 'w') as fo:
        fo.write('case\tclass\trule\tunit\tn_texts\tcells\teligible\tmaxNC_elig\tmaxNC_n10\tmaxNC_any\tpasses\tdistinct_pass_texts\ttexts_with_pass\n')
        for case in ('205', '206', '211', 'ALL'):
            for cl in ('K4', 'null'):
                for rule in ('Q', 'F'):
                    for un, fn in units:
                        sel = [r for r in rows if (case == 'ALL' or r['case'] == case) and r['cls'] == cl and fn(r)]
                        s = stats(sel, rule)
                        nt = len({(r['case'], r['lab']) for r in rows if (case == 'ALL' or r['case'] == case) and r['cls'] == cl})
                        fo.write(f"{case}\t{cl}\t{rule}\t{un}\t{nt}\t{s['cells']}\t{s['elig']}\t{f(s['mx_el'])}\t{f(s['mx_n10'])}\t{f(s['mx_any'])}\t{s['npass']}\t{s['ntexts']}\t{s['texts_pass']}\n")
    with open(W + '/counts_case_p.tsv', 'w') as fo:
        fo.write('case\tclass\tp\trule\tcells_U2\teligible\tmaxNC_elig\tmaxNC_any\tpasses\n')
        for case in ('205', '206', '211'):
            for cl in ('K4', 'null'):
                for p in range(1, 23):
                    for rule in ('Q', 'F'):
                        sel = [r for r in rows if r['case'] == case and r['cls'] == cl and r['p'] == p and r['u2']]
                        if not sel: continue
                        s = stats(sel, rule)
                        fo.write(f"{case}\t{cl}\t{p}\t{rule}\t{s['cells']}\t{s['elig']}\t{f(s['mx_el'])}\t{f(s['mx_any'])}\t{s['npass']}\n")
    with open(W + '/counts_text.tsv', 'w') as fo:
        fo.write('case\ttext\trule\tcells_U2\traw_hits\teligible_U1\tmaxNC_elig_U1\tmaxNC_elig_U2\tpasses_U1\tbest_p\n')
        for case in ('205', '206', '211'):
            for lab in sorted({r['lab'] for r in rows if r['case'] == case}, key=lambda x: (x != 'K4', x)):
                for rule in ('Q', 'F'):
                    sel = [r for r in rows if r['case'] == case and r['lab'] == lab]
                    s1 = stats(sel, rule); s2 = stats([r for r in sel if r['u2']], rule)
                    best = max(((r[rule]['nc'], r['p']) for r in sel if r[rule]['nc'] is not None and r[rule]['known'] >= 49 and r[rule]['n'] >= 10), default=(None, None))
                    fo.write(f"{case}\t{lab}\t{rule}\t{s2['cells']}\t{s1['cells']}\t{s1['elig']}\t{f(s1['mx_el'])}\t{f(s2['mx_el'])}\t{s1['npass']}\t{best[1]}\n")
    # summary text
    for case in ('205', '206', '211', 'ALL'):
        for cl in ('K4', 'null'):
            for rule in ('Q', 'F'):
                for un, fn in units[:2]:
                    sel = [r for r in rows if (case == 'ALL' or r['case'] == case) and r['cls'] == cl and fn(r)]
                    s = stats(sel, rule)
                    lines.append(f"case {case:3s} {cl:4s} rule {'tie=?' if rule=='Q' else 'first-vote':10s} {un}: cells {s['cells']} eligible {s['elig']} maxNC-elig {f(s['mx_el'])} maxNC-n10 {f(s['mx_n10'])} maxNC-any {f(s['mx_any'])} passes {s['npass']} (distinct texts {s['ntexts']})")
    return lines

if __name__ == '__main__':
    rows, idl = run()
    with open(W + '/input_delta.tsv', 'w') as fo:
        fo.write('case\ttext\tp\tstamped_strict\tstamped_oneerr\tH_strict\tH_total\n')
        for r in idl: fo.write('\t'.join(map(str, r)) + '\n')
    lines = summarize(rows)
    lines.append(f"hits read {len(rows)}; excess asserted == stamped on every hit")
    open(W + '/summary_nc_maxima.txt', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
