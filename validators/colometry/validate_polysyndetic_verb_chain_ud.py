"""
Polysyndetic Verb-Chain — UD-query detector.

**Canon basis.** §1 Structural Justification 1: "Members connected by formal
markers (and also, nor, correlative particles, polysyndetic *and*) where the
shared predicate is recoverable from the parallel structure. Each member
earns its own beat."

**Pattern.** A finite VERB head with ≥2 conj-VERB members (so chain ≥3 total),
each conj attached by `cc` lemma in {and, or}, sharing the head's nsubj (no
own nsubj on the conj members — confirms it is one subject doing multiple
actions, not a list of independent agents). When two or more chain members
sit on the same v2-mine line, the polysyndetic break is missing.

**Canonical example (Alma 30:20):**
    "for they took him,
     and bound him, and carried him before Ammon,"
  — chain head = took (line A); conj members = bound, carried (both on line B).
  Bound and carried share line B → STRONG-SPLIT before "and carried".

**N=2 exclusion.** This detector targets N≥3 chains only. For N=2 (head + 1
conj), M1 Gorgianic Bonded Pair adjudication applies (synonymous/cognate
pairs merge; distinct verbs split — judgment call requiring lexical
synonymy assessment that is non-mechanical at scale).

**Action.** STRONG-SPLIT-CANDIDATE: report the v2-mine line where ≥2 chain
members share a line, plus the chain root and members for context.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths


COORDINATORS = {"and", "or", "nor"}


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def is_polysyndetic_member(sent: Sentence, tok: Token) -> bool:
    """A polysyndetic chain member: VERB conj with cc='and'/'or'/'nor' and
    no own nsubj (shares the head's subject)."""
    if tok.upos != "VERB" or tok.deprel != "conj":
        return False
    ccs = sent.dependents_of(tok, deprel="cc")
    if not ccs:
        return False
    if not any(c.lemma.lower() in COORDINATORS for c in ccs):
        return False
    own_nsubj = (sent.dependents_of(tok, deprel="nsubj")
                 + sent.dependents_of(tok, deprel="nsubj:pass"))
    if own_nsubj:
        return False
    return True


def find_chains(sent: Sentence) -> list[tuple[Token, list[Token]]]:
    """Return [(head, members), ...] for chains where head is VERB and
    has ≥2 polysyndetic VERB conj members (chain length ≥3 total)."""
    by_head: dict[int, list[Token]] = {}
    for tok in sent.tokens:
        if is_polysyndetic_member(sent, tok):
            by_head.setdefault(tok.head, []).append(tok)

    result = []
    for head_id, members in by_head.items():
        if len(members) < 2:
            continue
        head = sent.by_id(head_id)
        if head is None or head.upos != "VERB":
            continue
        result.append((head, members))
    return result


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    findings: list[dict] = []
    for sent in sentences:
        for head, members in find_chains(sent):
            # Collect (token, line) for head + all members
            chain_tokens = [head] + members
            tok_lines = []
            for t in chain_tokens:
                ln = line_map.get((sent.sent_id, t.id))
                if ln is not None:
                    tok_lines.append((t, ln))

            # Group by line
            by_line: dict[int, list[Token]] = {}
            for t, ln in tok_lines:
                by_line.setdefault(ln, []).append(t)

            # Violation: any v2-mine line carrying ≥2 chain tokens
            for ln in sorted(by_line):
                if len(by_line[ln]) < 2:
                    continue
                shared = by_line[ln]
                # The split point is before the second chain member on this
                # line — find the second-or-later conj member (not the head).
                # Members are sorted by token id; second-or-later is the one
                # to split before.
                shared_sorted = sorted(shared, key=lambda x: x.id)
                # First on line is fine; need split before any subsequent.
                later = shared_sorted[1:]
                findings.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "head_form": head.form,
                    "head_lemma": head.lemma,
                    "head_line": line_map.get((sent.sent_id, head.id)),
                    "chain_members": [(m.form, m.lemma) for m in members],
                    "shared_line": ln,
                    "shared_tokens": [(t.form, t.lemma) for t in shared_sorted],
                    "split_before_form": later[0].form,
                    "split_before_lemma": later[0].lemma,
                    "v2_path": str(v2_path),
                })
                # Only report the first shared-line violation per chain
                break
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_findings: list[dict] = []
    for bid in book_ids:
        try:
            fs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_findings.extend(fs)
        if args.verbose:
            print(f"{bid}: {len(fs)} chain violations")

    print("=" * 72)
    print("Polysyndetic verb-chain UD-query (N>=3 chain with shared-line break missing)")
    print("=" * 72)
    print(f"Books scanned:           {len(book_ids)}")
    print(f"STRONG-SPLIT-CANDIDATE:  {len(all_findings)}")
    print()

    for f in all_findings[:25]:
        chain_str = " + ".join(f"{form}" for form, _ in f["chain_members"])
        print(f"  [{f['book']}] sent={f['sent_id']} "
              f"head='{f['head_form']}' (line {f['head_line']}) "
              f"+ chain [{chain_str}] — "
              f"shared on line {f['shared_line']}; split before '{f['split_before_form']}'")
    if len(all_findings) > 25:
        print(f"  ... +{len(all_findings) - 25} more")

    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
