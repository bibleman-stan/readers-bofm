# Reply: 2026-05-16-2203-r19-parser-suspect-prefilter

Processed 2026-05-16. Per the directive's §7.3 mandatory-audit protocol, ≥2 parallel adversarial agents were dispatched BEFORE any implementation. **Both audits returned REJECT with convergent must-fix findings; implementation halted at Item 2 per the directive's STOP gate.**

## Per-item status

| Item | Status |
|---|---|
| 1. ≥2 parallel adversarial audits | **completed** — agentIds `a9d31434c243db52a` (α, Opus) + `a710bed5338a864ad` (β, Opus) |
| 2. Implementation OR surface must-fix | **STOP — must-fix surfaced** per directive's branching gate |
| 3. Validator code change | **NOT IMPLEMENTED** (blocked by Item 2) |
| 4. Run validator fresh + before/after counts | **NOT RUN** (no change to validate) |
| 5. Canon prose update | **NOT WRITTEN** (no rule change to document) |
| 6. Resolver script update | **NOT WRITTEN** (no subtype to consume) |

## Convergent audit findings (α and β independently)

Both Opus audits arrived at the same verdict with independent corpus-evidence calls, and to a remarkable degree on the SAME numerical counts (α ran the validator and got 1,109 hits; β ran an audit script and got 1,111 hits; counts differ by 2 due to different tokenizers but the corpus-level picture is identical).

| Finding | Audit α | Audit β |
|---|---|---|
| Total proposed-signal hits (corpus-wide) | 1,109 | 1,111 |
| PRON-head matches | 988 | 990 |
| ADP rel_root matches | 74 | 74 |
| Same-word matches (S3) | 5 | 5 |
| **Verdict** | **REJECT** | **REJECT** |

## The decisive corpus collision

