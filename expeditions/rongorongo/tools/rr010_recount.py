"""RR010 independent recount of S1/S2 from raw CEIPP lines, own parser (no import of RR009/RR010 code).
Input: corpus.json and the results json (uses only its disagreement_list: bare line key + position, wanted strokes).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys
ST = {'1', '2', '3', '4', '9'}
def comps(u): return [c for c in re.split(r'[.:]', u) if c]
def num(c):
    m = re.match(r'0*(\d+)', c); return m.group(1) if m else None
def free(u):
    cs = comps(u)
    if not cs or any(num(c) not in ST for c in cs): return None
    return {num(c) for c in cs if not any(ch in c for ch in '!?)')}
c = json.load(open(sys.argv[1])); res = json.load(open(sys.argv[2])); s1 = s2 = 0
for d in res['disagreement_list']:
    _, k, p, _ = d['bare']; line = c[k]; want = {w.lstrip('0') for w in d['want']}
    nb = [free(line[q]) for q in (p - 1, p + 1) if 0 <= q < len(line)]; nb = [x for x in nb if x is not None]
    s2 += any(nb); s1 += any(x & want for x in nb)
print(dict(S1=s1, S2=s2, tool_S1=res['S1'], tool_S2=res['S2'], match=(s1, s2) == (res['S1'], res['S2'])))
