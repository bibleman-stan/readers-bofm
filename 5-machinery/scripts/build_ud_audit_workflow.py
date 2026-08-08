"""Build the Opus-audit Workflow on top of v2 Sonnet proposals.

Per the v2-then-audit architecture: v2 produced raw Sonnet proposals; this
script wraps them as input to a Workflow that fires 2 parallel Opus audits
per proposal (over-edit lens + downstream-effect lens). Same preamble as
v2 propose (framework rules, baseline CoNLL-U, anomaly flag) plus the
Sonnet proposal under review.

Run:  py -3 5-machinery/scripts/build_ud_audit_workflow.py <v2_output_json>
Out:  5-machinery/scripts/workflows/bofm-ud-audit-pilot.js
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WORKFLOWS = REPO / "5-machinery" / "scripts" / "workflows"
PILOT_CAND = REPO / "data" / "parses" / "audit" / "ud-pilot-candidates.json"

TEMPLATE = r"""export const meta = {
  name: 'bofm-ud-audit-pilot',
  description: 'Opus audit lenses on UD-correction v2 Sonnet proposals. Parallel over-edit + downstream-effect audits per proposal. Both lenses must pass — either kills the proposal. Halts at survivors; validate.py + three-way diff run mechanically post-workflow.',
  phases: [{ title: 'Audit' }],
}

const proposals = __PROPOSALS__

const RULES = `PROJECT RULES (these OUTRANK UD-v2 defaults on conflict):

Framework §2.1 — bidirectional ATU test (primary):
1. Forward grammatical closure: line is grammatically complete on its own terms; ellipsis-restoration from immediately-prior parallel clause permitted (shared FINITE verb only, not subject/object/PP). EME English requires overt copula or modal+verb.
2. Backward referential self-containment: referents from immediate prior chain OK, or self-introducing within line. Long-range antecedent without chain-continuity FAILS.
Cataphoric introduction OK (quotative frame stands; clausal complement BINDS regardless of cognition/speech/perception class — "I know that X" / "I say to you that X").
Restrictive relative clauses bind to their head noun (corollary).

PUNCTUATION HAS ZERO FORCE — including parser decisions conditioned on it. A binding boundary that flips on a comma is forbidden. Treat parataxis ≡ ccomp for a finite content clause of a speech verb.

Framework §2.2 — explicit-marker break-license (secondary):
A closure-eligible colon may be broken when opened by a registered marker. Marker does NOT make a fragment into an ATU — the colon is already closure-eligible under §2.1. Registry: BoFM = {yea, or rather} ONLY (the "that" extension was killed by hostile audit wlwl37c70).

Project macro-syntactic conventions (OUTRANK UD-v2):
- "and it came to pass" — discourse-frame; its "that"-complement BINDS to the frame.
- Sub-clausal "yea" — §2.2 marker (amplificative break-license).
- "or rather" — §2.2 marker (restatement).
- Genre is NEVER a criterion.`

const AUDIT_SCHEMA = {
  type: 'object',
  required: ['verdict', 'reasoning'],
  properties: {
    verdict: { enum: ['safe', 'kill'] },
    reasoning: { type: 'string' },
    specific_concerns: { type: 'array', items: { type: 'string' } },
  },
}

phase('Audit')

