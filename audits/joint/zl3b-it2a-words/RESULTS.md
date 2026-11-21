# Real count — ZL3b vs IT2a word division (descriptive; rule: CRITERION.md v2, frozen 09:20:58 MST)

Every share is k/n with Wilson 95 % interval; the table cells below the headline tables show the share only (full numbers in `real/real_all.json`). No test, no label, no ranking of the transcriptions.

## A. Pairing of loci (base)

- loci: ZL3b 5385, IT2a 5215
- **raw key match rate** (folio, line number, locus letter): ZL3b side 5214/5385 = 96.82% [96.32–97.26]; IT2a side 5214/5215 = 99.98% [99.89–100.00]
- key pairs failing the line threshold (released): 53; fallback pairs found among released + unpaired: 0
- **final key match rate**: ZL3b 5161/5385 = 95.84% [95.27–96.34]; IT2a 5161/5215 = 98.96% [98.65–99.20]
- paired 5161; only in ZL3b 224; only in IT2a 54

## Level A per configuration

| config | raw key pairs | released | fallback | paired | only ZL3b | only IT2a |
|---|---|---|---|---|---|---|
| base | 5214 | 53 | 0 | 5161 | 224 | 54 |
| a_glyphmap_rare | 5214 | 53 | 0 | 5161 | 224 | 54 |
| a2_question_wildcard | 5214 | 46 | 3 | 5171 | 214 | 44 |
| b_no_fallback | 5214 | 0 | 0 | 5214 | 171 | 1 |
| c_arrow_removed | 5214 | 53 | 0 | 5161 | 224 | 54 |
| d_comma_nosep | 5214 | 53 | 0 | 5161 | 224 | 54 |
| e_line_1_4 | 5214 | 82 | 0 | 5132 | 253 | 83 |
| e_line_1_2 | 5214 | 24 | 0 | 5190 | 195 | 25 |
| e_token_1_3 | 5214 | 53 | 0 | 5161 | 224 | 54 |
| e_token_2_3 | 5214 | 53 | 0 | 5161 | 224 | 54 |
| alt_second_reading | 5214 | 52 | 0 | 5162 | 223 | 53 |

## B. Paired lines by class (shares; denominator = paired lines of the stratum)

- **all** (n = 5161): division_only 708/5161 = 13.72% [12.81–14.68]; glyph_different 1966/5161 = 38.09% [36.78–39.43]; identical 2487/5161 = 48.19% [46.83–49.55]; unalignable_line 0/5161 = 0.00% [0.00–0.07]
- **P** (n = 4115): division_only 661/4115 = 16.06% [14.97–17.22]; glyph_different 1645/4115 = 39.98% [38.49–41.48]; identical 1809/4115 = 43.96% [42.45–45.48]; unalignable_line 0/4115 = 0.00% [0.00–0.09]
- **P_ret_both** (n = 2885): division_only 499/2885 = 17.30% [15.96–18.72]; glyph_different 1141/2885 = 39.55% [37.78–41.35]; identical 1245/2885 = 43.15% [41.36–44.97]; unalignable_line 0/2885 = 0.00% [0.00–0.13]
- **P_ret_one** (n = 168): division_only 39/168 = 23.21% [17.47–30.15]; glyph_different 119/168 = 70.83% [63.56–77.18]; identical 10/168 = 5.95% [3.26–10.61]; unalignable_line 0/168 = 0.00% [0.00–2.24]
- **CurrierA** (n = 1790): division_only 262/1790 = 14.64% [13.08–16.35]; glyph_different 632/1790 = 35.31% [33.13–37.55]; identical 896/1790 = 50.06% [47.74–52.37]; unalignable_line 0/1790 = 0.00% [0.00–0.21]
- **CurrierB** (n = 2640): division_only 405/2640 = 15.34% [14.02–16.77]; glyph_different 1030/2640 = 39.02% [37.17–40.89]; identical 1205/2640 = 45.64% [43.75–47.55]; unalignable_line 0/2640 = 0.00% [0.00–0.14]
- **CB_ZL3b** (n = 2108): division_only 364/2108 = 17.27% [15.71–18.94]; glyph_different 842/2108 = 39.94% [37.87–42.05]; identical 902/2108 = 42.79% [40.69–44.91]; unalignable_line 0/2108 = 0.00% [0.00–0.18]
- **CB_IT2a** (n = 2136): division_only 363/2136 = 16.99% [15.46–18.65]; glyph_different 868/2136 = 40.64% [38.57–42.73]; identical 905/2136 = 42.37% [40.29–44.48]; unalignable_line 0/2136 = 0.00% [0.00–0.18]

