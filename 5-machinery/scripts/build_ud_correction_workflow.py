"""Build the UD-correction Workflow script for the pilot.

Splices the UD-pilot candidate list inline + the project ruleset prefix
into a self-contained Workflow JS script (Sonnet proposes edit-group list,
2 parallel Opus audits over-edit + downstream-effect).

Run:  py -3 5-machinery/scripts/build_ud_correction_workflow.py
Out:  5-machinery/scripts/workflows/bofm-ud-correction-pilot.js
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CAND = REPO / "data" / "parses" / "audit" / "ud-pilot-candidates.json"
WORKFLOWS = REPO / "5-machinery" / "scripts" / "workflows"

TEMPLATE = r"""export const meta = {
  name: 'bofm-ud-correction-pilot',
  description: 'UD-correction pilot: Sonnet proposes edit-group lists fixing the Stanza baseline parses for 50 PARALLEL_THAT_ASYMMETRY pilot verses; 2 parallel Opus audits (over-edit + downstream-effect lenses) gate. Halts at survivors — validate.py delta-gate + ATU regen + 3-way diff run post-workflow.',
  phases: [
    { title: 'Propose' },
    { title: 'Audit' },
  ],
}

const candidates = __CANDIDATES__

const RULESET = `PROJECT RULESET (project rules OUTRANK UD-v2 defaults on conflict).

Framework §2.1 — bidirectional ATU test (primary):
1. Forward grammatical closure: the line is grammatically complete on its own terms; ellipsis-restoration from immediately-prior parallel clause permitted (shared FINITE verb only, not subject/object/PP). Verbless / nominal-predicate constructions count as closed when subject + predicate are juxtaposed in pro-drop languages; EME English requires overt copula or modal+verb.
2. Backward referential self-containment: referents from immediate prior chain OK, or self-introducing within line. Long-range antecedent without chain-continuity FAILS.
Asymmetry: cataphoric introduction OK (quotative frame announcing distinct direct discourse stands; clausal complement of a matrix verb BINDS regardless of cognition/speech/perception class — "I know that X" / "I say to you that X" — verb identity not the discriminator).
Restrictive relative clauses bind to their head noun (corollary).

PUNCTUATION HAS ZERO FORCE — including parser decisions conditioned on it. A binding boundary that flips on a comma is forbidden. Treat parataxis ≡ ccomp for a finite content clause of a speech verb (same grammatical relation, the difference is only the comma).

Framework §2.2 — explicit-marker break-license (secondary):
A closure-eligible colon may be broken when opened by a registered marker. Marker does NOT make a fragment into an ATU — the colon is already closure-eligible under §2.1 (often via ellipsis-restoration of a finite verb); the marker supplies the break-license. Registry: BoFM = {yea, or rather} ONLY (the "that" extension was killed by hostile audit wlwl37c70).

Project-specific macro-syntactic conventions (these OUTRANK UD-v2):
- "and it came to pass" — discourse-frame opening narrative coordination (EME analog of Hebrew wayhi); the "that"-complement that follows BINDS to the frame.
- Sub-clausal "yea" — §2.2 marker licensing a break (amplificative); NOT an interjection in the §2.1 sense.
- "or rather" — §2.2 marker (restatement).
- Genre is NEVER a criterion. No "prophetic oracle"-type holds.
`

