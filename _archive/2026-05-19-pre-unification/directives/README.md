# Directives Queue

Per-repo directive queue for cross-repo coordination between vault-Claude (Stan's primary interlocutor) and this repo's per-session Claude. Full protocol: [`../../atu-method/memories/feedback_directive_protocol.md`](../../atu-method/memories/feedback_directive_protocol.md).

## How it works

Vault-Claude writes directives to `pending/` and pushes. Stan reviews directives in his editor before triggering. On wake, this repo's Claude:

1. Completes mandatory orientation reads (CLAUDE.md, canon §0/§1/§2, git log, compaction-resume protocol)
2. Checks `pending/` for files in commit-order
3. For each pending directive:
   - Reads the directive
   - Executes items per their reporting + audit-trigger guidance
   - Writes a reply at `replies/<same-name>.md`
   - Moves the directive from `pending/` to `processed/<same-name>.md`
   - Commits + pushes per directive (or per coherent batch)
4. Surfaces processed items + open Stan-decisions in chat after the session

## Folders

- `pending/` — directives awaiting processing (commit-order)
- `processed/` — directives that have been executed (archive)
- `replies/` — per-directive status reports (mirror naming)

## Stan editorial controls

Stan reviews directives in his editor before triggering. Three actions:
- **Approve as written**: trigger with "go" or similar; no edit needed
- **Edit in place**: modify the directive file; saved edits are the directive's authoritative form
- **Reject**: delete the directive from `pending/` before triggering (no commit needed; working-tree-only deletion)

Direct engagement (Stan engaging this repo's Claude with custom input) remains available — the directive queue is the default workflow, not the only one.
