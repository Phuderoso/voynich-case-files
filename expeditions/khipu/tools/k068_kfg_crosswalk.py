#!/usr/bin/env python3
"""K068 - Khipu Field Guide (KFG) data migration: validated loader, OKR<->KFG crosswalk audit,
and re-test of the two duplicate claims of khipulab/open-khipu-repository#3 on KFG data.
No Monte Carlo, no p-values, no seeds (next free seed stays 6417).
Usage: python3 tools/k068_kfg_crosswalk.py <kfg_xlsx_dir> <okr khipu.db> <out kfg sqlite path>
Data: KFG per-khipu Excel files, https://www.khipufieldguide.com/databook/excel_khipus/<KH>.xlsx
(c) KFG data: Ashok Khosla, Manuel Medrano, Karen Thompson and the KFG team (MIT licence in each file).
Voynich - AI archaeologist, pimpolha of Phuderoso (github.com/Phuderoso)."""
import sys, os, re, glob, json, hashlib, sqlite3, shutil, time
from collections import defaultdict
import openpyxl

XD, OKR, OUTDB = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.join(HERE, '..', 'analysis')
t0 = time.time()
def norm_mus(s):
    return re.sub(r'[\s\.\-_"\']', '', (s or '')).upper()
def toks(s):
    return {t.upper() for t in re.split(r'[\s,/;]+', s or '') if t}
CL = re.compile(r',\s*(-?\d+)\s*$')

# ---------- 1. loader ----------
files = sorted(glob.glob(os.path.join(XD, '*.xlsx')))
K, CORDS, CHG, bad, manifest = {}, defaultdict(list), defaultdict(list), [], []
for f in files:
    nm = os.path.basename(f)[:-5]
    manifest.append((nm, hashlib.sha256(open(f, 'rb').read()).hexdigest(), os.path.getsize(f)))
    try:
        wb = openpyxl.load_workbook(f, read_only=True)
        meta = {}
        for (r,) in ((row[0],) for row in wb['Khipu'].iter_rows(values_only=True)):
            if isinstance(r, str) and ':' in r:
                k_, v_ = r.split(':', 1); meta[k_.strip()] = v_.strip()
        rows = list(wb['Cords'].iter_rows(values_only=True))
        hdr = [str(h) for h in rows[0]]
        for i, r in enumerate(rows[1:]):
            if r and r[0] is not None: CORDS[nm].append(dict(zip(hdr, r), idx=i))
        if 'ChangeLog' in wb.sheetnames:
            for r in list(wb['ChangeLog'].iter_rows(values_only=True))[1:]:
                if r and any(x is not None for x in r): CHG[nm].append([None if x is None else str(x) for x in r])
        K[nm] = meta
    except Exception as e:
        bad.append((nm, repr(e)))
# G1 parse, G3 name == filename
G1 = dict(files=len(files), parsed=len(K), failed=bad)
G3 = [nm for nm, m in K.items() if m.get('Name') != nm]
# G2 value vs knot-cluster sum
n_k = n_ok = 0; g2_bad = []
for nm, cs in CORDS.items():
    for c in cs:
        kn = c.get('Knots')
        if not kn or str(kn).strip() in ('', 'None'): continue
        try: s = sum(int(CL.search(x).group(1)) for x in str(kn).split(';') if x.strip())
        except Exception: s = None
        n_k += 1
        try: v = int(float(c.get('Value')))
        except Exception: v = None
        if s is not None and v == s: n_ok += 1
        elif len(g2_bad) < 30: g2_bad.append((nm, c.get('Cord_Name'), kn, c.get('Value')))
G2 = dict(cords_with_knots=n_k, value_equals_cluster_sum=n_ok, rate=round(n_ok / max(n_k, 1), 5), examples=g2_bad[:15])