const audited = await pipeline(
  proposals,
  (prop) => parallel([
    () => agent(
      `${RULES}

LENS A — OVER-EDIT AUDIT for ${prop.ref}.

Baseline Stanza parse — sent_ids ${prop.sent_ids.join(', ')}:
\`\`\`
${prop.baseline_conllu}
\`\`\`

Anomaly flag: PARALLEL_THAT_ASYMMETRY — ${prop.flag_detail}

Sonnet's proposed edits:
${JSON.stringify(prop.edits, null, 2)}

Sonnet's reasoning:
${prop.reasoning}

Task: Walk each proposed edit and judge:
- Does any edit chase a UD-v2 default that CONFLICTS with the project ruleset above? Project rules OUTRANK UD-v2.
- Does any edit change something that didn't need changing — a tidy-up that doesn't fix the anomaly?
- Does any edit drift from "and it came to pass" as discourse-frame? From sub-clausal yea as §2.2 marker? From genre-not-a-criterion?
- Does any edit break the "punctuation has zero force" rule by re-attaching based on commas?

KILL on ANY drift from project rules. Surface specific_concerns naming the edits.
DEFAULT verdict=kill if uncertain — over-edit is the doctrinal red line.`,
      { label: `over-edit:${prop.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
    ),
    () => agent(
      `${RULES}

LENS B — DOWNSTREAM-EFFECT AUDIT for ${prop.ref}.

The proposal claims to fix Stanza errors that propagated to the ATU layer. Predict the effect of applying these UD edits on regenerated ATU output (what bofm_generate.py's binding rules would produce).

Currently deployed ATU lines (${prop.deployed_lines.length}):
${prop.deployed_lines.map((l,i) => `L${i}: ${l}`).join('\n')}
${prop.deployed_override_present ? '(These came from a gate-passed override — the apples-to-apples comparison target.)' : '(These came from binding rules over baseline parse, no override deployed.)'}

Baseline Stanza parse:
\`\`\`
${prop.baseline_conllu}
\`\`\`

Anomaly flag: ${prop.flag_detail}

Proposed UD edits:
${JSON.stringify(prop.edits, null, 2)}

Sonnet's reasoning:
${prop.reasoning}

Task: Predict the ATU output after applying the corrections. Compare against the deployed lines above.

KILL if predicted ATU is:
- WRONG (would over-merge or fragment per §2.1/§2.2),
- ABSENT (no change from baseline — UD edits don't move the ATU needle),
- WORSE than deployed (regression vs override-driven version).

KEY ATU-EFFECT CONSIDERATIONS:
- If the corrections re-attach surface-identical sibling "that he might X / Y / Z" clauses as flat advcl siblings, the current binding rules may read those as cohesively bound and NOT split them — producing under-split ATU vs deployed.
- A cleaner UD substrate that produces a worse reader output doesn't earn its position.

SAFE only if predicted ATU is BETTER than deployed OR at least equivalent.

DEFAULT verdict=kill if uncertain. ATU regression is the user-facing failure.`,
      { label: `downstream:${prop.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
    ),
  ]).then(([overedit, downstream]) => ({
    proposal: prop,
    over_edit: overedit,
    downstream: downstream,
    survives: overedit?.verdict === 'safe' && downstream?.verdict === 'safe',
    killed_by_over_edit: overedit?.verdict === 'kill',
    killed_by_downstream: downstream?.verdict === 'kill',
  }))
)

const survivors = audited.filter(a => a?.survives)
const killed = audited.filter(a => a && !a.survives)
const oe_only = killed.filter(a => a.killed_by_over_edit && !a.killed_by_downstream)
const ds_only = killed.filter(a => !a.killed_by_over_edit && a.killed_by_downstream)
const both = killed.filter(a => a.killed_by_over_edit && a.killed_by_downstream)

log(`Audited: ${audited.length} proposals`)
log(`  Opus-survivors (both safe): ${survivors.length}`)
log(`  Killed by over-edit only: ${oe_only.length}`)
log(`  Killed by downstream only: ${ds_only.length}`)
log(`  Killed by both: ${both.length}`)

return {
  total_audited: audited.length,
  survivors: survivors.map(a => ({
    ref: a.proposal.ref,
    sent_ids: a.proposal.sent_ids,
    baseline_errors: a.proposal.baseline_errors,
    deployed_lines: a.proposal.deployed_lines,
    deployed_override_present: a.proposal.deployed_override_present,
    edits: a.proposal.edits,
    reasoning: a.proposal.reasoning,
    over_edit_reasoning: (a.over_edit?.reasoning || '').slice(0, 500),
    downstream_reasoning: (a.downstream?.reasoning || '').slice(0, 500),
  })),
  killed: killed.map(a => ({
    ref: a.proposal.ref,
    edits: a.proposal.edits,
    sonnet_reasoning: a.proposal.reasoning,
    over_edit_verdict: a.over_edit?.verdict,
    over_edit_reasoning: a.over_edit?.reasoning || '',
    over_edit_concerns: a.over_edit?.specific_concerns || [],
    downstream_verdict: a.downstream?.verdict,
    downstream_reasoning: a.downstream?.reasoning || '',
    downstream_concerns: a.downstream?.specific_concerns || [],
  })),
}
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    v2_path = Path(sys.argv[1])
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    if "result" in v2 and isinstance(v2.get("result"), dict):
        v2 = v2["result"]
    raw_proposals = v2.get("proposals", [])
    if not raw_proposals:
        print(f"No proposals in {v2_path.name}. Counts: {v2.get('counts',{})}")
        sys.exit(2)

    cand_by_ref = {c["ref"]: c for c in json.loads(PILOT_CAND.read_text(encoding="utf-8"))}

    enriched = []
    for p in raw_proposals:
        c = cand_by_ref.get(p["ref"], {})
        enriched.append({
            "ref": p["ref"],
            "sent_ids": p["sent_ids"],
            "baseline_errors": p["baseline_errors"],
            "baseline_conllu": c.get("baseline_conllu", ""),
            "flag_detail": c.get("flag_detail", ""),
            "deployed_lines": p["deployed_lines"],
            "deployed_override_present": p["deployed_override_present"],
            "edits": p["edits"],
            "reasoning": p["reasoning"],
        })

    script = TEMPLATE.replace("__PROPOSALS__", json.dumps(enriched))
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    out = WORKFLOWS / "bofm-ud-audit-pilot.js"
    out.write_text(script, encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO)}")
    print(f"  Proposals to audit: {len(enriched)}")
    print(f"  Script size: {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