### Level B per configuration (stratum all / CB_ZL3b): identical | division_only | glyph_different | unalignable_line

| config | all identical | all division_only | all glyph_different | all unalignable | CB_ZL3b identical | CB_ZL3b division_only |
|---|---|---|---|---|---|---|
| base | 48.19% | 13.72% | 38.09% | 0.00% | 42.79% | 17.27% |
| a_glyphmap_rare | 48.19% | 13.72% | 38.09% | 0.00% | 42.79% | 17.27% |
| a2_question_wildcard | 48.10% | 13.69% | 38.21% | 0.00% | 42.79% | 17.27% |
| b_no_fallback | 47.70% | 13.58% | 37.71% | 1.02% | 42.79% | 17.27% |
| c_arrow_removed | 47.86% | 14.05% | 38.09% | 0.00% | 42.69% | 17.36% |
| d_comma_nosep | 43.56% | 18.35% | 38.09% | 0.00% | 34.91% | 25.14% |
| e_line_1_4 | 48.46% | 13.80% | 37.74% | 0.00% | 42.81% | 17.28% |
| e_line_1_2 | 47.92% | 13.64% | 38.44% | 0.00% | 42.79% | 17.27% |
| e_token_1_3 | 48.19% | 13.72% | 38.09% | 0.00% | 42.79% | 17.27% |
| e_token_2_3 | 48.19% | 13.72% | 38.09% | 0.00% | 42.79% | 17.27% |
| alt_second_reading | 47.04% | 13.52% | 39.44% | 0.00% | 41.32% | 16.98% |

## C. Tokens (both transcriptions, in aligned lines; counted as tokens of both sides in the group)

- **all** (76206 tokens): glyph_different 5955/76206 = 7.81% [7.63–8.01]; identical 65734/76206 = 86.26% [86.01–86.50]; split_merge 4294/76206 = 5.63% [5.47–5.80]; unalignable 223/76206 = 0.29% [0.26–0.33]
- **P_ret_both** (52792 tokens): glyph_different 3076/52792 = 5.83% [5.63–6.03]; identical 46750/52792 = 88.56% [88.28–88.82]; split_merge 2909/52792 = 5.51% [5.32–5.71]; unalignable 57/52792 = 0.11% [0.08–0.14]
- **CurrierA** (22940 tokens): glyph_different 1741/22940 = 7.59% [7.25–7.94]; identical 19718/22940 = 85.95% [85.50–86.40]; split_merge 1416/22940 = 6.17% [5.87–6.49]; unalignable 65/22940 = 0.28% [0.22–0.36]
- **CurrierB** (46700 tokens): glyph_different 2886/46700 = 6.18% [5.96–6.40]; identical 41322/46700 = 88.48% [88.19–88.77]; split_merge 2444/46700 = 5.23% [5.04–5.44]; unalignable 48/46700 = 0.10% [0.08–0.14]
- **CB_ZL3b** (40893 tokens): glyph_different 2321/40893 = 5.68% [5.46–5.90]; identical 36388/40893 = 88.98% [88.68–89.28]; split_merge 2161/40893 = 5.28% [5.07–5.51]; unalignable 23/40893 = 0.06% [0.04–0.08]
- **CB_IT2a** (41392 tokens): glyph_different 2367/41392 = 5.72% [5.50–5.95]; identical 36790/41392 = 88.88% [88.58–89.18]; split_merge 2205/41392 = 5.33% [5.12–5.55]; unalignable 30/41392 = 0.07% [0.05–0.10]

