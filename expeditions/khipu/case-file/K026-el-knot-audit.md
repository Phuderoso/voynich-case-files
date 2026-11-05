# K026 · Where do the inconsistent E and L knots come from? (README line 4)

## Why
K007 found that `E` (figure-eight) and `L` (long) knots in `khipu.db` break the decimal reading rules a little more
often than the 1% bar: 89 `E` knots not valued 1 (R1) and 490 `L` knots whose value isn't their turn count in 2–9
(R2). Before writing a data-quality note to the Open Khipu Repository (OKR), two questions need exact answers:
**are these errors clustered in particular khipus or recording series** (a transcription batch) or spread evenly,
and **which field looks wrong** in each case (the knot type, the value, or the turn count)?

## Pre-registration (written before the analysis code was run)
Data: OKR `khipu.db` as in K001–K025, non-duplicate khipus. Audited knots are those K007 audited: all `E` knots, and
`L` knots with `NUM_TURNS` recorded. A **violation** is a K007 R1 or R2 violation.

**H1 (concentration).** Violations are concentrated by khipu beyond chance.
- Statistic: the G statistic (likelihood ratio) of violations per khipu against the expected count, which is the
  khipu's share of audited knots computed separately for `E` and `L`.
- Null: permute violation labels among audited knots, within knot type, across the corpus. 10 000 replicates.
- Second test with the same statistic and null, grouped by recording series (the letter prefix of
  `INVESTIGATOR_NUM`, e.g. UR, AS, JC).
- Decision: Bonferroni ×2, α = 0.025 each. Supported if p < 0.025.
- Power: plant 50 extra violations (relabel valid knots) into 3 random khipus on null-labelled data; 100 trials.
  Below 0.8 power, a non-significant result is *not testable*, not a negative.

**H2 (which field is wrong).** Exact classification, no test. Each violation goes into exactly one category:
- `E` knots:
  - **E-type**: value 10^k with k ≥ 1 and the knot's cluster is not the last cluster on its cord (the position
    agrees with the value, so the type code is the suspect).
  - **E-value**: value 10^k with k ≥ 1 in the last (units) cluster (the position agrees with `E`, so the value is the
    suspect).
  - **E-zero**: value 0 or empty.
  - **E-other**: anything else.
- `L` knots:
  - **L-shift**: turns in 2–9 and value = turns × 10^k with k ≥ 1.
  - **L-off1**: turns in 2–9 and |value − turns| = 1.
  - **L-zero**: turns in 2–9 and value 0 or empty.
  - **L-other**: turns in 2–9, anything else.
  - **L-turn1**: turns = 1 (the turn count says `E`).
  - **L-turn0**: turns = 0.
  - **L-turn10+**: turns ≥ 10.
- Decision: a category with ≥ 20 knots is reported as **noteworthy for an OKR note**, with example knot ids.
  Smaller categories are listed but not raised.

## Results
(Written after the run, below this line.)

Run: `python3 tools/k026_el_knot_audit.py ../khipu.db` (2.3 s). Output: `analysis/k026_results.json`, log `k026_run1.log`.
**Disclosure:** the first call pointed at an empty copy of the database (`exp/khipu.db`, no tables) and crashed
before computing anything. It was rerun on the real file. The code is unchanged from the pre-registration commit `f31294fe`.

30 209 audited knots, 579 violations (89 `E`, 490 `L`).

### H1 · Concentration: supported
| Grouping | G observed | Null mean (99th pct) | p | Verdict |
|---|---|---|---|---|
| Khipu | 2 249 | 476 (535) | < 10⁻⁴ | **supported** (power 1.00 at 50 planted in 3 khipus) |
| Recording series | 203 | 5.2 (14.8) | < 10⁻⁴ | **supported** |

The errors are clustered rather than spread evenly. One khipu, **KH0103 (AS090/N2, Munich)**, holds 98 of the 579 (2.8
expected). It's followed by KH0108 (UR1095, Munich; 51 vs 5.0), KH0001 (LL01/UR176; 33 vs 5.2) and KH0431 (UR193; 29 vs 7.6).
By series, the Ascher (AS) transcriptions have twice their share (200 vs 101), and the HP series is almost clean (1 vs 15.7).

### H2 · Which field looks wrong
| Category | n | Noteworthy (≥ 20) | Where | Reading |
|---|---|---|---|---|
| L-turn0 | 186 | **yes** | spread (UR003, UR1095, UR154, UR143: 16–18 each) | turns = 0, value mostly 10 or 100: type `L` looks wrong (a single knot coded as long) or turns weren't recorded |
| L-turn10+ | 155 | **yes** | UR1095 34, LL01/UR176 32, UR193 29, UR055 22 | turns 10–13 with value = turns: a units "digit" above 9, so either a real non-decimal use or a turn-count error |
| L-shift | 117 | **yes** | **AS090/N2 74**, AS028 14, AS080 10 | value = turns × 10 or × 100 (e.g. 3 turns valued 30): long knots read in a higher place |
| E-type | 43 | **yes** | **AS090/N2 22**, UR053A 6 | `E` valued 10/100 in a non-units cluster: the position agrees with the value, so the type code is the suspect |
| E-zero | 22 | **yes** | UR188 8, AS071 4 | `E` with value 0: value missing |
| E-value | 19 | no | AS027 6, UR1138 4 | `E` valued 10 in the units cluster |
| L-zero / L-other / L-off1 / L-turn1 / E-other | 11 / 10 / 6 / 5 / 5 | no | scattered | listed in the JSON |

Example knot ids for every category are in the JSON. **What this can't say:** the database alone can't tell a
transcription error from a real, unusual knotting practice. For example, long knots in the tens place on AS090/N2 may be
what the cord really shows. These are flags for someone with the original records, not corrections.

### Audit of earlier cycles
None of the ten K001 sum-cord khipus is in the top-12 concentration list, but KH0349 (UR113, K004) has 3 E-type knots.
Earlier results stay as they are: K008 showed they're robust to masking odd cords, and these 579 knots are 1.9% of
the audited set.

### Line 4 status
**Advanced, answered for the database:** the inconsistencies are concentrated and fall into five noteworthy patterns.
What's left is outreach: add a short per-category table to the pending OKR data-quality note.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
