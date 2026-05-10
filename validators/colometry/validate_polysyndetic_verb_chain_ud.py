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
from validators.parsing.line_mapping import build_line_map, build_line_map_full, book_paths


COORDINATORS = {"and", "or", "nor"}

# M1 Gorgianic Bonded Pair lemma sets — synonymous/cognate/hendiadic verb
# pairs that canon §1 licenses to MERGE despite polysyndetic 'and'.
#
# CRITICAL DISTINCTION (Stan correction 2026-05-10): M1 covers synonymy,
# cognate-acts, and hendiadys (one act named twice for emphasis or
# rhetorical pairing). It does NOT cover sequential narrative bonding,
# thematic clustering, or "rhetorically bonded" sequences. Per
# feedback_rhetorical_force.md and feedback_rhetoric_bandwagon.md,
# rhetorical/narrative bonding is NOT structural-rule territory —
# sequential distinct actions split per the generative principle even
# when they form a recognizable rhetorical figure.
#
# Examples that are NOT M1:
#   - "lifted + crucified + buried" — three sequential passion events
#   - "draw + smite" — sequential (draw weapon, then strike)
#   - "torture + bind" — sequential cruelties
#   - "took + came" — sequential travel
#   - "stone + cast" — sequential persecution
#   - "preach + prophesy" — distinct speech acts (prophet does both)
#
# Examples that ARE M1:
#   - "weep + gnash" — verbal-extrapolated from the canonical nominal
#     hendiadys "weeping and gnashing of teeth" (no verbal N=2 instance
#     in corpus; retained by analogy with the canon-named nominal pair)
#   - "repent + believe" — paired soteriological response (canon-named)
#   - "fight + quarrel" — synonymous discord
#   - "bless + sanctify" — liturgical synonymy (sacrament prayer)
#   - "fear + tremble" — cognate emotional+somatic state
#   - "murmur + complain" — synonymous discontent verbalization
#   - "hunger + thirst" — cognate appetitive (verbal)
M1_BONDED_VERB_PAIRS: frozenset = frozenset({
    frozenset({"repent", "believe"}),       # canon §1 named
    frozenset({"weep", "gnash"}),           # canon §1 named (verbal-extrapolated from nominal)
    # {weep, wail} and {wail, gnash} DROPPED 2026-05-10 Wave 6 audit:
    # zero N=2 verbal corpus instances; extrapolation-only (Mosiah 16:2
    # has the N=3 chain "weep, wail, gnash" — Justification 1 wins per
    # the N=3+ cliff). Detector should not protect zero-corpus pairs.
    # {pray, supplicate} DROPPED 2026-05-10 Wave 6 audit: only corpus
    # attestation is Moroni 6:9 N=6 worship-list (preach/exhort/pray/
    # supplicate/sing/speak) — DISTINCT-ACTS, same shape as canon-rejected
    # {preach,prophesy} and {exhort,preach}. Sixth catch of rhetoric-
    # bandwagon failure mode.
    frozenset({"fight", "quarrel"}),        # synonymous discord
    # {spare, stay} dropped per Stan-direct 2026-05-10 — corpus
    # attestations all read as sequential-narrative ("did not strike,
    # then withdrew weapon"), not simultaneous-synonymy. Same shape as
    # {draw, smite}, {torture, bind}, {take, come} — withdrawn earlier.
    # Audit-driven additions (2026-05-10 hostile audit B-4):
    frozenset({"bless", "sanctify"}),       # liturgical synonymy (Moroni 4:3, 5:2 — sacrament prayer)
    frozenset({"fear", "tremble"}),         # cognate emotional+somatic state (1 Ne 16:28, 2 Ne 1:25)
    frozenset({"murmur", "complain"}),      # synonymous discontent verbalization (1 Ne 17:48)
    frozenset({"hunger", "thirst"}),        # cognate appetitive (3 Ne 12:6)
})

# Stative head lemmas — these head a different predication-class than
# action-verb conj members and indicate parse-noise rather than a true
# polysyndetic series.
STATIVE_HEAD_LEMMAS = frozenset({"be", "have"})


def is_m1_bonded(a, b) -> bool:
    """True if (a.lemma, b.lemma) is a canonical M1 bonded pair."""
    return frozenset({a.lemma, b.lemma}) in M1_BONDED_VERB_PAIRS


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


