#!/usr/bin/env python3
"""resolve_review_required.py — R19 REVIEW-REQUIRED resolver prototype.

Implements Stan-directive 2026-05-16-1700-resolve-review-required-prototype.md
(BoFM directive queue). Prototype script that takes R19's REVIEW-REQUIRED
findings and asks a second-pass LLM (Sonnet) to resolve them given the
full §5 R19 canon entry + verse context. This is a READ-ONLY DIAGNOSTIC —
does NOT modify v2-mine. Does NOT auto-apply.

Architectural framing: extends the existing Stanza+LLM ensemble pattern
(parse pipeline) to validator-output resolution. Not new architecture;
new application of an established pattern.

Isaiah skeptical-mode (2026-05-16, per directive 2400): when a case
falls inside an Isaiah-quoting chapter range (1 Ne 20-22, 2 Ne 7-8,
2 Ne 12-24, 2 Ne 27, Mosiah 14, 3 Ne 22-24), the per-case prompt is
prepended with a skeptical-mode preamble warning Sonnet to verify
relative-clause genuineness before applying R19 routing — the 2102
BoFM Isaiah scan confirmed that the UD parser sometimes mis-classifies
Hebrew-style parallel exclamatory limbs as `acl:relcl`. The preamble
instructs Sonnet to return GENUINE-REVIEW-REQUIRED with rationale
"probable Hebrew-parallelism parser mis-classification" when the
construction looks like parser mis-attribution rather than a
restrictive relative.

Two run modes:

  --dump-prompts <file.jsonl>
      Emit one JSON record per sampled case to a JSONL file. Each record
      contains the full prompt text + metadata. External operator
      dispatches each prompt to Sonnet (via the Anthropic API or Agent
      tools) and feeds verdicts back via --import-verdicts.

  --api
      Call the Anthropic Messages API directly (requires
      ANTHROPIC_API_KEY in env). Uses claude-sonnet-4-6 by default.

  --import-verdicts <file.jsonl>
      Merge external verdicts back into the resolver. Each JSON record
      should match the emitted prompt's case_id and add fields:
      sonnet_verdict, sonnet_reasoning, sonnet_confidence.

Sampling:

  --sample N          number of REVIEW cases to sample (default 25)
  --sample-strategy   stratified | random   (default stratified)

  Stratified by head_lemma: high-volume lemmas (thing, word, time) get
  5 cases each; medium-volume get 3; low-volume get 2-3 to fill quota.

Output:

  --report <file.md>  markdown report (5-column table per directive
                      §Items #3). Default: stdout.

Status: prototype 2026-05-16. Diagnostic-only; no auto-apply gate. Calibration
findings + design-choice surfacing reported alongside the table per
directive §Items #5.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from validators.colometry.validate_rule_19_ud import scan_book, BOOKS


# ---------------------------------------------------------------------------
# Canon / scholarship context loading
# ---------------------------------------------------------------------------

CANON_PATH = REPO_ROOT / "1-method" / "colometry-canon.md"
SCHOLARSHIP_R19 = REPO_ROOT / "1-method" / "scholarship" / "r19.md"


def load_canon_r19() -> str:
    """Extract the §5 R19 rule entry from the canon."""
    if not CANON_PATH.exists():
        return "(canon not available)"
    canon = CANON_PATH.read_text(encoding="utf-8")
    m = re.search(
        r"<!-- =====\s+R19\s+=====\s+-->(.*?)(?=<!-- =====|\Z)",
        canon,
        re.DOTALL,
    )
    if not m:
        return "(R19 entry not found)"
    return m.group(1).strip()


def load_scholarship_r19() -> str:
    """Optional R19 scholarship companion."""
    if not SCHOLARSHIP_R19.exists():
        return ""
    return SCHOLARSHIP_R19.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Verse-context assembly
# ---------------------------------------------------------------------------

V2_DIR = REPO_ROOT / "data" / "text-files" / "v2"

_BOOK_FILE_MAP = {
    "1nephi": "01-1_nephi-2020-sb-v2.txt",
    "2nephi": "02-2_nephi-2020-sb-v2.txt",
    "jacob": "03-jacob-2020-sb-v2.txt",
    "enos": "04-enos-2020-sb-v2.txt",
    "jarom": "05-jarom-2020-sb-v2.txt",
    "omni": "06-omni-2020-sb-v2.txt",
    "words-of-mormon": "07-words_of_mormon-2020-sb-v2.txt",
    "mosiah": "08-mosiah-2020-sb-v2.txt",
    "alma": "09-alma-2020-sb-v2.txt",
    "helaman": "10-helaman-2020-sb-v2.txt",
    "3nephi": "11-3_nephi-2020-sb-v2.txt",
    "4nephi": "12-4_nephi-2020-sb-v2.txt",
    "mormon": "13-mormon-2020-sb-v2.txt",
    "ether": "14-ether-2020-sb-v2.txt",
    "moroni": "15-moroni-2020-sb-v2.txt",
}


VERSE_RE = re.compile(r"^\s*(\d+):(\d+)\s*$")


def load_v2_verses(book: str) -> dict[tuple[int, int], list[tuple[int, str]]]:
    """Load v2-mine for a book. Return {(ch, v): [(line_no, line_text), ...]}."""
    path = V2_DIR / _BOOK_FILE_MAP[book]
    if not path.exists():
        return {}
    out: dict[tuple[int, int], list[tuple[int, str]]] = {}
    cur_ch = None
    cur_v = None
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            stripped = line.rstrip("\n")
            m = VERSE_RE.match(stripped)
            if m:
                cur_ch = int(m.group(1))
                cur_v = int(m.group(2))
                continue
            if cur_ch is not None and cur_v is not None and stripped.strip():
                out.setdefault((cur_ch, cur_v), []).append((ln, stripped))
    return out


def find_verse_for_line(verses: dict, line_no: int) -> tuple[int, int] | None:
    """Find (ch, v) whose line range covers line_no."""
    for key, lines in verses.items():
        for ln, _ in lines:
            if ln == line_no:
                return key
    return None


def assemble_verse_context(
    verses: dict, ref: tuple[int, int], radius: int = 2
) -> str:
    """Return a printable block: target verse + radius verses before/after."""
    ch, v = ref
    all_refs = sorted(verses.keys())
    try:
        idx = all_refs.index(ref)
    except ValueError:
        return ""
    lo = max(0, idx - radius)
    hi = min(len(all_refs), idx + radius + 1)
    blocks = []
    for i in range(lo, hi):
        c, vv = all_refs[i]
        marker = "  >>> " if (c, vv) == ref else "      "
        blocks.append(f"{marker}{c}:{vv}")
        for _, txt in verses[(c, vv)]:
            blocks.append(f"        {txt}")
        blocks.append("")
    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# REVIEW-case sampling
# ---------------------------------------------------------------------------

def collect_review_cases(books: list[str]) -> list[dict]:
    out: list[dict] = []
    for b in books:
        try:
            recs = scan_book(b)
        except FileNotFoundError:
            continue
        for r in recs:
            if r.get("bucket") == "REVIEW-REQUIRED":
                out.append(r)
    return out


def stratified_sample(cases: list[dict], n: int, by_subtype: bool = False) -> list[dict]:
    """Stratified sample by head_lemma.

    If by_subtype is False (default): pure head_lemma stratification — top-3
    lemmas get ~5 each, next 3-5 get ~2-3, long-tail fills.

    If by_subtype is True: stratify by (review_subtype, head_lemma). The
    subtype-quota is proportional to the full-corpus distribution
    (currently 70% same-line / 30% cross-line at 2026-05-16). Within each
    subtype-bin, head_lemma stratification applies.

    Dedupes on (book, sent_id, head_line) to avoid the resolver-prototype
    issue where the validator emitted multiple findings per sent_id with
    the same head_line (codified surfacing: 2026-05-16 reply at
    directives/replies/2026-05-16-1700-resolve-review-required-prototype.md).
    """
    # Dedupe pass
    seen: set[tuple] = set()
    unique: list[dict] = []
    for c in cases:
        key = (c["book"], c.get("sent_id"), c["head_line"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    cases = unique

    if not by_subtype:
        return _stratify_by_lemma(cases, n)

    same = [c for c in cases if c.get("review_subtype") == "same-line"]
    cross = [c for c in cases if c.get("review_subtype") == "cross-line"]
    # Proportional quota matching corpus distribution
    total = len(same) + len(cross)
    if total == 0:
        return []
    same_quota = round(n * (len(same) / total))
    cross_quota = n - same_quota
    out = _stratify_by_lemma(same, same_quota) + _stratify_by_lemma(cross, cross_quota)
    return out[:n]


def _stratify_by_lemma(cases: list[dict], n: int) -> list[dict]:
    """Internal: head_lemma stratification with top-tier quota.

    Within each lemma's bucket, picks cases via round-robin across books to
    avoid the 1nephi-first ordering bias of a naive sort-by-(book, sent_id)
    slice. Cases-per-lemma is unchanged; just the per-lemma selection rotates
    through the books represented in the bucket so the final sample spans
    1nephi → Moroni rather than concentrating in early books.
    """
    if not cases or n <= 0:
        return []
    by_lemma: dict[str, list[dict]] = defaultdict(list)
    for c in cases:
        by_lemma[c["head_lemma"]].append(c)
    lemma_counts = sorted(
        ((k, len(v)) for k, v in by_lemma.items()), key=lambda x: -x[1]
    )

    def round_robin_by_book(bucket: list[dict], k: int) -> list[dict]:
        # Group by book, then interleave one-per-book until k filled
        by_book: dict[str, list[dict]] = defaultdict(list)
        for c in bucket:
            by_book[c["book"]].append(c)
        # Sort each book's cases for stable selection within the book
        for book in by_book:
            by_book[book].sort(key=lambda c: int(c.get("sent_id", 0)))
        # Round-robin: cycle through books in a stable order
        book_order = sorted(by_book.keys())
        picked: list[dict] = []
        idx = 0
        while len(picked) < k:
            progress = False
            for book in book_order:
                if idx < len(by_book[book]):
                    picked.append(by_book[book][idx])
                    progress = True
                    if len(picked) >= k:
                        break
            if not progress:
                break
            idx += 1
        return picked

    out: list[dict] = []
    quota_per_top = max(3, n // 6)
    quota_per_mid = max(2, n // 10)
    for i, (lemma, _) in enumerate(lemma_counts):
        if i < 3:
            quota = quota_per_top
        elif i < 8:
            quota = quota_per_mid
        else:
            quota = 1
        out.extend(round_robin_by_book(by_lemma[lemma], quota))
        if len(out) >= n:
            break
    return out[:n]


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a Book of Mormon colometric-rule resolver. You apply Rule 19 "
    "(Cataphoric vs Anaphoric Relative Clauses) to ambiguous NOUN-head cases "
    "that the deterministic validator could not resolve. You decide whether "
    "the relative clause should MERGE with its head (anaphoric — head is a "
    "specific established referent), SPLIT before the relative (cataphoric — "
    "head is forward-pointing generic), or remain GENUINE-REVIEW-REQUIRED "
    "(genuinely ambiguous even with discourse context). You ground decisions "
    "in the canon and verse-context only; you do NOT invent rules or import "
    "external frameworks."
)


# Isaiah-quoting chapter ranges per the 2102 Isaiah scan. When the resolver
# sees a case in one of these ranges, it prepends a skeptical-mode preamble
# warning that UD parsers sometimes mis-classify Hebrew-style parallelism
# as acl:relcl. Codified per directive 2026-05-16-2400-r19-isaiah-option-a-
# plus-d.md (Option D from the 2203 audit consensus).
ISAIAH_RANGES: dict[str, list[tuple[int, int]]] = {
    "1nephi": [(20, 22)],     # Isaiah 48-49 + Nephi discourse
    "2nephi": [(7, 8), (12, 24), (27, 27)],
                              # Isaiah 50-51, Isaiah 2-14, Isaiah 29
    "mosiah": [(14, 14)],     # Isaiah 53
    "3nephi": [(22, 24)],     # Isaiah 54 + Malachi 3-4
}


def in_isaiah_chapter(book: str, verse_ref: str) -> bool:
    """Return True if verse_ref's chapter falls in book's Isaiah ranges."""
    ranges = ISAIAH_RANGES.get(book)
    if not ranges:
        return False
    try:
        ch = int(str(verse_ref).split(":")[0])
    except (ValueError, IndexError, AttributeError):
        return False
    return any(lo <= ch <= hi for lo, hi in ranges)


ISAIAH_SKEPTICAL_PREAMBLE = (
    "## ⚠ ISAIAH-CHAPTER SKEPTICAL MODE\n\n"
    "This case is in an Isaiah-quoting chapter (or, for 3 Nephi 24, "
    "a Malachi-quoting chapter). The 2102 BoFM parser-scan confirmed "
    "that the UD parser sometimes mis-classifies Hebrew-style parallelism "
    "as `acl:relcl` when the construction is actually parallel "
    "exclamatory limbs WITHOUT a relative pronoun (e.g., 2 Nephi 24:4 "
    "*\"the golden city ceased!\"* tagged as a relative on *city* with "
    "root *ceased*, when the surface reading is a Hebrew-parallel "
    "exclamation, not a restrictive relative).\n\n"
    "**Before applying R19's normal routing, verify**:\n"
    "1. The construction has an actual relative pronoun (*which* / *whom* "
    "/ *whose* / *who* / *that*) AT THE HEAD of the relative clause, NOT "
    "just somewhere in the verse.\n"
    "2. The relative clause modifies the head NP restrictively (restricts "
    "or identifies the head's referent), not as a parallel independent "
    "exclamatory limb.\n"
    "3. The `rel_root` token is grammatically inside the relative clause "
    "(it should be the verb of the relative, not the verb of a parallel "
    "clause).\n\n"
    "**If the construction looks like Hebrew-parallel-limb mis-classification** "
    "(no clear restrictive function; rel_root looks like a main-clause verb; "
    "head-form == rel_root-form circular attachment; pronoun-subject head "
    "with which/that resumptive-exclamatory device), return:\n\n"
    "    VERDICT: GENUINE-REVIEW-REQUIRED\n"
    "    CONFIDENCE: <medium or high based on certainty>\n"
    "    REASONING: probable Hebrew-parallelism parser mis-classification "
    "(specify the diagnostic signal: parallel-limb shape / circular-attachment "
    "/ pronoun-resumptive / etc.)\n\n"
    "Otherwise apply R19's normal routing per the canon entry below.\n\n"
    "---\n"
)


def build_case_prompt(canon_r19: str, scholarship: str, case: dict, verse_block: str) -> str:
    extras = f"\n\nR19 SCHOLARSHIP COMPANION:\n\n{scholarship}\n" if scholarship.strip() else ""
    subtype = case.get("review_subtype") or "(unset — pre-restructure validator)"
    isaiah_preamble = (
        ISAIAH_SKEPTICAL_PREAMBLE
        if in_isaiah_chapter(case.get("book",""), case.get("verse_ref",""))
        else ""
    )
    return f"""{isaiah_preamble}## R19 §5 CANON ENTRY

