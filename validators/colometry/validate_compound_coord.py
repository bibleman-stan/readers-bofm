#!/usr/bin/env python3
"""
Validate compound coordinate argument under shared verb across the BofM corpus.

Pattern (Alma 30:18 women+men type):
  Line N:   ...[verb]... <argument NP>,
  Line N+1: and|or also <DET/POSS/PREP> ... [no own predication, ≤ 60c]

Second conjunct of a compound argument under shared governor verb fragmented
onto its own line without break-license. Per criterion 1 (atomic-thought) +
N=2 adjudication, the fragment alone fails own-proposition.

Filters mirror the applier's high-precision signature:
  - 'and|or also' opener required (NP-coord cue)
  - Next token is DET/POSS/DEMONSTRATIVE/PREP
  - Line N+1 length ≤ 60c
  - No participial-coord verb
  - No bare-infinitive verb
  - No finite-aux/be-form

Paired applier: validators/apply_compound_coord.py

Exit code: 0 if no violations, 1 if violations found.

Usage:
    python3 validate_compound_coord.py
    python3 validate_compound_coord.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


END_ON_COMMA_RE = re.compile(r',\s*$')

ALSO_COORD_RE = re.compile(
    r'^(?:and|or)\s+also\s+'
    r'(?:'
    r'the|a|an|his|her|their|our|my|thy|your|every|all|some|many|much|few|'
    r'other|another|that|this|these|those|such|any|no\s+|none|either|neither|'
    r'of|in|on|at|to|from|with|by|for|against|concerning|unto|into|upon|out|'
    r'across|through|over|under|about|among|amongst|because|when|where|after|'
    r'before|toward|towards|throughout|between|behind|beside|within|without|'
    r'during|until|since|though|although|whereas|whilst|while|wherefore'
    r')\b',
    re.IGNORECASE
)

PARTICIPIAL_COORD_RE = re.compile(
    r'^(?:and|or)\s+also\s+'
    r'(?:being|having|doing|going|coming|knowing|seeing|hearing|saying|'
    r'speaking|testifying|preaching|prophesying|leading|teaching|making|'
    r'taking|giving|sending|receiving|working|fighting|laboring|'
    r'thinking|believing|trusting|desiring|hoping|fearing|trembling|rejoicing)\b',
    re.IGNORECASE
)

VP_COORD_RE = re.compile(
    r'^(?:and|or)\s+also\s+'
    r'(?:perish|fall|fail|depart|return|wait|build|destroy|labor|teach|learn|'
    r'fight|preserve|seek|find|keep|bear|carry|take|give|send|love|hate|fear|'
    r'trust|flee|hide|press|hold|bind|loose|break|gather|scatter|dwell|cease|'
    r'continue|fulfill|come|go|see|hear|know|believe|worship|pray|speak|cry|'
    r'smite|slay|kill|arise|sit|stand|walk|run|live|die|grow|deny|confess|'
    r'repent|reign|rule|judge|punish|reward|forgive|save|deliver|raise|'
    r'lift|cast|throw|write|read|bring|leave|remember|forget|prepare|ordain|'
    r'plant|sow|reap|harvest|drink|eat|sleep|wake|hunger|thirst|suffer|'
    r'rejoice|mourn|weep|laugh|sing|shout|preach|prophesy|testify)\b',
    re.IGNORECASE
)

HAS_FINITE_PRED_RE = re.compile(
    r'\b(?:was|were|is|are|am|be|been|being|'
    r'did|do|does|done|'
    r'hath|hast|have|has|had|'
    r'shall|will|may|might|can|could|should|would|must|'
    r'spake|spoke|said|saith|saying|'
    r'came|come|went|go|gave|give|'
    r'made|make|saw|see|seeth|knew|know|'
    r'began|begin|behold|beheld|'
    r'cometh|goeth|leadeth|hardeneth|blindeth|'
    r'doth|liveth|dwelleth|'
    r'preached|prophesied|'
    r'testified|fled|prayed|loved|'
    r'arose|stood|sat|'
    r'taught|wrought|brought|sought|thought|'
    r'returned|departed|appeared|'
    r'wrote|written|read|'
    r'passed|fell|fallen|risen|rose|grew|grown|'
    r'wept|laughed|sang|sung|shouted|cried|'
    r'hungered|thirsted|suffered|rejoiced|mourned|'
    r'increased|decreased|gathered|scattered|'
    r'fulfilled|judged|reigned|ruled|repented|confessed|denied|'
    r'lived|died|caused|brought|sent|received|kept|broke|'
    r'destroyed|smote|slew|killed|prepared|ordained|planted)\b',
    re.IGNORECASE
)

LINE_N_PLUS_1_LEN_CAP = 60


def is_verse_number(line: str) -> bool:
    return bool(re.match(r"^\s*\d+:\d+\s*$", line))


def scan_file(path: Path, verbose: bool = False):
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i in range(len(lines) - 1):
        cur = lines[i].strip()
        nxt = lines[i + 1].strip()
        if not cur or not nxt or is_verse_number(cur) or is_verse_number(nxt):
            continue
        if not END_ON_COMMA_RE.search(cur):
            continue
        if not ALSO_COORD_RE.match(nxt):
            continue
        if len(nxt) > LINE_N_PLUS_1_LEN_CAP:
            continue
        if PARTICIPIAL_COORD_RE.match(nxt):
            continue
        if VP_COORD_RE.match(nxt):
            continue
        if HAS_FINITE_PRED_RE.search(nxt):
            continue
        violations.append({
            "file": path.name,
            "line_num": i + 1,
            "cur": cur,
            "nxt": nxt,
        })
        if verbose:
            print(f"[DEVIATION] {path.name}:{i+1}")
            print(f"    cur: {cur[:90]}")
            print(f"    nxt: {nxt[:90]}")
    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        all_violations.extend(scan_file(path, verbose=args.verbose))

    print()
    print("Compound coordinate argument under shared verb — BofM v2-mine corpus")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"violations found: {len(all_violations)}")
    print()

    if all_violations and not args.verbose:
        print("Sample (first 10):")
        for v in all_violations[:10]:
            print(f"  [{v['file']}:{v['line_num']}]")
            print(f"    cur: {v['cur'][:90]}")
            print(f"    nxt: {v['nxt'][:90]}")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
