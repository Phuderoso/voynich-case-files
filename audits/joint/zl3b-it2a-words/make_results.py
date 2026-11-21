#!/usr/bin/env python3
"""Builds RESULTS.md from real_all.json (no new computation). Usage: python3 make_results.py real/real_all.json RESULTS.md"""
import json, sys, glob, os
d, out = sys.argv[1], sys.argv[2]
order = ['base', 'a_glyphmap_rare', 'a2_question_wildcard', 'b_no_fallback', 'c_arrow_removed', 'd_comma_nosep', 'e_line_1_4', 'e_line_1_2', 'e_token_1_3', 'e_token_2_3', 'alt_second_reading']
R = json.load(open(d))
def f(v): return 'n/a' if v is None or v['share'] is None else f"{v['k']}/{v['n']} = {100*v['share']:.2f}% [{100*v['wilson'][0]:.2f}–{100*v['wilson'][1]:.2f}]"
def p(v): return 'n/a' if v is None or v['share'] is None else f"{100*v['share']:.2f}%"
L = ['# Real count — ZL3b vs IT2a word division (descriptive; rule: CRITERION.md v2, frozen 09:20:58 MST)', '',
     'Every share is k/n with Wilson 95 % interval; the table cells below the headline tables show the share only (full numbers in `real/real_all.json`). No test, no label, no ranking of the transcriptions.', '']
b = R['base']; A = b['A']
L += ['## A. Pairing of loci (base)', '', f"- loci: ZL3b {A['loci_ZL3b']}, IT2a {A['loci_IT2a']}",
      f"- **raw key match rate** (folio, line number, locus letter): ZL3b side {f(A['raw_key_match_rate_ZL3b'])}; IT2a side {f(A['raw_key_match_rate_IT2a'])}",
      f"- key pairs failing the line threshold (released): {A['key_released_to_fallback']}; fallback pairs found among released + unpaired: {A['fallback_matched']}",
      f"- **final key match rate**: ZL3b {f(A['key_match_rate_ZL3b'])}; IT2a {f(A['key_match_rate_IT2a'])}",
      f"- paired {A['matched']}; only in ZL3b {A['only_ZL3b']}; only in IT2a {A['only_IT2a']}", '']
L += ['## Level A per configuration', '', '| config | raw key pairs | released | fallback | paired | only ZL3b | only IT2a |', '|---|---|---|---|---|---|---|']
for c in order:
    a = R[c]['A']; L.append(f"| {c} | {a['raw_key_matched']} | {a['key_released_to_fallback']} | {a['fallback_matched']} | {a['matched']} | {a['only_ZL3b']} | {a['only_IT2a']} |")
L += ['', '## B. Paired lines by class (shares; denominator = paired lines of the stratum)', '']
for s in ('all', 'P', 'P_ret_both', 'P_ret_one', 'CurrierA', 'CurrierB', 'CB_ZL3b', 'CB_IT2a'):
    x = b['B'][s]; L.append(f"- **{s}** (n = {x['total']}): " + '; '.join(f"{k} {f(v)}" for k, v in x['classes'].items()))
L += ['', '### Level B per configuration (stratum all / CB_ZL3b): identical | division_only | glyph_different | unalignable_line', '', '| config | all identical | all division_only | all glyph_different | all unalignable | CB_ZL3b identical | CB_ZL3b division_only |', '|---|---|---|---|---|---|---|']
for c in order:
    x = R[c]['B']['all']['classes']; y = R[c]['B']['CB_ZL3b']['classes']
    L.append(f"| {c} | {p(x['identical'])} | {p(x['division_only'])} | {p(x['glyph_different'])} | {p(x['unalignable_line'])} | {p(y['identical'])} | {p(y['division_only'])} |")
L += ['', '## C. Tokens (both transcriptions, in aligned lines; counted as tokens of both sides in the group)', '']
for s in ('all', 'P_ret_both', 'CurrierA', 'CurrierB', 'CB_ZL3b', 'CB_IT2a'):
    x = b['C'][s]; L.append(f"- **{s}** ({x['tokens_in_aligned_lines']} tokens): " + '; '.join(f"{k} {f(v)}" for k, v in x['classes'].items()))
