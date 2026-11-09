"""RR004 audit A: RR003 re-run unchanged except that codes are padded before stroke matching (seed 3003).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, re
sys.path.insert(0, '.')
import rr003_stroke_clustering as R3
from rr004_stroke_hosts import pad
R3.is_stroke = lambda u: not re.search(r"[.:;'!?]", u) and re.match(r'00[12349]', pad(u)) is not None
R3.main(sys.argv[1], sys.argv[2])
