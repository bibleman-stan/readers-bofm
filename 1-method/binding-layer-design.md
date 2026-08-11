# Design spec — extend the BoFM binding layer to fix the dominant over-SPLIT

**Status:** DESIGN, pre-implementation. Under §7.3 adversarial-audit gate. No code until audits return.

## Problem (from the 2026-05-27 genre diagnostic)
Deployed BoFM v2 is **over-SPLIT ~15:1 over over-merge, every genre**. The existing binding layer
(`_forward_frame_bind` L355, AICTP forward-merge, `_is_forward_frame` L291, `_seg_independent_predication`
L247, `_speech_answer_peel`, `_apodosis_is_coordinated` L350) is INSUFFICIENT — it misses three
over-split sub-types. The defects are **attachment failures on correctly-tagged common words**, so this is a
binding (merge) problem, not a parse/POS problem. Goal: extend the binding layer to re-merge these, with the
**bidirectional test (forward grammatical closure + backward referential self-containment) as the sole arbiter**;
punctuation ZERO force.

## The three over-split sub-types to bind (with diagnostic exemplars)
1. **Coordinate verb-chain sharing ONE subject** — "they went forth AND stood"; 2 Ne 4:26 "why should my heart
   weep / AND my soul linger / AND my flesh waste away" (4 coordinate complements of one "why should…?" matrix,
   split into 4 lines). One subject (or one shared interrogative/modal matrix) → ONE ATU. (Hebrew B7 analog: bare
   coordinate verb pair = one ATU.)
2. **Protasis severed from apodosis** — Mosiah 2:18 "and if I…do labor to serve you" / "then ought not ye…";
   2 Ne 7:2 "when I called," / "there was none to answer." A subordinate protasis/temporal that does NOT
   forward-close must bind to its apodosis.
3. **Complement / perception severing** — Alma 36:22 "methought I saw" / "God sitting upon his throne" (the
   perception complement is the object of "saw"); finite ccomp severed from its matrix verb.

## Mechanism — a MERGE pass extending the existing forward-frame machinery
Two binding directions, each gated by the bidirectional test:
- **Forward-bind** (segment → next): a segment that does NOT forward-close — opens with a subordinator/protasis
  leader (`if/when/though/because/…`, the existing `_FORWARD_FRAME_LEADERS` L241) and contains no independent
  predication, OR ends "hanging" on a governing verb whose complement is the next segment — binds to the
  following segment. (Extends `_is_forward_frame`/`_forward_frame_bind` to the protasis + complement cases.)
- **Backward-bind** (segment → prior): a segment that is NOT backward-self-contained — a bare coordinate
  continuation (`and/or/nor` + a finite verb with NO own overt subject, sharing the prior segment's subject), or
  a coordinate member of a shared matrix (the 2 Ne 4:26 "why should…" case) — binds to the prior segment.
  (Extends `_apodosis_is_coordinated` L350, which already detects coordinator-led segments, into a merge.)

Signals (all from substrate we HOLD; no new acquisition):
- **Finiteness / verb-form** — Carmack type-level POS (held) + the existing parse; closed-class cue lists.
- **Subordinator vs coordinator** — closed-class lexeme sets (the bind/stand fork; `_FORWARD_FRAME_LEADERS` +
  a coordinator set), NOT the noisy Stanza `mark`/SCONJ alone.
- **Shared / absent subject** — the second coordinate conjunct lacking its own overt `nsubj` (subject-elision is
  the EModE coordinate-chain signature) → shares the prior subject → backward-bind.
- **Bidirectional test as arbiter** — `bofm_bidir_gate.py` informs, but per the prior audit it is NOT fully
  independent of Stanza attachment; the merge predicate must lean on closed-class lexical + finiteness cues +
  subject-elision, which are parse-robust, and use the gate as a secondary check.

## Pass ordering & idempotency
Insert as an EXTENSION of the existing merge passes in `_rule_passes` (L632-712), BEFORE the lone splitter
`_marker_split` (L711, which runs last). Must be idempotent and must not fight `_forward_frame_bind`/AICTP
(compose, don't double-merge). A merge is text-preserving (only removes an internal break).

## Gate (this is a MERGE pass — expect it to REDUCE merge-detector violations)
1. Parity (char-identical). 2. baseline-check WITH the per-violation triage the prior audit demanded
   (distinguish a correct merge that trips a split-detector from a real regression; bidir-test each changed
   boundary). 3. Re-run the genre diagnostic sample — over-split count must DROP, over-merge must NOT rise.
4. Prototype on the diagnostic's over-split verses FIRST, corpus-wide only after clean.

## OPEN RISKS (for the auditors to attack)
1. **Over-MERGING (the opposite failure):** pulling genuinely-separate ATUs together — e.g. two coordinate
   clauses with DISTINCT subjects ("the city of Moroni did sink / and the inhabitants were drowned", 3 Ne 8:9,
   correctly TWO ATUs). The shared-subject test must distinguish elided-shared-subject (bind) from distinct-overt-
   subject (keep). How robust is "no own overt nsubj" given Stanza mis-attachment?
2. **Shared-subject detection still leans on Stanza `nsubj`** — same circularity the prior audit flagged. Can
   subject-elision be detected parse-robustly (e.g., a coordinator immediately followed by a finite verb with no
   intervening NP)?
3. **The "shared matrix" case (2 Ne 4:26)** — coordinate complements of one interrogative/modal; how to detect
   the shared "why should…?" matrix without the parse getting it right?
4. **Interaction with the speech/quote layer and the existing forward-frame/AICTP merges** — precedence, double-merge.
5. **Genre skew** — over-split is worst in poetic/Isaiah/sermon (dense coordinate/conditional); does an aggressive
   coordinate-merge over-bind genuine parallel cola that the framework treats as separate idea-units? (The
   embedded-poetry cluster is exactly where Hebrew-side parallelism debates live.)
6. **Is the bidirectional test operationalizable as the arbiter here**, or does it inherit the Stanza-circularity
   that sank the prior design's "arbiter"?
