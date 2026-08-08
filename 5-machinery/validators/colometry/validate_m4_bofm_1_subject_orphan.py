#!/usr/bin/env python3
"""
Validate M4-BoFM-1 (Subject-Orphan Predicate Completion) across the BoFM corpus.

M4-BoFM-1: When a v2-mine line whose content is a subject NP (closed-list-
eligible shape) terminates in `,` or `;`, AND the immediately-next line is
a bare finite predicate (auxiliary or main-verb lead, no leading connective,
no independent subject), the predicate-line MUST be merged onto the
subject-line as a single ATU. Codified 2026-05-11 as BoFM corpus
instantiation of framework M4 (canon §5 M4-BoFM-1).

Stage 1 (surface-pattern) + Stage 2 (UD-aware) pipeline:
  - Stage 1 checks surface patterns and SCOPE-exclusions.
  - Stage 2 queries CoNLL-U parses to filter false positives via 5 UD checks:
      C1: line A has an nsubj (or nsubj:pass) token whose head lands on line B
      C2: line A tokens are NOT all inside a PP (no token with case-parent on line A)
      C3: line B root verb has no independent nsubj on line B itself
      C4: line A has no vocative-deprel token (catches "My son," etc.)
      C5: line A has no finite root verb (it is not already a complete clause)

Kind output:
  subject-orphan-predicate-STRONG    Stage 1 + Stage 2 pass  -> STRONG-MERGE-CANDIDATE
  subject-orphan-predicate-REVIEW    Stage 1 pass, Stage 2 fail (with reason)
  subject-orphan-predicate-LONG-REVIEW  Stage 1 pass, merged > 130 chars (unchanged)

SCOPE-exclusions implemented as surface patterns (Stage 1):
- R15 vocative on line A (`O Lord,` lead)
- J3 speech-act parenthetical on line A (`saith X` tail)
- J5 save-clause on line B (`save ...` lead)
- R21 participial absolute on line B (`being|having` lead)
- Leading connective on line B (and|or|but|for|because|that|which|...)
- Length-backstop: merged > 130 chars -> LONG-REVIEW (not auto-merge)

Exit code: 0 if zero violations, 1 if violations found.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

# Ensure the repo root is on sys.path so that `validators.parsing.*` and
# `atu_method.*` are importable when this script is run directly (not as a
# package).  __file__ is .../validators/colometry/<script>.py; repo root is
# two levels up.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ---------------------------------------------------------------------------
# Stage 1 surface patterns (unchanged from original)
# ---------------------------------------------------------------------------

# Auxiliary or finite main-verb predicate-lead patterns (line B start)
PREDICATE_LEAD_RE = re.compile(
    r"^\s*(?:did|doth|do|shall|will|would|wilt|hath|have|hast|"
    r"may|might|must|can|could|cannot|art|is|was|were|be|been)\s+\w+",
    re.IGNORECASE,
)

# Finite main-verb lead (no auxiliary)
MAIN_VERB_LEAD_RE = re.compile(
    r"^\s*(?:came|cometh|went|spake|said|gave|took|brought|made|sent|"
    r"deliver(?:ed|eth)?|protect(?:ed|s)?|yield(?:ed|eth|s)?|sav(?:e|ed|eth|es)?|"
    r"bless(?:ed|eth|es)?|come(?:th|s)?|go(?:eth|es)?|repent(?:ed|eth|s)?|"
    r"perish(?:ed|eth|es)?|prosper(?:ed|eth|s)?|fall(?:eth|en|s)?|"
    r"ris(?:e|en|eth|es)?|stand(?:eth|s|ing)?|sit(?:teth|s|ting)?|"
    r"dwell(?:eth|ed|s)?|caus(?:e|ed|eth|es)?|"
    r"appointed|assembled|departed|drew|fled|gathered|labored|murmur(?:ed|eth)?|"
    r"reign(?:ed|eth)?|return(?:ed|s)?|suffered)\s+\w+",
    re.IGNORECASE,
)

# Leading connectives that BLOCK firing (line B is a coordinate/subordinate
# clause, not an orphan predicate)
LEADING_CONNECTIVE_RE = re.compile(
    r"^\s*(?:and|or|but|for|because|that|which|who|whoso|whosoever|when|"
    r"while|if|though|unless|until|to|in|on|at|of|with|by|from|upon|nor|"
    r"yet|so|then|therefore|wherefore|notwithstanding)\b",
    re.IGNORECASE,
)

# R21 participial-absolute lead (line B starts with participial)
PARTICIPIAL_LEAD_RE = re.compile(
    r"^\s*(?:being|having|saying|seeing|knowing|believing|hearing|"
    r"finding|coming|going|speaking|teaching|preaching)\s+\w+",
    re.IGNORECASE,
)

# J5 save-clause lead
SAVE_CLAUSE_LEAD_RE = re.compile(r"^\s*save\b", re.IGNORECASE)

# R15 vocative-only line A (bare `O X,` style)
VOCATIVE_ONLY_RE = re.compile(r"^\s*O\s+(?:Lord|God|Father|Jesus|Christ|Israel|my\s+\w+)[,]?\s*$")

# J3 speech-act parenthetical (line A ends with `saith X`)
J3_SPEECH_TAG_RE = re.compile(
    r"saith\s+(?:the\s+)?(?:Lord|God|Father|prophet|Spirit|Lord\s+of\s+Hosts)\s*[,;]?\s*$",
    re.IGNORECASE,
)

LENGTH_BACKSTOP = 130

# ---------------------------------------------------------------------------
# Book filename -> conllu book-id mapping (avoids glob ambiguity for "mormon")
# ---------------------------------------------------------------------------
_FILENAME_TO_BOOK_ID: dict[str, str] = {
    "01-1_nephi-2020-sb-v2.txt": "1nephi",
    "02-2_nephi-2020-sb-v2.txt": "2nephi",
    "03-jacob-2020-sb-v2.txt": "jacob",
    "04-enos-2020-sb-v2.txt": "enos",
    "05-jarom-2020-sb-v2.txt": "jarom",
    "06-omni-2020-sb-v2.txt": "omni",
    "07-words_of_mormon-2020-sb-v2.txt": "words-of-mormon",
    "08-mosiah-2020-sb-v2.txt": "mosiah",
    "09-alma-2020-sb-v2.txt": "alma",
    "10-helaman-2020-sb-v2.txt": "helaman",
    "11-3_nephi-2020-sb-v2.txt": "3nephi",
    "12-4_nephi-2020-sb-v2.txt": "4nephi",
    "13-mormon-2020-sb-v2.txt": "mormon",
    "14-ether-2020-sb-v2.txt": "ether",
    "15-moroni-2020-sb-v2.txt": "moroni",
}

# ---------------------------------------------------------------------------
# UD Stage 2 data structures
# ---------------------------------------------------------------------------

class _UDBook:
    """Pre-built reverse index for a single book's UD parse.

    Maps v2-mine line number -> list of (Sentence, Token) pairs for every
    token that sits on that line.
    """

    def __init__(self, line_to_tokens: dict[int, list[tuple]]) -> None:
        # line_num -> [(sentence, token), ...]
        self._line_to_tokens = line_to_tokens

    def tokens_on_line(self, line_num: int):
        """Return list of (Sentence, Token) for every token on v2 line_num."""
        return self._line_to_tokens.get(line_num, [])


def _load_ud_book(v2_path: Path, conllu_path: Path) -> Optional["_UDBook"]:
    """Load and index a book's UD parse. Returns None if conllu absent."""
    if not conllu_path.exists():
        return None
    try:
        from validators.parsing.conllu_query import load_conllu
        from validators.parsing.line_mapping import build_line_map_full
    except ImportError:
        return None

    lmap = build_line_map_full(v2_path, conllu_path)
    sentences = load_conllu(conllu_path)
    # Build sent_id -> Sentence lookup
    sent_lookup: dict[str, object] = {s.sent_id: s for s in sentences}

    line_to_tokens: dict[int, list] = {}
    for (sid, tid), (lnum, _col) in lmap.items():
        sent = sent_lookup.get(sid)
        if sent is None:
            continue
        tok = sent.by_id(tid)
        if tok is None:
            continue
        line_to_tokens.setdefault(lnum, []).append((sent, tok))

    return _UDBook(line_to_tokens)


