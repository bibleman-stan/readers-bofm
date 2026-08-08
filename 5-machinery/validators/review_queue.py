"""
Review-queue aggregator for BofM Reader colometry validators.

Collects all REVIEW-REQUIRED items from every UD-query detector and writes
a dated markdown report to private/review-queue/YYYY-MM-DD-review-queue.md.

Usage:
    python 5-machinery/validators/review_queue.py
    python 5-machinery/validators/review_queue.py --detector rule_06
    python 5-machinery/validators/review_queue.py --out /tmp/my-queue.md

Return value: 0 always (aggregator, not a pass/fail checker).
"""
from __future__ import annotations

import argparse
import importlib
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Allow running from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# ---------------------------------------------------------------------------
# Detector registry
# Each entry:  (module_path, short_name, return_style)
#
#   return_style:
#     "list"  — scan_book returns list[dict]; filter by bucket field containing "REVIEW"
#     "tuple" — scan_book returns (strong_list, review_list); second element is review
#
# Detectors with NO REVIEW output are omitted:
#   rule_01, rule_16, rule_21, rule_28 (only STRONG/PASS buckets)
#   compound_coord, validate_line_final, validate_rule_20 (only STRONG/MALFORMED)
# ---------------------------------------------------------------------------
DETECTORS: list[tuple[str, str, str]] = [
    # (module_path, short_name, return_style)
    ("validators.colometry.validate_rule_05_ud",                   "rule_05",            "list"),
    ("validators.colometry.validate_rule_06_ud",                   "rule_06",            "list"),
    ("validators.colometry.validate_rule_07_ud",                   "rule_07",            "tuple"),
    ("validators.colometry.validate_rule_10_ud",                   "rule_10",            "tuple"),
    ("validators.colometry.validate_rule_17_ud",                   "rule_17",            "list"),
    ("validators.colometry.validate_rule_18_ud",                   "rule_18",            "list"),
    ("validators.colometry.validate_rule_19_ud",                   "rule_19",            "list"),
    ("validators.colometry.validate_rule_23_ud",                   "rule_23",            "list"),
    ("validators.colometry.validate_rule_26_ud",                   "rule_26",            "list"),
    ("validators.colometry.validate_rule_27_ud",                   "rule_27",            "list"),
    ("validators.colometry.validate_polysyndetic_verb_chain_ud",   "polysyndetic_chain", "tuple"),
    ("validators.colometry.validate_severed_complement_ud",        "severed_complement", "list"),
    ("validators.colometry.validate_frame_predication_merges_ud",  "frame_pred_merges",  "list"),
]


def _is_review(item: dict) -> bool:
    """Return True if this finding is in the REVIEW bucket."""
    bucket = item.get("bucket", "")
    return "REVIEW" in str(bucket).upper()


def _extract_review(result, return_style: str) -> list[dict]:
    """Extract review items from a scan_book result."""
    if return_style == "tuple":
        if not isinstance(result, tuple) or len(result) < 2:
            return []
        return list(result[1])
    else:
        if not isinstance(result, list):
            return []
        return [item for item in result if _is_review(item)]


def _group_key(item: dict) -> str:
    """Return a grouping label for the item (skip_reason or review_reason or bucket)."""
    for field in ("skip_reason", "review_reason"):
        val = item.get(field)
        if val:
            return str(val)
    bucket = item.get("bucket", "REVIEW-REQUIRED")
    return str(bucket)


def _format_item(item: dict) -> str:
    """Format one review item as a markdown list line."""
    book = item.get("book", "?")
    sent_id = item.get("sent_id", "?")

    # Build a compact summary from the most informative fields per detector type
    parts: list[str] = [f"[{book}]", f"sent={sent_id}"]

    # Line numbers
    for line_field in ("line", "head_line", "matrix_line", "part_line", "verb_line",
                        "first_line", "frame_line", "advcl_line", "line_min"):
        val = item.get(line_field)
        if val is not None:
            parts.append(f"line {val}")
            break

    # Token forms
    for form_field in ("head_form", "matrix_form", "part_form", "verb_form",
                        "first_conjunct_form", "governor_form", "frame_form"):
        val = item.get(form_field)
        if val is not None:
            parts.append(f"{form_field.replace('_form', '')}={val!r}")
            break

    # Secondary form / context
    for secondary in ("obj_form", "advcl_form", "second_conjunct_form", "mark_lemma",
                        "modal", "idiom", "formula_type", "pattern"):
        val = item.get(secondary)
        if val is not None:
            parts.append(f"{secondary}={val!r}")
            break

    # Numeric context
    for num_field in ("combined_size", "rc_words", "first_size", "second_size",
                        "line_gap", "obj_line", "mark_line", "rel_line"):
        val = item.get(num_field)
        if val is not None:
            label = num_field.replace("_", "-")
            parts.append(f"{label}={val}")
            break

    # Subject continuity (rule_27)
    subj = item.get("subj_continuity")
    if subj:
        parts.append(f"subj={subj}")

    return "- " + ", ".join(parts)


