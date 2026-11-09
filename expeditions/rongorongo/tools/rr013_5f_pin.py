"""RR013 line 5f, step 1 - pin a published variant list and measure what it would change, BEFORE any trigram test.
Source A: Spaelti/CEIPP 'List of Glyph Variants' (kohaumotu.org/Rongorongo/Glyph_Library/glyph_variants_list.html),
pinned by sha256. Each group is a 3-digit Barthel base followed by its variant codes. Rule (no judgement): a unit's
first component code (digits zero-padded to 3, suffix letters kept, '!'/'?' kept) maps to the group it is listed in.
Question answered exactly: on how many head-sign tokens of the 25 test pairs' sides (and Hr/Pr/Qr) does the list
assign a base DIFFERENT from RR005's head_norm (the 3-digit leading code)? If 0, 5f with this list is RR007 by
construction. Source B: Pozdniakov & Pozdniakov 2007 (PDF pinned): equivalences stated in machine-readable text.
Usage: python3 rr013_5f_pin.py corpus.json glyph_variants_list.html out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, html, hashlib, collections
sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # installs head_norm
import rr001_isolation as R1
SIDES8 = ['Aa', 'Ab', 'Br', 'Bv', 'Ca', 'Cb', 'Er', 'Ia']; CTRL = ['Hr', 'Pr', 'Qr']

def parse(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    s = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    lines = [l.strip() for l in s.split('\n') if l.strip()]
    groups = {}; cur = None
    for l in lines:
        if re.fullmatch(r'\d{3}', l): cur = l; continue
        if cur is not None and re.match(r'\d{3}', l):
            groups[cur] = [x.strip() for x in l.split(',') if x.strip()]; cur = None
    return groups

def main(cp, lp, op):
    corpus = json.load(open(cp)); groups = parse(lp)
    v2b = {}; cross = []
    for b, vs in groups.items():
        for v in vs:
            m = re.match(r'(\d{3})', v)
            if m and m.group(1) != b: cross.append((b, v))
            v2b.setdefault(v, set()).add(b)
    multi = {v: sorted(b) for v, b in v2b.items() if len(b) > 1}
    stats = collections.Counter(); diff_examples = []
    for k in sorted(corpus):
        if k[:2] not in SIDES8 + CTRL: continue
        for i, u in enumerate(corpus[k]):
            h = R1.head(u, (k, i))
            if isinstance(h, tuple): stats['illegible_or_marker'] += 1; continue
            first = re.split(r"[.:;']", u)[0]
            m = re.match(r'(\d{1,3})(.*)$', first)
            code = m.group(1).zfill(3) + m.group(2)
            if code in v2b:
                b = sorted(v2b[code])[0]; stats['listed'] += 1
                if b != h: stats['listed_base_differs'] += 1; diff_examples.append((k, i, u, h, b))
            else:
                stats['not_listed'] += 1
                if code[:3] in groups: stats['not_listed_base_exists'] += 1
    out = dict(list_sha256=hashlib.sha256(open(lp, 'rb').read()).hexdigest(),
               corpus_sha256=hashlib.sha256(open(cp, 'rb').read()).hexdigest(),
               n_groups=len(groups), n_variant_codes=sum(len(v) for v in groups.values()),
               cross_number_entries=len(cross), cross_examples=cross[:20], codes_in_two_groups=multi,
               token_stats=dict(stats), base_differs_examples=diff_examples[:20])
    # Source B: Pozdniakov & Pozdniakov 2007, text p. 8: "glyphs 6 and 64 should be considered variants of the same sign"
    c = collections.Counter()
    for k in sorted(corpus):
        if k[:2] in SIDES8:
            for i, u in enumerate(corpus[k]):
                h = R1.head(u, (k, i))
                if h in ('006', '064'): c[(k[:2], h)] += 1
    tot = sum(1 for k in corpus if k[:2] in SIDES8 for _ in corpus[k])
    out['pozdniakov_6_64'] = dict(tokens_064_in_8_sides=sum(v for (s, h), v in c.items() if h == '064'),
                                  tokens_006_in_8_sides=sum(v for (s, h), v in c.items() if h == '006'),
                                  units_in_8_sides=tot, per_side={f'{s}:{h}': v for (s, h), v in sorted(c.items())})
    json.dump(out, open(op, 'w'), indent=1); print(json.dumps({k: v for k, v in out.items() if k != 'codes_in_two_groups'}, indent=1)[:3000])
    print('codes_in_two_groups', len(multi))

if __name__ == '__main__':
    main(*sys.argv[1:4])