def shares_head_aux(sent: Sentence, head: Token, member: Token) -> bool:
    """True if the conj member depends on a shared auxiliary from the head
    (member has no own aux but head has one).

    Splitting such a chain would orphan the AUX from the conj-member
    participle, violating Rule 12 (compound-verb under shared aux). The
    polysyndetic principle yields to Rule 12 here.

    Examples:
        "shall be scattered, and smitten"  — both share 'shall be'
        "did fight, and quarrel, and vex"  — all share 'did'
    """
    head_aux = sent.aux_of(head)
    member_aux = sent.aux_of(member)
    if head_aux and not member_aux:
        return True
    return False


def has_heterogeneous_aux(sent: Sentence, head: Token, members: list[Token]) -> bool:
    """True when the chain is heterogeneous in auxiliary — i.e. the head and
    at least one member carry *different* auxiliaries, meaning they are
    separate predications that happen to be coordinated rather than a genuine
    polysyndetic series sharing one predicate frame.

    Decision matrix (head_aux / member_aux):
        both bare-finite (no aux)  → homogeneous — False
        head has aux, member bare  → Justification 1 territory (member shares
                                     head's aux elliptically) — False
        head bare, member has aux  → heterogeneous — True
        both have aux, SAME lemma  → homogeneous — False
        both have aux, DIFF lemma  → heterogeneous — True

    Examples that should return True (route to REVIEW):
        "had fled … were slain … were taken"  — had ≠ were
        "brought … were smitten … were driven" — bare ≠ were

    Examples that should return False (leave as STRONG):
        "took + bound + carried"              — all bare-finite
        "shall be scattered, and smitten"     — head has shall+be, member bare
        "did fight, and quarrel, and vex"     — head has did, members bare
    """
    head_aux_lemmas = frozenset(t.lemma.lower() for t in sent.aux_of(head))

    for member in members:
        member_aux_lemmas = frozenset(t.lemma.lower() for t in sent.aux_of(member))

        # Both bare-finite: homogeneous
        if not head_aux_lemmas and not member_aux_lemmas:
            continue

        # Head has aux, member bare: Justification 1 ellipsis — homogeneous
        if head_aux_lemmas and not member_aux_lemmas:
            continue

        # Member has aux but head is bare: heterogeneous
        if not head_aux_lemmas and member_aux_lemmas:
            return True

        # Both have aux — check whether they overlap
        if head_aux_lemmas and member_aux_lemmas:
            # If the member's aux set is a subset of the head's, homogeneous
            # (e.g. head: {shall, be}, member: {be} — both passive)
            if member_aux_lemmas <= head_aux_lemmas:
                continue
            # Otherwise the member carries a distinct aux: heterogeneous
            return True

    return False


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