{canon_r19}
{extras}

## CASE TO RESOLVE

book: {case['book']}
sent_id: {case.get('sent_id')}
head: form={case['head_form']!r} lemma={case['head_lemma']!r} upos={case['head_upos']!r} (line {case['head_line']})
relative-root: form={case['rel_root_form']!r} lemma={case['rel_root_lemma']!r} (line {case['rel_line']})
validator reason: {case.get('reason', '')}
review subtype: {subtype}   (same-line = "verify existing merge"; cross-line = "close existing split?")

## VERSE CONTEXT (±2 verses)

{verse_block}

## VERDICT REQUEST

Per R19's canon criteria, classify this case. Return STRICTLY in the form:

VERDICT: <STRONG-MERGE | STRONG-SPLIT | GENUINE-REVIEW-REQUIRED>
CONFIDENCE: <high | medium | low>
REASONING: <one sentence — the specific canon criterion that determined the verdict, anchored in this verse's context>

Constraints:
- STRONG-MERGE only when the head is referentially specific in this discourse (recoverable from the ±2 verse context or from the verse's own constituent structure). Apply the bidirectional atomic-thought test: if the relative is the head's identifying content (head is referentially content-empty without the relative), MERGE.
- STRONG-SPLIT only when the head is a forward-pointer with no on-line antecedent and the relative carries new propositional content.
- GENUINE-REVIEW-REQUIRED when EITHER the verse-context alone is insufficient OR the case sits at a canonical exclusion edge (J1 N>=3 series, R17 ccomp territory, comparative as-clause, R26 ADJ-predicate frame, etc.).
- Treat punctuation as inherited text (post-1830 overlay), not as evidence.
- Do NOT invent rules. Cite the canon criterion you applied.
"""


# ---------------------------------------------------------------------------
# Anthropic API mode (optional)
# ---------------------------------------------------------------------------

def call_sonnet_api(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    """Call Anthropic Messages API. Requires `pip install anthropic` and
    ANTHROPIC_API_KEY env var."""
    try:
        import anthropic
    except ImportError:
        sys.stderr.write(
            "anthropic SDK not installed. Run: pip install anthropic\n"
            "Or use --dump-prompts mode for external dispatch.\n"
        )
        sys.exit(2)

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

VERDICT_RE = re.compile(r"VERDICT:\s*(\S+)", re.IGNORECASE)
CONFIDENCE_RE = re.compile(r"CONFIDENCE:\s*(\S+)", re.IGNORECASE)
REASONING_RE = re.compile(r"REASONING:\s*(.+?)(?:\n\n|\Z)", re.IGNORECASE | re.DOTALL)


def parse_verdict(text: str) -> dict:
    v = VERDICT_RE.search(text)
    c = CONFIDENCE_RE.search(text)
    r = REASONING_RE.search(text)
    return {
        "verdict": v.group(1).strip().rstrip(".,;") if v else "(unparsed)",
        "confidence": c.group(1).strip().rstrip(".,;").lower() if c else "(unparsed)",
        "reasoning": (r.group(1).strip() if r else "(unparsed)").replace("\n", " "),
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def render_markdown_table(rows: list[dict]) -> str:
    out = []
    out.append("| Verse | Subtype | Original verdict | Sonnet verdict | Confidence | Reasoning |")
    out.append("|---|---|---|---|---|---|")
    for r in rows:
        verse_ref = f"{r['book']} {r.get('verse_ref','?')}"
        subtype = r.get("review_subtype") or "—"
        original = f"REVIEW-REQUIRED ({r.get('reason','')})"
        sonnet_v = r.get("sonnet_verdict", "—")
        conf = r.get("sonnet_confidence", "—")
        reason = r.get("sonnet_reasoning", "—").replace("|", "\\|")
        # Truncate reasoning to keep table readable
        if len(reason) > 220:
            reason = reason[:217] + "..."
        out.append(f"| {verse_ref} | {subtype} | {original} | {sonnet_v} | {conf} | {reason} |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=int, default=25)
    ap.add_argument(
        "--sample-strategy",
        choices=["stratified", "stratified-by-subtype", "random"],
        default="stratified",
    )
    ap.add_argument("--dump-prompts", type=str, help="Write JSONL prompts to FILE")
    ap.add_argument(
        "--import-verdicts",
        type=str,
        help="Merge JSONL verdicts back (each case_id matches the prompt)",
    )
    ap.add_argument("--api", action="store_true", help="Call Anthropic API directly")
    ap.add_argument("--report", type=str, help="Markdown report output path")
    ap.add_argument("--books", nargs="+", default=BOOKS, help="Books to scan")
    args = ap.parse_args()

    # Step 1: gather REVIEW cases
    print("Scanning R19 validator for REVIEW-REQUIRED cases...", file=sys.stderr)
    cases = collect_review_cases(args.books)
    print(f"  Found {len(cases)} REVIEW-REQUIRED cases", file=sys.stderr)

    if not cases:
        print("No REVIEW-REQUIRED cases found.", file=sys.stderr)
        return 0

    # Step 2: sample
    if args.sample_strategy == "stratified":
        sampled = stratified_sample(cases, args.sample, by_subtype=False)
    elif args.sample_strategy == "stratified-by-subtype":
        sampled = stratified_sample(cases, args.sample, by_subtype=True)
    else:
        import random
        random.seed(20260516)
        sampled = random.sample(cases, min(args.sample, len(cases)))
    print(f"  Sampled {len(sampled)} cases", file=sys.stderr)

    # Step 3: assemble context per case
    canon = load_canon_r19()
    scholarship = load_scholarship_r19()
    by_book_verses: dict[str, dict] = {}

    for c in sampled:
        b = c["book"]
        if b not in by_book_verses:
            by_book_verses[b] = load_v2_verses(b)
        verses = by_book_verses[b]
        ref = find_verse_for_line(verses, c["head_line"])
        c["verse_ref"] = f"{ref[0]}:{ref[1]}" if ref else "?"
        verse_block = assemble_verse_context(verses, ref) if ref else "(verse context unavailable)"
        c["prompt"] = build_case_prompt(canon, scholarship, c, verse_block)
        c["case_id"] = f"{c['book']}_{c.get('sent_id','?')}_{c['head_line']}"

    # Step 4: dispatch (API direct, or dump prompts for external dispatch)
    verdicts_by_id: dict[str, dict] = {}

    if args.import_verdicts:
        with open(args.import_verdicts, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                verdicts_by_id[rec["case_id"]] = rec

    if args.dump_prompts:
        with open(args.dump_prompts, "w", encoding="utf-8") as f:
            for c in sampled:
                rec = {
                    "case_id": c["case_id"],
                    "book": c["book"],
                    "verse_ref": c["verse_ref"],
                    "head_lemma": c["head_lemma"],
                    "review_subtype": c.get("review_subtype"),
                    "prompt": c["prompt"],
                    "system": SYSTEM_PROMPT,
                }
                f.write(json.dumps(rec) + "\n")
        print(
            f"Wrote {len(sampled)} prompts to {args.dump_prompts}. "
            "Feed each to Sonnet and import verdicts via --import-verdicts.",
            file=sys.stderr,
        )

    if args.api:
        for c in sampled:
            print(f"  Calling Sonnet on {c['case_id']}...", file=sys.stderr)
            try:
                text = call_sonnet_api(c["prompt"])
            except Exception as e:
                print(f"    API error: {e}", file=sys.stderr)
                continue
            parsed = parse_verdict(text)
            verdicts_by_id[c["case_id"]] = {
                "case_id": c["case_id"],
                "sonnet_raw": text,
                **parsed,
            }

    # Step 5: merge verdicts onto sampled cases
    for c in sampled:
        v = verdicts_by_id.get(c["case_id"])
        if v:
            c["sonnet_verdict"] = v.get("verdict", "—")
            c["sonnet_confidence"] = v.get("confidence", "—")
            c["sonnet_reasoning"] = v.get("reasoning", "—")

    # Step 6: emit report
    table = render_markdown_table(sampled)
    if args.report:
        Path(args.report).write_text(table + "\n", encoding="utf-8")
        print(f"Wrote markdown report to {args.report}", file=sys.stderr)
    else:
        print(table)

    return 0


if __name__ == "__main__":
    sys.exit(main())