# ---------------------------------------------------------------------------
# Stage 2 UD checks
# ---------------------------------------------------------------------------

_NSUBJ_DEPRELS = {"nsubj", "nsubj:pass"}
_FINITE_VERB_UPOS = {"VERB", "AUX"}
_FINITE_MOODS = {"Ind", "Imp", "Sub"}  # VerbForm=Fin is unreliable in older parsers


def _has_finite_verb(sent, tok) -> bool:
    """True if tok is a finite verb (VERB/AUX with Mood feature, or bare root)."""
    if tok.upos not in _FINITE_VERB_UPOS:
        return False
    mood = tok.feats.get("Mood")
    if mood and mood in _FINITE_MOODS:
        return True
    # Fallback: if it's the root of the sentence and is a VERB, treat as finite
    if tok.head == 0 and tok.deprel == "root":
        return True
    return False


def _ud_stage2_passes(
    line_a_num: int,
    line_b_num: int,
    ud_book: "_UDBook",
) -> tuple[bool, str]:
    """Apply the 5 UD checks.

    Returns (passes: bool, reason: str).
    'reason' is empty string on pass; short tag on fail.
    """
    tokens_a = ud_book.tokens_on_line(line_a_num)
    tokens_b = ud_book.tokens_on_line(line_b_num)

    if not tokens_a or not tokens_b:
        # No parse coverage -> can't confirm; treat as REVIEW
        return False, "no-parse-coverage"

    # Collect the set of line-B line numbers for quick membership test
    sents_b = {id(s) for s, _ in tokens_b}
    toks_b_ids = {tok.id for _, tok in tokens_b}

    # ------------------------------------------------------------------
    # C4: line A has no vocative-deprel token
    #     Catches: "My son, / be faithful" where son=vocative
    # ------------------------------------------------------------------
    for _sent, tok in tokens_a:
        if tok.deprel == "vocative":
            return False, "C4-vocative-on-line-A"

    # ------------------------------------------------------------------
    # C5: line A has no finite root verb (not already a complete clause)
    #     Catches coordinate-chain cases: "seeketh not her own, / is not easily provoked"
    #     where seeketh is conj of a root verb — meaning it IS a finite predicate.
    # ------------------------------------------------------------------
    for sent, tok in tokens_a:
        if tok.upos in _FINITE_VERB_UPOS:
            # Check if it's a root or a conj of a root (= effectively a clause root)
            if tok.deprel == "root":
                return False, "C5-finite-root-on-line-A"
            if tok.deprel == "conj":
                # conj of root -> still a predicate in its own clause
                head = sent.head_of(tok)
                if head and head.deprel == "root":
                    return False, "C5-finite-conj-of-root-on-line-A"
            # Also catch auxiliaries that are the main finite element on line A
            # (e.g., "wilt thou" where wilt is AUX head=deliver on line B -> OK,
            # but "did they go," where did is AUX of a root already on line A)
            if tok.deprel.startswith("aux") and tok.head != 0:
                head_tok = sent.by_id(tok.head)
                if head_tok is not None:
                    head_line = None
                    for (s2, t2) in tokens_a:
                        if id(s2) == id(sent) and t2.id == head_tok.id:
                            head_line = line_a_num
                            break
                    if head_line == line_a_num:
                        return False, "C5-aux-with-head-on-line-A"

    # ------------------------------------------------------------------
    # C1: line A has an nsubj (or nsubj:pass) token whose head lands on line B
    #     This confirms line A is grammatically the subject of line B's verb.
    # ------------------------------------------------------------------
    c1_found = False
    for sent, tok in tokens_a:
        if tok.deprel not in _NSUBJ_DEPRELS:
            continue
        # tok is an nsubj; check if its head is on line B
        head_tok = sent.by_id(tok.head)
        if head_tok is None:
            continue
        # head must appear on line B
        for (s2, t2) in tokens_b:
            if id(s2) == id(sent) and t2.id == head_tok.id:
                c1_found = True
                break
        if c1_found:
            break

    if not c1_found:
        return False, "C1-no-nsubj-link-A-to-B"

    # ------------------------------------------------------------------
    # C2: line A is NOT a PP-object (no token on line A has deprel=case
    #     and its head also on line A, making it a preposition-headed NP)
    #     More precisely: the nsubj token on line A should not itself be
    #     the obl/nmod object of a preposition that also lives on line A.
    # ------------------------------------------------------------------
    for sent, tok in tokens_a:
        if tok.deprel not in _NSUBJ_DEPRELS:
            continue
        # Check if this nsubj token has a 'case' sibling (both sharing same head),
        # which would mean its head-NP is a PP-object
        head_tok = sent.by_id(tok.head)
        if head_tok is None:
            continue
        # The nsubj should point to line B — we already verified above.
        # Check whether the nsubj token's own head (on line A) is governed
        # by a preposition: look for case dependents of the nsubj itself
        for child in sent.dependents_of(tok, deprel="case"):
            # If this case marker is on line A, the NP is inside a PP
            for (s2, t2) in tokens_a:
                if id(s2) == id(sent) and t2.id == child.id:
                    return False, "C2-PP-object-on-line-A"

    # ------------------------------------------------------------------
    # C3: line B root verb has no independent nsubj on line B itself
    #     Catches: "wilt thou deliver me" where thou=nsubj lives on line B
    # ------------------------------------------------------------------
    # Find the root verb on line B
    root_b = None
    for sent, tok in tokens_b:
        if tok.deprel == "root":
            root_b = (sent, tok)
            break
    # If no root found on line B, look for the highest-head token on line B
    # (some sentences span multiple lines; the root may be on line A)
    if root_b is None:
        # Find the token on line B whose head is either 0 or on a different line
        for sent, tok in tokens_b:
            head_tok = sent.by_id(tok.head)
            if head_tok is None:
                root_b = (sent, tok)
                break

    if root_b is not None:
        sent_r, tok_r = root_b
        # Find all nsubj dependents of tok_r
        for child in sent_r.dependents_of(tok_r):
            if child.deprel not in _NSUBJ_DEPRELS:
                continue
            # Is this nsubj token on line B?
            for (s2, t2) in tokens_b:
                if id(s2) == id(sent_r) and t2.id == child.id:
                    return False, "C3-nsubj-already-on-line-B"

    return True, ""


