#!/usr/bin/env python3
"""K062 part 1 - pre-registered literature audit of the two K061 leads (K043/K052 style, with positive controls).
Lead A: KH0132 (UR1118; Ascher AS118) . KH0456 (UR218), Pachacamac, Berlin VA42601 / VA 42559.
Lead B: KH0446 (UR208) . KH0451 (UR213), Pachacamac, Berlin 42549 / VA42508(B).
Not a statistical test. Modes:
  targets : check the pinned khipu.db hash and the OKR <-> investigator ids of subjects and controls, check that
            analysis/k061_results.json names exactly these two leads, write analysis/k062_targets.json (URLs to look up).
  context : read-only khipu.db labels (museum, notes, orig ids) of the four subjects -> analysis/k062_okr_context.json (descriptive).
  merge   : read analysis/k062_records.json (hand-recorded after the reads), enforce the pre-registered labels and control
            gates, write analysis/k062_literature_results.json.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import hashlib, json, os, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.join(HERE, '..', 'analysis'); DB = os.path.join(HERE, '..', 'data', 'khipu.db')
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
LEADS = {'A': ('KH0132', 'KH0456'), 'B': ('KH0446', 'KH0451')}
SUBJECTS = {'KH0132': 'UR1118', 'KH0456': 'UR218', 'KH0446': 'UR208', 'KH0451': 'UR213'}
ALIASES = {'KH0132': ['UR1118', 'AS118', 'VA42601', 'VA 42601'], 'KH0456': ['UR218', 'VA 42559', 'VA42559'],
           'KH0446': ['UR208', '42549'], 'KH0451': ['UR213', 'VA42508']}
CONTROLS = {'C1': dict(evidence_class='E1_similar_field', okr='KH0616', inv='JC009', partner_okr='KH0620', partner_inv='JC013'),
            'C2': dict(evidence_class='E2_publication_match', okr='KH0502', inv='UR266', partner_okr='KH0514', partner_inv='UR275')}
SRC_LABELS = {'pairs_them', 'other_partner_or_discussed', 'not_mentioned', 'source_missing'}
KFG = 'https://www.khipufieldguide.com/catalog/{}.html'; XLSX = 'https://www.khipufieldguide.com/databook/excel_khipus/{}.xlsx'
APPX = 'https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1045663500008786/resource/name/S1045663500008786sup001.pdf'
def open_db():
    h = hashlib.sha256(open(DB, 'rb').read()).hexdigest()
    if h != SHA: sys.exit(f'EXCLUDED: khipu.db hash {h}')
    return sqlite3.connect('file:' + DB + '?mode=ro', uri=True)
def check():
    db = open_db(); want = dict(SUBJECTS)
    for cc in CONTROLS.values(): want[cc['okr']] = cc['inv']; want[cc['partner_okr']] = cc['partner_inv']
    got = {o: i for o, i in db.execute('select OKR_NUM, INVESTIGATOR_NUM from khipu_main where OKR_NUM in (%s)' % ','.join('?' * len(want)), tuple(want))}
    if got != want: sys.exit(f'EXCLUDED: id map differs {got}')
    d = json.load(open(os.path.join(AN, 'k061_results.json')))['H1']['discoveries']
    new = {frozenset((r['a'], r['b'])) for r in d if not r['known_k012'] and frozenset((r['a'], r['b'])) != frozenset(('KH0616', 'KH0620'))}
    if new != {frozenset(v) for v in LEADS.values()}: sys.exit(f'EXCLUDED: K061 leads differ {new}')
    return db
def targets():
    check()
    out = dict(cycle='K062', leads={k: list(v) for k, v in LEADS.items()},
               subjects=[dict(okr=o, inv=i, aliases=ALIASES[o], kfg=KFG.format(o), xlsx=XLSX.format(o)) for o, i in SUBJECTS.items()],
               controls={k: dict(v, kfg=KFG.format(v['okr'])) for k, v in CONTROLS.items()}, appendix_I=APPX,
               publications=['Urton 2014, Quipus de Pachacamac (subject pages per KFG bibliographies)', 'Ascher databook entry AS118',
                             'Urton 2017 Inka History in Knots', 'any UR-series note (KFG notes, OKR NOTES)'])
    json.dump(out, open(os.path.join(AN, 'k062_targets.json'), 'w'), indent=1); print('targets written')
def context():
    db = check(); cols = [r[1] for r in db.execute('pragma table_info(khipu_main)')]; out = {}
    for o in SUBJECTS:
        r = dict(zip(cols, db.execute('select * from khipu_main where OKR_NUM=?', (o,)).fetchone()))
        out[o] = {k: r[k] for k in ('INVESTIGATOR_NUM', 'orig_inv_num', 'PROVENANCE', 'MUSEUM_NAME', 'MUSEUM_NUM', 'DUPLICATE_FLAG', 'DUPLICATE_ID', 'NOTES', 'NICKNAME', 'DISCOVERED_BY', 'CREATED_BY')}
        out[o]['level1_cords'] = db.execute('select count(*) from cord where KHIPU_ID=? and CORD_LEVEL=1', (r['KHIPU_ID'],)).fetchone()[0]
    json.dump(out, open(os.path.join(AN, 'k062_okr_context.json'), 'w'), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
def merge():
    rec = json.load(open(os.path.join(AN, 'k062_records.json')))
    ctrl = {k: bool(rec['controls'][k]['passed']) for k in CONTROLS}; cls_ok = {CONTROLS[k]['evidence_class']: v for k, v in ctrl.items()}
    res = dict(controls=ctrl, leads={})
    for L, (a, b) in LEADS.items():
        srcs = [s for s in rec['sources'] if s['lead'] == L]
        for s in srcs:
            assert s['label'] in SRC_LABELS, s
            s['usable'] = s['label'] != 'source_missing' and cls_ok.get(s['evidence_class'], True)
        pairs = [s for s in srcs if s['usable'] and s['label'] == 'pairs_them']
        cover = {x: any(s['usable'] and x in s['subjects'] for s in srcs) for x in (a, b)}
        if not any(ctrl.values()): v = 'method_excluded'
        elif pairs: v = 'already_published'
        elif all(cover.values()): v = 'not_found_in_retrieved_sources'
        else: v = 'method_excluded'
        res['leads'][L] = dict(pair=[a, b], verdict=v, sources=len(srcs), usable=sum(s['usable'] for s in srcs), pairing_sources=[s['id'] for s in pairs],
                               coverage=cover, unresolved=[s['id'] for s in srcs if s['label'] == 'source_missing'])
    res['searches'] = rec.get('searches', [])
    json.dump(res, open(os.path.join(AN, 'k062_literature_results.json'), 'w'), indent=1); print(json.dumps(res, indent=1))
if __name__ == '__main__': dict(targets=targets, context=context, merge=merge)[sys.argv[1]]()
