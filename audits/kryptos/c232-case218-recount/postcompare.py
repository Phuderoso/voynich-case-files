#!/usr/bin/env python3
"""postcompare.py -- POST HOC (written after opening analyze232.log and case 218, 16:40 MST): checks of her descriptive extras that my frozen
recount232.py did not print. Uses my frozen coefficients/k from res/summary232_voynich.json and my own unit builder (imported logic copied)."""
import json, math, re, glob, os, sys
import numpy as np
from scipy.optimize import brentq
REPO = sys.argv[1]; S = json.load(open('res/summary232_voynich.json')); b = np.array(S['beta']); k = S['k_text']; k05 = S['k05']
fit = lambda nq, N: b[0] + b[1]*math.log(N) + b[2]*math.log(N)**2 + b[3]*nq
bar = lambda nq, N: fit(nq, N) + k
PAT = re.compile(r'^Y model=(\w) p=(\d+) nq=(\d+) n=(\d+) pass=(\d+) max=(\S+)\s*$')
def units(d, lab):
    u = {}
    for f in sorted(glob.glob(f'{d}/R/{lab}_*.txt')):
        for l in open(f):
            g = PAT.match(l)
            if not g: continue
            nq, n = int(g.group(3)), int(g.group(4)); mx = float(g.group(6))
            if nq < 10 or n <= 0: continue
            a = u.setdefault(nq, [0, -1e9]); a[0] += n; a[1] = max(a[1], mx)
    return {q: v for q, v in u.items() if v[0] >= 10}
K4 = units(REPO + '/data/cycle229', 'k4')
over = [(q, n, mx) for q, (n, mx) in sorted(K4.items()) if mx >= fit(q, n) + k05]
print('K4 units over fit+k05:', len(over), 'of', len(K4), over)
cnt = [sum(mx >= fit(q, n) + k05 for q, (n, mx) in units(REPO + '/data/cycle232', f'null{s}').items()) for s in range(209609, 209629)]
print('calibration per-text units over fit+k05:', cnt, 'mean %.2f' % np.mean(cnt))
print('closest K4 unit nq 55 N 24177: bar %.3f' % bar(55, 24177))
print('most lenient bar in domain (N 10, nq 64): %.3f' % bar(64, 10))
print('case 213 null 209425 (-5.292, nq 10): bar at N 17 %.3f; N where bar = -5.292: %.0f' % (bar(10, 17), math.exp(brentq(lambda x: bar(10, math.exp(x)) + 5.292, 1, 15))))
lo = lambda k_, n: ((k_/n + 1.959964**2/(2*n)) - 1.959964*math.sqrt(k_/n*(1-k_/n)/n + 1.959964**2/(4*n*n)))/(1+1.959964**2/n)
hi = lambda k_, n: ((k_/n + 1.959964**2/(2*n)) + 1.959964*math.sqrt(k_/n*(1-k_/n)/n + 1.959964**2/(4*n*n)))/(1+1.959964**2/n)
print('0/28 Wilson hi %.4f; one-error 11/12 Wilson %.3f-%.3f; 0/73 hi %.4f, 0/72 hi %.4f' % (hi(0, 28), lo(11, 12), hi(11, 12), hi(0, 73), hi(0, 72)))
