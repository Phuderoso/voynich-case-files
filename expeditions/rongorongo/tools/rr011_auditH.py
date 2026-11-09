"""Audit H: RR010 re-run unchanged except seed 10011 (was 10010). The tool writes seed=10010 into its json as a
literal, so this wrapper rewrites that field after the run. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, json, random, rr010_loose_strokes as m
_R = random.Random
m.random.Random = lambda s: _R(10011 if s == 10010 else s)
m.main(sys.argv[1], sys.argv[2])
r = json.load(open(sys.argv[2])); r['seed'] = 10011; r['note'] = 'Audit H: seed field corrected by wrapper (tool writes 10010 literally)'
json.dump(r, open(sys.argv[2], 'w'), indent=1)
