"""C024 helpers: line-level glyph comparison of ZL 3b vs Takahashi IT2a (both IVTFF, data/)."""
import re
from collections import defaultdict

def clean(t):
    t = re.sub(r'<[^>]*>', '', t)
    t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t)       # ZL alternatives: first reading
    t = re.sub(r'@\d+;', '?', t)                          # rare/extended glyph codes
    t = t.replace('{', '').replace('}', '').replace("'", '')
    return re.sub(r'[.,\s!%*-]', '', t)                    # drop word and uncertain-space separators

def lines(path):
    meta, out, page = {}, {}, None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        m = re.match(r'<(f\w+)>\s*<!(.*)>', line)
        if m:
            page = m.group(1); meta[page] = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))); continue
        m = re.match(r'<(f\w+)\.(\d+)[^>]*>\s*(.*)', line)
        if m: out[(m.group(1), int(m.group(2)))] = clean(m.group(3))
    return meta, out

def lev(a, b):
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def page_rates(zl='data/ZL3b-n.txt', it='data/IT2a-n.txt'):
    mz, lz = lines(zl); mi, li = lines(it)
    ed, ln, nl = defaultdict(int), defaultdict(int), defaultdict(int)
    for k, a in lz.items():
        if k in li and a and li[k]:
            ed[k[0]] += lev(a, li[k]); ln[k[0]] += max(len(a), len(li[k])); nl[k[0]] += 1
    return mz, {p: (ed[p], ln[p], nl[p]) for p in ln}
