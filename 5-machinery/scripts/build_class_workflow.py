"""Build chunked propose-only Workflow scripts for any anomaly class.

Run:  py -3 5-machinery/scripts/build_class_workflow.py CLASS_NAME [--chunks=N]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AUDIT = REPO / "data" / "parses" / "audit"
WORKFLOWS = REPO / "5-machinery" / "scripts" / "workflows"

TEMPLATE = r"""export const meta = {
  name: '__NAME__',
  description: 'Corpus-wide UD-correction (TF-query substrate). Sonnet flat-edit proposes per candidate. validate.py delta-gate + apply run mechanically post-workflow.',
  phases: [{ title: 'Propose' }],
}

const candidates = __CANDIDATES__

const RULES = `PROJECT RULES (these OUTRANK UD-v2 defaults on conflict):
- Punctuation has ZERO force, including parser decisions conditioned on it. Treat parataxis ≡ ccomp for a finite content clause.
- "and it came to pass" is a discourse-frame; its "that"-complement BINDS to the frame.
- Surface-identical sibling clauses should receive identical deprels and attach to the same head.
- Goal: fix Stanza's asymmetric/wrong-attached structures; do NOT chase UD-v2 taxonomy adjustments that don't fix the anomaly.`

const CLASS_HINT = __CLASS_HINT__

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

${CLASS_HINT}

Verse: ${cand.ref}
Source: ${cand.source_text}

Stanza baseline parse:
\`\`\`
${cand.baseline_conllu}
\`\`\`

Anomaly: ${cand.flag_class} — ${cand.flag_detail}

Task: Propose specific UD edits (HEAD and/or DEPREL changes) that fix the diagnosed anomaly. Conservative bias: default has_corrections=false on ambiguous.`,
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

CLASS_HINTS = {
    "PUNCTUATION_DRIVEN_SPLIT":
        "Class signature: Stanza split a verse into multiple sentences at a semicolon/comma "
        "mid-coordinate-stack, then a continuation sentence opens with a coordinator/subordinator "
        "(and/that/but/etc.). The break is a punctuation-driven artifact, not a structural boundary. "
        "Fix the attachment so the punctuation-segmented pieces re-join into one coherent tree.",
    "LONG_DISTANCE_ATTACHMENT":
        "Class signature: an advcl or parataxis token is attached >30 tokens away from its head. "
        "Almost always Stanza misrooted the apodosis or chose the wrong governor over a long span. "
        "Fix the head to a closer correct governor.",
    "BIGRAM_DEPREL_DIVERGENCE":
        "Class signature: the same subordinator/coordinator bigram (e.g. 'and he', 'when he', 'that they') "
        "appears 2+ times in one sentence with different deprels on the lead token. Stanza tagged "
        "linguistically-identical openers asymmetrically. Symmetrize the deprels.",
    "PARALLEL_THAT_ASYMMETRY":
        "Class signature: >=2 'that'-headed clauses with disagreeing parent deprels on parallel beats. "
        "Restore symmetric deprels on surface-identical sibling clauses.",
}


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cls = sys.argv[1]
    chunks = 4
    for a in sys.argv[2:]:
        if a.startswith("--chunks="):
            chunks = int(a.split("=", 1)[1])
    cand_path = AUDIT / f"candidates-{cls}-enriched.json"
    if not cand_path.exists():
        print(f"Missing {cand_path}. Run enrich_class_candidates.py {cls} first.")
        sys.exit(1)
    candidates = json.loads(cand_path.read_text(encoding="utf-8"))
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    cls_slug = cls.lower().replace("_", "-")
    hint = CLASS_HINTS.get(cls, "")
    paths = []
    for ci in range(chunks):
        chunk = candidates[ci::chunks]
        script = (
            TEMPLATE
            .replace("__NAME__", f"bofm-ud-{cls_slug}-chunk{ci}of{chunks}")
            .replace("__CANDIDATES__", json.dumps(chunk))
            .replace("__CLASS_HINT__", json.dumps(hint))
        )
        out = WORKFLOWS / f"bofm-ud-{cls_slug}-chunk{ci}of{chunks}.js"
        out.write_text(script, encoding="utf-8")
        paths.append(out)
        print(f"  {out.name}: {len(chunk)} candidates, {out.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