**S1 (`head_upos in {VERB, PRON, AUX}`) collides directly with R19's CATAPHORIC_UPOS closed list** (canon §5 R19's settled rule: PRON/DET heads → cataphoric → STRONG-SPLIT). Top PRON-head matches (from audit α's enumeration):

| Head form | Count | Canonical status |
|---|---:|---|
| `those` | 206 | Canonical CATAPHORIC paradigm (canon §5 R19 explicit example) |
| `that` | 124 | Canonical CATAPHORIC |
| `they` | 99 | KJV-register: *"they that wait for me"* (1 Ne 21:23) |
| `those` (lemma `that`) | 79 | Canonical |
| `he` | 77 | KJV-register: *"he that diligently seeketh"* (1 Ne 10:19) |
| `him` | 72 | KJV-register: *"him that contendeth with thee"* (1 Ne 21:25) |
| `many` | 55 | Cataphoric quantifier |
| `them` | 55 | KJV-register: *"them that sit in darkness"* (1 Ne 21:9) |
| `all`, `whosoever`, `one`, `none`, `nothing`, `some` | ~110 | All R19 STRONG-SPLIT paradigm |

Of 988 PRON-head matches, **897 are currently classified STRONG-SPLIT mechanical Category-A apply targets.** The directive would replace 897 mechanical-apply cases with 897 PARSER-SUSPECT-requiring-review cases — the **opposite** of the directive's intent.

The conceptual error (both audits identified independently): the 2102 reply correctly noted *"relative clauses do not standardly attach to pronoun subjects in English"* citing 2 Ne 24:12 *"Art thou cut down...which did weaken"*. But that observation applies to **first/second-person pronoun matrix subjects** (`thou`/`I`/`we`/`ye` — small finite class), NOT to **demonstrative/quantifier pronoun heads** (`those`/`he-that`/`they-that`/`many`/`all` — large legitimate KJV-register class). The signal was pattern-enumerated from 1 case (`thou` in 2 Ne 24:12) and over-generalized to all PRON.

## The S3 self-contradiction (audit β + α)

**S3 (`head_form == rel_root_form`) catches a case canon §5 R19 explicitly cites as a legitimate MERGE example.**

5 corpus cases:
1. 2 Ne 24:2 `captives/captives` — TRUE parser error (the prototype target)
2. 2 Ne 9:30 *"the rich who are rich"* — legitimate Hebrew-style rhetorical pun
3. Alma 19:6 *"the light which did light up his mind"* — homograph (noun *light* + verb *light up*)
4. **Alma 21:18 *"the land of Ishmael which was the land of their inheritance"*** — **directly parallel to canon §5 R19's worked predicative-identifier MERGE example** (*"commandment which is the word of God"*)
5. Helaman 15:13 *"the true knowledge which is the knowledge of their Redeemer"* — same predicative-identifier shape

**TP rate: 1/5 = 20%.** And the FPs include a case shape canon explicitly endorses. Routing the canon-§5-affirmed MERGE example to PARSER-SUSPECT is a regression.

## The ADP signal mis-fire (audit α + β)

74 ADP rel_root cases corpus-wide. Audit α's sample of legitimate ones:

- *"the people who were of his seed"* (1 Ne 5:18)
- *"the faith which is in thee"* (1 Ne 7:17)
- *"the Spirit of the Lord which was in him"* (2 Ne 1:27)
- *"the holy prophets which were before us"* (Jacob 4:4)
- *"the resurrection which is in Christ"* (Jacob 4:11)
- *"the things which shall be done among them"* (2 Ne 26:17)

These are **parse-internal root-misassignments** (the parser promoted the PP `in/of/with/under` to the relative-clause root because the copular `be` was elided). The relative itself is genuine; only the root-token assignment is irregular. R19's existing routing handles these correctly (NOUN-head → REVIEW). Routing them to PARSER-SUSPECT is a regression.

## Cross-validator propagation gap (both audits)

4 other validators consume `acl:relcl`:

- `validators/colometry/validate_frame_predication_merges_ud.py:135` — reads `acl:relcl` as boolean substantive-frame indicator
- `validators/colometry/validate_severed_complement_ud.py:110` — reads `acl:relcl` as boolean substantive-advcl indicator
- `validators/colometry/validate_rule_17_ud.py` — ccomp-vs-relative discrimination
- `validators/colometry/validate_rule_21_ud.py` — excludes acl:relcl from participial-absolute

**None of these would honor R19's PARSER-SUSPECT subtype.** They consume the raw UD parse arc. The pre-filter is a leaky abstraction — R19 quarantines its routing, but downstream validators continue to ingest the (allegedly suspect) acl:relcl arc as evidence. The fix would be partial-by-design.

## Sample-size discipline (both audits, citing Factor C)

The 2102 scan classified 7 cases as probable parser errors. The proposed signal set was derived by pattern-enumeration from those 7 cases.

- Audit α: *"7-case sample, then promoting the pattern to a closed-list mechanical rule"*
- Audit β: *"The whole 'choose your handling' Item-6 framing presupposes the classification is sound. It isn't."*

§7.8 ≥80% adoption test: estimated 7-12 true positives out of 1,111 hits = **~1% clean rate**, well below the 20% ambiguity ceiling and two orders of magnitude below the 80% adoption threshold. The proposed rule fails §7.8.

Per `feedback_three_anti_default_factors`: **Factor C is the precedent that retracted EP-6**, which was a closed-list extension grounded in a similarly-small sample. The proposal is a structural recurrence of the same pattern.

## Discipline violations identified (audit β explicitly enumerated)

| Memory | Violation |
|---|---|
| `feedback_three_anti_default_factors` Factor C | 7-case extrapolation; EP-6 precedent |
| `feedback_grammar_constrains_not_determines` | Surface UPOS shape used as determination, not constraint |
| `feedback_audit_outputs_need_canon_check` | Audit classification smuggled into canon as if canon authority |
| `feedback_rhetoric_bandwagon` (adjacent) | Errors clustered in densely-parallel Isaiah chapter; fix imports parallelism-shape into validator routing |
| `feedback_principle_vs_mechanical_coverage` | Rule's WHY (7 Isaiah errors) vs mechanical scope (1,111 corpus hits) |
| `feedback_over_structuring_disposition` | 5 of the 5 diagnostic questions ("smallest version?") point to Option A, not Option E |
| `feedback_no_eyeball_offers` | Manufactures REVIEW-REQUIRED tags on canon-clean cases |

## MUST-FIX findings (if Stan elects to repair rather than reject — both audits converged)

If Stan wants validator-layer protection at all, the only defensible signals from the audit-evidence are the genuinely diagnostic ones:

1. **DROP S1 entirely** OR narrow to `head_lemma in {I, thou, thee, ye, you, we, us} AND head.deprel == nsubj` (1-2-person personal pronouns in matrix subject position — small finite class; needs corpus validation before commit)
2. **DROP S2's ADP branch** (74/82 hits are legitimate copular-elision relatives)
3. **DROP S3 entirely** (collides with canon §5 R19's predicative-identifier MERGE example)
4. **DROP S1's AUX branch** (0 corpus hits; dead code)
5. **DROP S1's VERB branch** (49 cases mostly root-misassignments where relative is genuine; R19's existing REVIEW already handles)
6. **Address cross-validator propagation** — if parser-suspect routing has any value, it must be a corpus-level token-annotation visible to all 4 consumers, not a single-validator routing layer
7. **Pair any surviving signal with canon §6 defensibility writeup** (`WHY` / `HOW WE KNOW` / `SCOPE`) before validator code lands

After (1)-(7), the residual signal set is essentially empty.

## The right path (both audits converged)

**Option A (per-case override JSON, 7-15 entries) plus Option D (resolver-skeptical-mode for Isaiah-quoting chapters)** — neither trips §7.3 trigger #1 or #2, and both address the actual 7-case Isaiah-scan inventory without canon-rule-extension risk.

The 2102 reply itself surfaces Option A as "trivial to maintain at this scale" — the audit findings reinforce that the 2102 reply's own framing was correct.

## Predicted retraction shape (audit α, paraphrased)

If implemented and the cascade rebuild ran, ~897 STRONG-SPLIT cases would disappear from the apply pipeline. The visual regression on bomreader.com would be immediate (KJV-pronominal-relative constructions — *"he that"*, *"they that"*, *"those who"* — collapse from split to merged-then-REVIEW). Predictable Stan-escalation: *"WHY did you route the entire CATAPHORIC paradigm to PARSER-SUSPECT?"* The adversarial-audit gate is functioning exactly as designed — catching this before the cascade rebuild ran.

## Reporting per directive items

- **Item 1 audit findings + cross-agent agreement:** above. Both REJECT with convergent must-fix list.
- **Item 3 implementation commit hash:** N/A — implementation halted per directive's STOP gate.
- **Item 4 before/after counts:** N/A — no change to validate.
- **Item 5 canon prose:** N/A — no rule change to document.
- **Item 6 resolver-script handling:** N/A — no subtype to consume.

## Surfaced concerns

1. **The directive's premise is structurally defective.** The 2102 reply's Option E was the worst of the 5 surfaced options; the directive elevated it for implementation. Future directives should evaluate the alternatives against canon-discipline gates BEFORE selecting one for the §7.3 audit slot.
2. **The §7.3 audit gate worked.** Both audits independently flagged the same fundamental issues with the same corpus evidence. This is the discipline operating as intended — catching a fake-rule before any validator code lands.
3. **Option A (7-entry override JSON) and Option D (resolver-skeptical-prompt) remain available.** Both can be pursued in follow-on directives without the §7.3 trigger #1+#2 audit overhead. Surfacing for Stan-decision: should a follow-on directive draft Option A?
4. **The 7-case Isaiah-scan inventory was actionable; the proposed rule was not.** The data was sound; the design layer was wrong.

## Cost note

2 Opus audit dispatches × ~5-6 min each. Per `feedback_model_selection_frugality`, Opus was the right tier ("hostile adversarial scope-scrutiny" — the rubric ITSELF was under audit). Justified.

## Audit status

**§7.3 trigger #1 + #2: AUDIT FAILED.** Implementation blocked per directive's Item 2 STOP gate. Implementation directive (this one) is moved to `processed/` with verdict REJECT; the must-fix list is the canonical Stan-decision surface.

If/when a successor directive (Option A or Option D) is drafted, that's a separate §7.4 (or possibly §7.3 trigger #X for the corpus-level annotation in Option A) conversation.

## Artifacts

- Audit α full output: `C:\Users\bibleman\AppData\Local\Temp\claude\c--Users-bibleman-repos-readers-bofm\5e934fd5-32e0-4958-9b1e-00dd9f0e6d19\tasks\a9d31434c243db52a.output`
- Audit β full output: `C:\Users\bibleman\AppData\Local\Temp\claude\c--Users-bibleman-repos-readers-bofm\5e934fd5-32e0-4958-9b1e-00dd9f0e6d19\tasks\a710bed5338a864ad.output`
- Audit β's corpus-fire counter (referenced): `C:/tmp/audit_r19_prefilter.py` (local)
- This reply
