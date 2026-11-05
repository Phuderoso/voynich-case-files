#!/usr/bin/env python3
"""C034 post-hoc (disclosed, not pre-registered): AUC with context k = 1 and 3, all texts, no null (descriptive).
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import c034_harris_boundaries as X, c003_position_rigidity as T, c030_line_edge_glyphs as L
C = 'data/corpora/'
corp = {'Voynich_ZL3b': ([ws for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt')], T.units),
        'Voynich_IT2a': ([ws for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt')], T.units),
        'Generator_TimmSchinner': ([ws for ws, _ in L.generator()], T.units),
        'Latin_Caesar': (T.gutenberg(C + 'pg218.txt'), None), 'Latin_Descartes': (T.gutenberg(C + 'pg23306.txt'), None),
        'Italian_Dante': (T.gutenberg(C + 'pg1012.txt'), None), 'Italian_Machiavelli': (T.gutenberg(C + 'pg56498.txt'), None),
        'Spanish_Cervantes': (T.gutenberg(C + 'pg2000.txt'), None),
        'Hebrew_Genesis': (T.hebrew(C + 'Gen.xml'), None), 'Hebrew_Exodus': (T.hebrew(C + 'Exod.xml'), None)}
R = {}
for k_ in (1, 3):
    X.K = k_
    for name, (lines, tok) in corp.items():
        s, lab, _ = X.stream(X.words_of(lines), tok)
        R[f'{name}_k{k_}'] = round(X.auc(X.scores(s), lab), 4)
print(json.dumps(R, indent=0)); json.dump(R, open('analysis/C034_posthoc_k.json', 'w'), indent=1)