# ---------------------------------------------------------------------------
# Stage 1 helpers (unchanged)
# ---------------------------------------------------------------------------

def _line_ends_in_comma_or_semicolon(line: str) -> bool:
    stripped = line.rstrip()
    return stripped.endswith(",") or stripped.endswith(";")


def _is_orphan_predicate_line(line: str) -> bool:
    """Detect bare-predicate line: auxiliary or main-verb lead, no connective,
    no participial, no save-clause."""
    if LEADING_CONNECTIVE_RE.match(line):
        return False
    if PARTICIPIAL_LEAD_RE.match(line):
        return False
    if SAVE_CLAUSE_LEAD_RE.match(line):
        return False
    return bool(PREDICATE_LEAD_RE.match(line) or MAIN_VERB_LEAD_RE.match(line))


def _is_blocked_line_a(line: str) -> bool:
    """SCOPE-exclusions on line A: bare vocative, J3 speech-tag tail."""
    if VOCATIVE_ONLY_RE.match(line):
        return True
    if J3_SPEECH_TAG_RE.search(line):
        return True
    return False


VERSE_NUM_RE = re.compile(r"^\s*\d+:\d+\s*$")


def parse_verse_blocks(content: str):
    """Yield (block_start_line_num, block_lines) for v2-mine verse blocks."""
    lines = content.splitlines()
    buf: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                yield buf[0][0], [t[1] for t in buf]
                buf = []
            continue
        buf.append((i, line))
    if buf:
        yield buf[0][0], [t[1] for t in buf]


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def scan_file(path: Path, ud_book: Optional["_UDBook"] = None) -> list[dict]:
    violations = []
    content = path.read_text(encoding="utf-8")
    for block_start, block_lines in parse_verse_blocks(content):
        # Skip verse-marker lines from analysis
        content_indices = [i for i, ln in enumerate(block_lines) if not VERSE_NUM_RE.match(ln)]
        for idx_pos, i in enumerate(content_indices):
            if idx_pos + 1 >= len(content_indices):
                continue
            line_a = block_lines[i]
            j = content_indices[idx_pos + 1]
            line_b = block_lines[j]

            # --- Stage 1 surface filter ---
            if not _line_ends_in_comma_or_semicolon(line_a):
                continue
            if _is_blocked_line_a(line_a):
                continue
            if not _is_orphan_predicate_line(line_b):
                continue

            merged = line_a.rstrip() + " " + line_b.lstrip()
            line_a_num = block_start + i
            line_b_num = block_start + j

            # Length backstop (unchanged; takes precedence over Stage 2)
            if len(merged) > LENGTH_BACKSTOP:
                violations.append({
                    "file": path.name,
                    "kind": "subject-orphan-predicate-LONG-REVIEW",
                    "start_line_num": line_a_num,
                    "end_line_num": line_b_num,
                    "matched_text": (line_a.strip()[:70] + " / " + line_b.strip()[:70]),
                    "merged_length": len(merged),
                    "ud_reason": "",
                })
                continue

            # --- Stage 2 UD filter ---
            if ud_book is not None:
                passes, reason = _ud_stage2_passes(line_a_num, line_b_num, ud_book)
                kind = (
                    "subject-orphan-predicate-STRONG" if passes
                    else "subject-orphan-predicate-REVIEW"
                )
            else:
                # No UD data available: fall back to Stage 1 label
                kind = "subject-orphan-predicate"
                reason = ""

            violations.append({
                "file": path.name,
                "kind": kind,
                "start_line_num": line_a_num,
                "end_line_num": line_b_num,
                "matched_text": (line_a.strip()[:70] + " / " + line_b.strip()[:70]),
                "merged_length": len(merged),
                "ud_reason": reason,
            })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2",
    )
    ap.add_argument(
        "--conllu-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/parses/llm-direct",
    )
    ap.add_argument(
        "--no-ud", action="store_true",
        help="Disable Stage 2 UD filter (Stage 1 surface only)",
    )
    args = ap.parse_args()

    v2_dir = Path(args.v2_dir)
    conllu_dir = Path(args.conllu_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        # Resolve UD book for Stage 2
        ud_book = None
        if not args.no_ud:
            book_id = _FILENAME_TO_BOOK_ID.get(path.name)
            if book_id:
                conllu_path = conllu_dir / f"{book_id}.conllu"
                ud_book = _load_ud_book(path, conllu_path)

        all_violations.extend(scan_file(path, ud_book))

    print("=" * 72)
    print("M4-BoFM-1 (Subject-Orphan Predicate Completion) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    strong = [v for v in all_violations if v["kind"] == "subject-orphan-predicate-STRONG"]
    review = [v for v in all_violations if v["kind"] == "subject-orphan-predicate-REVIEW"]
    review_long = [v for v in all_violations if v["kind"] == "subject-orphan-predicate-LONG-REVIEW"]
    stage1_only = [v for v in all_violations if v["kind"] == "subject-orphan-predicate"]

    print(f"  STRONG-MERGE-CANDIDATE (Stage 1+2 pass, length OK): {len(strong)}")
    print(f"  REVIEW-REQUIRED (Stage 2 demoted): {len(review)}")
    print(f"  LONG-REVIEW (merged > {LENGTH_BACKSTOP} chars): {len(review_long)}")
    if stage1_only:
        print(f"  STAGE-1-ONLY (no UD parse available): {len(stage1_only)}")
    print()

    for v in all_violations:
        reason_str = f" [{v['ud_reason']}]" if v.get("ud_reason") else ""
        print(
            f"[{v['kind']}]{reason_str}  {v['file']}:{v['start_line_num']}-{v['end_line_num']} "
            f"(merged_len={v['merged_length']})"
        )
        print(f"    {v['matched_text'][:160]}")
        print()

    print(f"RESULT: violations={len(all_violations)} status={'FAIL' if all_violations else 'CLEAN'}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
