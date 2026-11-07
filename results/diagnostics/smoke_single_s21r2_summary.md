# S22 single-agent smoke summary — run `smoke_single_s21r2`

Descriptive tallies of S16–S19 evaluation over all saved episodes. No interpretation.

## Overview

|Agent|Episodes|Status counts|ERROR causes|Early-stop share|Budget-hit share|Largest prompt / num_ctx|Episodes > 90% num_ctx|
|---|---:|---|---|---:|---:|---|---|
|Gemma4-12B|20|SUCCESS 20|none|0.10|0.00|21660 / 32768 (66.1%)|none|
|Granite41-8B|20|SUCCESS 20|none|0.35|0.10|18192 / 32768 (55.5%)|none|
|Ministral3-14B|20|PARSE_FAIL 1, SUCCESS 19|none|0.40|0.00|30048 / 32768 (91.7%)|BH2_04003|
|Cogito-14B|20|ERROR 2, SUCCESS 18|CONNECTION 2|0.25|0.00|20914 / 32768 (63.8%)|none|

## Gemma4-12B

- Label A: ALT_VALID 17, GOLD 1265, OFF_QUESTION 24
- Label B: SUPPORTED 1282, UNGROUNDED 24
- Reason codes (all): none
- Reason codes (primary path): none
- Hop-1 status: H1_CLEAN 20
- OUT_OF_MEMORY episodes: 0

## Granite41-8B

- Label A: ALT_VALID 17, GOLD 593, OFF_QUESTION 74
- Label B: PATH_INVALID 74, SUPPORTED 610
- Reason codes (all): SHORTCUT 56, WRONG_HOP_COUNT 18, WRONG_TARGET_TYPE 18
- Reason codes (primary path): SHORTCUT 56, WRONG_HOP_COUNT 18, WRONG_TARGET_TYPE 18
- Hop-1 status: H1_CLEAN 17, H1_MIXED 2, H1_WRONG 1
- OUT_OF_MEMORY episodes: 0

## Ministral3-14B

- Label A: ALT_VALID 17, GOLD 1143, OFF_QUESTION 11
- Label B: PATH_INVALID 11, SUPPORTED 1160
- Reason codes (all): SHORTCUT 11
- Reason codes (primary path): SHORTCUT 11
- Hop-1 status: H1_CLEAN 17, H1_MIXED 2, H1_NONE 1
- OUT_OF_MEMORY episodes: 0

## Cogito-14B

- Label A: ALT_VALID 17, GOLD 615
- Label B: SUPPORTED 632
- Reason codes (all): none
- Reason codes (primary path): none
- Hop-1 status: H1_CLEAN 19, H1_MIXED 1
- OUT_OF_MEMORY episodes: 0

## Assertion: no answer is both OFF_QUESTION and SUPPORTED

PASS: none found.