### Level C per configuration (stratum all)

| config | identical | split_merge | glyph_different | unalignable |
|---|---|---|---|---|
| base | 86.26% | 5.63% | 7.81% | 0.29% |
| a_glyphmap_rare | 86.26% | 5.63% | 7.81% | 0.29% |
| a2_question_wildcard | 86.20% | 5.92% | 7.65% | 0.22% |
| b_no_fallback | 86.26% | 5.63% | 7.81% | 0.29% |
| c_arrow_removed | 85.72% | 5.90% | 8.06% | 0.31% |
| d_comma_nosep | 83.35% | 8.10% | 8.27% | 0.27% |
| e_line_1_4 | 86.37% | 5.65% | 7.74% | 0.24% |
| e_line_1_2 | 86.18% | 5.63% | 7.89% | 0.31% |
| e_token_1_3 | 86.26% | 5.63% | 6.97% | 1.14% |
| e_token_2_3 | 86.26% | 5.63% | 7.93% | 0.18% |
| alt_second_reading | 86.06% | 5.62% | 8.01% | 0.31% |

### Split/merge detail (base)

- groups: ZL3b token divided in IT2a 478; ZL3b tokens merged in IT2a 914; shift (2:2) 16
- separator on the dividing side: `.` 619, `,` 843
- glyph_different groups: 1:1 2551, other 274
- separator cross-table at group boundaries (ZL3b sep / IT2a sep): {'ZL3b,_IT2a.': 1695, 'ZL3b._IT2a.': 30154}
- top equal-length glyph substitutions (ZL3b>IT2a): [['a>o', 418], ['o>a', 188], ['e>h', 154], ['r>s', 153], ['e>c', 150], ['s>r', 144], ['h>e', 105], ['c>e', 84], ['k>t', 81], ['y>o', 77], ['c>s', 70], ['t>k', 67], ['s>c', 58], ['g>m', 49], ['h>s', 49]]
- top boundary glyph pairs on dividing sides: [['r|a', 109], ['l|s', 81], ['o|l', 76], ['l|k', 75], ['l|c', 73], ['s|a', 66], ['o|k', 55], ['y|k', 51], ['o|d', 46], ['l|d', 46], ['o|r', 43], ['y|c', 39], ['y|t', 33], ['l|a', 31], ['y|d', 30]]
- retention flag over paired lines: {'ZL3b_ret=False_IT2a_ret=False': 2037, 'ZL3b_ret=False_IT2a_ret=True': 92, 'ZL3b_ret=True_IT2a_ret=False': 102, 'ZL3b_ret=True_IT2a_ret=True': 2930}
- words per line, ZL3b − IT2a: equal 3879/5161 = 75.16% [73.96–76.32]; mean 0.098; mean |diff| 0.298

## (h) `_` symbols of the CB unit stream that differ (base)

Share of a transcription's `_` symbols (one per word) in paired lines that have no counterpart at the same glyph-alignment column in the other transcription. Position class = the line in its own CB 4-line-block geometry.

### ZL3b-side

CB lines 2114; `_` in the CB stream {'ALL': 20744, 'first': 4894, 'interior': 9891, 'last': 4911, 'tail': 1048}; `_` in CB lines without a paired counterpart {'ALL': 154, 'first': 33, 'interior': 71, 'last': 45, 'tail': 5} (not part of *differ*).

