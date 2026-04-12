# 14 — Operational Protocols

This file codifies the "work smarter" practices that govern how Claude Code should approach corpus-wide changes, bug fixes, and methodology refinements. These protocols are ported from the Reader's GNT project (`readers-gnt/handoffs/04-editorial-workflow.md`) where they were established through hard experience — every violation of the patterns below has resulted in either a bottleneck, a regression, or a partial fix that had to be redone.

These are not optional. They are the operating discipline of the project.

---

## A. Standard Operating Procedures

### A1. When Fixing a Bug

**Identify the CLASS of problem, not the single instance.**

When you find one bug, do not fix only the one bug. Find every instance of the same class in the corpus and fix them all in one commit.

1. Identify the class of problem (the underlying pattern)
2. Enumerate ALL instances of that class across the entire corpus
3. Fix them all in one commit
4. Verify no remaining instances after the fix

**Example from this project:** When the merge script for obligatory complement verbs stripped newlines without inserting a space, it produced 28 stuck-together words ("supposethat", "commandedthat", "desirethat") across 7 books. The correct response was to grep for ALL such forms (not just "supposethat"), generate fixes for the entire class in one pass, and verify zero remaining instances. Fixing only the visible ones would have left bugs scattered in books we hadn't yet looked at.

**The class identification habit:** when you find a problem, ask "what is the broader pattern this is an instance of?" and search for that pattern, not just the surface symptom.

### A2. When Changing the Pipeline (MANDATORY Two-Phase Pattern)

Pipeline changes must always be two separate dispatches:

1. **Phase 1 — Algorithm change:** ONE agent modifies the script (e.g., `build_book.py`, `senseline_reformat_v8.py`). This is a single-file code change. The agent does only the code change, not the rebuild.

2. **Phase 2 — Corpus rebuild:** SEPARATE agents run the modified script on book groups. For BOM Reader, the natural genre groups are:
   - Small plates (1 Nephi, 2 Nephi, Jacob, Enos, Jarom, Omni, Words of Mormon)
   - Mosiah
   - Alma
   - Helaman
   - 3 Nephi + 4 Nephi
   - Mormon, Ether, Moroni

These are ALWAYS two separate dispatches. **Never dispatch one agent to do both code change AND full corpus rebuild.** Never run one agent on all 15 books — Alma alone is more than a third of the BOM by line count.

When the task is "find and fix," each agent should find AND fix in its section, not just report. Otherwise the "find" phase becomes a sequential bottleneck where Claude has to manually consolidate findings before dispatching fix agents.

**This is not optional. Every violation of this pattern has resulted in a bottleneck.**

### A3. When Proposing Rule Changes

Before implementing a new colometric rule or swap rule:

1. Generate **multiple candidate approaches** (3–5 angles), not just the first instinct
2. Dispatch parallel adversarial agents to evaluate EACH approach against real corpus data
3. Each evaluation agent tests:
   - Accuracy rate (how often it produces the desired result)
   - False positive rate (how often it produces unwanted side effects)
   - Implementation complexity (how hard it is to write and maintain)
4. Compile a ranked recommendation with data BEFORE implementing anything
5. Only implement the top-ranked approach (or top 2 if complementary)

This prevents building the wrong solution and having to undo it. The "I'll just try it and see" approach has cost real time on this project — see the Wayyehi rule contradiction with Rule 16 that wasn't caught until the four-agent adversarial audit.

### A4. When Running Adversarial Agents

1. **Specific scoped mandates**, not "review all of X." Instead: "check Alma 5, 7, 12 and Helaman 5, 6 for these 5 specific patterns."
2. Use the **haiku model** for read-only review tasks (faster, cheaper, and just as effective for finding issues)
3. Use **opus** for tasks requiring code changes or complex multi-step reasoning
4. Each agent should **find AND fix**, not just find — avoid the sequential bottleneck where you have to manually consolidate findings and dispatch fix agents
5. **Split by genre group** for corpus-wide reviews (see A2 for groups)

### A5. When Adding Split/Merge Rules

1. Every split must validate that **both halves are viable cola** (each passes the atomic thought test)
2. Never split: article+noun, preposition+object, negation+verb, noun+genitive modifier, noun+possessive pronoun, verb+obligatory complement
3. After any split pass, re-run the dangling-function-word fix
4. **Test on gold standard chapters before corpus-wide rollout.** For BOM Reader, the gold standards are: 1 Nephi 8 (Tree of Life vision), Mosiah 2-5 (King Benjamin's address), Alma 5 (Alma's Zarahemla sermon), Alma 32 (faith chapter), Moroni 7 (charity chapter)

---

## B. Adversarial Testing Pattern

After ANY significant change to merge/split rules, dispatch parallel adversarial agents BEFORE committing:

1. **Feature-specific adversary** — tests the new rule for over-merges, under-merges, and edge cases. "I just changed X. Find every place where X might be wrong."

2. **Rule-interaction adversary** — tests all rules together for cascading errors and fights between passes. "Rule X interacts with rule Y. Find conflicts."

3. **Benchmark regression adversary** — re-runs known-good test cases to check for regressions. "Check that 1 Nephi 8, Mosiah 3, Alma 5, Alma 32, Moroni 7 still look right."

This pattern catches HIGH severity issues (rule interactions, sentence boundary violations, over-splitting) that code review alone misses. Established as a mandatory practice after the four-agent adversarial audit caught the Wayyehi/Rule 16 contradiction, the "know" obligatory complement gap, and 38 misclassified "insomuch that" instances.

**The pattern: change → rebuild → dispatch adversaries → fix what they find → commit.** Not change → commit → discover issues later.

---

## C. Parallel Dispatch Discipline

### C1. Run Independent Tasks in Parallel

