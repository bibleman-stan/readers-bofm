# Pending Decisions — readers-bofm

One dated entry per decision that is **Stan's to make**. Each carries the ask, the
options, a recommendation, and what happens next. Resolved entries are deleted and
the resolution recorded in the relevant doc (canon, retraction log, or commit
message). An empty "Open" section means nothing is waiting on you.

Same name and format as `atu-nlp-wiki/Pending-Decisions.md`, deliberately — one
place to look, in every repo.

---

## Open

### [2026-08-07] Is line length a *detector*, or is it barred entirely?

**The ask.** `atu-method/memories/operational/feedback_external_unit_is_not_atu.md`
says to *"reject the granularity calibrated to their unit (Scheppers' fronting rule,
**Marschall's syllable counts**)."* Framework §2 likewise admits only the
bidirectional test and the marker registry as break licensors. Both are right that a
syllable count must never *license a break* — that is the objectivity firewall.

But the same rule currently also blocks using length to **notice** a bad line. As
measured 2026-08-07: 2,459 deployed lines exceed Marschall's 35-syllable Law and 465
exceed 60 syllables, with a maximum of 121 words. Nothing in the pipeline can see
those, because the only instrument that would is barred.

**This gates the whole evidence loop.** A finding measured in Marschall's or
Skousen's units arrives at a canon with a standing instruction to reject it, so
`docs/findings/` fills up and discharges nowhere.

**Options.**
- **(a) Licensor/detector split (recommended).** External units may never license or
  place a break. They MAY rank lines for human review. Concretely: a long line is
  never re-broken because it is long — it is *looked at* because it is long, and any
  resulting break must still earn its way through the bidirectional test.
- **(b) Keep the bar absolute.** Length plays no role at any stage. Accept that the
  program has no instrument for systematic coarseness and that the gold yardstick
  cannot supply one (it shares the bar's calibration).
- **(c) Narrow waiver.** Permit length as a detector only for a named audit, expiring
  when that audit closes.

**Recommendation: (a).** It preserves the firewall exactly where the firewall is
load-bearing — nothing about what licenses a break changes — while ending the
condition where the one non-circular check available is unusable. §7.3 trigger: this
is a scope claim on a settled rule, so it wants an adversarial audit before it lands.

---

### [2026-08-07] Non-finite predication — the §2.1 reconstruction

**The ask.** `atu-method/docs/04-process/proposal-2026-08-06-criterion-reconstruction.md`
found that three live §2.1 allowances rest on two carve-outs *"cited as existing and
defined nowhere,"* and a fourth appears to contradict §2.2's firewall directly. Its
step 1 is a single ruling: **does non-finite material ever constitute a thought unit
on its own, and on what argument?** Three allowances stand or fall together on it.

**Status:** the proposal is analysis only; nothing has been applied. Retiring live
allowances is a §7.3 trigger #5 event and needs adversarial audit first.

**Recommendation:** rule on it before any further allowance is added, because the
sprawl is downstream of the thin criterion, not independent of it.

---

### [2026-08-07] The four validator regressions — investigate or waive?

**The ask.** `rule_12` +2, `rule_15` +3, `rule_19` +10, `rule_29` +1 sit above a
baseline last captured **2026-05-29**. At least six corpus- and parse-changing ships
landed after that date without the baseline moving, so it was almost certainly
bypassed repeatedly through early June. **The baseline has stopped functioning as a
control**, which matters more than the four numbers.

Three of the four are `_ud` validators keyed on the parse, which the lever-2 sweeps
*corrected* — so a rising count there can mean the instrument got sharper, not that
the text got worse. A count cannot distinguish these; only a per-violation set diff
can, and that tool does not exist.

**Options.** Investigate (blocked on tooling that must be built first) · waive
specific commits that provably cannot affect the counts, with the reason in the
message · `--update-baseline` (**forbidden by canon**, and correctly — it would
silently accept the drift forever).

**Recommendation:** build the set-diff, then re-baseline from a known-good state.
Until then, waive only commits that touch no corpus, parse, or rule, and say so
explicitly in the message.

---

### [2026-08-07] Parry in git history

**The ask.** The overlay has been removed from the build and the live pages
(2026-08-07). The source data was committed historically and the blobs remain
reachable in git history across 21 commits, so an old checkout still yields his
arrangement.

**Status: DEFERRED by Stan, 2026-08-07** — risk assessed as very low; no history
rewrite for now. Recorded here so the exposure is not forgotten rather than
forgotten. Revisit if the repo is ever mirrored, archived, or publicised.

---

### [2026-08-07] Tier-2 repo reorganisation

**The ask.** `private/01-method/` is tracked, public, and load-bearing canon whose
name says the opposite. It should become `docs/01-method/`. But canon citations
across four repos point at that path, and the 2026-08-06 incident (103 dangling
citations) was caused by a repointer that skipped `private/`.

**Recommendation:** one move at a time, each with `validate_doc_pointers.py` and
`atu-method/scripts/check_broken_pointers.py` run before and after, and archival
material (`private/03-sessions/`, `_archive/`) never rewritten.

---

## Resolved

*(none yet — resolved entries are deleted, with the resolution recorded where it
belongs)*
