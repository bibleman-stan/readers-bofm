"""Parity test: compare regex vs UD detector outputs for the same rule.

For each paired rule, normalise both detectors' findings to (book, line_num)
sets and compute the set-difference, telling us:
  - regex_only  : regex flags but UD does not (possible regex FPs or UD FNs)
  - ud_only     : UD flags but regex does not (possible regex FNs or UD FPs)
  - shared      : both agree

"Flags" means STRONG-actionable output only — REVIEW-REQUIRED items in the UD
detector are surfaced separately in the reconcile section because they sit in
an intentional adjudication bucket, not a miss.

Usage:
    python validators/parity/parity_test.py
    python validators/parity/parity_test.py --rule rule_17
    python validators/parity/parity_test.py --rule rule_17 --verbose
    python validators/parity/parity_test.py --verbose
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow running from repo root or validators/parity/
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Parity pairs registry
# ---------------------------------------------------------------------------
# Each entry: (rule_name, description)
# The actual extraction logic is implemented per-rule in the extractor
# functions below, keyed by rule_name.
PARITY_PAIRS = [
    ("rule_17",            "Complement Integrity"),
    ("rule_18",            "Fixed Idiom Integrity"),
    ("rule_19",            "Anaphoric Relative"),
    ("rule_27",            "Insomuch That Binding"),
    ("rule_28",            "Speech-Act After Frame"),
    ("severed_complement", "Severed Complement-Spanning-Frame"),
]

V2_DIR = REPO / "data" / "text-files" / "v2-mine"

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


# ---------------------------------------------------------------------------
# Utility: map v2-mine filename -> book id
# ---------------------------------------------------------------------------
def _filename_to_book(filename: str) -> str:
    """Convert a v2-mine filename like '04-enos-2020-sb-v2.txt' -> 'enos'.
    Also handles '01-1_nephi-2020-sb-v2.txt' -> '1nephi'."""
    # Strip extension and known suffix
    stem = filename
    for suffix in ["-2020-sb-v2.txt", "-2020-sb-v2", ".txt"]:
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    # Remove leading NN- prefix
    stem = re.sub(r"^\d+-", "", stem)
    # Remove trailing -sb if present
    stem = re.sub(r"-sb$", "", stem)
    # Normalise: 1_nephi -> 1nephi, words_of_mormon -> words-of-mormon
    stem = stem.replace("_", "-")
    # But digit-initial: 1-nephi -> 1nephi (no hyphen after digit)
    stem = re.sub(r"^(\d)-", r"\1", stem)
    return stem


def _v2_filename_for_book(book_id: str) -> str | None:
    """Return the v2-mine filename for a book id, or None if not found."""
    v2_id = book_id.replace("-", "_")
    if v2_id and v2_id[0].isdigit():
        v2_id = v2_id[0] + "_" + v2_id[1:]
        v2_id = v2_id.replace("__", "_")
    matches = sorted(V2_DIR.glob(f"*{v2_id}-2020-sb-v2.txt"))
    return matches[0].name if matches else None


def normalize_findings(findings: list[dict], *, book_key="book", line_key: str) -> set[tuple]:
    """Convert a list of finding dicts to {(book, line_num)} set.

    Args:
        findings: list of dicts with at least book_key and line_key fields.
        book_key: dict key for the book identifier.
        line_key: dict key for the line number.
    """
    result: set[tuple] = set()
    for f in findings:
        book = f.get(book_key)
        line = f.get(line_key)
        if book and line is not None:
            result.add((book, int(line)))
    return result


# ---------------------------------------------------------------------------
# Regex extractor helpers
# ---------------------------------------------------------------------------

def _scan_all_regex_files(scan_file_fn, *, filter_fn=None) -> list[dict]:
    """Run scan_file_fn on every v2-mine file; optionally filter results."""
    findings = []
    for path in sorted(V2_DIR.glob("*-v2.txt")):
        results = scan_file_fn(path)
        if filter_fn is not None:
            results = [r for r in results if filter_fn(r)]
        for r in results:
            r["_book"] = _filename_to_book(path.name)
        findings.extend(results)
    return findings


def _scan_all_ud_books(scan_book_fn) -> list[dict]:
    """Run scan_book_fn on every book; collect results, skip FileNotFoundError."""
    findings = []
    for book_id in BOOKS:
        try:
            results = scan_book_fn(book_id)
        except FileNotFoundError:
            continue
        # scan_book_fn may return a tuple (passes, violations) for rule_28
        if isinstance(results, tuple):
            results = results[1]  # take only violations
        findings.extend(results)
    return findings


# ---------------------------------------------------------------------------
# Per-rule extraction
# ---------------------------------------------------------------------------

# ---- Rule 17 ----

def _extract_rule_17():
    from validators.colometry.validate_rule_17_complement_integrity import scan_file as regex_scan
    from validators.colometry.validate_rule_17_ud import scan_book as ud_scan

    regex_raw = _scan_all_regex_files(regex_scan)
    # Regex emits all violations (no buckets); line_num is the governing-verb line
    regex_set = {(r["_book"], int(r["line_num"])) for r in regex_raw}

    ud_raw = _scan_all_ud_books(ud_scan)
    # UD: STRONG-MERGE-CANDIDATE items — use head_line (governing verb line)
    ud_strong = [v for v in ud_raw if v.get("bucket") == "STRONG-MERGE-CANDIDATE"]
    ud_review = [v for v in ud_raw if v.get("bucket") == "REVIEW-REQUIRED"]
    ud_strong_set = normalize_findings(ud_strong, line_key="head_line")
    ud_review_set = normalize_findings(ud_review, line_key="head_line")

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---- Rule 18 ----

def _extract_rule_18():
    from validators.colometry.validate_rule_18_fixed_idioms import scan_file as regex_scan
    from validators.colometry.validate_rule_18_ud import scan_book as ud_scan

    regex_raw = _scan_all_regex_files(regex_scan)
    # Regex: start_line_num is where the idiom begins
    regex_set = {(r["_book"], int(r["start_line_num"])) for r in regex_raw}

    ud_raw = _scan_all_ud_books(ud_scan)
    ud_strong = [v for v in ud_raw if v.get("bucket") == "STRONG-MERGE-CANDIDATE"]
    ud_review = [v for v in ud_raw if v.get("bucket") == "REVIEW-REQUIRED"]
    ud_strong_set = normalize_findings(ud_strong, line_key="line_min")
    ud_review_set = normalize_findings(ud_review, line_key="line_min")

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---- Rule 19 ----

def _extract_rule_19():
    from validators.colometry.validate_rule_19_anaphoric_relative import scan_file as regex_scan
    from validators.colometry.validate_rule_19_ud import scan_book as ud_scan

    # Regex: line_num is the NP-anchor line (line N, the head-noun line)
    # Only flag STRONG-MERGE and STRONG-MERGE-PREDICATIVE-IDENTIFIER as
    # the regex equivalent of UD's STRONG-MERGE bucket.
    STRONG_CATEGORIES = {"STRONG-MERGE", "STRONG-MERGE-PREDICATIVE-IDENTIFIER"}
    regex_raw_all = _scan_all_regex_files(regex_scan)
    regex_raw = [r for r in regex_raw_all if r.get("category") in STRONG_CATEGORIES]
    regex_review_raw = [r for r in regex_raw_all if r.get("category") == "REVIEW-REQUIRED"]

    # line_num in regex is the NP line (line N). UD's head_line is the head noun line.
    # They should align.
    regex_set = {(r["_book"], int(r["line_num"])) for r in regex_raw}

    ud_raw = _scan_all_ud_books(ud_scan)
    # UD STRONG-MERGE = anaphoric head on different lines → merge
    ud_strong = [v for v in ud_raw if v.get("bucket") == "STRONG-MERGE"]
    ud_review = [v for v in ud_raw if v.get("bucket") == "REVIEW-REQUIRED"]
    # head_line = the line the head noun is on
    ud_strong_set = normalize_findings(ud_strong, line_key="head_line")
    ud_review_set = normalize_findings(ud_review, line_key="head_line")

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---- Rule 27 ----

def _extract_rule_27():
    from validators.colometry.validate_rule_27_insomuch_that import scan_file as regex_scan
    from validators.colometry.validate_rule_27_ud import scan_book as ud_scan

    # Regex: line_num is the line where "insomuch that" appears.
    # Only STRONG-MERGE-CANDIDATE instances have actionable merge advice.
    regex_raw_all = _scan_all_regex_files(regex_scan)
    regex_raw = [r for r in regex_raw_all if r.get("category") == "STRONG-MERGE-CANDIDATE"]
    regex_review_raw = [r for r in regex_raw_all if r.get("category") == "REVIEW-REQUIRED"]
    regex_set = {(r["_book"], int(r["line_num"])) for r in regex_raw}

    ud_raw = _scan_all_ud_books(ud_scan)
    ud_strong = [v for v in ud_raw if v.get("bucket") == "STRONG-MERGE-CANDIDATE"]
    ud_review = [v for v in ud_raw if v.get("bucket") == "REVIEW-REQUIRED"]
    # mark_line = where the "insomuch" token sits
    ud_strong_set = normalize_findings(ud_strong, line_key="mark_line")
    ud_review_set = normalize_findings(ud_review, line_key="mark_line")

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---- Rule 28 ----

def _extract_rule_28():
    from validators.colometry.validate_rule_28_speech_act_after_frame import scan_file as regex_scan
    from validators.colometry.validate_rule_28_ud import scan_book as ud_scan

    # Regex: scan_file returns (pass_instances, violations). We want violations.
    def _regex_scan_violations(path):
        _passes, violations = regex_scan(path)
        return violations

    regex_raw = _scan_all_regex_files(_regex_scan_violations)
    # Regex violations: line_num is the line with both frame+speech-verb merged
    regex_set = {(r["_book"], int(r["line_num"])) for r in regex_raw}

    ud_raw_raw = _scan_all_ud_books(ud_scan)
    # Note: scan_book for rule_28 returns (passes, violations) tuple — handled in _scan_all_ud_books
    ud_strong = [v for v in ud_raw_raw if v.get("bucket") == "STRONG-SPLIT-CANDIDATE"]
    ud_review: list[dict] = []  # Rule 28 UD has no REVIEW bucket
    # verb_line = where the speech verb is (the merged line)
    ud_strong_set = normalize_findings(ud_strong, line_key="verb_line")
    ud_review_set: set[tuple] = set()

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---- Severed Complement ----

def _extract_severed_complement():
    from validators.colometry.validate_severed_complement import scan_file as regex_scan
    from validators.colometry.validate_severed_complement_ud import scan_book as ud_scan

    regex_raw = _scan_all_regex_files(regex_scan)
    # Regex: line_num is line N (the "that when/after/..." line)
    regex_set = {(r["_book"], int(r["line_num"])) for r in regex_raw}

    ud_raw = _scan_all_ud_books(ud_scan)
    ud_strong = [v for v in ud_raw if v.get("bucket") == "STRONG-MERGE-CANDIDATE"]
    ud_review = [v for v in ud_raw if v.get("bucket") == "REVIEW-REQUIRED"]
    # advcl_line = where the frame (advcl) sits — corresponds to regex's line N
    ud_strong_set = normalize_findings(ud_strong, line_key="advcl_line")
    ud_review_set = normalize_findings(ud_review, line_key="advcl_line")

    return regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review


# ---------------------------------------------------------------------------
# Extractor dispatch
# ---------------------------------------------------------------------------

EXTRACTORS = {
    "rule_17":            _extract_rule_17,
    "rule_18":            _extract_rule_18,
    "rule_19":            _extract_rule_19,
    "rule_27":            _extract_rule_27,
    "rule_28":            _extract_rule_28,
    "severed_complement": _extract_severed_complement,
}


# ---------------------------------------------------------------------------
# Parity computation
# ---------------------------------------------------------------------------

def parity_for_rule(rule_name: str) -> dict:
    """Compute parity metrics for a single rule.

    Returns dict with keys:
      regex_total, ud_total, shared, regex_only, ud_only,
      ud_review_set (items UD put in REVIEW that regex flagged as strong),
      regex_raw, ud_strong, ud_review
    """
    extractor = EXTRACTORS[rule_name]
    regex_set, ud_strong_set, ud_review_set, regex_raw, ud_strong, ud_review = extractor()

    shared = regex_set & ud_strong_set
    regex_only = regex_set - ud_strong_set
    ud_only = ud_strong_set - regex_set

    # Of regex_only, how many did UD put in REVIEW (not a hard miss — UD saw
    # it but was uncertain)?
    regex_in_ud_review = regex_only & ud_review_set

    return {
        "regex_total": len(regex_set),
        "ud_total": len(ud_strong_set),
        "ud_review_total": len(ud_review_set),
        "shared": shared,
        "regex_only": regex_only,
        "ud_only": ud_only,
        "regex_in_ud_review": regex_in_ud_review,
        # raw data for verbose output
        "regex_raw": regex_raw,
        "ud_strong": ud_strong,
        "ud_review": ud_review,
    }


# ---------------------------------------------------------------------------
# Retirement-readiness verdict
# ---------------------------------------------------------------------------

def retirement_verdict(result: dict) -> str:
    """Return a per-rule verdict string."""
    regex_only = result["regex_only"]
    regex_in_review = result["regex_in_ud_review"]
    hard_misses = regex_only - regex_in_review   # regex-only AND not in UD review

    if result["regex_total"] == 0 and result["ud_total"] == 0:
        return "N/A (both detectors found 0)"

    if len(hard_misses) == 0 and len(regex_only) == 0:
        return "READY-TO-RETIRE-REGEX  (UD covers all regex findings)"

    if len(hard_misses) == 0 and len(regex_only) > 0:
        # Regex-only items are all in UD's review bucket — UD saw them, chose adjudication
        return (
            f"READY-TO-RETIRE-REGEX  ({len(regex_only)} regex-only "
            f"items all in UD REVIEW-REQUIRED bucket)"
        )

    if len(hard_misses) <= 3:
        return (
            f"INVESTIGATE  ({len(hard_misses)} hard misses — "
            f"regex finds cases UD neither flags strong nor reviews)"
        )

    return (
        f"INVESTIGATE  ({len(hard_misses)} hard misses, "
        f"{len(regex_only)} regex-only total — UD has significant coverage gaps)"
    )


# ---------------------------------------------------------------------------
# Verbose sample helpers
# ---------------------------------------------------------------------------

def _sample_regex_only(regex_only_set: set, regex_raw: list, n: int = 5) -> list[str]:
    """Return up to n human-readable lines for the regex-only set."""
    lines = []
    for book, line_num in sorted(regex_only_set)[:n]:
        # Find matching raw entry for context
        ctx = next(
            (r for r in regex_raw
             if r.get("_book") == book and int(r.get("line_num", r.get("start_line_num", 0))) == line_num),
            None,
        )
        if ctx:
            snippet = (ctx.get("line") or ctx.get("cur") or ctx.get("matched_text") or "")[:70]
            lines.append(f"    ({book}, {line_num})  {snippet!r}")
        else:
            lines.append(f"    ({book}, {line_num})")
    return lines


def _sample_ud_only(ud_only_set: set, ud_strong: list, rule_name: str, n: int = 5) -> list[str]:
    """Return up to n human-readable lines for the UD-only set."""
    lines = []
    # Pick a reasonable line_key per rule
    lk_map = {
        "rule_17": "head_line",
        "rule_18": "line_min",
        "rule_19": "head_line",
        "rule_27": "mark_line",
        "rule_28": "verb_line",
        "severed_complement": "advcl_line",
    }
    lk = lk_map.get(rule_name, "head_line")
    for book, line_num in sorted(ud_only_set)[:n]:
        ctx = next(
            (v for v in ud_strong
             if v.get("book") == book and v.get(lk) == line_num),
            None,
        )
        if ctx:
            # Try to get a readable snippet from the finding (field names vary by rule)
            snippet = (
                ctx.get("sent_text")
                or ctx.get("sequence")
                or ctx.get("head_form")
                or ctx.get("verb_form")
                or ctx.get("governor_form")
                or ctx.get("matrix_form")
                or ctx.get("rel_root_form")
                or ""
            )[:70]
            lines.append(f"    ({book}, {line_num})  {snippet!r}")
        else:
            lines.append(f"    ({book}, {line_num})")
    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", help="single rule (e.g. rule_17); default: all")
    ap.add_argument("--verbose", action="store_true",
                    help="show sample items from each diff bucket")
    args = ap.parse_args()

    pairs = [(name, desc) for name, desc in PARITY_PAIRS
             if not args.rule or name == args.rule]

    if not pairs:
        print(f"ERROR: unknown rule {args.rule!r}. "
              f"Choose from: {[n for n, _ in PARITY_PAIRS]}")
        return 2

    print("=" * 72)
    print("Regex vs UD parity report")
    print("=" * 72)

    verdicts: list[tuple[str, str]] = []

    for rule_name, description in pairs:
        print(f"\n{'=' * 72}")
        print(f"  {rule_name}  —  {description}")
        print(f"{'=' * 72}")

        try:
            result = parity_for_rule(rule_name)
        except Exception as exc:
            print(f"  ERROR running extractor: {exc}")
            import traceback
            traceback.print_exc()
            verdicts.append((rule_name, f"ERROR: {exc}"))
            continue

        print(f"  regex strong-actionable : {result['regex_total']}")
        print(f"  UD strong-actionable    : {result['ud_total']}")
        print(f"  UD REVIEW-REQUIRED      : {result['ud_review_total']}")
        print(f"  shared                  : {len(result['shared'])}")
        print(f"  regex-only (strong)     : {len(result['regex_only'])}")
        print(f"    of which in UD REVIEW : {len(result['regex_in_ud_review'])}")
        print(f"    hard misses (neither) : {len(result['regex_only'] - result['regex_in_ud_review'])}")
        print(f"  ud-only                 : {len(result['ud_only'])}")

        verdict = retirement_verdict(result)
        print(f"\n  VERDICT: {verdict}")
        verdicts.append((rule_name, verdict))

        if args.verbose:
            regex_only = result["regex_only"]
            ud_only = result["ud_only"]

            if regex_only:
                print(f"\n  -- REGEX-ONLY sample (up to 5 of {len(regex_only)}) --")
                for ln in _sample_regex_only(regex_only, result["regex_raw"]):
                    print(ln)
                # Also show how many overlap with UD REVIEW
                in_review = result["regex_in_ud_review"]
                if in_review:
                    print(f"\n  -- REGEX-ONLY also in UD REVIEW sample (up to 5 of {len(in_review)}) --")
                    for ln in _sample_regex_only(in_review, result["regex_raw"]):
                        print("   [also-in-UD-REVIEW]", ln.strip())

            if ud_only:
                print(f"\n  -- UD-ONLY sample (up to 5 of {len(ud_only)}) --")
                for ln in _sample_ud_only(ud_only, result["ud_strong"], rule_name):
                    print(ln)

    # Summary table
    print(f"\n{'=' * 72}")
    print("RETIREMENT-READINESS SUMMARY")
    print(f"{'=' * 72}")
    for rule_name, verdict in verdicts:
        print(f"  {rule_name:<22}  {verdict}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
