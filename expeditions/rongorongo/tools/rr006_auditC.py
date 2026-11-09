"""RR006 audit C of RR005: replicate RR005 unchanged with a fresh seed (5006) to measure how much the per-pair
detection floor l1* and the p-values move with the Monte Carlo seed alone.
Usage: python3 rr006_auditC.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, random; sys.path.insert(0, '.')
import rr005_fuzzy_isolation as F
_R = random.Random
F.random.Random = lambda s=None: _R(5006 if s == 5005 else s)
F.main(sys.argv[1], sys.argv[2])
