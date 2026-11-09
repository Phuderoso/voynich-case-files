"""Audit G: RR009 re-run unchanged except seed 9010 (was 9009). Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, random, rr009_fusion_conservation as m
_R = random.Random
m.random.Random = lambda s: _R(9010 if s == 9009 else s)
m.main(sys.argv[1], sys.argv[2])
