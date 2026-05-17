# Reply: 2026-05-16-2102-isaiah-quotation-parser-scan

Processed 2026-05-16. Diagnostic scan of `acl:relcl` tokens across Isaiah-quoting BoFM chapters; classification by probable-parser-error / genuine-relative / ambiguous; intervention options surfaced for Stan-decision.

## Per-item status

| Item | Status |
|---|---|
| 1. Scope Isaiah chapters; extract `acl:relcl` | **completed** — 180 tokens across 6 chapter ranges |
| 2. Classify each `acl:relcl` case | **completed** — 172 genuine / 7 probable-error / 1 ambiguous |
| 3. Counts table + full probable-error list | **completed** below |
| 4. Don't fix anything | **honored** — diagnostic only |
| 5. Propose intervention options | **completed** — see "Intervention options" below |

## Scope

Six chapter ranges scanned via [scripts/extract_isaiah_aclrelcl.py](../../scripts/extract_isaiah_aclrelcl.py) (new). Per-token extraction uses the UD parses at `data/parses/llm-direct/` (the same source the R19 validator consumes), line-mapped to v2-mine to confirm chapter membership.

| Chapter range | Source | Total `acl:relcl` |
|---|---|---:|
| 1 Nephi 20-22 | Isaiah 48-49 + Nephi discourse | 60 |
| 2 Nephi 7-8 | Isaiah 50-51 + Nephi discourse | **0** (parse-coverage gap — see below) |
| 2 Nephi 12-24 | Isaiah 2-14 | 48 |
| 2 Nephi 27 | Isaiah 29 (heavily expanded) | 41 |
| Mosiah 14 | Isaiah 53 | **0** (parse-coverage gap — see below) |
| 3 Nephi 22-24 | Isaiah 54 + Malachi 3-4 | 31 |
| **Total** | | **180** |

## Classification counts

| Classification | Count | % |
|---|---:|---:|
| genuine-relative | 172 | 96% |
| probable-parser-error | 7 | 4% |
| ambiguous | 1 | <1% |

**Chapter hotspot: 2 Nephi 24 (Isaiah 14) accounts for 4 of the 7 parser errors plus the lone ambiguous case** (5 of 8 anomalies in one chapter). This is the "taunt against the king of Babylon" chapter — the densest Hebrew lyric poetry in the BoFM Isaiah quotations, with parallel exclamatory clauses, wordplay repetition, and participial stacks. Other parser errors scatter as 1 per chapter (2 Ne 17, 23; 3 Ne 23).

## The 7 probable-parser-error cases (full list)

### 1. 2 Nephi 24:4 — `city / ceased` (the prototype-flagged case)

> *"How hath the oppressor ceased, the golden city ceased!"*

The second clause is a bare Hebrew-style exclamatory parallel with no relative pronoun. The parser attached `ceased` as `acl:relcl` on `city` because both share the verb `ceased` and appear adjacent, but structurally this is clause apposition, not a relative. This is the exact case the resolver prototype (commit `eb821f6`) flagged and 2 of 3 second-round runs also flagged.

### 2. 2 Nephi 24:12 — `thou / weaken` (PRON head)

> *"Art thou cut down to the ground, which did weaken the nations!"*

`head_upos=PRON`. Relative clauses do not standardly attach to pronoun subjects in English. The `which` refers backward as a resumptive/exclamatory device in the Isaiah poetic register, not as a restrictive relative.

### 3. 2 Nephi 17:23 — `were / be` (VERB head)

> *"every place shall be, where there were a thousand vines at a thousand silverlings, which shall be for briers and thorns."*

Head is a finite verb. The `which shall be for briers` is an adverbial-result clause, not modifying `were`.

### 4. 2 Nephi 24:19 — `thrust / go` (VERB head)

> *"the remnant of those that are slain, thrust through with a sword, that go down to the stones of the pit"*

Head is the participial verb `thrust`. The `that go down` clause continues the description of `remnant`/`those`, but the parser attached it to `thrust` as its head instead.

### 5. 2 Nephi 23:17 — `Medes / regard` (Hebrew-parallel limb)

