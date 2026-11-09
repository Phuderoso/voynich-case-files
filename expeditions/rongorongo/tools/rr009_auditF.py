"""RR009 audit F - RR007 re-run unchanged except seed 7008 instead of 7007. Usage: python3 rr009_auditF.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, random; sys.path.insert(0, '.')
_R = random.Random
random.Random = lambda s=None: _R(7008 if s == 7007 else s)
import rr007_shared_trigrams as T
T.main(sys.argv[1], sys.argv[2])
