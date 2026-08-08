"""Hand-jam authoring surface for ATU gold (Route B).

Reads private/gold/bofm-gold.txt (plain-text, one block per verse), validates
each block against the v0 master text for char-exact parity, then writes to
BOTH:
  - data/text-files/v2-adjudicated/overrides.json (the deployed override map)
  - private/substrate/emode-substrate/bofm-atu-gold-yardstick.json (the gold
    regression-test substrate)

Authoring format (private/gold/bofm-gold.txt):

  === moroni 4:3 LITURGICAL ===
  O God, the Eternal Father, we ask thee in the name of thy Son, Jesus Christ, to bless and sanctify this bread to the souls of all those who partake of it;
  that they may eat in remembrance of the body of thy Son,
  and witness unto thee, O God, the Eternal Father,
  that they are willing to take upon them the name of thy Son,
  and always remember him,
  and keep his commandments which he hath given them,
  that they may always have his Spirit to be with them.
  Amen.

Run:  py -3 5-machinery/scripts/sync_gold.py

Failures HALT (no partial writes). Idempotent: re-run with same input = no-op.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
GOLD_TXT = REPO / "private" / "gold" / "bofm-gold.txt"
OVERRIDES = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"
YARDSTICK = REPO / "private" / "substrate" / "emode-substrate" / "bofm-atu-gold-yardstick.json"
V0 = REPO / "data" / "text-files" / "v0-bofm-original"

BOOK_TO_V0 = {
    "1nephi": "1_Nephi.txt", "2nephi": "2_Nephi.txt", "jacob": "Jacob.txt",
    "enos": "Enos.txt", "jarom": "Jarom.txt", "omni": "Omni.txt",
    "words-of-mormon": "Words_of_Mormon.txt", "mosiah": "Mosiah.txt",
    "alma": "Alma.txt", "helaman": "Helaman.txt", "3nephi": "3_Nephi.txt",
    "4nephi": "4_Nephi.txt", "mormon": "Mormon.txt", "ether": "Ether.txt",
    "moroni": "Moroni.txt",
}

HEADER_RE = re.compile(r"^===\s+([\w-]+)\s+(\d+):(\d+)(?:\s+(\w+))?\s+===\s*$")


def load_v0_book(book):
    """{(c,v): text} for one book, v0 master text re-joined with single spaces."""
    path = V0 / BOOK_TO_V0[book]
    text = path.read_text(encoding="utf-8")
    out, ref = {}, None
    ref_re = re.compile(r"^.+?\s+(\d+):(\d+)\s*$")
    for line in text.splitlines():
        m = ref_re.match(line.strip())
        if m:
            ref = (int(m.group(1)), int(m.group(2))); out[ref] = ""
        elif ref is not None and line.strip():
            out[ref] = (out[ref] + " " + line.strip()).strip()
    return out


def parse_gold_txt(path):
    """Returns list of {ref, book, ch, v, genre, lines}."""
    if not path.exists():
        return []
    blocks, current = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = HEADER_RE.match(line)
        if m:
            if current is not None:
                blocks.append(current)
            book, ch, v, genre = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4) or "UNKNOWN"
            current = {
                "ref": f"{book} {ch}:{v}",
                "book": book, "ch": ch, "v": v,
                "genre": genre.upper(),
                "lines": [],
            }
        elif current is not None and line.strip():
            current["lines"].append(line)
    if current is not None:
        blocks.append(current)
    return blocks


def normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def find_twins(ref, source_text, v0_index, threshold=0.55):
    """Scan v0_index for verses with high lexical overlap with source_text.
    Returns list of (other_ref, jaccard) tuples sorted by overlap desc."""
    own = set(re.findall(r"\w+", source_text.lower()))
    if not own:
        return []
    twins = []
    for (book, c, v), text in v0_index:
        other_ref = f"{book} {c}:{v}"
        if other_ref == ref:
            continue
        other = set(re.findall(r"\w+", text.lower()))
        if not other:
            continue
        j = len(own & other) / len(own | other)
        if j >= threshold:
            twins.append((other_ref, round(j, 3)))
    return sorted(twins, key=lambda t: -t[1])[:5]


def main():
    if not GOLD_TXT.exists():
        print(f"Authoring file not found: {GOLD_TXT.relative_to(REPO)}")
        print("Create it with verse blocks. See sync_gold.py docstring for format.")
        sys.exit(1)

    blocks = parse_gold_txt(GOLD_TXT)
    if not blocks:
        print("No verse blocks parsed. Check format.")
        sys.exit(1)

    print(f"Parsed {len(blocks)} verse block(s) from {GOLD_TXT.relative_to(REPO)}")

    v0_cache = {}
    failures = []
    validated = []
    for blk in blocks:
        book = blk["book"]
        if book not in BOOK_TO_V0:
            failures.append((blk["ref"], f"unknown book '{book}'"))
            continue
        if book not in v0_cache:
            v0_cache[book] = load_v0_book(book)
        src = v0_cache[book].get((blk["ch"], blk["v"]))
        if src is None:
            failures.append((blk["ref"], f"verse not in v0 source"))
            continue
        reconstructed = normalize(" ".join(blk["lines"]))
        master = normalize(src)
        if reconstructed != master:
            failures.append((blk["ref"], _parity_diagnostic(reconstructed, master)))
            continue
        blk["source_text"] = src
        validated.append(blk)

    if failures:
        print(f"\n{len(failures)} PARITY FAILURE(S) — no writes performed:")
        for ref, why in failures:
            print(f"  {ref}: {why}")
        sys.exit(2)

    v0_index = []
    for book in BOOK_TO_V0:
        if book not in v0_cache:
            v0_cache[book] = load_v0_book(book)
        for (c, v), text in v0_cache[book].items():
            v0_index.append(((book, c, v), text))

    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    yardstick = json.loads(YARDSTICK.read_text(encoding="utf-8")) if YARDSTICK.exists() else []
    ys_by_ref = {e["ref"]: e for e in yardstick}

    print(f"\n--- Writing {len(validated)} validated entries ---")
    twins_to_review = []
    for blk in validated:
        ref = blk["ref"]
        overrides[ref] = blk["lines"]
        ys_by_ref[ref] = {"ref": ref, "genre": blk["genre"], "gold_lines": blk["lines"]}
        print(f"  ok  {ref:30s} ({len(blk['lines'])} lines, genre={blk['genre']})")
        twins = find_twins(ref, blk["source_text"], v0_index)
        for twin_ref, j in twins:
            twin_gold = ys_by_ref.get(twin_ref)
            if twin_gold is None or twin_gold.get("gold_lines") != overrides.get(twin_ref):
                twins_to_review.append((ref, twin_ref, j, twin_gold is not None))

    OVERRIDES.write_text(json.dumps(overrides, indent=2) + "\n", encoding="utf-8")
    yardstick_sorted = sorted(ys_by_ref.values(), key=lambda e: e["ref"])
    YARDSTICK.parent.mkdir(parents=True, exist_ok=True)
    YARDSTICK.write_text(json.dumps(yardstick_sorted, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OVERRIDES.relative_to(REPO)} ({len(overrides)} entries)")
    print(f"Wrote {YARDSTICK.relative_to(REPO)} ({len(yardstick_sorted)} entries)")

    if twins_to_review:
        print(f"\n--- TWIN FLAG ({len(twins_to_review)} potential symmetric pair(s)) ---")
        for own, twin, j, has_gold in twins_to_review:
            status = "has gold (verify symmetric)" if has_gold else "NO GOLD YET"
            print(f"  {own}  ~  {twin}  (Jaccard {j})  [{status}]")
        print(f"\n^^ review these for parallel-verbatim symmetric ATU treatment.")


def _parity_diagnostic(got, want):
    if len(got) != len(want):
        return f"length mismatch: got {len(got)} chars, want {len(want)} chars"
    for i, (a, b) in enumerate(zip(got, want)):
        if a != b:
            ctx_a = got[max(0, i-20):i+20]
            ctx_b = want[max(0, i-20):i+20]
            return f"diverges at char {i}: got ...{ctx_a!r}... want ...{ctx_b!r}..."
    return "(unknown diff)"


if __name__ == "__main__":
    main()