> *"I will stir up the Medes against them, which shall not regard silver and gold, nor shall they delight in it."*

The `nor shall they delight` clause switches to full independent-pronoun syntax (`they`), signaling Hebrew-style parallel independent clauses. The relative `which...nor shall they` is a compound construction with the second limb not syntactically subordinated.

### 6. 2 Nephi 24:2 — `captives / captives` (circular same-word attachment)

> *"take them captives unto whom they were captives"*

The `rel_root_form` and `head_form` are the same word. The parser has circularly attached the second `captives` as a relative-clause root on the first `captives`. The underlying sense is "they shall take their captors captive" (Hebrew wordplay), not a relative clause.

### 7. 3 Nephi 23:6 — `scriptures / not` (PART head)

> *"other scriptures I would that ye should write that ye have not"*

`rel_root_upos=PART` and `rel_root_form='not'`. The negation particle has been mis-tagged as the root of the relative-clause subtree rather than the elided verb it modifies (`[written]`).

## The 1 ambiguous case

### 2 Nephi 24:26 — `hand / out` (ADP root)

> *"the hand that is stretched out upon all nations"*

This IS a genuine relative, but the parser tagged `out` (ADP/particle) as the `acl:relcl` root instead of `stretched`. The relative exists; the root assignment is wrong. This is a parse-internal error that would NOT trigger the R19 resolver downstream (the effective relative root is `VERB stretched`), but the ADP root could cause issues for other consumers.

## Patterns observed

### Where errors concentrate

- **2 Nephi 24 (Isaiah 14) is the hotspot.** 5 of 8 anomalies (4 errors + 1 ambiguous) in this one chapter. Hebrew lyric poetry at maximum density.
- **Hebrew-parallelism signature: independent-clause parallel limb attached as relative.** Pattern: clause 1 has a `which`/`that` opener; clause 2 (or 3) shifts to independent pronoun syntax (`they`/`he`/etc.) but is still attached to the original `acl:relcl` arc. Examples: 2 Ne 23:17 (Medes); 2 Ne 24:4 (city ceased).
- **VERB-head and PRON-head as parser-error signals:** 2 of 7 errors had `head_upos=VERB` (2 Ne 17:23, 24:19); 1 had `head_upos=PRON` (2 Ne 24:12). Relative clauses on verb or pronoun heads are syntactically anomalous in English — strong error indicator.
- **Wordplay misattachment:** 2 Ne 24:2 (`captives/captives`) — same word repeated under Hebrew wordplay gets circularly attached.

### Non-VERB rel_root signal: weaker than expected

The directive's hypothesis ("unexpected `rel_root_upos` is a parser-error signal") only partially holds:
- `rel_root_upos=PART` (3 Ne 23:6): **reliable error signal**
- `rel_root_upos=ADP` (2 Ne 24:26): **reliable error signal** (root misassignment)
- `rel_root_upos=NOUN` (2 Ne 24:2 same-word): **reliable error signal**
- `rel_root_upos=ADJ` (5 cases): **NOT a reliable signal** — these are legitimate copular constructions (`that is holy`, `that is faithful`)
- `rel_root_upos=AUX` (1 case): **NOT a reliable signal** — legitimate copular case
- `rel_root_upos=VERB` with `head_upos=VERB` or `head_upos=PRON`: **reliable error signal** (the head is the diagnostic, not the rel_root)

### Parse-coverage gaps

**2 Nephi 7-8 and Mosiah 14 returned 0 `acl:relcl` tokens.** This is implausible for Isaiah 50-51 and Isaiah 53 — both chapters have extensive restrictive-relative constructions in MT and LXX traditions ("he that walketh in darkness," "him that justifieth me," "he was despised and rejected of men," "a man of sorrows"). The classifier confirmed this is a parse-coverage gap worth surfacing rather than absence of relatives.

Two possible causes:
1. The UD parser's English KJV-style English Isaiah text is being parsed with a different deprel for those constructions (e.g., `acl` without `:relcl`, or `nsubj`-based fronting). The classification regex picked up only `acl:relcl` — broader signature might catch the gap.
2. The chapters' parses themselves have arc gaps (the parser produced an empty `acl:relcl` set for these sentences).

