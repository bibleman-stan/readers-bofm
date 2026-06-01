"""Build a self-contained Workflow script that v2-sprays a candidate set.

Reads a candidate JSON (from audit_to_candidates.py), splices the candidates
inline as a JS literal, writes the complete .js workflow script.

Run:
  py -3 scripts/build_spray_workflow.py PARALLEL_THAT_ASYMMETRY --pilot
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / "data" / "parses" / "audit"
WORKFLOWS = REPO / "scripts" / "workflows"


WORKFLOW_TEMPLATE = r"""export const meta = {
  name: 'bofm-spray-__CLS__-__TAG__',
  description: 'v2-spray over Stanza-flagged __CLS__ candidates. Sonnet adjudicates per verse, 2 parallel Opus audits (over-merge + atomicity), survivors of both returned. HALTS at survivors — deploy is a separate gated decision.',
  phases: [
    { title: 'Adjudicate' },
    { title: 'Audit' },
  ],
}

const candidates = __CANDIDATES__

const ADJ_SCHEMA = {
  type: 'object',
  required: ['has_gap', 'reasoning'],
  properties: {
    has_gap: { type: 'boolean' },
    reasoning: { type: 'string' },
    proposed_lines: { type: 'array', items: { type: 'string' } },
    matrix_predicate: { type: 'string' },
    n_beats: { type: 'integer' },
    confidence: { enum: ['high', 'medium', 'low'] },
  },
}

const AUDIT_SCHEMA = {
  type: 'object',
  required: ['verdict', 'reasoning'],
  properties: {
    verdict: { enum: ['safe', 'kill'] },
    reasoning: { type: 'string' },
    specific_concerns: { type: 'array', items: { type: 'string' } },
  },
}

phase('Adjudicate')