L += ['', '### Level C per configuration (stratum all)', '', '| config | identical | split_merge | glyph_different | unalignable |', '|---|---|---|---|---|']
for c in order:
    x = R[c]['C']['all']['classes']; L.append(f"| {c} | {p(x['identical'])} | {p(x['split_merge'])} | {p(x['glyph_different'])} | {p(x['unalignable'])} |")
dd = b['C_detail']
L += ['', '### Split/merge detail (base)', '', f"- groups: ZL3b token divided in IT2a {dd.get('ZL3b_divided_in_IT2a',0)}; ZL3b tokens merged in IT2a {dd.get('ZL3b_merged_in_IT2a',0)}; shift (2:2) {dd.get('shift_2_2',0)}",
      f"- separator on the dividing side: `.` {dd.get('dividing_sep_.',0)}, `,` {dd.get('dividing_sep_,',0)}",
      f"- glyph_different groups: 1:1 {dd.get('glyph_different_1_1',0)}, other {dd.get('glyph_different_other',0)}",
      f"- separator cross-table at group boundaries (ZL3b sep / IT2a sep): {b['C_separator_cross_at_group_boundaries']}",
      f"- top equal-length glyph substitutions (ZL3b>IT2a): {b['C_top_glyph_substitutions_equal_length']}",
      f"- top boundary glyph pairs on dividing sides: {b['C_top_split_boundary_pairs']}",
      f"- retention flag over paired lines: {b['retention_matched_pairs']}",
      f"- words per line, ZL3b − IT2a: equal {f(b['words_per_line_diff_ZL3b_minus_IT2a']['equal'])}; mean {b['words_per_line_diff_ZL3b_minus_IT2a']['mean']:.3f}; mean |diff| {b['words_per_line_diff_ZL3b_minus_IT2a']['mean_abs']:.3f}", '']
H = b['h_underscore_differs_in_CB_unit_stream']
L += ['## (h) `_` symbols of the CB unit stream that differ (base)', '', 'Share of a transcription\'s `_` symbols (one per word) in paired lines that have no counterpart at the same glyph-alignment column in the other transcription. Position class = the line in its own CB 4-line-block geometry.', '']
for t in ('ZL3b', 'IT2a'):
    h = H[t]; L += [f"### {t}-side", '', f"CB lines {h['CB_lines']}; `_` in the CB stream {h['underscores_total_CB_stream']}; `_` in CB lines without a paired counterpart {h['underscores_in_lines_without_counterpart_or_unalignable']} (not part of *differ*).", '',
                    '| class | all `_` | non-final `_` | line-final `_` | all `_`, lines with identical G | non-final, identical G |', '|---|---|---|---|---|---|']
    for cl in ('ALL', 'first', 'interior', 'last', 'tail'):
        g = lambda k: f(h['table'].get(f'{cl}|{k}'))
        L.append(f"| {cl} | {g('all')} | {g('interior')} | {g('final')} | {g('all_Gidentical')} | {g('interior_Gidentical')} |")
    L.append('')
L += ['### (h) per configuration, all `_` of the CB stream', '', '| config | ZL3b side | IT2a side | ZL3b first / last / interior (non-final) | IT2a first / last / interior (non-final) |', '|---|---|---|---|---|']
for c in order:
    hh = R[c]['h_underscore_differs_in_CB_unit_stream']; z, i = hh['ZL3b']['table'], hh['IT2a']['table']
    L.append(f"| {c} | {p(z['ALL|all'])} | {p(i['ALL|all'])} | {p(z['first|interior'])} / {p(z['last|interior'])} / {p(z['interior|interior'])} | {p(i['first|interior'])} / {p(i['last|interior'])} / {p(i['interior|interior'])} |")
L += ['', '— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04', '']
open(out, 'w').write('\n'.join(L))
