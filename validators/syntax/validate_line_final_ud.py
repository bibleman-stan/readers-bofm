"""
Layer 1 line-final POS prohibitions — UD-query implementation.

Covers Rules 9, 11, 12, 13a from canon §3:

  Rule 9   line-final CCONJ                              [MALFORMED]
  Rule 11  line-final DET (article: the/a/an)            [MALFORMED]
  Rule 12  line-final AUX whose head VERB is on next line [MALFORMED]
  Rule 13a line-final ADP (case) whose head is on next line [MALFORMED]

Replaces validators/syntax/validate_line_final_tokens.py wordlist heuristics
with direct UPOS / DEPREL / head-line checks. Phrasal-verb particles
(DEPREL=compound:prt) and adverbs (UPOS=ADV) are naturally distinguished
from prepositions and so don't need an exception list.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths


ARTICLE_FORMS = {"the", "a", "an"}


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def all_tokens_by_line(sentences: list[Sentence], line_map: dict
                        ) -> dict[int, list[tuple[Sentence, Token]]]:
    """Return {v2_line_num: [(sent, tok) on that line, in (sent_id, tok_id) order]}.

    Aggregates across all sentences. This is essential for line-final
    detection: when line_mapping has minor anchor noise, a single v2-mine
    line may receive tokens from more than one parsed sentence, and the
    true line-final token is the global-last across all of them.
    """
    by_line: dict[int, list[tuple[Sentence, Token]]] = {}
    for sent in sentences:
        try:
            sent_id_int = int(sent.sent_id)
        except (ValueError, TypeError):
            sent_id_int = 0
        for tok in sent.tokens:
            ln = line_map.get((sent.sent_id, tok.id))
            if ln is None:
                continue
            by_line.setdefault(ln, []).append((sent_id_int, sent, tok))
    out: dict[int, list[tuple[Sentence, Token]]] = {}
    for ln, lst in by_line.items():
        lst.sort(key=lambda x: (x[0], x[2].id))
        out[ln] = [(s, t) for _, s, t in lst]
    return out


def last_content_pair(pairs: list[tuple[Sentence, Token]]
                      ) -> tuple[Sentence, Token] | None:
    for sent, t in reversed(pairs):
        if t.upos != "PUNCT":
            return (sent, t)
    return None


def _v2_lines(v2_path: Path) -> list[str]:
    with open(v2_path, encoding="utf-8") as f:
        return [line.rstrip() for line in f]


def _line_ends_with(v2_lines: list[str], line_num: int, form: str) -> bool:
    """Sanity check: does v2-mine line `line_num` actually end with `form`
    (after stripping trailing punctuation)?

    Guards against line_mapping drift artifacts where a token gets attributed
    to a v2-mine line whose actual content doesn't end with that form.
    """
    if line_num < 1 or line_num > len(v2_lines):
        return False
    line = v2_lines[line_num - 1]
    stripped = line.rstrip()
    while stripped and stripped[-1] in ',;:.!?"\'-':
        stripped = stripped[:-1]
    stripped = stripped.rstrip()
    if not stripped:
        return False
    parts = stripped.split()
    if not parts:
        return False
    return parts[-1].lower() == form.lower()


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)
    v2_lines = _v2_lines(v2_path)

    by_line = all_tokens_by_line(sentences, line_map)

    violations: list[dict] = []
    for line_num in sorted(by_line):
        pair = last_content_pair(by_line[line_num])
        if pair is None:
            continue
        sent, last = pair

        rule = None
        note = None

        if last.upos == "CCONJ":
            rule = "Rule 9"
            note = f"line-final CCONJ {last.form!r}"
        elif last.upos == "DET" and last.form.lower() in ARTICLE_FORMS:
            rule = "Rule 11"
            note = f"line-final article {last.form!r}"
        elif last.upos == "AUX":
            head = sent.head_of(last)
            if head is not None and head.upos == "VERB":
                head_line = line_map.get((sent.sent_id, head.id))
                # Require small line-gap to avoid line_mapping drift artifacts
                if head_line is not None and 0 < (head_line - line_num) <= 3:
                    rule = "Rule 12"
                    note = f"line-final AUX {last.form!r} (head VERB on line {head_line})"
        elif last.upos == "ADP" and last.deprel == "case":
            head = sent.head_of(last)
            if head is not None:
                head_line = line_map.get((sent.sent_id, head.id))
                if head_line is not None and 0 < (head_line - line_num) <= 3:
                    rule = "Rule 13a"
                    note = f"line-final ADP {last.form!r} (head {head.form!r} on line {head_line})"

        if rule is not None:
            # Verify against v2-mine ground truth — guards against
            # line_mapping drift artifacts.
            if not _line_ends_with(v2_lines, line_num, last.form):
                continue
            violations.append({
                "book": book_id,
                "rule": rule,
                "sent_id": sent.sent_id,
                "line": line_num,
                "note": note,
                "v2_path": str(v2_path),
            })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--rule", help="filter to one rule (e.g. 'Rule 9')")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_violations = []
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    if args.rule:
        all_violations = [v for v in all_violations if v["rule"] == args.rule]

    print("=" * 72)
    print("Layer 1 line-final POS UD-query — BofM corpus")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"MALFORMED:     {len(all_violations)}")
    print()

    by_rule: dict[str, list] = {}
    for v in all_violations:
        by_rule.setdefault(v["rule"], []).append(v)
    for rule in sorted(by_rule):
        items = by_rule[rule]
        print(f"--- {rule} ({len(items)}) ---")
        for v in items[:8]:
            print(f"  [{v['book']}] line {v['line']}: {v['note']}")
        if len(items) > 8:
            print(f"  ... +{len(items) - 8} more")
        print()

    print(f"RESULT: violations={len(all_violations)} malformed={len(all_violations)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