| class | all `_` | non-final `_` | line-final `_` | all `_`, lines with identical G | non-final, identical G |
|---|---|---|---|---|---|
| ALL | 591/20590 = 2.87% [2.65–3.11] | 586/18482 = 3.17% [2.93–3.43] | 5/2108 = 0.24% [0.10–0.55] | 294/11964 = 2.46% [2.20–2.75] | 294/10698 = 2.75% [2.46–3.08] |
| first | 143/4861 = 2.94% [2.50–3.45] | 143/4364 = 3.28% [2.79–3.85] | 0/497 = 0.00% [0.00–0.77] | 64/2682 = 2.39% [1.87–3.04] | 64/2391 = 2.68% [2.10–3.40] |
| interior | 275/9820 = 2.80% [2.49–3.15] | 272/8826 = 3.08% [2.74–3.46] | 3/994 = 0.30% [0.10–0.88] | 139/5710 = 2.43% [2.07–2.87] | 139/5110 = 2.72% [2.31–3.20] |
| last | 135/4866 = 2.77% [2.35–3.27] | 134/4370 = 3.07% [2.60–3.62] | 1/496 = 0.20% [0.04–1.13] | 69/2984 = 2.31% [1.83–2.92] | 69/2679 = 2.58% [2.04–3.25] |
| tail | 38/1043 = 3.64% [2.67–4.96] | 37/922 = 4.01% [2.93–5.48] | 1/121 = 0.83% [0.15–4.53] | 22/588 = 3.74% [2.48–5.60] | 22/518 = 4.25% [2.82–6.35] |

### IT2a-side

CB lines 2136; `_` in the CB stream {'ALL': 20556, 'first': 4882, 'interior': 9906, 'last': 4822, 'tail': 946}; `_` in CB lines without a paired counterpart {} (not part of *differ*).

| class | all `_` | non-final `_` | line-final `_` | all `_`, lines with identical G | non-final, identical G |
|---|---|---|---|---|---|
| ALL | 319/20556 = 1.55% [1.39–1.73] | 312/18420 = 1.69% [1.52–1.89] | 7/2136 = 0.33% [0.16–0.68] | 157/11873 = 1.32% [1.13–1.54] | 157/10605 = 1.48% [1.27–1.73] |
| first | 78/4882 = 1.60% [1.28–1.99] | 78/4375 = 1.78% [1.43–2.22] | 0/507 = 0.00% [0.00–0.75] | 39/2810 = 1.39% [1.02–1.89] | 39/2508 = 1.56% [1.14–2.12] |
| interior | 146/9906 = 1.47% [1.26–1.73] | 144/8892 = 1.62% [1.38–1.90] | 2/1014 = 0.20% [0.05–0.72] | 77/5656 = 1.36% [1.09–1.70] | 77/5060 = 1.52% [1.22–1.90] |
| last | 78/4822 = 1.62% [1.30–2.01] | 74/4315 = 1.71% [1.37–2.15] | 4/507 = 0.79% [0.31–2.01] | 37/2916 = 1.27% [0.92–1.74] | 37/2606 = 1.42% [1.03–1.95] |
| tail | 17/946 = 1.80% [1.12–2.86] | 16/838 = 1.91% [1.18–3.08] | 1/108 = 0.93% [0.16–5.06] | 4/491 = 0.81% [0.32–2.08] | 4/431 = 0.93% [0.36–2.36] |

### (h) per configuration, all `_` of the CB stream

| config | ZL3b side | IT2a side | ZL3b first / last / interior (non-final) | IT2a first / last / interior (non-final) |
|---|---|---|---|---|
| base | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| a_glyphmap_rare | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| a2_question_wildcard | 2.87% | 1.54% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.61% |
| b_no_fallback | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| c_arrow_removed | 2.89% | 1.60% | 3.32% / 3.09% / 3.09% | 1.87% / 1.76% / 1.65% |
| d_comma_nosep | 0.46% | 6.26% | 0.55% / 0.42% / 0.45% | 7.66% / 6.98% / 6.56% |
| e_line_1_4 | 2.86% | 1.55% | 3.28% / 3.02% / 3.08% | 1.78% / 1.71% / 1.62% |
| e_line_1_2 | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| e_token_1_3 | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| e_token_2_3 | 2.87% | 1.55% | 3.28% / 3.07% / 3.08% | 1.78% / 1.71% / 1.62% |
| alt_second_reading | 2.86% | 1.54% | 3.25% / 3.07% / 3.09% | 1.78% / 1.69% / 1.63% |

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