When you have multiple independent tasks (different files, different audits, different scans), dispatch them as **parallel agents in a single message**, not sequentially. Sequential dispatch turns parallel work into a queue.

**Bad:** Dispatch agent 1, wait for result, dispatch agent 2, wait for result, dispatch agent 3.
**Good:** Single message with three Agent tool calls, all dispatched simultaneously.

### C2. Don't Batch Tasks That Should Be Independent

When auditing the corpus, don't ask one agent to "audit all 15 books." Split it across 4-6 agents by genre group. Each agent finishes faster, you get results faster, and any failure is contained to one genre.

### C3. Don't Be Sequential When You Don't Have To Be

Common Claude failure mode: "first I'll do A, then B, then C." If A, B, and C don't depend on each other, do them simultaneously. The agentic horde is the project's superpower — use it.

---

## D. Documentation Discipline

### D1. Update Handoffs at Important Decision Points

The handoff docs are the memory layer between sessions. Update them whenever:

1. A decision is made that affects future work
2. A principle is refined or a new rule is established
3. A pattern is identified across the corpus
4. A methodology reset happens (the rules themselves change)
5. A bug class is discovered and fixed
6. A feature is shipped or deprecated

Don't wait for end of session — update the relevant handoff(s) at the moment the decision is made. Future sessions need the reasoning, not just the result.

### D2. Append Dated Updates — Never Overwrite History

```markdown
---
### Update — 2026-MM-DD
- What changed
- What was decided
- New state
```

Never overwrite existing content. Append at the end. Future sessions need to trace how the methodology evolved, not just what it currently says.

### D3. Document the WHY, Not Just the WHAT

When updating a handoff, explain *why* the change was made. The "what" can be derived from git diff. The "why" is what makes the decision legible to future sessions.

**Bad:** "Merged 44 'insomuch that' instances."
**Good:** "Merged 44 'insomuch that' instances classified as DEGREE under the new image test. The image test distinguishes 'insomuch that' clauses that paint a new mental image (break) from those that quantify or specify the same image (merge). 91 instances confirmed as RESULT (correctly split). The rule eliminates 50/50 ambiguity in earlier treatment."

---

## E. The Cognitive Hierarchy (from GNT)

When colometric criteria conflict, the priority order is:

**Chunking > Oral > Rhetorical**

1. **Cognitive chunking** — line breaks first serve comprehension. Each line is a unit the reader can process as one cognitive bite. This is the foundational purpose.
2. **Oral delivery** — line breaks support read-aloud at natural breath pace. This is the ESL/youth/audio purpose.
3. **Rhetorical structure revelation** — line breaks make the author's compositional architecture visible (parallels, escalation, climax, chiasm). This is the literary purpose.

When these conflict, chunking wins. A break that aids cognitive chunking but flattens rhetoric is acceptable. A break that reveals rhetoric but creates a fragment that can't be processed is not.

This hierarchy was established in the Reader's GNT project (`readers-gnt/handoffs/04-editorial-workflow.md`, session 6 update). It governs editorial decisions when the four criteria leave ambiguity.

---

## F. Pre-Commit Checklist

Before committing source text changes:

1. ☐ All files saved and verified on disk (run `git diff` to confirm)
2. ☐ Build pipeline successful (`PYTHONIOENCODING=utf-8 python3 build_book.py --all`)
3. ☐ Spot-check the build output for obvious damage (sense-line view of one affected verse)
4. ☐ Service worker cache version bumped in `sw.js`
5. ☐ Commit message explains WHY, not just WHAT
6. ☐ Co-author trailer included

Before pushing source pipeline changes (build_book.py, etc.):

1. ☐ Two-phase pattern observed (algorithm change committed separately from corpus rebuild)
2. ☐ Adversarial agents dispatched and findings addressed
3. ☐ Gold standard chapters spot-checked for regressions
4. ☐ The "find the class, not the instance" rule applied — no related forms left unfixed

---

## G. The "Don't Be Sequential" Maxim

The single biggest performance gain in this project comes from parallel agent dispatch. When Stan tells me to do something, my default should be: **what parts of this can run simultaneously?**

- Reading multiple files → parallel Read calls in one message
- Auditing multiple books → parallel Agent calls split by genre group
- Independent fixes across files → parallel Agent calls
- Build + commit + handoff update → parallel where possible (though commit must follow build)

The exception is when one task genuinely depends on another's output. But even then, ask: can I dispatch the dependent task speculatively in parallel with a fallback if needed?

The "agentic horde" is not a metaphor. It's the operating model.

---

## H. Origin of These Protocols

These protocols were established in the Reader's GNT project after experience showed that ad hoc workflows don't scale. The GNT team's specific failure modes that led to each protocol:

- **A1 (find the class):** A bug was fixed in one place, then re-discovered three more times in subsequent sessions before the class was identified
- **A2 (two-phase pattern):** A single agent was given "modify the script and rebuild the corpus" — it spent 90% of its time on the rebuild and never finished the modification properly
- **A3 (multiple candidates):** A first-instinct fix was implemented, shipped, and then had to be undone two sessions later when a better approach was found
- **A4 (haiku for review):** Opus was being used for simple read-only audits at 5x the cost and 3x the latency
- **B (adversarial testing):** A change shipped, looked clean in spot checks, and then 94 ἰδού over-splits were discovered by adversarial review three sessions later
- **C (parallel dispatch):** Sequential agent dispatches were bottlenecking the project — what should have been 30 minutes of parallel work was taking 3 hours sequentially

The BOM Reader project has hit the same failure modes during the April 2026 sessions. Adopting these protocols formally prevents the same lessons from being relearned.

---

*Created: 2026-04-12*
*Origin: Ported from Reader's GNT project (readers-gnt/handoffs/04-editorial-workflow.md)*
