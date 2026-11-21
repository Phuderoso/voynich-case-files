#!/usr/bin/env python3
"""After FROZEN.txt: compare my bsk230 outputs (out/fresh) with her data/cycle231/R/* (sets of S lines and T lines), verify SHA256SUMS_R, and her an231/pool231 numbers vs my counts.
Usage: python3 postcompare.py HER_CYCLE231_DIR  -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import os, re, sys, csv, hashlib
her = sys.argv[1].rstrip('/') + '/'; mine = 'out/fresh/'
ok = bad = 0
for f in sorted(os.listdir(her + 'R')):
    if not f.startswith('null'): continue
    a = open(mine + f).read().splitlines(); b = open(her + 'R/' + f).read().splitlines()
    same = sorted(l for l in a if l.startswith('S')) == sorted(l for l in b if l.startswith('S')) and [l for l in a if l.startswith('T')] == [l for l in b if l.startswith('T')]
    ok += same; bad += (not same)
    if not same: print('DIFF', f)
print(f'survivor files identical (S sets and T lines): {ok}; different: {bad}')
h = 0; n = 0
for l in open(her + 'SHA256SUMS_R.txt'):
    s, f = l.split(); n += 1
    if hashlib.sha256(open(her + 'R/' + f, 'rb').read()).hexdigest() == s: h += 1
print(f'SHA256SUMS_R.txt: {h}/{n} OK')
rows = list(csv.DictReader(open('res/counts231.tsv'), delimiter='\t')); mineC = {}
for r in rows:
    if r['text'].startswith('fresh:null'): mineC.setdefault((r['scope'], int(r['W'])), {})[int(r['text'][10:])] = (int(r['raw']), int(r['clusters_I291R']), int(r['cells_house']))
for l in open(her + 'an231.log'):
    m = re.match(r'(direct|bank|all) W(\d+) K4 full raw (\d+) clusters (\d+) .*?raw (\[.*?\]) clusters (\[.*?\]) \|', l)
    if m:
        sc, W = m.group(1), int(m.group(2)); raw = eval(m.group(5)); cl = eval(m.group(6)); d = mineC[(sc, W)]; n = len(raw)
        print(f'{sc} W<={W}: her per-null raw == mine {raw == [d[i][0] for i in range(n)]}; her clusters == my I-291R {cl == [d[i][1] for i in range(n)]}; == my house cells {cl == [d[i][2] for i in range(n)]}')
