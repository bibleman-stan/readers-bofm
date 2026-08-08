"""Build the corpus-wide UD-correction Workflow (propose-only, no Opus).

The §2.2 parallel-stack rule shipped 9101ea9 handles ATU output mechanically;
downstream-effect lens no longer applies. Sonnet propose-only + validate.py
gate is sufficient for TF-query-only substrate correction.

Splits 781 candidates into N chunks under workflow script size limit.

Run:  py -3 5-machinery/scripts/build_ud_fullclass_workflow.py [--chunks=4]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CAND = REPO / "data" / "parses" / "audit" / "ud-correction-fullclass-candidates.json"
WORKFLOWS = REPO / "5-machinery" / "scripts" / "workflows"

TEMPLATE = r"""export const meta = {
  name: 'bofm-ud-fullclass-__CHUNK__',
  description: 'Corpus-wide UD-correction (TF-query substrate). Sonnet flat-edit proposes per candidate. No Opus (downstream lens no longer applies after §2.2 stack rule shipped). validate.py + apply runs mechanically post-workflow.',
  phases: [{ title: 'Propose' }],
}

const candidates = __CANDIDATES__

const RULES = `PROJECT RULES (these OUTRANK UD-v2 defaults on conflict):
- Punctuation has ZERO force, including parser decisions conditioned on it. Treat parataxis ≡ ccomp for a finite content clause.
- "and it came to pass" is a discourse-frame; its "that"-complement BINDS to the frame.
- Surface-identical sibling clauses should receive identical deprels and attach to the same head.
- Goal: fix Stanza's asymmetric attachment of parallel structures; do NOT chase UD-v2 taxonomy adjustments that don't fix the anomaly.`

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

Stanza baseline parse:
\`\`\`
${cand.baseline_conllu}
\`\`\`

Anomaly: PARALLEL_THAT_ASYMMETRY — ${cand.flag_detail}

Task: Propose specific UD edits (HEAD and/or DEPREL changes) that restore symmetric deprels on surface-identical sibling clauses. Conservative bias: default has_corrections=false on ambiguous.`,
  { label: `propose:${cand.ref}`, schema: PROPOSE_SCHEMA, model: 'sonnet' }
).then(p => ({ candidate: cand, proposal: p }))))

const valid = proposals.filter(Boolean)
const with_edits = valid.filter(v => v.proposal?.has_corrections && (v.proposal?.edits || []).length > 0)
const no_corr = valid.filter(v => !v.proposal?.has_corrections || (v.proposal?.edits || []).length === 0)

log(`Total: ${candidates.length}, returned: ${valid.length}, with_edits: ${with_edits.length}, no_corr: ${no_corr.length}`)

return {
  total: candidates.length,
  returned: valid.length,
  with_edits: with_edits.length,
  no_corrections: no_corr.length,
  proposals: with_edits.map(v => ({
    ref: v.candidate.ref,
    sent_ids: v.candidate.sent_ids,
    edits: v.proposal.edits,
    reasoning: (v.proposal.reasoning || '').slice(0, 400),
  })),
}
"""


def main():
    chunks = 4
    for a in sys.argv[1:]:
        if a.startswith("--chunks="):
            chunks = int(a.split("=", 1)[1])
    candidates = json.loads(CAND.read_text(encoding="utf-8"))
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    paths = []
    for ci in range(chunks):
        chunk = candidates[ci::chunks]
        script = (
            TEMPLATE
            .replace("__CHUNK__", f"chunk{ci}of{chunks}")
            .replace("__CANDIDATES__", json.dumps(chunk))
        )
        out = WORKFLOWS / f"bofm-ud-fullclass-chunk{ci}of{chunks}.js"
        out.write_text(script, encoding="utf-8")
        paths.append(out)
        print(f"Wrote {out.relative_to(REPO)}: {len(chunk)} candidates, {out.stat().st_size/1024:.1f} KB")
    return paths


if __name__ == "__main__":
    main()
