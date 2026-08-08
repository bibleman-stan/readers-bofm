# Colometry Rule Validators

Mechanical validators for the BofM colometry canon. Split into two layers
matching the project's theoretical stack.

## Directory layout

```
5-machinery/validators/
  syntax/      — Layer 1: generic English grammar checks
  colometry/   — Layer 3: BofM-specific editorial rule checks
```

---

## `syntax/` — Layer 1 (generic English grammar)

These validators check facts about English grammar that hold regardless of
BofM-specific editorial policy. A failure here is a structural error in the
line break, not just a policy choice.

**Reference:** `data/syntax-reference/ud-taxonomy.md`

**Error class: `[MALFORMED]`** — hard grammatical failure; must fix before
any editorial review is meaningful.

| Validator | Rules covered | Notes |
|---|---|---|
| `validate_line_final_tokens.py` | Rules 9, 11, 12, 13a — line-final prohibited POS (conjunctions, articles, auxiliaries, prepositions) | Rules 9+11 fully mechanical; 12/13a use heuristics — false positives possible (Rule 13b was removed from the mechanical suite as judgment-dependent in archaic English) |

**Run:**
```bash
python3 5-machinery/validators/syntax/validate_line_final_tokens.py
python3 5-machinery/validators/syntax/validate_line_final_tokens.py --verbose
```

---

## `colometry/` — Layer 3 (BofM-specific editorial rules)

These validators check whether Stan's editorial line-break decisions conform
to the settled rules of the BofM colometry canon. A failure here is a policy
deviation — a rule says the break should be elsewhere.

**Reference:** `1-method/colometry-canon.md`

**Error class: `[DEVIATION]`** — editorial policy violation; review required
before deciding whether to merge, split, or document an exception.

| Validator | Rule | Notes |
|---|---|---|
| `validate_rule_10_verb_do_split.py` | Rule 10 — governing verb must not be split from its direct-object NP | Heuristic; false positives expected (relatives, appositives) |
| `validate_rule_16_aictp_dangling_that.py` | Rule 16 — "that" must lead the post-AICTP line, not dangle at AICTP line end | Fully mechanical |
| `validate_rule_17_complement_integrity.py` | Rule 17 — causative/aspectual/speech/cognition/volition verbs keep "that"-clause complement on same line | Six exception filters; CLEAN as of 2026-04-18 |
| `validate_rule_18_fixed_idioms.py` | Rule 18 — fixed multi-word idioms must not be split across lines | Regex across newlines; fully mechanical |
| `validate_rule_23_date_colophon.py` | Rule 23 — date/colophon formulas always stay on one line | Regex across newlines; fully mechanical |

**Run:**
```bash
python3 5-machinery/validators/colometry/validate_rule_10_verb_do_split.py
python3 5-machinery/validators/colometry/validate_rule_16_aictp_dangling_that.py
python3 5-machinery/validators/colometry/validate_rule_17_complement_integrity.py
python3 5-machinery/validators/colometry/validate_rule_17_complement_integrity.py --verbose
python3 5-machinery/validators/colometry/validate_rule_18_fixed_idioms.py
python3 5-machinery/validators/colometry/validate_rule_23_date_colophon.py
```

---

## Error class distinction

| Tag | Layer | Meaning | Action |
|---|---|---|---|
| `[MALFORMED]` | syntax/ | Hard grammatical failure — line break violates English structural grammar | Fix before review |
| `[DEVIATION]` | colometry/ | Editorial policy violation — break diverges from canon rule | Review; document exception or merge/split |

---

## Exit codes

All validators use the same convention:
- `0` — zero violations found; corpus is clean for this rule
- `1` — violations found; output lists each with file, line number, and tag
- `2` — setup error (e.g. v2-mine directory not found)

---

## Philosophy

A rule earns a validator when three conditions hold:

1. **Mechanical trigger** — the trigger reduces to morphology, position, or
   lexical lists. No semantic judgment required.
2. **Error cost × token frequency** — the rule fires frequently enough that
   systematic drift is possible, and a wrong call is visible.
3. **Systematicity of the failure mode** — violations tend to be systematic
   (same pattern missed across many verses), not idiosyncratic one-offs.

Rules failing condition 1 stay as editorial principles without validators. The
validator-build exercise is also a canon-pruning exercise: walking the canon
asking "does this rule earn a validator?" forces the question "does this rule
earn its place?"
