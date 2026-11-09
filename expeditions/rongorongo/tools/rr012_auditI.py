"""RR012 audit I - seed replication of RR008 (shared trigrams after H/P/Q-learned sign families): RR008 step 2 exactly
(rr008_equiv_trigrams.py logic, same pinned equivalences rr008_equivalences.json), seed 12008 instead of 8008.
Pass = every pair keeps its verdict and k* moves by at most 1.
Usage: python3 rr012_auditI.py corpus.json rr008_equivalences.json out.json
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
random.Random = lambda s=None: _R(12008 if s == 7007 else s)
import rr007_shared_trigrams as T
T.main(sys.argv[1], sys.argv[3])
