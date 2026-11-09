"""RR008 step 2 - RR007's shared-trigram test with head signs mapped to the equivalence classes learned in step 1 from
the H/P/Q copies only (rr008_equivalences.py). Everything else is RR007 unchanged (statistic, Markov null on the
MAPPED y, R 999, Holm over 25, gates, planted 4-sign excerpts, k* <= 8), seed 8008 instead of 7007.
Usage: python3 rr008_equiv_trigrams.py corpus.json equivalences.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random; sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # installs head_norm
import rr001_isolation as R1
cmap = json.load(open(sys.argv[2]))['map']
_h = R1.head
def head_mapped(u, k):
    h = _h(u, k)
    return h if isinstance(h, tuple) else cmap.get(h, h)
R1.head = head_mapped
_R = random.Random
random.Random = lambda s=None: _R(8008 if s == 7007 else s)
import rr007_shared_trigrams as T
T.main(sys.argv[1], sys.argv[3])