def scan_book(book_id: str) -> tuple[list[dict], list[dict]]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map_full = build_line_map_full(v2_path, conllu_path)
    line_map = {k: v[0] for k, v in line_map_full.items()}

    findings: list[dict] = []
    review: list[dict] = []
    for sent in sentences:
        for head, members in find_chains(sent):
            # Audit-driven filter (2026-05-10): cross-class head guard.
            # Stative heads (be/have) with action-verb conj members are
            # parse-noise rather than true polysyndetic series.
            if head.lemma in STATIVE_HEAD_LEMMAS:
                continue

            # CORRECTION (2026-05-10, Stan): the prior shared-AUX filter was
            # over-conservative. Justification 1 explicitly licenses splits
            # in chains where the predicate (including AUX) is recoverable
            # from parallel structure: "shall be scattered, and smitten" →
            # split each member; the reader carries "shall be" mentally to
            # the second member. Rule 12 protects WITHIN a single AUX+verb
            # predication ("he had / done X" — wrong), not BETWEEN
            # coordinate members of a polysyndetic chain. Filter removed.

            # Heterogeneous-AUX filter (2026-05-10): chains where the head
            # and at least one member carry *different* auxiliaries are not
            # a genuine polysyndetic series — they are separate predications
            # coordinated syntactically. Route to REVIEW rather than STRONG.
            if has_heterogeneous_aux(sent, head, members):
                review.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "head_form": head.form,
                    "head_lemma": head.lemma,
                    "head_line": line_map.get((sent.sent_id, head.id)),
                    "chain_members": [(m.form, m.lemma) for m in members],
                    "skip_reason": "heterogeneous-aux-chain",
                    "v2_path": str(v2_path),
                })
                continue

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
                shared_sorted = sorted(shared, key=lambda x: x.id)

                # Audit-driven filter (2026-05-10): M1 bonded-pair
                # protection. If the two earliest tokens on the shared
                # line are a canonical M1 verb pair, the split between
                # them is suppressed by canon §1 M1.
                first_two = shared_sorted[:2]
                if len(first_two) == 2 and is_m1_bonded(first_two[0], first_two[1]):
                    # If only those two share the line, no real violation.
                    if len(shared_sorted) == 2:
                        # M1 protects this — bucket as REVIEW for visibility,
                        # do not flag as STRONG.
                        review.append({
                            "book": book_id,
                            "sent_id": sent.sent_id,
                            "head_form": head.form,
                            "head_lemma": head.lemma,
                            "shared_line": ln,
                            "shared_tokens": [(t.form, t.lemma) for t in shared_sorted],
                            "skip_reason": "M1-bonded-pair-merge-protected",
                            "v2_path": str(v2_path),
                        })
                        break
                    # If a third+ chain member also on this line, still
                    # split before the later (post-pair) member.
                    later = shared_sorted[2:]
                    split_before = later[0]
                else:
                    # First member on line is fine; split before second.
                    later = shared_sorted[1:]
                    split_before = later[0]

                # Find the cc token (the "and"/"or"/"nor") that introduces
                # split_before in the chain — this is where the line break
                # should go (per Rule 9: split BEFORE conjunction so it leads
                # the new line). Char offset of the cc token gives precise
                # split position.
                cc_deps = sent.dependents_of(split_before, deprel="cc")
                split_before_token = cc_deps[0] if cc_deps else split_before
                split_before_line_col = line_map_full.get(
                    (sent.sent_id, split_before_token.id)
                )
                split_col = split_before_line_col[1] if split_before_line_col else None

                findings.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "head_form": head.form,
                    "head_lemma": head.lemma,
                    "head_line": line_map.get((sent.sent_id, head.id)),
                    "chain_members": [(m.form, m.lemma) for m in members],
                    "shared_line": ln,
                    "shared_tokens": [(t.form, t.lemma) for t in shared_sorted],
                    "split_col": split_col,
                    "split_before_form": split_before.form,
                    "split_before_lemma": split_before.lemma,
                    "v2_path": str(v2_path),
                })
                # Only report the first shared-line violation per chain
                break
    return findings, review


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_findings: list[dict] = []
    all_review: list[dict] = []
    for bid in book_ids:
        try:
            fs, rev = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_findings.extend(fs)
        all_review.extend(rev)
        if args.verbose:
            print(f"{bid}: {len(fs)} STRONG, {len(rev)} REVIEW")

    m1_review = [r for r in all_review if r.get("skip_reason") == "M1-bonded-pair-merge-protected"]
    hetaux_review = [r for r in all_review if r.get("skip_reason") == "heterogeneous-aux-chain"]

    print("=" * 72)
    print("Polysyndetic verb-chain UD-query (N>=3 chain with shared-line break missing)")
    print("=" * 72)
    print(f"Books scanned:                    {len(book_ids)}")
    print(f"STRONG-SPLIT-CANDIDATE:           {len(all_findings)}")
    print(f"REVIEW (M1 protected):            {len(m1_review)}")
    print(f"REVIEW (heterogeneous-aux-chain): {len(hetaux_review)}")
    print(f"REVIEW (total):                   {len(all_review)}")
    print()

    for f in all_findings[:25]:
        chain_str = " + ".join(f"{form}" for form, _ in f["chain_members"])
        print(f"  [{f['book']}] sent={f['sent_id']} "
              f"head='{f['head_form']}' (line {f['head_line']}) "
              f"+ chain [{chain_str}] — "
              f"shared on line {f['shared_line']}; split before '{f['split_before_form']}'")
    if len(all_findings) > 25:
        print(f"  ... +{len(all_findings) - 25} more")

    if hetaux_review:
        print()
        print("REVIEW — heterogeneous-aux-chain:")
        for r in hetaux_review:
            chain_str = " + ".join(form for form, _ in r["chain_members"])
            print(f"  [{r['book']}] sent={r['sent_id']} "
                  f"head='{r['head_form']}' (line {r.get('head_line', '?')}) "
                  f"+ chain [{chain_str}] — {r['skip_reason']}")

    print(f"RESULT: violations={len(all_findings)} strong={len(all_findings)} review={len(all_review)}")
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
