# Colometry Rule Validators

Mechanical rule-application validators for the BofM colometry canon.
Each validator implements a specific canon rule as a bottom-up test
against the v2-mine canonical source files.

## Principle

Pattern-shape scanners ask *"does this line contain pattern P?"*
Rule-application validators ask *"does this line structure follow
from applying rule R to this text?"* — which is a stronger test.
Validators scale with the canon, not with syntactic variety.

Only rules with **mechanical triggers** (reducible to surface features
— lexical lists, line-final token checks, regex patterns) earn a
validator. Rules requiring cognitive/semantic judgment (atomic-thought
analysis, image-unity, rhetorical-register) stay as editorial
principles without validators — a validator for a judgment rule would
be a shape-detector with a better name.

## Current validators

| Validator | Rules covered | Status |
|---|---|---|
| `validate_rule_17_complement_integrity.py` | Rule 17 (generalized: causative, aspectual, speech, cognition, volition verbs + "that" complement; FEF extraposition) | CLEAN — 0 violations as of 2026-04-18 |
| `validate_line_final_tokens.py` | Rules 9, 11, 12, 13a, 13b (line-final prohibited-token checks) | Rules 9 + 11 CLEAN; 12/13a/13b need semantic filters (line-final "not"/"no" is legitimate in archaic English; "about"/"beyond"/etc. often adverbial not prepositional) |

## Usage

```bash
python3 validators/validate_rule_17_complement_integrity.py
python3 validators/validate_line_final_tokens.py

# Verbose (shows skipped exceptions):
python3 validators/validate_rule_17_complement_integrity.py --verbose
```

Exit code 0 = clean. Exit code 1 = violations found. Exit code 2 = setup error.

## Philosophy

A rule earns a validator when three conditions hold:

1. **Mechanical trigger** — the trigger reduces to morphology, position,
   or lexical lists. No semantic judgment required.
2. **Error cost × token frequency** — the rule fires frequently enough
   that systematic drift is possible, and a wrong call is visible.
3. **Systematicity of the failure mode** — violations tend to be
   systematic (same pattern missed across many verses due to a
   drafter's blind spot), not idiosyncratic one-offs.

Rules that fail condition 1 stay as editorial principles. Rules that
fail 2 or 3 get human review without validator infrastructure.

The validator-build exercise is also a **canon-pruning exercise**:
walking the canon asking "does this rule earn a validator?" forces the
question "does this rule earn its place?" Rules with fuzzy triggers
that can't be mechanically validated are disproportionately likely to
be over-structured — specific-case crystallizations masquerading as
general principles.
