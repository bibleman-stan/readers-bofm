# Scholarship — per-rule scholarly grounding companion

This directory holds per-rule companion documents carrying the scholarly substrate, grammatical-grounding citations, rationale, and empirical-pattern evidence that the rule-template explicitly forbids inline in the canon §5 rule entry.

The rule entry is operational — it carries what an LLM agent or validator needs to apply the rule. The defensibility surface (CGEL / BDF / Skousen / Joüon / Smyth / Wallace citations, rhetoric-figure references, audit precedent narratives, pragmatic-stance disclaimers) lives here.

## Filename convention

One file per rule, named for the rule ID in lower-kebab-case:

```
r17.md         # R17: Complement Integrity
r26.md         # R26: ADJ-as-Predicate + that
m4-bofm-1.md   # M4-BoFM-1: Subject-Orphan Predicate Completion
ep-1.md        # EP-1: According-To Manner vs. Source
```

## Contract (from [atu-method/docs/rule-template.md](../../../../atu-method/docs/rule-template.md))

| Content type | Belongs in |
|---|---|
| Rationale / WHY the rule exists | `scholarship/r{N}.md` |
| Grammatical-grounding citations (CGEL, BDF, Skousen, Joüon, Smyth, Wallace, etc.) | `scholarship/r{N}.md` |
| Corpus empirics ("zero hits in v2-mine") as empirical-validation evidence | `scholarship/r{N}.md` |
| Pragmatic-stance disclaimers | `scholarship/r{N}.md` |
| Audit precedent narratives | `../audit-trail/r{N}.md` |
| Sweep results with dates | `../audit-trail/r{N}.md` |
| Cross-project provenance ("BoFM coined; Tanakh ported") | `../audit-trail/r{N}.md` or git log |
| Stan-direct decision records | git log |

## Discipline: move, don't delete

When future §5 work touches a rule whose canon body still carries scholarly-grounding citations inline (a violation of the rule-template), MOVE the citations to `scholarship/r{N}.md`. Do NOT delete them — the defensibility surface is load-bearing, just relocated.

## Status

Empty — to be populated per rule as §5 entries are touched. Parallel surfaces already exist at:

- [`readers-gnt/private/01-method/scholarship/`](../../../../readers-gnt/private/01-method/scholarship/) — has `m4-gnt-1.md`
- `readers-tanakh/private/01-method/scholarship/` — pending creation

## Tracking

Files here are tracked in git via `git add -f` despite the `private/` gitignore — same pattern as `colometry-canon.md` and `pericope-canon.md`. The intent is that any future scholar weighing the methodology on its merits can read both the operational rule entry AND its scholarly grounding from the public repo.
