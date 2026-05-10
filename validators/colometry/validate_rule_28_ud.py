"""
Rule 28 (Speech-Act Announcement After Frame) — UD-query implementation.

UD signature (per canon §3/§5):
    Main-clause VERB with lemma in speech-verb set, having both:
      - nsubj dependent (the announcing subject, e.g. "the king")
      - advcl sibling (temporal/causal/locative frame, e.g. "after Aaron had...")
    The speech tag is a complete independent predication and earns its own line.

Violation: the speech VERB and an advcl sibling sit on the SAME v2-mine line
    (i.e. the speech tag is merged into the frame line instead of standing alone).

Two output buckets:
    PASS               — speech verb already on its own line (frame on prior line)
    STRONG-SPLIT-CANDIDATE — speech verb merged into the same line as the advcl

Why UD over regex:
    The regex implementation detects MERGED_VIOLATION_RE as a single line
    containing both a subordinating conjunction and a colon-terminated speech
    verb. That catches the merged case but cannot confirm whether the speech
    verb truly has an nsubj + advcl as syntactic siblings (vs a mere
    surface co-occurrence). The UD query checks both structural conditions,
    reducing false positives from chains like "as far as he said:" where
    "as" is a degree adverb, not a subordinating conjunction heading an advcl.

Detection logic:
    For each sentence, find every VERB token whose lemma is in SPEECH_LEMMAS.
    Check that it has:
      (a) at least one nsubj dependent (it is an announcing predicate, not
          embedded under another verb — but see Caveat below)
      (b) at least one advcl sibling (i.e. a token whose head is the same as
          the speech verb's head, deprel="advcl")  OR  an advcl dependent of
          the speech verb itself (advcl may hang on the speech verb directly
          in some parse trees)
    Then compare the v2-mine line of the speech verb to the line of the advcl
    root:
      - same line → STRONG-SPLIT-CANDIDATE
      - different line → PASS (already split)

Caveat: BofM parses frequently attach speech verbs as parataxis under the
    AICTP "pass" verb. This does not disqualify them — Rule 28 applies
    regardless of whether the speech verb is the sentence root or a parataxis
    dependent.

Speech verb lemma set (per canon §5 Rule 28 cross-reference to Rule 17):
    say, speak, declare, cry, answer — plus surface forms spake, saith,
    answered (lemmatised by the parser).

Comparison target: validators/colometry/validate_rule_28_speech_act_after_frame.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths


SPEECH_LEMMAS = {"say", "speak", "declare", "cry", "answer"}

# advcl roots to EXCLUDE — these are not temporal/causal/locative frames;
# they are participial speech-continuation markers or other non-frame adverts.
# "saying" as an advcl of a speech verb is the canonical BofM ", saying:"
# pattern (a participial introducer, not a scene-setting frame). Filtering it
# prevents the very common "spake ... saying:" construction from flooding the
# output with false Rule 28 violations.
ADVCL_EXCLUDED_LEMMAS = {"say"}   # "saying" lemma is "say"

# UD mark lemmas that unambiguously introduce temporal/causal frame adverts.
# "as" is excluded: it is ambiguous between temporal ("as he walked") and
# comparative ("as a man speaketh") — both parse as advcl but only the former
# is a Rule 28 scene-setting frame. Using only unambiguous subordinators
# keeps false positives minimal.
FRAME_MARK_LEMMAS = {
    "after", "when", "while", "before", "since",
    "until", "because", "though", "although", "lest", "except",
}

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def _is_frame_advcl(sent: Sentence, advcl: Token, *, speech_verb: Token | None = None) -> bool:
    """
    Return True if this advcl is a genuine scene-setting frame BEFORE speech —
    not a result/consequence clause AFTER speech, a participial speech-
    continuation marker, or a comparative clause.

    Audit-driven filters (2026-05-10):
    - Result-direction filter: when speech_verb precedes advcl in token order
      AND advcl's mark is in RESULT_MARK_LEMMAS, it's a result not a frame.
      Example: "I did speak many words ... that they were pacified" — frame
      direction is inverted.
    - Tightened aux:pass: passive participle alone isn't a scene frame; it's
      manner ("being filled with the Spirit"). Require ALSO a temporal/locative
      subordinator OR true absolute construction.

    Existing filters:
    - advcl lemma must not be in ADVCL_EXCLUDED_LEMMAS ("say" / "saying:")
    - "as if" comparative clauses excluded
    """
    if advcl.lemma in ADVCL_EXCLUDED_LEMMAS:
        return False

    # Check for a temporal/causal mark
    all_marks = [m for m in sent.dependents_of(advcl, deprel="mark")]
    mark_lemmas = {m.lemma.lower() for m in all_marks}

    # "as if" — comparative, not a scene frame
    if "as" in mark_lemmas and "if" in mark_lemmas:
        return False

    # Result-direction filter: if speech VERB precedes advcl AND mark is
    # result-introducing ("that"/"insomuch"/"until"), it's consequence not
    # frame. Skip.
    RESULT_MARK_LEMMAS = {"that", "insomuch", "until"}
    if speech_verb is not None and speech_verb.id < advcl.id:
        if mark_lemmas & RESULT_MARK_LEMMAS:
            return False

    if mark_lemmas & FRAME_MARK_LEMMAS:
        return True

    # Tightened aux:pass branch: passive participle alone is too permissive
    # (catches circumstantial-manner like "being filled with the Spirit").
    # Require either a temporal subordinator (already handled above) or a
    # true absolute construction (no shared subject — i.e., advcl has its
    # own nsubj that differs from the matrix).
    aux_pass = [a for a in sent.aux_of(advcl) if a.deprel == "aux:pass"]
    if aux_pass:
        # Check for own nsubj
        advcl_nsubj = sent.dependents_of(advcl, deprel="nsubj")
        if advcl_nsubj and speech_verb is not None:
            speech_nsubj = sent.dependents_of(speech_verb, deprel="nsubj")
            if speech_nsubj and advcl_nsubj[0].lemma != speech_nsubj[0].lemma:
                # True absolute: different subjects
                return True
        # Otherwise it's manner-circumstantial — not a frame
        return False

    return False


def _find_advcl_sibling(sent: Sentence, verb: Token) -> Token | None:  # noqa: ARG001 (used via closure)
    """
    Return the first genuine frame-advcl sibling of `verb` — a token whose
    head is the same as verb.head and whose deprel is "advcl", and which
    passes the _is_frame_advcl test.
    Also accepts a frame advcl that is a DIRECT DEPENDENT of verb (some
    parsers attach the frame advcl onto the speech verb rather than a shared
    parent).
    Returns None if none found.
    """
    # Case 1: advcl as a dependent of the speech verb
    for child in sent.dependents_of(verb, deprel="advcl"):
        if _is_frame_advcl(sent, child, speech_verb=verb):
            return child

    # Case 2: advcl as a sibling (shares the same head as the speech verb)
    if verb.head == 0:
        return None
    parent = sent.by_id(verb.head)
    if parent is None:
        return None
    for sib in sent.dependents_of(parent, deprel="advcl"):
        if sib.id != verb.id and _is_frame_advcl(sent, sib, speech_verb=verb):
            return sib
    return None


def scan_book(book_id: str) -> tuple[list[dict], list[dict]]:
    """Return (pass_instances, violations)."""
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    passes: list[dict] = []
    violations: list[dict] = []

    for sent in sentences:
        for verb in sent.find(upos="VERB", lemma_in=SPEECH_LEMMAS):
            # Condition (a): must have an nsubj dependent
            nsubj_list = sent.dependents_of(verb, deprel="nsubj")
            if not nsubj_list:
                continue

            # Condition (b): must have an advcl sibling or dependent
            advcl = _find_advcl_sibling(sent, verb)
            if advcl is None:
                continue

            # Map both to v2-mine lines
            verb_line = line_map.get((sent.sent_id, verb.id))
            advcl_line = line_map.get((sent.sent_id, advcl.id))
            if verb_line is None or advcl_line is None:
                continue

            nsubj = nsubj_list[0]
            nsubj_line = line_map.get((sent.sent_id, nsubj.id))

            record = {
                "book":       book_id,
                "sent_id":    sent.sent_id,
                "verb_form":  verb.form,
                "verb_lemma": verb.lemma,
                "verb_line":  verb_line,
                "advcl_line": advcl_line,
                "nsubj_form": nsubj.form,
                "nsubj_line": nsubj_line,
                "advcl_form": advcl.form,
            }

            if verb_line == advcl_line:
                # Speech verb merged with the advcl on the same line
                record["bucket"] = "STRONG-SPLIT-CANDIDATE"
                violations.append(record)
            else:
                # Speech verb already on a different line from the advcl
                record["bucket"] = "PASS"
                passes.append(record)

    return passes, violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_passes: list[dict] = []
    all_violations: list[dict] = []
    books_scanned = 0

    for bid in book_ids:
        try:
            p, v = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        books_scanned += 1
        all_passes.extend(p)
        all_violations.extend(v)
        if args.verbose:
            print(f"{bid}: {len(p)} pass, {len(v)} violations")

    total = len(all_passes) + len(all_violations)

    print("=" * 72)
    print("Rule 28 UD-query (Speech-Act Announcement After Frame) — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:              {books_scanned}")
    print(f"Speech+advcl instances:     {total}")
    print(f"  PASS (already split):     {len(all_passes)}")
    print(f"  STRONG-SPLIT-CANDIDATE:   {len(all_violations)}")
    print()

    if all_violations:
        print("STRONG-SPLIT-CANDIDATE instances (first 5):")
        print("-" * 72)
        for v in all_violations[:5]:
            print(f"  [{v['book']}] sent={v['sent_id']}")
            print(f"    speech verb: {v['verb_form']!r} (lemma={v['verb_lemma']}) "
                  f"line {v['verb_line']}")
            print(f"    advcl root:  {v['advcl_form']!r} line {v['advcl_line']}")
            print(f"    nsubj:       {v['nsubj_form']!r}")
        if len(all_violations) > 5:
            print(f"  ... +{len(all_violations) - 5} more")
        print()
    else:
        print("No STRONG-SPLIT-CANDIDATE instances found.")
        print()

    print("PASS instances (first 5):")
    print("-" * 72)
    for p in all_passes[:5]:
        print(f"  [{p['book']}] sent={p['sent_id']}")
        print(f"    speech verb: {p['verb_form']!r} (lemma={p['verb_lemma']}) "
              f"line {p['verb_line']}")
        print(f"    advcl root:  {p['advcl_form']!r} line {p['advcl_line']}")
        print(f"    nsubj:       {p['nsubj_form']!r}")
    if not all_passes:
        print("  (none detected)")
    print()

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
