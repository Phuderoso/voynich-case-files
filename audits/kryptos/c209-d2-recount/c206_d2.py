#!/usr/bin/env python3
"""I-322 side check: D2 (alphabet, form, model, p, j[0..23]) on the published case 206 (cycle 220, w11, col1e4 NAL=4) hit lines.
j recomputed from pi/mode/dir with recount209.perm_maps (same grid construction as col21/col1e4)."""
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount209 import perm_maps, CRP
print("text\tp\tR\tD2\tdistinct_j_only")
for fn in sorted(glob.glob(sys.argv[1]+'/results_*.txt')):
    lab=os.path.basename(fn)[8:-4]; st=collections.defaultdict(lambda:[0,set(),set()])
    for l in open(fn):
        if not l.startswith('H '): continue
        f=l.split(); w,mode,dr,al,be,model,p,e,bad=map(int,f[1:10]); pi=list(map(int,f[10].split(',')))
        S=perm_maps(w,pi)[mode][1 if dr else 0]; j=tuple(S[x] for x in CRP)
        d=st[p]; d[0]+=1; d[1].add((al,be,model,p,j)); d[2].add(j)
    if not st: print(f"{lab}\t-\t0\t0\t0")
    for p in sorted(st): print(f"{lab}\t{p}\t{st[p][0]}\t{len(st[p][1])}\t{len(st[p][2])}")