const PROPOSE_SCHEMA = {
  type: 'object',
  required: ['has_corrections', 'reasoning'],
  properties: {
    has_corrections: { type: 'boolean' },
    reasoning: { type: 'string' },
    edit_groups: {
      type: 'array',
      items: {
        type: 'object',
        required: ['group_id', 'edits', 'rationale'],
        properties: {
          group_id: { type: 'integer' },
          edits: {
            type: 'array',
            items: {
              type: 'object',
              required: ['sent_id', 'token', 'column', 'baseline', 'new'],
              properties: {
                sent_id: { type: 'string' },
                token: { type: 'integer' },
                column: { enum: ['HEAD', 'DEPREL', 'UPOS', 'LEMMA'] },
                baseline: { type: 'string' },
                new: { type: 'string' },
              },
            },
          },
          rationale: { type: 'string' },
        },
      },
    },
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

phase('Propose')

const verses = await pipeline(
  candidates,
  (cand) => agent(
    `${RULESET}

UD-correction proposal for ${cand.ref}.

Source text: ${cand.source_text}

Stanza baseline parse(s) — sent_ids ${cand.sent_ids.join(', ')}:
\`\`\`
${cand.baseline_conllu}
\`\`\`

Baseline errors per sentence (UD validate.py):
${JSON.stringify(cand.baseline_errors)}

Structural anomaly flag (audit_stanza_parses.py):
PARALLEL_THAT_ASYMMETRY — ${cand.flag_detail}

Currently deployed ATU split (${cand.deployed_lines.length} lines):
${cand.deployed_lines.map((l,i) => `L${i}: ${l}`).join('\n')}
${cand.deployed_override ? '\nA gate-passed override IS deployed for this verse.' : '\nNo deployed override — runs through the binding rules unmodified.'}

Tasks:
1. Identify the Stanza parse errors that contributed to the structural anomaly (e.g., asymmetric deprels on parallel siblings, wrong HEAD on a purpose-'that' verb, misrooted apodosis after a punctuation-driven sentence split).
2. Propose edit_groups. EACH GROUP is one ATOMIC correction — multi-token edits MUST be declared as one group if re-attaching one HEAD requires dependent re-attachments. A group's edits succeed or fail together at the validate gate.
3. Each edit specifies: sent_id, token (1-indexed integer), column (HEAD/DEPREL/UPOS/LEMMA), baseline (current value), new (corrected value).
4. Cite the project ruleset clause justifying each group — particularly if the correction conflicts with a UD-v2 default. Conservative bias: default has_corrections=false on ambiguous; chase a "cleaner" UD-v2 default that breaks our conventions only with explicit justification.

Goal: edit_groups that, when applied, will produce internally-consistent parallel-structure parses (same deprel for surface-identical sibling clauses) and remove the punctuation-laundering source of the anomaly — without introducing UD validate errors beyond baseline.`,
    { phase: 'Propose', label: `propose:${cand.ref}`, schema: PROPOSE_SCHEMA },
  ),
  (proposal, cand) => {
    if (!proposal.has_corrections || !proposal.edit_groups || proposal.edit_groups.length === 0) {
      return { proposal, candidate: cand, audits: null, status: 'no_corrections' }
    }
    return parallel([
      () => agent(
        `${RULESET}

LENS A — OVER-EDIT AUDIT for ${cand.ref}.

The proposal claims to fix Stanza errors. Walk each edit_group and judge:
- Does any edit chase a UD-v2 default that CONFLICTS with the project ruleset above? (Project rules OUTRANK UD-v2.)
- Does any edit change something that didn't need changing — a tidy-up that doesn't fix the anomaly?
- Does any edit drift from "and it came to pass" as discourse-frame? From sub-clausal yea as §2.2 marker?

Proposal:
${JSON.stringify(proposal.edit_groups, null, 2)}

Reasoning given:
${proposal.reasoning}

KILL on ANY drift from project rules. Surface specific_concerns by group_id.
DEFAULT verdict=kill if uncertain.`,
        { phase: 'Audit', label: `over-edit:${cand.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
      ),
      () => agent(
        `${RULESET}

LENS B — DOWNSTREAM-EFFECT AUDIT for ${cand.ref}.

Predict the effect on the regenerated ATU output if the proposed UD edits are applied. The binding rules (in 5-machinery/scripts/bofm_generate.py) key on the corrected deprels/heads.

Currently deployed ATU lines (${cand.deployed_lines.length}):
${cand.deployed_lines.map((l,i) => `L${i}: ${l}`).join('\n')}
${cand.deployed_override ? '(These came from a gate-passed override — apples-to-apples target.)' : '(These came from binding rules over the baseline parse.)'}

Proposed UD edits:
${JSON.stringify(proposal.edit_groups, null, 2)}

Reasoning given:
${proposal.reasoning}

Predict the new ATU lines after rules run over corrected UD. Compare against the deployed lines above.

KILL if predicted ATU output is:
- WRONG (violates §2.1/§2.2 — would over-merge or fragment),
- ABSENT (no change from baseline — UD edit doesn't move the ATU needle),
- WORSE than deployed (deployed already split this verse correctly; correction would regress).

SAFE only if predicted ATU is BETTER than deployed or AT LEAST as good for verses where deployed has known issues.

DEFAULT verdict=kill if uncertain. A locally-correct UD edit that produces no improvement (or a regression) at the ATU layer doesn't earn its position.`,
        { phase: 'Audit', label: `downstream:${cand.ref}`, schema: AUDIT_SCHEMA, model: 'opus' }
      ),
    ]).then(([overedit, downstream]) => ({
      proposal, candidate: cand,
      audits: { overedit, downstream },
      status: 'audited',
      survives: overedit?.verdict === 'safe' && downstream?.verdict === 'safe'
    }))
  }
)

const audited = verses.filter(v => v && v.status === 'audited')
const survivors = audited.filter(v => v.survives)
const killed = audited.filter(v => !v.survives)
const no_corr = verses.filter(v => v && v.status === 'no_corrections')

log(`Total candidates: ${verses.length}`)
log(`  No corrections proposed: ${no_corr.length}`)
log(`  Audit-killed: ${killed.length}`)
log(`  Survived BOTH audits: ${survivors.length}`)

return {
  total: verses.length,
  counts: {
    no_corrections: no_corr.length,
    killed: killed.length,
    survivors: survivors.length,
  },
  survivors: survivors.map(v => ({
    ref: v.candidate.ref,
    sent_ids: v.candidate.sent_ids,
    baseline_errors: v.candidate.baseline_errors,
    deployed_lines: v.candidate.deployed_lines,
    deployed_override_present: !!v.candidate.deployed_override,
    edit_groups: v.proposal.edit_groups,
    reasoning: (v.proposal.reasoning || '').slice(0, 400),
  })),
  killed: killed.map(v => ({
    ref: v.candidate.ref,
    edit_groups: v.proposal.edit_groups,
    over_edit_verdict: v.audits.overedit?.verdict,
    over_edit_reasoning: (v.audits.overedit?.reasoning || '').slice(0, 400),
    downstream_verdict: v.audits.downstream?.verdict,
    downstream_reasoning: (v.audits.downstream?.reasoning || '').slice(0, 400),
  })),
  no_corrections: no_corr.map(v => ({
    ref: v.candidate.ref,
    reasoning: (v.proposal.reasoning || '').slice(0, 240),
  })),
}
"""


def main():
    candidates = json.loads(CAND.read_text(encoding="utf-8"))
    script = TEMPLATE.replace("__CANDIDATES__", json.dumps(candidates))
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    out = WORKFLOWS / "bofm-ud-correction-pilot.js"
    out.write_text(script, encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO)}")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Script size: {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
