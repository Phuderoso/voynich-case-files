"""RR005 audit B: RR001 (exact longest common run) re-run with the RR004 code normalisation (head_norm), same seed 3001,
R 999, 100 plants. In RR001, 95 of 680 Aa units had unpadded heads ('4.120a') and were read as illegible.
Usage: python3 rr005_auditB.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys; sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # installs head_norm into rr001_isolation
import rr001_isolation as R1
R1.main(sys.argv[1], sys.argv[2], 999, 100)
