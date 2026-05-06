#!/usr/bin/env python3
"""
Validate canon §1 M3 extension: bare trailing participial heads merge
with their matrix predication, with 4 structural guards + length backstop.

Canon source: private/01-method/colometry-canon.md, M3 extension subsection.

Each candidate line gets classified as:

  APPLY                — clean merge candidate (auto-apply OK)
  KEEP-stack           — adjacent rhetorical stack (≥3 OR ≥2 same lemma OR merged > 130c)
  KEEP-coord           — coordinate-list parallel beat
  KEEP-antecedent      — antecedent-locality fail (subject in PP / relative / fronted)
  KEEP-fronted         — participial precedes matrix verb
  REVIEW-length        — merged-line would exceed 130 characters

NOTE on retired carve-outs: A prior version had three editorial carve-outs
(KEEP-theological, KEEP-antithetic, KEEP-gerund) with hand-curated verse-
lists. Retired 2026-05-06 PM as a category fudge inconsistent with §0 Mission
objective (3). Cases that formerly fell into those classes are now classified
case-by-case on the atomic-thought test directly — some stay KEEP- via the
4 structural guards or REVIEW-length, others move to APPLY.

Usage:
    python3 validate_participial_phrases.py            # text summary
    python3 validate_participial_phrases.py --jsonl    # one JSON per candidate
    python3 validate_participial_phrases.py --class APPLY    # filter
    python3 validate_participial_phrases.py --book alma      # filter

Exit code: 0 always (this is a classifying validator, not a violation reporter
in the run_all baseline-check sense).
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "data" / "text-files" / "v2-mine"

PARTICIPIAL_VERBS = {
    "entering", "going", "having", "leaving", "coming", "standing", "looking",
    "saying", "hearing", "knowing", "crying", "preaching", "teaching", "fearing",
    "trusting", "running", "fleeing", "seeking", "finding", "holding", "carrying",
    "raising", "lifting", "bearing", "believing", "repenting", "laboring",
    "exhorting", "expounding", "baptizing", "admonishing", "supposing", "thinking",
    "speaking", "telling", "showing", "working", "doing", "being", "remembering",
    "trembling", "rejoicing", "weeping", "marvelling", "mourning", "gathering",
    "calling", "asking", "praying", "blessing", "cursing", "smiting", "slaying",
    "killing", "destroying", "building", "establishing", "preserving", "delivering",
    "saving", "casting", "throwing", "putting", "placing", "setting", "making",
    "giving", "taking", "receiving", "offering", "perceiving", "understanding",
    "forgetting", "loving", "hating", "desiring", "wishing", "willing", "wanting",
    "leading", "following", "feeding", "ruling", "judging", "passing", "departing",
    "returning", "approaching", "drawing", "fighting", "contending", "warring",
    "yielding", "submitting", "resisting", "trampling", "dwelling", "wandering",
    "abiding", "remaining", "tarrying", "waiting", "watching", "guarding",
    "keeping", "obeying", "serving", "worshipping", "ministering", "harkening",
    "hearkening", "beholding", "viewing", "gazing", "weighing", "considering",
    "discussing", "reasoning", "answering", "responding", "replying", "demanding",
    "requiring", "commanding", "charging", "bidding", "permitting", "suffering",
    "allowing", "needing", "lacking", "performing", "fulfilling", "accomplishing",
    "ending", "beginning", "starting", "stopping", "ceasing", "continuing",
    "persisting", "denying", "rejecting", "refusing", "accepting", "embracing",
    "spurning", "raging", "thundering", "lightening", "shining", "burning",
    "shaking", "hiding", "appearing", "vanishing", "moving", "sparing",
    "imparting", "succoring", "subjecting", "rebelling",
}

EXCLUDED_ING = {
    "concerning", "according", "notwithstanding", "during", "regarding",
    "respecting",
}

VERSE_RE = re.compile(r"^\s*(\d+):(\d+)\s*$")
LENGTH_CAP = 130


def is_participial_lead(line: str) -> tuple[bool, str]:
    stripped = line.strip()
    if not stripped:
        return False, ""
    raw = re.match(r"\s*([A-Za-z']+)", stripped)
    if not raw:
        return False, ""
    fw = raw.group(1)
    fwl = fw.lower()
    if not fwl.endswith("ing") or fwl in EXCLUDED_ING or fw[0].isupper():
        return False, ""
    if fwl not in PARTICIPIAL_VERBS:
        return False, ""
    return True, fwl


def get_verse_context(book_lines: list[str], idx: int) -> tuple[str, int, int]:
    marker_idx = -1
    for i in range(idx, -1, -1):
        m = VERSE_RE.match(book_lines[i])
        if m:
            marker_idx = i
            break
    if marker_idx == -1:
        return "", -1, -1
    end_idx = len(book_lines)
    for j in range(marker_idx + 1, len(book_lines)):
        if not book_lines[j].strip():
            end_idx = j
            break
        if VERSE_RE.match(book_lines[j]):
            end_idx = j
            break
    m = VERSE_RE.match(book_lines[marker_idx])
    return f"{m.group(1)}:{m.group(2)}", marker_idx, end_idx


def participials_in_verse(book_lines: list[str], marker_idx: int, end_idx: int) -> list[tuple[int, str]]:
    out = []
    for i in range(marker_idx + 1, end_idx):
        ok, fw = is_participial_lead(book_lines[i])
        if ok:
            out.append((i, fw))
    return out


def book_id_from_filename(filepath: Path) -> str:
    stem = filepath.stem
    m = re.match(r"\d+-(.+?)-2020-sb-v2", stem)
    if not m:
        return stem
    raw = m.group(1)
    return {
        "1_nephi": "1nephi", "2_nephi": "2nephi", "3_nephi": "3nephi",
        "4_nephi": "4nephi", "jacob": "jacob", "enos": "enos", "jarom": "jarom",
        "omni": "omni", "words_of_mormon": "words-of-mormon", "mosiah": "mosiah",
        "alma": "alma", "helaman": "helaman", "mormon": "mormon",
        "ether": "ether", "moroni": "moroni",
    }.get(raw, raw)


# Antecedent-locality heuristic: tightened 2026-05-06 after over-flagging.
# Only fires on patterns where the PP genuinely supplies the participial's
# antecedent — not on routine locative/temporal/manner PPs.
#
# Pattern A: "concerning <name-or-person-NP>" — audit's canonical example
#   (Ether 13:21, 3 Ne 3:11). The "concerning"-PP introduces the topic that
#   the following participial then describes; the participial inherits FROM
#   the concerning-NP, not from the matrix subject.
# Pattern B: "<which|who|whom> ... <verb>" in the prev line, suggesting the
#   participial subject is the relative clause's subject, not the matrix.
OBLIQUE_PREV_RE = re.compile(
    r"\bconcerning\s+(?:[A-Z]\w+(?:\s+\w+){0,3}|the\s+\w+(?:\s+\w+){0,3}|his\s+\w+|their\s+\w+)[,;]?\s*$",
    re.IGNORECASE,
)
RELATIVE_PREV_RE = re.compile(r"\b(?:which|who|whom)\s+\w+\s+\w+", re.IGNORECASE)
FRONTED_NEXT_RE = re.compile(r"^\s*(?:therefore|wherefore|then|thus)\b", re.IGNORECASE)


def is_coord_list(book_lines: list[str], idx: int, marker_idx: int) -> bool:
    if idx - marker_idx < 3:
        return False
    p1, p2 = idx - 1, idx - 2
    if p2 <= marker_idx:
        return False
    ok1, _ = is_participial_lead(book_lines[p1])
    ok2, _ = is_participial_lead(book_lines[p2])
    if not (ok1 and ok2):
        return False
    if not (book_lines[p1].rstrip().endswith(",") and book_lines[p2].rstrip().endswith(",")):
        return False
    return True


def merged_length(prev_line: str, line: str) -> int:
    return len(prev_line.rstrip()) + 1 + len(line.strip())


def classify(book_lines: list[str], idx: int, fw: str, book_id: str) -> tuple[str, str]:
    line = book_lines[idx]
    prev_line = book_lines[idx - 1].rstrip() if idx > 0 else ""
    next_line = book_lines[idx + 1].rstrip() if idx + 1 < len(book_lines) else ""

    verse_ref, marker_idx, end_idx = get_verse_context(book_lines, idx)
    chap, verse = (None, None)
    if verse_ref:
        try:
            cs, vs = verse_ref.split(":")
            chap, verse = int(cs), int(vs)
        except ValueError:
            pass

    # Stack-cap (verse-context-extended)
    in_verse = participials_in_verse(book_lines, marker_idx, end_idx)
    if len(in_verse) >= 3:
        return "KEEP-stack", f"verse depth N={len(in_verse)} adjacent participials"
    if len(in_verse) >= 2:
        lemmas = [lem for _, lem in in_verse]
        for lem in lemmas:
            if lemmas.count(lem) >= 2:
                return "KEEP-stack", f"verse has N>=2 with same -ing lemma '{lem}'"

    # Length cap
    if merged_length(prev_line, line) > LENGTH_CAP:
        return "REVIEW-length", f"merged-line {merged_length(prev_line, line)} chars > {LENGTH_CAP}"

    # Coord-list guard
    if is_coord_list(book_lines, idx, marker_idx):
        return "KEEP-coord", "prev 2+ participial-fronted comma-ending lines"

    # Fronted-position guard
    if FRONTED_NEXT_RE.match(next_line):
        return "KEEP-fronted", f"next line starts with discourse particle: '{next_line[:40]}'"

    # Antecedent-locality guard
    if OBLIQUE_PREV_RE.search(prev_line):
        return "KEEP-antecedent", f"prev ends with oblique-NP: '...{prev_line[-50:]}'"
    if RELATIVE_PREV_RE.search(prev_line) and len(prev_line) < 80:
        return "KEEP-antecedent", f"prev contains relative pattern: '...{prev_line[-50:]}'"

    return "APPLY", "subject-inheriting bare participial — merge with matrix"


def scan_book(filepath: Path) -> list[dict]:
    book_id = book_id_from_filename(filepath)
    with open(filepath, encoding="utf-8") as f:
        lines = f.read().split("\n")
    candidates = []
    for idx, line in enumerate(lines):
        ok, fw = is_participial_lead(line)
        if not ok:
            continue
        verse_ref, _, _ = get_verse_context(lines, idx)
        cls, reason = classify(lines, idx, fw, book_id)
        prev_line = lines[idx - 1].strip() if idx > 0 else ""
        next_line = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
        candidates.append({
            "book": book_id,
            "file_line": idx + 1,
            "verse": verse_ref,
            "class": cls,
            "reason": reason,
            "first_word": fw,
            "line": line.strip(),
            "prev_line": prev_line,
            "next_line": next_line,
            "merged_length": merged_length(prev_line, line),
        })
    return candidates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", action="store_true")
    ap.add_argument("--class", dest="cls", default=None)
    ap.add_argument("--book", default=None)
    args = ap.parse_args()

    all_candidates = []
    for filepath in sorted(CORPUS_DIR.glob("*.txt")):
        all_candidates.extend(scan_book(filepath))

    if args.cls:
        all_candidates = [c for c in all_candidates if c["class"] == args.cls]
    if args.book:
        all_candidates = [c for c in all_candidates if c["book"] == args.book]

    if args.jsonl:
        for c in all_candidates:
            print(json.dumps(c, ensure_ascii=False))
        return 0

    print("=" * 76)
    print("M3 extension validator -- bare trailing participials")
    print("=" * 76)
    print()
    counts = {}
    for c in all_candidates:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    total = len(all_candidates)
    print(f"Total candidates: {total}")
    print()
    print("By class:")
    classes_order = (
        "APPLY", "KEEP-stack", "KEEP-coord", "KEEP-antecedent",
        "KEEP-fronted", "REVIEW-length",
    )
    for cls in classes_order:
        n = counts.get(cls, 0)
        pct = (n / total * 100) if total else 0
        print(f"  {cls:20}  {n:5}  ({pct:5.1f}%)")
    print()

    by_book = {}
    for c in all_candidates:
        by_book.setdefault(c["book"], 0)
        by_book[c["book"]] += 1
    print("By book:")
    for book in sorted(by_book.keys()):
        print(f"  {book:18}  {by_book[book]:4}")
    print()

    apply_count = counts.get("APPLY", 0)
    review_count = counts.get("REVIEW-length", 0)
    keep_count = sum(counts.get(c, 0) for c in classes_order if c.startswith("KEEP"))
    print(f"Mechanical-apply candidates: {apply_count}")
    print(f"Stay-own-line via carve-outs: {keep_count}")
    print(f"REVIEW-required:              {review_count}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
