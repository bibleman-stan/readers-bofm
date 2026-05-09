"""
Aggregate per-batch filled CoNLL-U files into one chapter file, after
verifying each batch preserved the skeleton's tokenization.

Usage:
    python validators/parsing/aggregate_overlay.py \\
        --skeleton-dir data/parses/llm-direct/alma-ch30-batches \\
        --skeleton-prefix skeleton \\
        --filled-prefix filled \\
        --out data/parses/llm-direct/alma-ch30.conllu
"""
import argparse
import sys
from pathlib import Path


def parse_conllu_blocks(path: Path):
    """Yield (header_lines, token_rows) per sentence block."""
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


def get_token_id_form(row: str) -> tuple[str, str]:
    cols = row.split("\t")
    return cols[0], cols[1] if len(cols) > 1 else ""


def validate_overlay(skeleton_path: Path, filled_path: Path) -> list[str]:
    """Return list of validation errors. Empty list = clean."""
    errors = []
    skel_blocks = list(parse_conllu_blocks(skeleton_path))
    fill_blocks = list(parse_conllu_blocks(filled_path))
    if len(skel_blocks) != len(fill_blocks):
        errors.append(
            f"sentence-count mismatch: skeleton={len(skel_blocks)} filled={len(fill_blocks)}"
        )
        return errors

    for i, ((skh, skr), (fh, fr)) in enumerate(zip(skel_blocks, fill_blocks)):
        # Check sent_id preserved
        sk_text_lines = [l for l in skh if l.startswith("# text") or l.startswith("# sent_id")]
        f_text_lines = [l for l in fh if l.startswith("# text") or l.startswith("# sent_id")]
        for sl in sk_text_lines:
            if sl not in f_text_lines:
                errors.append(f"sentence {i}: header line missing in filled: {sl[:80]}")

        # Check token count preserved
        if len(skr) != len(fr):
            errors.append(
                f"sentence {i}: token-count mismatch skeleton={len(skr)} filled={len(fr)}"
            )
            continue

        # Check each token's ID and FORM preserved
        for j, (sr, fr_row) in enumerate(zip(skr, fr)):
            sk_id, sk_form = get_token_id_form(sr)
            fl_id, fl_form = get_token_id_form(fr_row)
            if sk_id != fl_id:
                errors.append(
                    f"sentence {i} token {j}: ID mismatch skeleton={sk_id} filled={fl_id}"
                )
            if sk_form != fl_form:
                errors.append(
                    f"sentence {i} token {j}: FORM mismatch skeleton={sk_form!r} filled={fl_form!r}"
                )

    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton-dir", type=Path, required=True)
    ap.add_argument("--skeleton-prefix", default="skeleton")
    ap.add_argument("--filled-prefix", default="filled")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--strict", action="store_true",
                    help="Fail (non-zero exit) if any batch fails validation")
    args = ap.parse_args()

    skeletons = sorted(args.skeleton_dir.glob(f"{args.skeleton_prefix}-*.conllu"))
    if not skeletons:
        print(f"ERROR: no skeleton files matching {args.skeleton_prefix}-*.conllu", file=sys.stderr)
        sys.exit(2)

    all_blocks = []
    n_errors_total = 0
    n_clean = 0
    for sk in skeletons:
        suffix = sk.name.replace(f"{args.skeleton_prefix}-", "")
        filled = args.skeleton_dir / f"{args.filled_prefix}-{suffix}"
        if not filled.exists():
            print(f"  [SKIP] {filled.name} not found")
            continue

        errors = validate_overlay(sk, filled)
        if errors:
            print(f"  [FAIL] {filled.name}: {len(errors)} errors")
            for e in errors[:5]:
                print(f"    - {e}")
            if len(errors) > 5:
                print(f"    ... +{len(errors) - 5} more")
            n_errors_total += len(errors)
        else:
            print(f"  [OK]   {filled.name}: clean overlay")
            n_clean += 1

        # Append blocks regardless (downstream measurement still useful)
        for header, rows in parse_conllu_blocks(filled):
            all_blocks.append((header, rows))

    print(f"\nValidated {len(skeletons)} batches: {n_clean} clean, {len(skeletons) - n_clean} with errors ({n_errors_total} total errors)")

    if args.strict and n_errors_total > 0:
        print("Strict mode: aborting (some batches had errors)", file=sys.stderr)
        sys.exit(1)

    # Write aggregated CoNLL-U
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for header, rows in all_blocks:
            for h in header:
                f.write(h + "\n")
            for r in rows:
                f.write(r + "\n")
            f.write("\n")
    n_tok = sum(len(r) for _, r in all_blocks)
    print(f"\nAggregated {len(all_blocks)} sentences, {n_tok} tokens to {args.out}")


if __name__ == "__main__":
    main()
