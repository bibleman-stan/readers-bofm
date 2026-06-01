"""Convert audit/stanza-anomalies.json into v2-spray candidate payloads.

For each flagged verse: reads v0 source (master), reads v2 current-deployed split,
attaches the Stanza flag diagnostic. Outputs a list of candidate dicts ready to
hand to the Workflow as args (or to chunk for batched runs).

Run:
  py -3 scripts/audit_to_candidates.py PARALLEL_THAT_ASYMMETRY            # all (786)
  py -3 scripts/audit_to_candidates.py PARALLEL_THAT_ASYMMETRY --pilot    # 50 (12 known + 38 random)
"""

import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / "data" / "parses" / "audit" / "stanza-anomalies.json"
V0 = REPO / "data" / "text-files" / "v0-bofm-original"
V2 = REPO / "data" / "text-files" / "v2"
OUT_DIR = REPO / "data" / "parses" / "audit"

BOOK_TO_V0 = {
    "1nephi": "1_Nephi.txt", "2nephi": "2_Nephi.txt", "jacob": "Jacob.txt",
    "enos": "Enos.txt", "jarom": "Jarom.txt", "omni": "Omni.txt",
    "words-of-mormon": "Words_of_Mormon.txt", "mosiah": "Mosiah.txt",
    "alma": "Alma.txt", "helaman": "Helaman.txt", "3nephi": "3_Nephi.txt",
    "4nephi": "4_Nephi.txt", "mormon": "Mormon.txt", "ether": "Ether.txt",
    "moroni": "Moroni.txt",
}
BOOK_TO_V2 = {
    "1nephi": "01-1_nephi-2020-sb-v2.txt", "2nephi": "02-2_nephi-2020-sb-v2.txt",
    "jacob": "03-jacob-2020-sb-v2.txt", "enos": "04-enos-2020-sb-v2.txt",
    "jarom": "05-jarom-2020-sb-v2.txt", "omni": "06-omni-2020-sb-v2.txt",
    "words-of-mormon": "07-words_of_mormon-2020-sb-v2.txt",
    "mosiah": "08-mosiah-2020-sb-v2.txt", "alma": "09-alma-2020-sb-v2.txt",
    "helaman": "10-helaman-2020-sb-v2.txt", "3nephi": "11-3_nephi-2020-sb-v2.txt",
    "4nephi": "12-4_nephi-2020-sb-v2.txt", "mormon": "13-mormon-2020-sb-v2.txt",
    "ether": "14-ether-2020-sb-v2.txt", "moroni": "15-moroni-2020-sb-v2.txt",
}

KNOWN_NAMED = [
    "moroni 4:3", "moroni 5:2", "words-of-mormon 1:8", "alma 13:30", "alma 29:17",
    "mosiah 5:5", "alma 7:13", "helaman 5:8", "ether 2:11", "alma 10:13",
    "alma 4:19", "alma 7:22",
]


def load_v0(book):
    """{(c, v): text} from v0 source — re-joins multi-line prose per verse."""
    path = V0 / BOOK_TO_V0[book]
    text = path.read_text(encoding="utf-8")
    out, ref = {}, None
    ref_re = re.compile(r"^.+?\s+(\d+):(\d+)\s*$")
    for line in text.splitlines():
        m = ref_re.match(line.strip())
        if m:
            ref = (int(m.group(1)), int(m.group(2)))
            out[ref] = ""
        elif ref is not None and line.strip():
            out[ref] = (out[ref] + " " + line.strip()).strip()
    return out


def load_v2(book):
    """{(c, v): [lines]} from v2 deployed file — ATU breaks as the reader sees."""
    path = V2 / BOOK_TO_V2[book]
    text = path.read_text(encoding="utf-8")
    out, ref = {}, None
    ref_re = re.compile(r"^(\d+):(\d+)\s*$")
    for line in text.splitlines():
        m = ref_re.match(line.strip())
        if m:
            ref = (int(m.group(1)), int(m.group(2)))
            out[ref] = []
        elif ref is not None and line.strip():
            out[ref].append(line.rstrip())
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cls = sys.argv[1]
    pilot = "--pilot" in sys.argv

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    flagged = [(ref, vv) for ref, vv in audit["verses"].items()
               if any(f["class"] == cls for f in vv["flags"])]
    print(f"Class {cls}: {len(flagged)} verses flagged")

    cache_v0, cache_v2 = {}, {}
    candidates = []
    for ref, vv in flagged:
        book, cv = ref.rsplit(" ", 1)
        c, v = (int(x) for x in cv.split(":"))
        if book not in cache_v0:
            cache_v0[book] = load_v0(book)
            cache_v2[book] = load_v2(book)
        src = cache_v0[book].get((c, v))
        lines = cache_v2[book].get((c, v))
        if src is None or lines is None:
            continue
        flag_details = [f["detail"] for f in vv["flags"] if f["class"] == cls]
        candidates.append({
            "ref": ref, "book": book, "ch": c, "v": v,
            "source_text": src,
            "deployed_lines": lines,
            "flag_class": cls,
            "flag_detail": flag_details[0] if flag_details else "",
            "n_sentences": vv.get("n_sentences", 1),
        })

    if pilot:
        known = [c for c in candidates if c["ref"] in KNOWN_NAMED]
        rest = [c for c in candidates if c["ref"] not in KNOWN_NAMED]
        random.seed(20260531)
        random.shuffle(rest)
        candidates = known + rest[:max(0, 50 - len(known))]
        out_path = OUT_DIR / f"candidates-{cls}-pilot.json"
    else:
        out_path = OUT_DIR / f"candidates-{cls}.json"

    out_path.write_text(json.dumps(candidates, indent=2), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(REPO)} ({len(candidates)} candidates)")
    print(f"Size: {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
