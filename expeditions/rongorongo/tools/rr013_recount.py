"""RR013 independent recount (own parser, no import of the RR001/RR005/RR013 tools):
(1) Spaelti list: number of groups, codes, codes listed under a base other than their own leading 3 digits;
    and, over Aa Ab Br Bv Ca Cb Er Ia Hr Pr Qr, tokens whose listed base differs from the leading code;
(2) K entries: count, units, strokes, entries holding a stroke, exact floor prod(1 - s/n), expected S3;
(3) Pozdniakov 6~64: tokens of head 064 / 006 in the 8 sides.
Usage: python3 rr013_recount.py corpus.json glyph_variants_list.html out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys
from fractions import Fraction
def lead(u):
    d = ''
    for ch in u:
        if ch.isdigit(): d += ch
        else: break
    return d
def first_comp(u):
    for i, ch in enumerate(u):
        if ch in ".:;'": return u[:i]
    return u
corpus = json.load(open(sys.argv[1])); txt = open(sys.argv[2], encoding='utf-8', errors='replace').read()
# strip tags by hand
buf, intag = [], False
for ch in txt:
    if ch == '<': intag = True; buf.append('\n')
    elif ch == '>': intag = False
    elif not intag: buf.append(ch)
lines = [l.strip() for l in ''.join(buf).replace('&nbsp;', ' ').split('\n') if l.strip()]
groups, cur = {}, None
for l in lines:
    if len(l) == 3 and l.isdigit(): cur = l; continue
    if cur and l[:3].isdigit():
        groups[cur] = [c.strip() for c in l.split(',')]; cur = None
code2base = {c: b for b, cs in groups.items() for c in cs}
cross = sum(1 for b, cs in groups.items() for c in cs if c[:3] != b)
differs = listed = 0
for k, us in corpus.items():
    if k[:2] not in ('Aa', 'Ab', 'Br', 'Bv', 'Ca', 'Cb', 'Er', 'Ia', 'Hr', 'Pr', 'Qr'): continue
    for u in us:
        if '!' in u or ')' in u: continue
        fc = first_comp(u); d = lead(fc)
        if not d or int(d) == 0: continue
        code = d.zfill(3) + fc[len(d):]
        if code in code2base:
            listed += 1; differs += code2base[code] != d.zfill(3)
def stroke(u):
    if any(c in u for c in ".:;'!?"): return False
    d = lead(u); return d != '' and d.zfill(3) in ('001', '002', '003', '004', '009')
ent = []
for s in ('Kr', 'Kv'):
    seq = [u for k in sorted(k for k in corpus if k[:2] == s) for u in corpus[k]]
    pos = [i for i, u in enumerate(seq) if u[:7] == '380.001']
    for a, b in zip(pos, pos[1:]):
        if b - a > 1: ent.append(seq[a + 1:b])
floor = Fraction(1)
for e in ent: floor *= Fraction(len(e) - sum(map(stroke, e)), len(e))
c64 = c6 = 0
for k, us in corpus.items():
    if k[:2] in ('Aa', 'Ab', 'Br', 'Bv', 'Ca', 'Cb', 'Er', 'Ia'):
        for u in us:
            if '!' in u or ')' in u: continue
            d = lead(first_comp(u))
            if d and d.zfill(3) == '064': c64 += 1
            if d and d.zfill(3) == '006': c6 += 1
out = dict(groups=len(groups), codes=sum(map(len, groups.values())), cross_number_codes=cross, tokens_listed=listed,
           tokens_base_differs=differs, K_entries=len(ent), K_units=sum(map(len, ent)), K_strokes=sum(stroke(u) for e in ent for u in e),
           K_entries_with_stroke=sum(any(map(stroke, e)) for e in ent), K_floor_exact=str(floor), K_floor=float(floor),
           K_expected_S3=round(sum(sum(map(stroke, e)) / len(e) for e in ent), 3), tokens_064=c64, tokens_006=c6)
json.dump(out, open(sys.argv[3], 'w'), indent=1); print(out)
