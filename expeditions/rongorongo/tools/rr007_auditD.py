"""RR007 audit D of RR004: re-run RR004 unchanged with seed 4006 instead of 4004 (generator swapped, label unchanged).
Usage: python3 rr007_auditD.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, random; sys.path.insert(0, '.')
_R = random.Random
random.Random = lambda s=None: _R(4006 if s == 4004 else s)
import rr004_stroke_hosts as H
H.main(sys.argv[1], sys.argv[2])