def run_detector(
    module_path: str,
    short_name: str,
    return_style: str,
    book_filter: str | None = None,
) -> tuple[list[dict], list[str]]:
    """Run one detector across all books. Returns (review_items, error_messages)."""
    review_items: list[dict] = []
    errors: list[str] = []

    try:
        mod = importlib.import_module(module_path)
    except ImportError as e:
        errors.append(f"  ImportError loading {module_path}: {e}")
        return review_items, errors

    if not hasattr(mod, "scan_book"):
        errors.append(f"  {module_path} has no scan_book function — skipped")
        return review_items, errors

    book_ids = [book_filter] if book_filter else BOOKS

    for book_id in book_ids:
        try:
            result = mod.scan_book(book_id)
        except FileNotFoundError:
            # Book data not available — skip silently
            continue
        except Exception as e:
            errors.append(f"  [{book_id}] {short_name} raised {type(e).__name__}: {e}")
            continue

        items = _extract_review(result, return_style)
        review_items.extend(items)

    return review_items, errors


def build_report(
    detector_results: list[tuple[str, list[dict], list[str]]],
    generated_at: str,
    date_str: str,
) -> str:
    """Build the full markdown report string."""
    total = sum(len(items) for _, items, _ in detector_results)

    lines: list[str] = [
        f"# Review Queue — {date_str}",
        "",
        f"Generated by `5-machinery/validators/review_queue.py` at {generated_at}.",
        f"Total REVIEW items across detectors: **{total}**",
        "",
    ]

    # Collect all errors across detectors
    all_errors: list[str] = []
    for _, _, errs in detector_results:
        all_errors.extend(errs)

    if all_errors:
        lines.append("## Load / Runtime Errors")
        lines.append("")
        for err in all_errors:
            lines.append(f"- {err.strip()}")
        lines.append("")

    for det_name, items, _ in detector_results:
        if not items:
            continue

        lines.append(f"## {det_name} — {len(items)} item{'s' if len(items) != 1 else ''}")
        lines.append("")

        # Group by skip_reason / review_reason / bucket
        groups: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            key = _group_key(item)
            groups[key].append(item)

        for group_key in sorted(groups):
            group_items = groups[group_key]
            lines.append(f"### {group_key} — {len(group_items)}")
            lines.append("")
            for item in group_items:
                lines.append(_format_item(item))
            lines.append("")

    # Summary table at the end
    lines.append("---")
    lines.append("")
    lines.append("## Summary by Detector")
    lines.append("")
    lines.append("| Detector | REVIEW items |")
    lines.append("|----------|-------------|")
    for det_name, items, _ in detector_results:
        lines.append(f"| {det_name} | {len(items)} |")
    lines.append(f"| **Total** | **{total}** |")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--detector", "-d",
        metavar="NAME",
        help="Restrict to one detector short name (e.g. rule_06)",
    )
    ap.add_argument(
        "--book", "-b",
        metavar="BOOK_ID",
        help="Restrict to one book (e.g. 1nephi)",
    )
    ap.add_argument(
        "--out", "-o",
        metavar="PATH",
        help="Override output path (default: private/review-queue/YYYY-MM-DD-review-queue.md)",
    )
    ap.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output to stderr",
    )
    args = ap.parse_args()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S")

    # Resolve output path
    if args.out:
        out_path = Path(args.out)
    else:
        queue_dir = REPO_ROOT / "private" / "review-queue"
        queue_dir.mkdir(parents=True, exist_ok=True)
        out_path = queue_dir / f"{date_str}-review-queue.md"

    # Select detectors to run
    detectors = DETECTORS
    if args.detector:
        detectors = [(mp, sn, rs) for mp, sn, rs in DETECTORS if sn == args.detector]
        if not detectors:
            print(f"Error: unknown detector {args.detector!r}", file=sys.stderr)
            known = ", ".join(sn for _, sn, _ in DETECTORS)
            print(f"Known detectors: {known}", file=sys.stderr)
            return 1

    detector_results: list[tuple[str, list[dict], list[str]]] = []

    for module_path, short_name, return_style in detectors:
        if not args.quiet:
            print(f"  scanning {short_name}...", file=sys.stderr, flush=True)
        items, errors = run_detector(module_path, short_name, return_style,
                                     book_filter=args.book)
        detector_results.append((short_name, items, errors))
        if not args.quiet:
            print(f"    -> {len(items)} REVIEW items", file=sys.stderr, flush=True)

    report = build_report(detector_results, generated_at, date_str)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    total = sum(len(items) for _, items, _ in detector_results)
    print(f"Review queue written: {out_path}")
    print(f"Total REVIEW items: {total}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
