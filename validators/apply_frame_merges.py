"""
Sweep corpus for AICTP/temporal-frame lines (ending with comma, no own
finite predication beyond the frame) immediately followed by a matrix
predication line. Merge them into a single line (one proposition = one
line, per §1 generative principle + M4).

Length cap: merged > 130 chars → REVIEW (skip auto-apply).

Usage:
  python validators/apply_frame_merges.py            # dry-run
  python validators/apply_frame_merges.py --apply    # write merges
"""
import re
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent / "data/text-files/v2"

# Frame patterns: line begins with AICTP-like phrase or "And/But/Now/Then" + AICTP
# AND line contains a temporal/circumstantial subordinator marker
FRAME_LINE_RE = re.compile(
    r'^(?:And |But |Now |Then |And now |But now |Yea, |For )?'
    r'(?:it came to pass|in the days|after\b|in the \w+ year|in the year|'
    r'when |after they|after I|after he|after we|as he\b|as I\b|as they\b|'
    r'in the (?:commencement|midst|latter|space)|during)\b',
    re.IGNORECASE
)

# Predication marker on the FOLLOWING line. Includes demonstrative-`that/this`
# matrix subjects (extended 2026-05-09 for Alma 30:18 type cases).
PRED_LEAD_RE = re.compile(
    r'^(?:there (?:was|were|came|arose|did|stood|appeared)|'
    r'that (?:was|were|is|are)\b|'
    r'this (?:was|were|is|are)\b|'
    r'(?:he|she|they|it|we|I|ye|thou|the (?:people|Lord|king|Lamanites|Nephites|land|words?|brethren|priests?|servants?|men|man|woman|earth|wind|man|fruit|spirit|voice|prophets?|whole))\b)',
    re.IGNORECASE
)

LENGTH_CAP = 130


def is_frame_only(line: str) -> bool:
    """Heuristic: line is a frame fragment, not an own predication."""
    s = line.strip()
    if not s.endswith(','):
        return False
    if not FRAME_LINE_RE.match(s):
        return False
    return True


def line_starts_with_predication(line: str) -> bool:
    return bool(PRED_LEAD_RE.match(line.strip()))


def main():
    total = 0
    apply_count = 0
    review_count = 0
    review_cases = []
    actions = []  # (filepath, line_idx_0based) of APPLY merges

    for fp in sorted(CORPUS.glob("*.txt")):
        with open(fp, encoding="utf-8") as f:
            lines = f.read().split("\n")
        for i in range(len(lines) - 1):
            cur = lines[i]
            nxt = lines[i + 1]
            if not cur.strip() or not nxt.strip():
                continue
            if not is_frame_only(cur):
                continue
            if not line_starts_with_predication(nxt):
                continue
            merged_len = len(cur.rstrip()) + 1 + len(nxt.strip())
            total += 1
            if merged_len > LENGTH_CAP:
                review_count += 1
                review_cases.append((fp.name, i + 1, merged_len, cur.strip()[:60], nxt.strip()[:60]))
                continue
            apply_count += 1
            actions.append((fp, i))

    print(f"Total candidates: {total}")
    print(f"  APPLY:  {apply_count} (merged <= {LENGTH_CAP}c)")
    print(f"  REVIEW: {review_count} (merged > {LENGTH_CAP}c)")
    print()
    print("REVIEW cases (kept own-line):")
    for name, ln, ml, cur, nxt in review_cases[:15]:
        print(f"  {name}:{ln}  (merged_len={ml})")
        print(f"    cur: {cur}...")
        print(f"    nxt: {nxt}...")
    if len(review_cases) > 15:
        print(f"  ... +{len(review_cases) - 15} more")
    print()

    import sys
    if "--apply" not in sys.argv:
        print("(dry run -- pass --apply to write)")
        return

    by_file = {}
    for fp, idx in actions:
        by_file.setdefault(fp, []).append(idx)
    for fp, indices in by_file.items():
        with open(fp, encoding="utf-8") as f:
            lines = f.read().split("\n")
        for idx in sorted(indices, reverse=True):
            cur = lines[idx]
            nxt = lines[idx + 1]
            merged = cur.rstrip() + " " + nxt.strip()
            lines[idx] = merged
            del lines[idx + 1]
        with open(fp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  applied {len(indices)} merges to {fp.name}")

    print(f"\nTotal merges applied: {apply_count}")


if __name__ == "__main__":
    main()
