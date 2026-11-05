#!/usr/bin/env python3
"""C040 POST-HOC (labelled, not pre-registered): rerun the identical C040 pipeline, seed and gates on the 20 pages that
C039 never saw (drop f58r, f58v, f111r, f113v), as an out-of-sample check on the HALF verdict.
Run: timeout 600 python3 tools/c040_posthoc_new_pages_only.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import c040_comma_gap_widths_pages as M
for f in ('f58r', 'f58v', 'f111r', 'f113v'): M.PAGES.pop(f)
M.OUT = 'analysis/C040_posthoc_new_pages_only.json'
M.main()