const verses = await pipeline(
  candidates,
  (cand) => agent(
    `BoFM ATU-gap audit, structural-anomaly candidate.

This verse was flagged by the deterministic Stanza-parse auditor for class:
${cand.flag_class}. Flag detail: ${cand.flag_detail}

The class signature is >=2 'that'-headed clauses in one sentence whose Stanza-
assigned parent deprels disagree on linguistically-identical parallel beats
(canonical case: Moroni 4:3 "we ask thee... that X... that Y... that Z" where
Stanza tagged two 'that' clauses parataxis and one advcl, despite identical
structure).

Verse: ${cand.ref}
v0 source (MASTER — joined output MUST equal this char-for-char):
${cand.source_text}

Current deployed ATU split (${cand.deployed_lines.length} lines):
${cand.deployed_lines.map((l,i) => `L${i}: ${l}`).join('\n')}

Apply framework canon:
- BIDIRECTIONAL TEST (sole arbiter): forward grammatical closure + backward
  referential self-containment. Elision-restoration from immediately-prior
  parallel clause permitted (a shared FINITE verb only — not subject/object/PP).
- §2.2 MARKER-LICENSE: a line led by 'that' is closure-eligible iff the marker-
  stripped residual passes §2.1. E.g. "that they may eat..." → strip 'that' →
  "they may eat..." → forward-closed (modal+finite "may eat" + complement);
  backward-OK ("they" chain-continuous with prior "those who partake"). SAFE.
- §2.1 PUNCTUATION HAS ZERO FORCE. Never split/bind on a mark. Treat parataxis
  ≡ ccomp; punctuation is symptom not cause.
- GENRE IS NEVER A CRITERION. No "prophetic oracle"-type holds.

Tasks (in order):
1. has_gap: does the deployed split lump 2+ distinct parallel ATU beats onto one
   line that should be enumerated under a single matrix predicate?
   Common matrices: "we ask thee... that X / that Y / that Z" (petition),
   "I would that ye should X / that ye should Y" (volition), "I know that X /
   that Y" (declaration), "I say unto you that X / that Y" (assertion).
2. If yes: matrix_predicate + n_beats + proposed_lines.
   PARITY CONSTRAINT: proposed_lines joined by single spaces with whitespace
   normalized MUST EQUAL the source_text normalized. No added/removed/reordered
   words. Reorder breaks only. CHECK THIS BEFORE RETURNING.
3. If no: state why (single complement of cognition/speech verb; AICTP "came to
   pass that X" frame binds forward; relative clause "the X that..."; demonstrative
   "that day"; current split is already optimal).

Conservative bias: default has_gap=false on ambiguous. Over-merge is the red
line. Cite ATU bidirectional logic, NOT punctuation or genre.`,
    { phase: 'Adjudicate', label: `adj:${cand.ref}`, schema: ADJ_SCHEMA },
  ),
  (adj, cand) => {
    if (!adj.has_gap || !adj.proposed_lines || adj.proposed_lines.length < 2) {
      return { adj, audits: null, candidate: cand, status: 'no_change' }
    }
    const norm = (s) => s.replace(/\s+/g, ' ').trim()
    const reconstructed = norm(adj.proposed_lines.join(' '))
    const original = norm(cand.source_text)
    if (reconstructed !== original) {
      return {
        adj, audits: null, candidate: cand, status: 'parity_fail',
        parity_diff: { reconstructed_len: reconstructed.length, original_len: original.length }
      }
    }
    return parallel([
      () => agent(
        `Adversarial OVER-MERGE LENS audit. Stan's red line: lumping 2 distinct
ATUs onto one line is forbidden.

Verse: ${cand.ref}
Original deployed (current production, ${cand.deployed_lines.length} lines):
${cand.deployed_lines.map(l => `  ${l}`).join('\n')}

Proposed split (${adj.proposed_lines.length} lines):
${adj.proposed_lines.map(l => `  ${l}`).join('\n')}

Adjudicator's matrix: ${adj.matrix_predicate || '(not stated)'}
Adjudicator's reasoning:
${adj.reasoning}

Walk each PROPOSED line. If any proposed line still lumps 2+ distinct ATUs
(e.g., two distinct 'that'-purposes; one purpose + one independent 'and X'
continuation that should also be its own beat), KILL.

Question: does every proposed line contain exactly ONE atomic beat?

DEFAULT verdict=kill if uncertain. Over-merge is the red line.`,
        { phase: 'Audit', label: `over-merge:${cand.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
      ),
      () => agent(
        `Adversarial ATOMICITY LENS audit. Framework §2.2 LICENSES a line led by
a bare 'that' subordinator IFF the marker-stripped residual passes §2.1. Do NOT
kill solely for opening with 'that' — that's exactly what §2.2 overrides.

Verse: ${cand.ref}
Proposed split:
${adj.proposed_lines.map((l,i) => `  L${i}: ${l}`).join('\n')}

For each proposed line:
1. Strip any leading marker mentally ('that', 'and that', 'yea').
2. Forward closure: residual has a finite verb (modal+verb "may eat" /
   "might know" counts; copula "are willing" counts); obligatory valency
   satisfied; elision-restoration of FINITE verb from immediate prior line
   permitted (a shared finite, not subject/object/PP).
3. Backward containment: pronoun referents from immediate prior chain OK.

KILL ONLY IF: truly verbless fragment; pronoun with no antecedent visible
anywhere; dangling preposition with no object; cataphor with no resolution.

DEFAULT verdict=safe if marker-stripped residual passes §2.1.`,
        { phase: 'Audit', label: `atomicity:${cand.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
      ),
    ]).then(([overmerge, atomicity]) => ({
      adj, candidate: cand,
      audits: { overmerge, atomicity },
      status: 'audited',
      survives: overmerge?.verdict === 'safe' && atomicity?.verdict === 'safe'
    }))
  }
)

const audited = verses.filter(v => v && v.status === 'audited')
const survivors = audited.filter(v => v.survives)
const killed = audited.filter(v => !v.survives)
const no_change = verses.filter(v => v && v.status === 'no_change')
const parity_fails = verses.filter(v => v && v.status === 'parity_fail')

log(`Total candidates: ${verses.length}`)
log(`  No change (Sonnet says current is correct): ${no_change.length}`)
log(`  Parity-fail (proposed split lost/added text): ${parity_fails.length}`)
log(`  Audit-killed: ${killed.length}`)
log(`  Survived BOTH audits: ${survivors.length}`)

return {
  class: '__CLS__',
  total: verses.length,
  counts: {
    no_change: no_change.length,
    parity_fails: parity_fails.length,
    killed: killed.length,
    survivors: survivors.length,
  },
  survivors: survivors.map(v => ({
    ref: v.candidate.ref,
    matrix: v.adj.matrix_predicate,
    n_beats: v.adj.n_beats,
    confidence: v.adj.confidence,
    deployed_lines: v.candidate.deployed_lines,
    proposed_lines: v.adj.proposed_lines,
  })),
  killed: killed.map(v => ({
    ref: v.candidate.ref,
    matrix: v.adj.matrix_predicate,
    proposed_lines: v.adj.proposed_lines,
    over_merge_verdict: v.audits.overmerge?.verdict,
    over_merge_reasoning: (v.audits.overmerge?.reasoning || '').slice(0, 400),
    atomicity_verdict: v.audits.atomicity?.verdict,
    atomicity_reasoning: (v.audits.atomicity?.reasoning || '').slice(0, 400),
  })),
  no_change: no_change.map(v => ({
    ref: v.candidate.ref,
    reasoning: (v.adj.reasoning || '').slice(0, 240),
  })),
  parity_fails: parity_fails.map(v => ({
    ref: v.candidate.ref,
    diff: v.parity_diff,
  })),
}
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cls = sys.argv[1]
    pilot = "--pilot" in sys.argv
    chunk_arg = next((a for a in sys.argv if a.startswith("--chunk=")), None)
    chunk = None
    if chunk_arg:
        n, m = chunk_arg.split("=")[1].split("/")
        chunk = (int(n), int(m))
    tag = "pilot" if pilot else ("full" if chunk is None else f"chunk{chunk[0]}of{chunk[1]}")
    name = f"candidates-{cls}-pilot.json" if pilot else f"candidates-{cls}.json"

    candidates_path = AUDIT / name
    if not candidates_path.exists():
        print(f"Missing {candidates_path}. Run audit_to_candidates.py {cls}{' --pilot' if pilot else ''} first.")
        sys.exit(1)

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    if chunk is not None:
        n, m = chunk
        candidates = candidates[n::m]

    script = (
        WORKFLOW_TEMPLATE
        .replace("__CLS__", cls)
        .replace("__TAG__", tag)
        .replace("__CANDIDATES__", json.dumps(candidates))
    )

    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    out = WORKFLOWS / f"bofm-spray-{cls}-{tag}.js"
    out.write_text(script, encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO)}")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Script size: {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
