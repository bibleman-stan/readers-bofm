---
name: repoint-paths-safely
description: Move or rename a file or directory that other files point at, across this repo and its siblings, without leaving dangling references or blinding a gate. Use whenever a path changes — renaming a folder, relocating a doc, moving canon, reorganizing the tree — or when a pointer/citation checker starts reporting a suspiciously different number of files scanned.
---

# Repointing a path without breaking the gates

**Every trap below has already been paid for.** On 2026-08-06 a cross-repo
repoint left **103 dangling canon citations**, because the repointer skipped
`private/` and the other repo's checker could not see what the repointer refused
to walk — two tools, one shared blind spot, both reporting clean. On 2026-08-07 a
`handoffs/` → `docs/` rename reproduced the same *class* of failure three more
times in a single hour. This skill is that hour, written down.

**The one-line lesson:** *a gate only sees what it is pointed at* — so a move can
break a gate silently, and the gate will report clean while blind.

## The procedure

### 1. Inventory before you move

Find inbound references in **two** forms, because one regex will not catch both:

```
grep -rn "oldname/" --include=*.md --include=*.py --include=*.json --include=*.js
grep -rn "oldname"  --include=*.py            # ← bare, no trailing slash
```

**The bare form is the one that bites.** Code says `(REPO_ROOT / "handoffs")` —
no slash — so a `handoffs/` pattern misses it entirely. On 2026-08-07 two
validators globbed a directory that no longer existed; one silently fell from 18
files scanned to 3 and still exited 0. *A validator that scans nothing passes.*

Check sibling repos too (`../atu-method`, `../readers-*`), and check whether a
matched path belongs to a **different** repo: `readers-gnt/handoffs/...` must NOT
be rewritten when renaming *this* repo's `handoffs/`. A negative lookbehind for
`/` handles that: `(?<![\w/-])handoffs/`.

### 2. Move with `git mv`, and know that it stages

`git mv` puts the rename in the index immediately. If you then stage other work,
`validators/check_commit_scope.py` will refuse the mixed commit. Either commit
the move on its own or `git restore --staged` the parts that belong elsewhere.

### 3. Rewrite references — walk everything except the record

**Walk `private/`.** That omission is the whole 2026-08-06 incident.

**Never rewrite archival material:** `_archive/`, `private/03-sessions/`, and any
transcript or dated session record. Rewriting a path inside a transcript makes
the record say something it never said. A pointer in an archive is *supposed* to
name the world as it was. (On 2026-08-07 the first pass rewrote 11 such files and
they had to be reverted.)

Skip `.obsidian/` (volatile), `books/` and `audio/` (build output), `.git/`.

Write the repointer to a **file** and run it — never a heredoc. Regex plus
heredoc quoting is the recurring mangling failure; see the `safe-scripting` skill.

### 4. Do not "fix" a checker by widening its skip list

The most damaging edit of 2026-08-07: a repointer rewrote atu-method's
`check_broken_pointers.py` `SKIP_PREFIXES` from `"handoffs/"` to `"docs/"`. That
entry exists to skip *reader-repo* paths — and `docs/` is atu-method's **own**
docs tree, so the change would have made the checker skip every pointer into the
canon it exists to check.

**Rule: a pointer checker's own skip lists are out of scope for a mechanical
repoint.** Revert any change to them and edit by hand, deliberately, if at all.

### 5. Expect a moved file to enter a validator's scope for the first time

A file that moves *into* a scanned directory gets scanned for the first time, and
may light up instantly. That is an artefact of the move, not new breakage —
diagnose before suppressing, then fix at the right level.

Worked case: `retraction-log.md` moved from the repo root into `docs/` and
`validate_canon_retirement_residue.py` went 0 → 14. Every hit was legitimate:
naming retired terms is that file's entire purpose. The right fix was a
whole-file retirement-context exemption — the file-scope form of an exemption the
validator already granted to Update Log *sections* — not a blanket suppression
and not editing the log.

Ask: *is this violation new information, or did the instrument just start
looking?* If the latter, the fix belongs in the instrument's notion of scope.

### 6. Verify — both checkers, and read the file count

```
py -3 validators/colometry/validate_doc_pointers.py
py -3 validators/colometry/validate_canon_retirement_residue.py
cd ../atu-method && py -3 scripts/check_broken_pointers.py
```

**Read "Files scanned: N", not just the violation count.** A drop in N is a
blinded gate and it looks exactly like success. Record N before and after; if it
fell, you broke a glob. (2026-08-07: 18 → 3 → fixed → 21.)

Then update `docs/00-index.md` if the map changed, and say in the commit message
which gates you ran and what N was.

## The checklist

- [ ] grepped both `oldname/` and bare `oldname` (incl. `.py`)
- [ ] checked sibling repos; left *their* same-named paths alone
- [ ] repointer walked `private/`
- [ ] repointer skipped `_archive/`, `private/03-sessions/`, transcripts
- [ ] no checker's `SKIP_*` list was mechanically rewritten
- [ ] investigated any newly-scanned file's violations before suppressing
- [ ] both repos' pointer checkers run; **files-scanned count did not drop**
- [ ] doc index updated; commit message records the gates and the counts
