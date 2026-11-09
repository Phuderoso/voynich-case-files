"""RR014 triage-only structural count (run AFTER G1 failed; not a test, no S1/S2): family N of rr014_new_family.py
with the run threshold lowered to LMIN 4 and 3, to see whether any looser passage rule could reach G1 (D >= 10).
Usage: python3 rr014_triage_structural.py corpus.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, rr014_new_family as t
c = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'corpus.json'))
for L in (4, 3):
    orig = t.runs
    t.runs = lambda x, y, lmin=L, f=orig: f(x, y, lmin)
    sides, links, passages, D = t.disagreements(c)
    elig = sum(1 for a, i, b, j in links if sides[a][i][1] or sides[b][j][1])
    print(dict(LMIN=L, passages=len(passages), aligned=len(links), eligible=elig, disagreements=len(D)))
    t.runs = orig
