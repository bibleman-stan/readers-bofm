# Design spec — BoFM v2 narrow-task LLM adjudication layer

**Status:** DESIGN, pre-implementation. Under §7.3 audit gate. Framework-sanctioned stage (framework §3: v2 = narrow-task LLM adjudication on residuals, over a mechanical v1). Stan-chosen direction 2026-05-27 after three mechanical designs hit the judgment wall.

## Why v2 (the wall the mechanical layer can't cross)
The 3 binding-layer audits established that the genuine residual ATU decisions require **token-in-context judgments** a mechanical layer on the Stanza-EModE parse cannot make:
- **complement-vs-quote** — a finite ccomp after a perception/cognition/speech verb BINDS (shared deixis) or STANDS (re-performed direct discourse, own deictic center). Framework §2.1 says this needs Macula-style `referent`/`subjref` tracking — **absent on the BoFM (Stanza) substrate**. An LLM CAN read the deictic shift in context. This is v2's core competency.
- **parallel-cola-vs-overspilt** — coordinate cola with distinct overt subjects (2 Ne 4:26 "my heart weep / my soul linger") are correct standalone ATUs (§1/§2.2 KEEP-AS-IS), NOT defects; genuine over-splits (subject-elided hendiadys) and editorial parallelism are a judgment the mechanical layer over-counted. LLM adjudicates per case.

## What v2 IS / IS NOT (Container-not-Originator)
- **IS:** adjudication of FLAGGED residual boundaries ONLY, given the v1 draft + the verse text + framework §2.1 criteria, emitting {BIND | STAND | KEEP-AS-IS} + confidence + justification + provenance.
- **IS NOT:** regenerating segmentation from scratch; touching boundaries v1 is confident on; inventing structure. The LLM never generates the parse — it judges residuals the mechanical v1 surfaces. Human (Stan) retains final authority (semi-automatic-treebank discipline).

## Residual identification (what gets flagged for v2)
A boundary/verse is a v2 residual iff v1 hits a known judgment-class:
1. Finite ccomp/complement clause following a perception/cognition/**speech** verb (complement-vs-quote). 
2. Coordinate finite clauses (≥2 coordinate predications) — parallel-cola-vs-overspilt-vs-hendiadys.
3. v1 mechanical low-confidence (abstention zones: gold-POS abstained AND Stanza deprel is the only signal).
Everything else = v1 ships unchanged (most of the corpus; the reader is mostly correct).

## The adjudication task (per residual, Opus)
Input: verse text (original), v1 segmentation, the framework §2.1 test (forward grammatical closure + backward referential self-containment; punctuation ZERO force; complement binds / re-performed quote stands via deixis; parallel cola KEEP-AS-IS unless genuine hendiadys). Output per residual: decision + confidence + one-line justification grounded in the test + provenance=`v2-llm`. The LLM performs the **deixis judgment** (person/deictic shift inside the complement) that Stanza can't — this is the explicit licensed use.

## Provenance + auditability
Every v2 decision logged: (book, chap:verse, boundary, v1-decision, v2-decision, justification, model, confidence). A reviewable adjudication log — Stan reviews; v2 is a proposal layer, not an oracle. Mirrors the Hebrew/GNT v2 precedent.

## GATE — and the hard PREREQUISITE
**Prerequisite (canon audit CRITICAL):** fix the validator infra BEFORE v2 output can be gated:
- F1: retrofit the override-blind split-detectors (`rule_15`, `participial_phrases`, `rule_28`, `rule_17`, `rule_18/18a`, `compound_coord`, `severed_complement`, `m4_subject_orphan`) to honor `BOFM_V2_DIR` (else a prototype scores the stale corpus → false green).
- SET-diff harness (per-violation new/cleared, not just counts).
- Over-merge meter: the genre diagnostic over-merge count per genre (the ONLY corpus-wide over-merge signal — no validator catches over-merge).
- Bidir-test on every CHANGED boundary.
Gate sequence: char-identity (text-preserving) → SET-diff triage (ARTIFACT vs REAL regression, bidir-tested) → over-merge meter flat-or-down per genre → zero-baseline tripwires. STOP on any real regression or any over-merge rise. `--update-baseline` forbidden on a regressed run.

## Rollout
Prototype on a residual SAMPLE first (the complement + coordinate cases + the diagnostic verses), human-review the adjudications, gate, THEN corpus-wide. Deployed bomreader.com untouched until clean (prototype via override dirs).

## OPEN RISKS (for the audit)
1. **Confabulation / scope-creep** — LLM "adjudicating" non-residuals or inventing readings. Guard: hard residual-flagging gate; the LLM only sees flagged cases + is instructed to defer (KEEP v1) when the test is indeterminate.
2. **Reproducibility** — LLM non-determinism. Guard: fixed prompt, logged provenance, human-gate, decisions are data (re-runnable, diffable).
3. **Residual-identification recall** — false negatives (missed residuals ship v1-wrong). How complete is the flagging?
4. **Deixis-judgment reliability** — is the LLM's complement-vs-quote call trustworthy? Validate against framework + a labeled set; confidence-threshold + human review on low-confidence.
5. **Cost/scale** — N residuals × Opus. Bound N via the flagging; batch.
6. **Consistency with the Hebrew/GNT v2 stage** — same discipline, same provenance schema.
