"""Build a SIMPLIFIED UD-correction Workflow for the pilot.

v2 design changes from v1 (which had 76% propose-step failure rate):
  - Flat edits schema (no nested group_id / per-group arrays)
  - Leaner ruleset prefix (~600 chars vs ~2200)
  - NO in-workflow Opus audit (the audits were specified to PREDICT ATU
    effect; validate.py + ATU-regen + three-way-diff MEASURE ATU effect
    empirically post-workflow, fully replacing both audit lenses with
    mechanical ground truth)
  - Single Sonnet call per candidate, no parallel schema cascade

Run:  py -3 5-machinery/scripts/build_ud_correction_workflow_v2.py
Out:  5-machinery/scripts/workflows/bofm-ud-correction-pilot-v2.js
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CAND = REPO / "data" / "parses" / "audit" / "ud-pilot-candidates.json"
WORKFLOWS = REPO / "5-machinery" / "scripts" / "workflows"

TEMPLATE = r"""export const meta = {
  name: 'bofm-ud-correction-pilot-v2',
  description: 'UD-correction pilot v2: simplified flat-edit schema, no in-loop Opus audit. Sonnet proposes UD edits per candidate; validate.py delta-gate + ATU regen + 3-way diff run mechanically post-workflow.',
  phases: [{ title: 'Propose' }],
}

const candidates = __CANDIDATES__

const RULES = `PROJECT RULES (these OUTRANK UD-v2 defaults on conflict):
- Punctuation has ZERO force, including parser decisions conditioned on it. Treat parataxis ≡ ccomp for a finite content clause; a boundary that flips on a comma is forbidden.
- "and it came to pass" is a discourse-frame; its "that"-complement BINDS to the frame.
- BoFM §2.2 marker registry: {yea, or rather} ONLY (the "that"-extension was killed by hostile audit).
- Genre is NEVER a criterion.
- Goal: surface-identical sibling clauses (e.g. "that he might X / that he might Y") should receive identical deprels and attach to the same head.`

const PROPOSE_SCHEMA = {
  type: 'object',
  required: ['has_corrections', 'reasoning'],
  properties: {
    has_corrections: { type: 'boolean' },
    reasoning: { type: 'string' },
    edits: {
      type: 'array',
      items: {
        type: 'object',
        required: ['sent_id', 'token', 'column', 'baseline', 'new'],
        properties: {
          sent_id: { type: 'string' },
          token: { type: 'integer' },
          column: { enum: ['HEAD', 'DEPREL'] },
          baseline: { type: 'string' },
          new: { type: 'string' },
          rationale: { type: 'string' },
        },
      },
    },
  },
}

phase('Propose')

const proposals = await parallel(candidates.map(cand => () => agent(
  `${RULES}

Verse: ${cand.ref}
Source: ${cand.source_text}

Stanza baseline parse (sent_ids ${cand.sent_ids.join(', ')}):
\`\`\`
${cand.baseline_conllu}
\`\`\`

Anomaly flag: PARALLEL_THAT_ASYMMETRY — ${cand.flag_detail}

Task: Propose specific UD edits (HEAD and/or DEPREL changes) that restore symmetric deprels on surface-identical sibling clauses (e.g. three "that he might X" siblings should share deprel + head). Each edit specifies sent_id, token (1-indexed), column (HEAD or DEPREL), baseline (current value), new (corrected). Conservative bias: default has_corrections=false on ambiguous; chase a "cleaner" UD-v2 default that breaks project rules only with explicit justification in rationale.

If has_corrections=true, list the minimum atomic set of edits. Each edit gets its own rationale citing the project rule it implements.`,
  { label: `propose:${cand.ref}`, schema: PROPOSE_SCHEMA, model: 'sonnet' }
).then(p => ({ candidate: cand, proposal: p }))))

const valid = proposals.filter(Boolean)
const with_edits = valid.filter(v => v.proposal?.has_corrections && (v.proposal?.edits || []).length > 0)
const no_corr = valid.filter(v => !v.proposal?.has_corrections || (v.proposal?.edits || []).length === 0)

log(`Total candidates: ${candidates.length}`)
log(`  Returned: ${valid.length}`)
log(`  With edits: ${with_edits.length}`)
log(`  No corrections: ${no_corr.length}`)

return {
  total: candidates.length,
  returned: valid.length,
  with_edits: with_edits.length,
  no_corrections: no_corr.length,
  proposals: with_edits.map(v => ({
    ref: v.candidate.ref,
    sent_ids: v.candidate.sent_ids,
    baseline_errors: v.candidate.baseline_errors,
    deployed_lines: v.candidate.deployed_lines,
    deployed_override_present: !!v.candidate.deployed_override,
    edits: v.proposal.edits,
    reasoning: (v.proposal.reasoning || '').slice(0, 600),
  })),
  no_corrections_refs: no_corr.map(v => ({
    ref: v.candidate.ref,
    reasoning: (v.proposal?.reasoning || '').slice(0, 240),
  })),
}
"""


def main():
    candidates = json.loads(CAND.read_text(encoding="utf-8"))
    script = TEMPLATE.replace("__CANDIDATES__", json.dumps(candidates))
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    out = WORKFLOWS / "bofm-ud-correction-pilot-v2.js"
    out.write_text(script, encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO)}")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Script size: {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
