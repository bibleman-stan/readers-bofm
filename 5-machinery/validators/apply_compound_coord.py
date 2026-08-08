"""
Sweep corpus for compound coordinate argument under shared verb.

Signature (Alma 30:18 women+men type):
  Line N:   ...[verb]... <argument NP>,
  Line N+1: and|or also <DET/POSS/PREP> ...

The second conjunct of a compound argument (DObj, oblique, subject) under a
shared governor verb is split onto its own line without break-license. Per
criterion 1 (atomic-thought) + N=2 adjudication, the fragment alone fails own-
proposition and should rejoin the head.

Filters (high-precision):
  - 'and|or also' opener required (strong NP-coord cue, not VP-coord)
  - Next token must be DET / POSS / DEMONSTRATIVE / PREP (filters bare verbs,
    bare subject pronouns, bare proper nouns)
  - Line N+1 length ≤ 60c (pure-NP fragments are short)
  - No participial-coord verb (being / having / saying / etc.)
  - No bare-infinitive verb (perish / fall / depart / etc.)
  - No finite-aux/be-form (was / hath / shall / etc.)
  - Combined length ≤ 130c

Usage:
  python 5-machinery/validators/apply_compound_coord.py            # dry-run
  python 5-machinery/validators/apply_compound_coord.py --apply    # write merges
"""
import re
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent.parent / "data/text-files/v2"

END_ON_COMMA_RE = re.compile(r',\s*$')

# 'and also' or 'or also' followed by a strong NP-cue token: determiner,
# possessive, demonstrative, or preposition. This filters out:
#  - 'and also we/he/they...' (coordinate clauses)
#  - 'and also <bare verb>' (coordinate VPs)
#  - 'and also <bare noun> <past-tense verb>' (coordinate clauses with NP+VP)
ALSO_COORD_RE = re.compile(
    r'^(?:and|or)\s+also\s+'
    r'(?:'
    # determiners / possessives / demonstratives
    r'the|a|an|his|her|their|our|my|thy|your|every|all|some|many|much|few|'
    r'other|another|that|this|these|those|such|any|no\s+|none|either|neither|'
    # prepositions
    r'of|in|on|at|to|from|with|by|for|against|concerning|unto|into|upon|out|'
    r'across|through|over|under|about|among|amongst|because|when|where|after|'
    r'before|toward|towards|throughout|between|behind|beside|within|without|'
    r'during|until|since|though|although|whereas|whilst|while|wherefore'
    r')\b',
    re.IGNORECASE
)

# Coordinate-participial false positive: 'and also being/having/...'
PARTICIPIAL_COORD_RE = re.compile(
    r'^(?:and|or)\s+also\s+'
    r'(?:being|having|doing|going|coming|knowing|seeing|hearing|saying|'
    r'speaking|testifying|preaching|prophesying|leading|teaching|making|'
    r'taking|giving|sending|receiving|working|fighting|laboring|'
    r'thinking|believing|trusting|desiring|hoping|fearing|trembling|rejoicing)\b',
    re.IGNORECASE
)

# VP-coord false positive: 'and also [bare-infinitive verb] ...'
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

# Finite/aux verb forms that would make N+1 self-contained predication
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
