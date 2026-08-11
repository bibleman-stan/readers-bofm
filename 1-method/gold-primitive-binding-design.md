# Design spec — gold structural primitives read DIRECTLY in the BoFM binding rules

**Status:** DESIGN, pre-implementation. Under §7.3 adversarial-audit gate. Do NOT implement until audits return.

## Problem this solves

The deployed BoFM fabric over-merges **fused independent predications** — multiple
independent clauses rendered as one ATU line. Stan-flagged exemplars (live, NOT overrides):

- **Alma 32:24** — one block fusing the address + *"now I do not desire that ye should
  suppose that I mean to judge you…"* (own subject "I", finite "desire" → independent).
- **3 Ne 19:4** — fuses a name-list + *"now these were the names of the disciples whom
  Jesus had chosen"* (subject "these", copula "were") + *"and it came to pass that they
  went forth and stood"* (another independent predication).

These are mis-**attachment**, not mis-tagging. The just-failed gold-POS-into-Stanza
experiment (text-safe, +0.9% breaks, but baseline-check FAIL: rule_07 inf-merge +81,
vocative +10, subject-orphan +14; feats don't propagate through depparse) proved that
**laundering gold through Stanza's modern-English depparse is a blunt, low-ceiling,
mixed-effect instrument.** Stanza mis-attaches EModE clause structure regardless of POS
correctness (probe: `saith`→VERB still attached as `obl` of the wrong verb).

## The approach (Stan-chosen 2026-05-27)

Read Carmack's gold structural primitives (finiteness, imperative, subordination,
relative-pronoun) **directly in the binding rules**, with the **bidirectional test as
sole arbiter**. Mechanical-first + Container-not-Originator: the rules organize what the
gold-tagged fabric supports; gold signals PROPOSE candidate boundaries, the test DISPOSES.
This does NOT perturb the corpus-wide Stanza parse (unlike the reverted approach).

## Component 1 — gold-signal lexicon (new helper, original-surface-keyed)

Source: `research/carmack-pos/wordwheel-fine.tsv` (245 fine tags, the rich export).
Keyed on **original surface form** (Carmack tagged original BoFM), lowercased.
**Single-dimension-unambiguous-only** (abstain where a word-type's gold tags disagree on
the dimension):

- `gold_finite(w)` → True iff all gold tags are finite (`V.lex.pres.th|.s|.st|.past|.base`
  used finitely), False iff non-finite (`V.lex.inf`, `V.lex.*.ptcp`), None if mixed/unknown.
- `gold_imperative(w)` → True iff `V.lex.imp`.
- `gold_subordinator(w)` → True iff `CONJ.subord` (optionally which: that/because/if/when…).
- `gold_relpron(w)` → True iff relative pronoun (which/whom/who/whose).

## Component 2 — consumption points (AUGMENT existing parse-robust logic, never blind-replace)

**(a) `_seg_independent_predication` (bofm_generate.py:247)** — currently guesses finiteness
from `upos in (VERB,AUX)` + a crude `endswith("ing")` participle filter + deprel
root/conj/parataxis. AUGMENT: treat a token as an independent main predication when
`gold_finite(form)` is True OR `gold_imperative(form)` is True, it has its own subject, and
it is NOT governed by an in-segment `gold_subordinator`. Gold finiteness REPLACES the `-ing`
heuristic (use `gold_nonfinite` to exclude participles precisely). Falls back to the existing
Stanza-derived logic where gold abstains.

**(b) NEW fused-predication split** — if a segment contains ≥2 independent predications
(≥2 distinct gold-finite/imperative verbs, EACH with its own subject, NEITHER governed by an
in-segment subordinator, and NOT a coordinate pair sharing ONE subject), propose a split
between them. Then **CONFIRM via the bidirectional test**: each resulting segment must close
forward (grammatical completeness) AND self-contain backward (referential). Reject the split
if the test fails. This is the direct fix for Alma 32:24 / 3 Ne 19.

**(c) subordinator confirmation** — `sub_marks` (line 263) and `_is_forward_frame` (line 291)
currently key subordinator detection on a lexeme set + Stanza `mark`/SCONJ. Use
`gold_subordinator` to CONFIRM a genuine subordinator and `gold_relpron` to exclude the
relativizer reading (disambiguating "that/as/since/after/which", which Stanza conflates).

## Component 3 — bidirectional test as arbiter

Gold proposes; the bidirectional test (cf. `5-machinery/scripts/bofm_bidir_gate.py`) disposes. No gold
signal forces a boundary the test rejects. Punctuation has ZERO force throughout (em-dashes,
colons, commas never consulted — the Alma/3Ne dashes are incidental).

## Component 4 — provenance + gating

Each gold-driven decision tagged with its source (`gold-finite` / `gold-subord` /
`gold-imp`) for auditability (per the semi-automatic-treebank discipline). Gate: text parity
(char-identical) + baseline-check (NO canon-rule violation increase — the bar the last
attempt failed) + verify Alma 32:24 / 3 Ne 19 fixed + Isaiah/Malachi oracle direction.
Prototype on flagged verses + a sample BEFORE corpus-wide rebuild.

## OPEN RISKS (for the auditors to attack)

1. **Coordinate verb chains sharing one subject** — "they went forth AND stood", "they arose
   AND ministered": TWO gold-finite verbs, ONE subject. Is that one ATU or two? Over-splitting
   coordinate predicates is the dominant failure mode (recall ~90-95% of GNT failures were
   over-split). How does the split rule avoid shattering coordinate cola? (ties to R5/R10.)
2. **Existential/copular** — EXIST tag, `cop` clauses: does gold-finite + subject reliably
   flag these as independent, and should they always split?
3. **Ambiguity abstention** — 1,246 word-types are POS-ambiguous; how many verbs/subordinators
   fall in the abstain zone, leaving the rule on the old Stanza guess? Is coverage enough to
   matter?
4. **Homograph / surface keying** — gold is word-TYPE; keying on form.lower() can't disambiguate
   a word that is finite-verb in one verse, noun in another. Risk?
5. **Rule interaction / precedence** — ordering vs R-INV, R-WLD, `_is_forward_frame`, the
   verba-dicendi/M2 speech rules. Will gold-driven splits REGRESS existing canon rules (the
   way the gold-POS approach regressed rule_07)? What's the safe precedence?
6. **Is the bidirectional test a trustworthy arbiter** here, or does its own operationalization
   lean on the same garbled Stanza attachment we're trying to bypass?