Worth a separate parse-quality audit to confirm.

## Intervention options (for Stan-decision)

Per directive Item 5, surfacing 5 intervention shapes without recommendation:

**Option A — Per-chapter override list.** Maintain a small JSON of `(book, chapter, verse, token_id) → corrected_deprel` overrides; validators consult before consuming UD output. For the 7 cases here, that's 7 entries. Trivial to maintain at this scale, but doesn't scale if the underlying parse-quality issue surfaces in other corpora.

**Option B — Parser re-run with different model/config.** Investigate whether a different UD parser (or Stanza with different configuration) handles Hebrew-style parallel clauses better. High investment; uncertain payoff.

**Option C — Validator-level exclusion: skip Isaiah-quoting chapters entirely.** R19 (and any other affected validator) would not fire on `acl:relcl` in the scoped chapters; editorial review handles those chapters by hand. Cleanest but coarsest — only 7 of 180 cases are errors (4%), so 96% of the work is correctly handled.

**Option D — Targeted resolver prompt:** when the resolver sees an Isaiah-quoting chapter, instruct it to treat `acl:relcl` skeptically (check for parser-error signals before applying R19). Captures the LLM-detection path the resolver prototype already showed works.

**Option E — Validator pre-filter on structural error signals.** Add inline checks in `validate_rule_19_ud.py` to flag specific parser-error signatures BEFORE classifying:
- `head_upos in {VERB, PRON, AUX}` → route to PARSER-SUSPECT bucket
- `rel_root_upos in {PART, ADP}` → route to PARSER-SUSPECT bucket
- `head_form == rel_root_form` (same-word circular attachment) → route to PARSER-SUSPECT bucket

This would catch 5 of the 7 + the 1 ambiguous case mechanically. The remaining 2 (Hebrew-parallel limb without surface signal — 2 Ne 23:17, 2 Ne 24:4) would still need LLM judgment.

## Surfaced concerns

1. **Parse-coverage gap for 2 Nephi 7-8 and Mosiah 14.** Zero `acl:relcl` is implausible for these Isaiah-rich chapters. Worth a separate parse-quality audit; could be a broader parse-shape issue affecting more than just the Isaiah scan.
2. **The R19 validator + resolver pipeline tolerates parser errors fairly well.** Of the 7 probable parser errors, the resolver prototype (commit `eb821f6`) and second-round runs (commit `65c38bc`) caught 2 Ne 24:4 as suspicious (GENUINE-REVIEW-REQUIRED in 2 of 3 runs). The system has a working failure-detection layer. But it's load-bearing on the LLM; **Option E (validator pre-filter) would shift detection upstream where it's deterministic.**
3. **96% genuine-relative rate is actually high.** The hypothesis was 30-60% probable-error rate (per directive's "expected" estimate). The actual 4% rate means UD parsing of BoFM Isaiah quotations is largely sound; the intervention scope is much narrower than initially feared.
4. **The hotspot pattern (2 Ne 24 = Isaiah 14) is concentrated enough that even Option A (per-case override) would be cheap.** 5 of 8 anomalies in one chapter; the entire Isaiah-scan-error inventory fits in a 7-entry JSON.

## Artifacts

- **Extractor script:** [`scripts/extract_isaiah_aclrelcl.py`](../../scripts/extract_isaiah_aclrelcl.py) (new; uses validators/parsing UD-query infra; scope is the 6 chapter ranges per directive)
- **Raw extraction:** `C:/tmp/isaiah-aclrelcl.jsonl` (180 records; local artifact)
- **Sonnet classification:** `C:/tmp/isaiah-aclrelcl-classified.jsonl` (180 records with classification + rationale; local artifact)
- **This reply**

## Audit status

Audit-skippable per §7.4 (read-only diagnostic; no rule change, no validator code change, no parser change; output is information for Stan-decision).

If/when an intervention from Options A-E is selected, that's a separate directive with its own audit trigger assessment.
