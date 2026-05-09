"""
Auto-fix common LLM-overlay errors against the skeleton ground truth.

Detects and mechanically fixes:
  1. Surface form mismatch — copy FORM from skeleton (LLM altered token text)
  2. # text alteration — copy text comment from skeleton
  3. # sent_id alteration — copy sent_id from skeleton
  4. Token-count mismatch — flag (cannot auto-fix; needs re-dispatch)

Use after agent completes, before aggregate. Saves manual fix cycles.

Usage:
    python validators/parsing/auto_fix_overlay.py \\
        --skeleton path/to/skeleton-NN.conllu \\
        --filled path/to/filled-NN.conllu \\
        [--in-place]   # overwrite filled (default: write .fixed.conllu)
"""
import argparse
import re
import shutil
import sys
from pathlib import Path


def parse_blocks(path: Path):
    """Yield list of (header_lines, token_rows) per sentence."""
    header = []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if header or rows:
                    yield header, rows
                    header, rows = [], []
                continue
            if line.startswith("#"):
                header.append(line)
            else:
                rows.append(line)
    if header or rows:
        yield header, rows


def fix_block(skel_block, filled_block):
    """Return (fixed_block, fix_log) — fixed (header, rows) tuple + list of fix records."""
    sk_h, sk_r = skel_block
    f_h, f_r = filled_block
    fixes = []

    # Fix header: re-emit text + sent_id from skeleton if they exist there.
    # Preserve any # llm_note lines from filled.
    sk_text = next((l for l in sk_h if l.startswith("# text")), None)
    sk_sentid = next((l for l in sk_h if l.startswith("# sent_id")), None)
    f_text = next((l for l in f_h if l.startswith("# text")), None)
    f_sentid = next((l for l in f_h if l.startswith("# sent_id")), None)

    new_header = []
    if sk_text:
        if f_text and f_text != sk_text:
            fixes.append(("text-altered", f_text, sk_text))
        new_header.append(sk_text)
    if sk_sentid:
        if f_sentid and f_sentid != sk_sentid:
            fixes.append(("sentid-altered", f_sentid, sk_sentid))
        new_header.append(sk_sentid)
    # Preserve all llm_note lines from filled
    for l in f_h:
        if l.startswith("# llm_note") or (l.startswith("#") and not l.startswith("# text") and not l.startswith("# sent_id")):
            new_header.append(l)

    # Fix tokens: if token-count mismatch, can't fix
    if len(sk_r) != len(f_r):
        fixes.append(("token-count-mismatch", len(sk_r), len(f_r)))
        return (new_header, f_r), fixes  # leave as-is, flag

    new_rows = []
    for sr, fr in zip(sk_r, f_r):
        sk_cols = sr.split("\t")
        f_cols = fr.split("\t")
        if len(f_cols) < 10 or len(sk_cols) < 10:
            new_rows.append(fr)
            continue
        # Check ID
        if sk_cols[0] != f_cols[0]:
            fixes.append(("id-mismatch", sk_cols[0], f_cols[0]))
            f_cols[0] = sk_cols[0]
        # Check FORM
        if sk_cols[1] != f_cols[1]:
            fixes.append(("form-altered", f"{sk_cols[1]!r}", f"{f_cols[1]!r}"))
            f_cols[1] = sk_cols[1]
        new_rows.append("\t".join(f_cols))

    return (new_header, new_rows), fixes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", type=Path, required=True)
    ap.add_argument("--filled", type=Path, required=True)
    ap.add_argument("--in-place", action="store_true",
                    help="Overwrite filled file (default: write .fixed.conllu sibling)")
    args = ap.parse_args()

    sk_blocks = list(parse_blocks(args.skeleton))
    f_blocks = list(parse_blocks(args.filled))

    if len(sk_blocks) != len(f_blocks):
        print(f"ERROR: sentence-count mismatch: skeleton={len(sk_blocks)} filled={len(f_blocks)}",
              file=sys.stderr)
        sys.exit(2)

    fixed_blocks = []
    all_fixes = []
    flagged = []
    for i, (sk, fl) in enumerate(zip(sk_blocks, f_blocks)):
        fixed_block, fixes = fix_block(sk, fl)
        fixed_blocks.append(fixed_block)
        for fix in fixes:
            if fix[0] == "token-count-mismatch":
                flagged.append((i, fix))
            else:
                all_fixes.append((i, fix))

    out_path = args.filled if args.in_place else args.filled.with_suffix(".fixed.conllu")
    with open(out_path, "w", encoding="utf-8") as f:
        for header, rows in fixed_blocks:
            for h in header:
                f.write(h + "\n")
            for r in rows:
                f.write(r + "\n")
            f.write("\n")

    print(f"Output: {out_path}")
    print(f"Fixes applied: {len(all_fixes)}")

    if all_fixes:
        # Group by fix type for a tidy summary
        by_type = {}
        for sent_idx, fix in all_fixes:
            by_type.setdefault(fix[0], []).append((sent_idx, fix[1:]))
        for fix_type, items in sorted(by_type.items()):
            print(f"  {fix_type}: {len(items)} occurrences")
            for sent_idx, args_tup in items[:3]:
                print(f"    sentence {sent_idx}: {args_tup}")
            if len(items) > 3:
                print(f"    ... +{len(items) - 3} more")

    if flagged:
        print(f"\nFLAGGED (cannot auto-fix, needs manual or re-dispatch):")
        for sent_idx, fix in flagged:
            print(f"  sentence {sent_idx}: {fix}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