# versioned sqlite + backup
if os.path.exists(OUTDB): shutil.copy2(OUTDB, OUTDB + '.bak')
db = sqlite3.connect(OUTDB + '.tmp') if False else None
if os.path.exists(OUTDB + '.tmp'): os.remove(OUTDB + '.tmp')
db = sqlite3.connect(OUTDB + '.tmp')
db.execute('create table khipu(name text primary key, aliases, museum_name, museum_number, provenance, region, creation_date, excel_write_date, sha256)')
db.execute('create table cord(khipu, idx int, cord_name, twist, attachment, knots, length, termination, thickness, color, value, alt_value, position, notes)')
db.execute('create table changelog(khipu, date, who, what, frm, too, impact, explanation)')
sha = {m[0]: m[1] for m in manifest}
for nm, m in K.items():
    db.execute('insert into khipu values(?,?,?,?,?,?,?,?,?)', (nm, m.get('Aliases'), m.get('Museum Name'), m.get('Museum Number'), m.get('Provenance'), m.get('Region'), m.get('Creation_Date'), m.get('Excel Write Date'), sha[nm]))
    for c in CORDS[nm]:
        db.execute('insert into cord values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (nm, c['idx'], *[None if c.get(h) is None else str(c.get(h)) for h in ['Cord_Name', 'Twist', 'Attachment', 'Knots', 'Length', 'Termination', 'Thickness', 'Color', 'Value', 'Alt_Value', 'Position', 'Notes']]))
    for r in CHG[nm]:
        r = (r + [None] * 7)[:7]; db.execute('insert into changelog values(?,?,?,?,?,?,?,?)', (nm, *r))
db.commit(); db.close(); os.replace(OUTDB + '.tmp', OUTDB)

# ---------- 2. crosswalk ----------
oc = sqlite3.connect(OKR)
okr = {r[0]: dict(kid=r[1], inv=r[2] or '', orig=r[3] or '', mus=r[4] or '', dup=r[5]) for r in oc.execute('select OKR_NUM, KHIPU_ID, INVESTIGATOR_NUM, orig_inv_num, MUSEUM_NUM, DUPLICATE_FLAG from khipu_main')}
both = sorted(set(okr) & set(K)); okr_only = sorted(set(okr) - set(K)); kfg_only = sorted(set(K) - set(okr))
mus_agree = [k for k in both if norm_mus(okr[k]['mus']) == norm_mus(K[k].get('Museum Number'))]
mus_dis = [(k, okr[k]['mus'], K[k].get('Museum Number')) for k in both if k not in mus_agree]
alias_hit = [k for k in both if (toks(okr[k]['inv']) | toks(okr[k]['orig'])) & toks(K[k].get('Aliases'))]
# OKR-only ids: is any OKR alias / museum number carried by a KFG khipu?
kfg_alias_index = defaultdict(set); kfg_mus_index = defaultdict(set)
for nm, m in K.items():
    for t in toks(m.get('Aliases')): kfg_alias_index[t].add(nm)
    kfg_mus_index[norm_mus(m.get('Museum Number'))].add(nm)
okr_only_where = {k: dict(okr_inv=okr[k]['inv'], okr_orig=okr[k]['orig'], okr_mus=okr[k]['mus'],
                          kfg_by_alias=sorted(set().union(*[kfg_alias_index.get(t, set()) for t in toks(okr[k]['inv']) | toks(okr[k]['orig'])] or [set()])),
                          kfg_by_museum=sorted(kfg_mus_index.get(norm_mus(okr[k]['mus']), set())) if norm_mus(okr[k]['mus']) else [])
                  for k in okr_only}

# ---------- 3. pendant-level concordance (raw values, no masking) ----------
val = defaultdict(int)
for cid, v in oc.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None: val[cid] += int(v)
okr_p = defaultdict(list)
for kid, cid in oc.execute('select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    okr_p[kid].append(val.get(cid, 0))
PEN = re.compile(r'^p\d+$')
def kfg_p(nm):
    out = []
    for c in CORDS[nm]:
        if PEN.match(str(c.get('Cord_Name') or '')):
            try: out.append(int(float(c.get('Value') or 0)))
            except Exception: out.append(0)
    return out
conc = dict(identical=[], same_len_diff=[], reversed_identical=[], diff_len=[])
for k in both:
    a, b = okr_p[okr[k]['kid']], kfg_p(k)
    if a == b: conc['identical'].append(k)
    elif a == b[::-1]: conc['reversed_identical'].append(k)
    elif len(a) == len(b): conc['same_len_diff'].append((k, sum(x != y for x, y in zip(a, b)), len(a)))
    else: conc['diff_len'].append((k, len(a), len(b)))

# ---------- 4. duplicate re-test ----------
def collapse(s):
    out = []
    for x in s:
        if not out or out[-1] != x: out.append(x)
    return out
def find_block(seq, blk, tol=0):
    hits = []
    for i in range(len(seq) - len(blk) + 1):
        d = sum(x != y for x, y in zip(seq[i:i + len(blk)], blk))
        if d <= tol: hits.append((i, d, seq[i:i + len(blk)]))
    return hits
def lcb(a, b):  # longest common contiguous block (exact)
    best = (0, 0, 0)
    for i in range(len(a)):
        for j in range(len(b)):
            L = 0
            while i + L < len(a) and j + L < len(b) and a[i + L] == b[j + L]: L += 1
            if L > best[0]: best = (L, i, j)
    return best
PAIRS = [('KH0140', 'KH0483'), ('KH0132', 'KH0456')]
BLOCK = {('KH0132', 'KH0456'): ([620, 470, 528, 935, 474, 319, 453, 492], [620, 470, 528, 932, 474, 319, 453, 492])}
dup = {}
for a, b in PAIRS:
    r = dict(present={x: x in K for x in (a, b)})
    for x, y in ((a, b), (b, a)):
        if x in K:
            names_y = {y} | toks(okr[y]['inv']) | toks(okr[y]['orig'])
            txt_alias = toks(K[x].get('Aliases'))
            chg_txt = ' '.join(' '.join(z or '' for z in row) for row in CHG[x]).upper()
            notes_txt = ' '.join(str(c.get('Notes') or '') for c in CORDS[x]).upper()
            r['%s_mentions_%s' % (x, y)] = dict(in_aliases=sorted(names_y & txt_alias),
                                                 in_changelog=sorted(t for t in names_y if t and t in chg_txt),
                                                 in_cord_notes=sorted(t for t in names_y if t and t in notes_txt),
                                                 museum_number=K[x].get('Museum Number'), aliases=K[x].get('Aliases'),
                                                 changelog_rows=len(CHG[x]), pendants=len(kfg_p(x)))
    if all(r['present'].values()):
        A, B = collapse(kfg_p(a)), collapse(kfg_p(b)); L, i, j = lcb(A, B)
        r['kfg_longest_common_collapsed_block'] = dict(length=L, at_a=i, at_b=j, block=A[i:i + L])
        Ao, Bo = collapse(okr_p[okr[a]['kid']]), collapse(okr_p[okr[b]['kid']]); Lo, io, jo = lcb(Ao, Bo)
        r['okr_longest_common_collapsed_block'] = dict(length=Lo, block=Ao[io:io + Lo])
    if (a, b) in BLOCK:
        ba, bb = BLOCK[(a, b)]
        r['block_search'] = {a: find_block(collapse(kfg_p(a)), ba, 1) if a in K else 'absent',
                             b: find_block(collapse(kfg_p(b)), bb, 1) if b in K else 'absent'}
    # pre-registered outcome classes
    if not all(r['present'].values()):
        surv = [x for x in (a, b) if x in K][0] if any(r['present'].values()) else None
        gone = [x for x in (a, b) if x not in K]
        m = r.get('%s_mentions_%s' % (surv, gone[0]), {}) if surv else {}
        r['outcome'] = ('C1 merged/retired: survivor %s cross-references %s' % (surv, gone[0]) if m and (m['in_aliases'] or m['in_changelog'] or m['in_cord_notes'])
                        else 'C2 one record absent from KFG, no cross-reference in survivor' if surv else 'C0 both absent')
    else:
        ref = any(v['in_aliases'] or v['in_changelog'] or v['in_cord_notes'] for kk, v in r.items() if kk.endswith(tuple('_mentions_' + x for x in (a, b))))
        blk = r['kfg_longest_common_collapsed_block']['length']
        r['outcome'] = ('B both present and cross-referenced/flagged' if ref else
                        ('A both present, unflagged, shared block persists (L=%d)' % blk if blk >= 6 else 'D both present, shared block no longer holds (L=%d)' % blk))
    dup[a + '_' + b] = r

out = dict(cycle='K068', fetched='2026-11-11', source='https://www.khipufieldguide.com/databook/excel_khipus/<KH>.xlsx',
           excel_write_dates=sorted({m.get('Excel Write Date') for m in K.values()}),
           G1=G1, G2=G2, G3_name_mismatch=G3,
           crosswalk=dict(kfg=len(K), okr=len(okr), both=len(both), okr_only=okr_only, kfg_only_n=len(kfg_only), kfg_only=kfg_only,
                          museum_agree=len(mus_agree), museum_disagree=mus_dis, alias_agree=len(alias_hit),
                          okr_only_where=okr_only_where),
           concordance={k: (len(v), v) for k, v in conc.items()}, duplicates=dup, runtime_s=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(AN, 'k068_results.json'), 'w'), indent=1, default=str)
with open(os.path.join(AN, 'k068_kfg_manifest.tsv'), 'w') as fh:
    fh.write('name\tsha256\tbytes\n'); [fh.write('%s\t%s\t%d\n' % m) for m in manifest]
print(json.dumps(dict(G1={k: (v if k != 'failed' else len(v)) for k, v in G1.items()}, G2={k: v for k, v in G2.items() if k != 'examples'}, G3=len(G3),
                      both=len(both), okr_only=len(okr_only), kfg_only=len(kfg_only), museum_agree=len(mus_agree), museum_disagree=len(mus_dis), alias_agree=len(alias_hit),
                      conc={k: len(v) for k, v in conc.items()}, dup={k: v['outcome'] for k, v in dup.items()}, runtime_s=out['runtime_s']), indent=1))
