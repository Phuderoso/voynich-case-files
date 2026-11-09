"""RR011a independent recount of T1 and T2 on the observed Keiti text (numpy, own parser; imports nothing from the
RR011 tool). Must equal the tool's T1/T2 to 1e-9. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, numpy as np
c = json.load(open(sys.argv[1])); res = json.load(open(sys.argv[2]))
streams = {}
for side in ('Er', 'Ev'):
    toks, lid = [], []
    for k in sorted(x for x in c if x.startswith(side)):
        for u in c[k]:
            t = u.replace('?', '').replace('!', '').replace(')', '')
            head = t.replace(':', '.').split('.')[0]
            toks.append(None if set(head) == {'0'} else t); lid.append(k)
    streams[side] = (toks, lid)
pairs = {}
for side, (toks, lid) in streams.items():
    for i in range(len(toks) - 1):
        if lid[i] == lid[i + 1] and toks[i] is not None and toks[i + 1] is not None:
            pairs.setdefault((toks[i], toks[i + 1]), {}).setdefault(side, []).append(i)
ref = {g: v for g, v in pairs.items() if sum(map(len, v.values())) >= 4}
cvs, ws, zs = [], [], []
for g in sorted(ref):
    for side in ('Er', 'Ev'):
        s = np.array(ref[g].get(side, []))
        if len(s) < 3: continue
        gap = np.diff(s); cvs.append(gap.std() / gap.mean()); ws.append(len(gap))
        P = np.arange(4, 61)[:, None]; z = np.abs(np.exp(2j * np.pi * s[None, :] / P).sum(1)) ** 2 / len(s); zs.append(z.max())
T1 = float(np.dot(cvs, ws) / np.sum(ws)); T2 = float(np.mean(zs))
print(dict(refrains=len(ref), units=len(cvs), T1=T1, T2=T2, tool_T1=res['T1'], tool_T2=res['T2'],
           match=abs(T1 - res['T1']) < 1e-9 and abs(T2 - res['T2']) < 1e-9))
