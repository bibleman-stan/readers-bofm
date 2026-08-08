"""
Sweep corpus for severed complement-spanning-frame pattern.

Signature (Alma 30:18 type):
  Line N:   [V-ing | speech-verb] them that [WHEN|AFTER|BEFORE|AS|...] ...,
  Line N+1: [matrix predication starting with subject pronoun OR demonstrative]

The complementizer 'that' belongs to a speech/cognition governor on line N;
inside its complement, a temporal/conditional frame is followed by a matrix
predication that has been split onto line N+1. Per Rule 17 + M3 + frame+matrix
one-proposition, the body should rejoin the governor.

Length cap: 130c. Anything over → REVIEW (skipped from --apply).

Usage:
  python 5-machinery/validators/apply_severed_complement.py            # dry-run
  python 5-machinery/validators/apply_severed_complement.py --apply    # write merges
"""
import re
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent.parent / "data/text-files/v2"

# Line N pattern: "...that <temporal-conjunction> ...," at end of line.
# The 'that' is the complementizer; the temporal conj launches the frame.
SEVERED_COMP_RE = re.compile(
    r'\bthat\s+(when|after|before|as|while|until|if|because|since|though|although)\b'
    r'.*,\s*$',
    re.IGNORECASE
)

# Line N+1: matrix predication. Subject is pronoun, demonstrative, or short NP +
# finite verb / be-form / shall-will.
PRED_LEAD_RE = re.compile(
    r'^(?:'
    r'there (?:was|were|came|arose|did|stood|appeared|shall|will|is|are|hath|have)'
    r'|that (?:was|were|is|are|shall|will|hath|have)'
    r'|this (?:was|were|is|are|shall|will|hath|have)'
    r'|(?:he|she|they|it|we|I|ye|thou)\b'
    r'|(?:the )?(?:people|Lord|king|Lamanites|Nephites|land|words?|brethren|'
    r'priests?|servants?|men|man|woman|earth|spirit|voice|prophets?|whole)\b'
    r')',
    re.IGNORECASE
)

LENGTH_CAP = 130


def main():
    candidates = []
    for fp in sorted(CORPUS.glob("*.txt")):
        with open(fp, encoding="utf-8") as f:
            lines = f.read().split("\n")
        for i in range(len(lines) - 1):
            cur = lines[i].strip()
            nxt = lines[i + 1].strip()
            if not cur or not nxt:
                continue
            if not SEVERED_COMP_RE.search(cur):
                continue
            if not PRED_LEAD_RE.match(nxt):
                continue
            merged_len = len(cur) + 1 + len(nxt)
            status = "APPLY" if merged_len <= LENGTH_CAP else "REVIEW"
            candidates.append((fp.name, i + 1, status, merged_len, cur, nxt))

    apply_n = sum(1 for c in candidates if c[2] == "APPLY")
    review_n = sum(1 for c in candidates if c[2] == "REVIEW")
    print(f"Total: {len(candidates)} | APPLY: {apply_n} | REVIEW: {review_n}\n")
    for c in candidates:
        marker = "[APPLY]" if c[2] == "APPLY" else "[REVIEW]"
        print(f"{marker} {c[0]}:{c[1]} (merged_len={c[3]})")
        print(f"  cur: {c[4][:110]}")
        print(f"  nxt: {c[5][:110]}")
        print()

    import sys
    if "--apply" not in sys.argv:
        print("(dry run -- pass --apply to write)")
        return

    by_file = {}
    for fp_name, line_1based, status, _, _, _ in candidates:
        if status != "APPLY":
            continue
        by_file.setdefault(fp_name, []).append(line_1based - 1)
    total_applied = 0
    for fp_name, indices in by_file.items():
        fp = CORPUS / fp_name
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
        print(f"  applied {len(indices)} merges to {fp_name}")
        total_applied += len(indices)
    print(f"\nTotal APPLY merges written: {total_applied}")


if __name__ == "__main__":
    main()
