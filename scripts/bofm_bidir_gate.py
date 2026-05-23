#!/usr/bin/env python3
"""BoFM bidirectional-test GATE — the real yardstick, made repeatable.

Canon-conformance ('did this line trip an encoded rule') is an UPPER BOUND on
correctness, not a measure of it (bare 'And it came to pass.' is 100% conformant
yet a broken thought). The real yardstick is the bidirectional ATU test: each
rendered line must be exactly ONE complete thought. A 5-genre agent audit
(2026-05-22) measured ~51% of pure-method lines failing that test while the
metric reported 97.8% 'conformant'.

This module turns the audit's failure taxonomy into a fast STRUCTURAL detector
so the test can gate every rule change. It maps each rendered line back to its
UD tokens (char-range cursor over the verse text) and flags the failure classes
the agents found:

  FRAGMENT (fails FORWARD — not a complete thought on its own):
    stranded-relative      acl:relcl whose antecedent is on another line
    stranded-coordinate     conj verb, head on another line, no subject of its own
    stranded-subordinate    advcl/ccomp/acl headed off-line, line opens with sub.
    infinitive-orphan       opens 'to <VERB>', governor on another line
    participial-orphan       only non-finite participles, no subject
    verbless-fragment        no VERB/AUX and not a bare vocative/interjection
  OVER-MERGE (fails because two complete thoughts share one line):
    over-merge-multi-clause  >=2 finite clauses each with their own subject

Calibrated against the agent ground truth (see --calibrate). It is a PROXY: it
will not match agent judgment line-for-line, but tracking the same rate and the
same dominant classes makes it a valid iteration gate; periodic fresh agent
samples remain the ground truth.

Usage:
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_bidir_gate.py --calibrate
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_bidir_gate.py            # whole corpus
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_bidir_gate.py enos 1 --show
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import bofm_generate as G  # noqa: E402

G_FRAME_MARKS = {"when", "before", "after", "while", "whilst", "until", "as",
                 "if", "unless", "though", "although", "since", "whereas"}
G_SUBORD_ADV = {"when", "after", "before", "while", "whilst", "until", "since",
                "whereas", "where", "whensoever", "whithersoever", "wherein"}
_REL = {"who", "whom", "which", "whose", "whence"}
# phrase-internal deprels: a modifier bound tightly inside one constituent; if one
# of these crosses a line boundary, a single phrase was fractured across lines.
_PHRASE_INTERNAL = {"det", "amod", "nummod", "compound", "flat", "fixed",
                    "case", "aux", "cop"}
_SUB = {"because", "that", "when", "if", "though", "although", "since",
        "while", "whereas", "until", "before", "after", "unless"}
_ALNUM = re.compile(r"[^0-9a-zA-Z]")


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _key(s):
    return _ALNUM.sub("", s).lower()


def map_lines_to_tokens(verse_text, sentences, lines):
    """Return [(line_text, [(sx, Tok),...]), ...] by locating each rendered
    line's content span in verse_text (cursor left-to-right) and collecting the
    verse's tokens whose char-start falls in that span. Each token is paired with
    its sentence index `sx` so head lookups resolve within the right sentence
    (Tok uses __slots__, so the index rides alongside rather than as an attr)."""
    toks = []  # (sx, Tok)
    for sx, sent in enumerate(sentences):
        for t in sent:
            toks.append((sx, t))
    toks.sort(key=lambda st: (st[1].start if st[1].start is not None else 0))
    vkey = _key(verse_text)
    # Build a parallel index: for each char position in vkey, the original idx.
    orig_idx, j = [], 0
    for ci, ch in enumerate(verse_text):
        if not _ALNUM.match(ch):
            orig_idx.append(ci)
            j += 1
    # cursor in vkey space
    cur = 0
    out = []
    for ln in lines:
        lk = _key(ln)
        if not lk:
            out.append((ln, []))
            continue
        pos = vkey.find(lk, cur)
        if pos < 0:
            pos = vkey.find(lk)  # fallback: search from start
        lo_k, hi_k = pos, pos + len(lk)
        cur = hi_k
        lo_c = orig_idx[lo_k] if lo_k < len(orig_idx) else 0
        hi_c = orig_idx[hi_k - 1] + 1 if 0 < hi_k <= len(orig_idx) else len(verse_text)
        seg = [(sx, t) for sx, t in toks if t.start is not None and lo_c <= t.start < hi_c]
        out.append((ln, seg))
    return out


def classify(lines_toks):
    """Assign each line a failure class (or None=pass). lines_toks is the full
    verse mapping (each seg = list of (sx, Tok)) so we can test whether a token's
    head lands on another line."""
    # line index of every (sent_idx, token-id)
    where = {}
    for li, (_ln, seg) in enumerate(lines_toks):
        for sx, t in seg:
            where[(sx, _i(t.id))] = li

    def headline(sx, t):
        return where.get((sx, _i(t.head)))

    results = []
    for li, (ln, seg) in enumerate(lines_toks):
        content = [(sx, t) for sx, t in seg if t.upos != "PUNCT"]
        if not content:
            results.append(None)
            continue
        in_line = {(sx, _i(t.id)) for sx, t in seg}
        verbs = [(sx, t) for sx, t in content if t.upos in ("VERB", "AUX")]
        has_subj = any((t.deprel or "").split(":")[0] in ("nsubj", "csubj")
                       and (sx, _i(t.head)) in in_line for sx, t in seg)
        fsx, first = content[0]
        ff = first.form.lower()

        def head_off(sx, t):
            hl = headline(sx, t)
            return hl is not None and hl != li

        cls = None
        # mid-phrase fracture: a PHRASE-INTERNAL dependency (det/amod/compound/
        # case/aux/cop/poss — a modifier bound tightly inside one constituent)
        # crosses the line boundary, so a single phrase was split across lines
        # ("good / works", "the / voice"). Clausal relations crossing a boundary
        # are expected (that is where ATUs split); phrase-internal ones are breaks.
        if any((c.deprel or "").split(":")[0] in _PHRASE_INTERNAL and head_off(sx, c)
               for sx, c in content):
            results.append("mid-phrase-fracture"); continue
        # stranded relative: a relativizer clause whose antecedent is off-line
        rel = next((t for sx, t in seg if (t.deprel or "") == "acl:relcl"
                    and head_off(sx, t)), None)
        if rel is not None:
            cls = "stranded-relative"
        elif ff in _REL and head_off(fsx, first):
            cls = "stranded-relative"
        # stranded coordinate verb (no own subject, conj-head off-line)
        if cls is None:
            conj = next((t for sx, t in seg if (t.deprel or "").split(":")[0] == "conj"
                         and t.upos in ("VERB", "AUX") and head_off(sx, t)), None)
            if conj is not None and not has_subj:
                cls = "stranded-coordinate"
        # infinitive orphan / stranded subordinate
        if cls is None:
            sub = next((t for sx, t in seg if (t.deprel or "").split(":")[0]
                        in ("advcl", "ccomp", "csubj", "acl") and head_off(sx, t)), None)
            if sub is not None:
                if ff == "to":
                    cls = "infinitive-orphan"
                elif ff in _SUB or (len(content) > 1 and content[1][1].form.lower() in _SUB):
                    cls = "stranded-subordinate"
        # participial orphan: verbs present but all non-finite participles, no subj
        if cls is None and verbs and not has_subj:
            def is_participle(sx, v):
                kids = [c for csx, c in seg if csx == sx and _i(c.head) == _i(v.id)]
                return (any(c.upos == "AUX" and (c.lemma or "") in ("have", "be")
                            for c in kids)
                        and (v.deprel or "").split(":")[0] in ("advcl", "acl", "conj"))
            vverbs = [(sx, v) for sx, v in verbs if v.upos == "VERB"]
            if vverbs and all(is_participle(sx, v) for sx, v in vverbs):
                cls = "participial-orphan"
        # verbless fragment: a line with no verb is a fragment ONLY if it is a
        # stranded dependent -- it has no in-line clause anchor (root/parataxis)
        # and its top attaches OFF-line via a non-clausal relation (obl/nmod/case/
        # cc/appos...). A verbless line that IS a root/parataxis is a complete
        # verbless utterance: an interrogative whose archaic verb stanza mis-tags
        # ("what desirest thou?"), a nominal answer ("A virgin, most beautiful"),
        # an exclamative, or a verbless predicate -- those PASS.
        if cls is None and not verbs:
            has_anchor = any((t.deprel or "").split(":")[0] in ("root", "parataxis")
                             for sx, t in content)
            stranded = any(head_off(sx, t) and (t.deprel or "").split(":")[0] in
                           ("obl", "nmod", "advmod", "amod", "appos", "nummod",
                            "case", "cc", "conj", "obj", "iobj", "dep")
                           for sx, t in content)
            if stranded and not has_anchor:
                cls = "verbless-fragment"
        # over-merge: >=2 INDEPENDENT finite clauses on one line. A clause counts
        # as independent only if it has its OWN non-expletive subject and is NOT a
        # bound frame: the empty AICTP "came (to) pass" frame and temporal/
        # conditional advcls (mark in _FRAME_MARKS) bind to their clause and must
        # NOT be counted (else "it came to pass that Lehi prayed" reads as 2).
        if cls is None:
            def real_subj(sx, v):
                return any(csx == sx and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                           and _i(c.head) == _i(v.id) for csx, c in seg)
            def is_aictp(sx, v):
                return (v.lemma or "").lower() == "come" and any(
                    csx == sx and _i(c.head) == _i(v.id)
                    and (c.lemma or "").lower() == "pass"
                    and (c.deprel or "").split(":")[0] == "xcomp" for csx, c in seg)
            def frame_advcl(sx, v):
                if (v.deprel or "").split(":")[0] != "advcl":
                    return False
                # ANY subordinator = subordinate clause (frame/causal/purpose) ->
                # not an independent thought -> exclude. Detect by `mark`, by SCONJ,
                # or by a subordinator lemma stanza mis-tagged as advmod (fronted
                # "when"/"after"). A subordinator-less advcl with its own finite
                # subject is an asyndetic parallel colon (poetry) -> counts.
                return any(
                    csx == sx and _i(c.head) == _i(v.id) and (
                        (c.deprel or "") == "mark" or c.upos == "SCONJ"
                        or ((c.deprel or "").split(":")[0] == "advmod"
                            and (c.lemma or c.form or "").lower() in G_SUBORD_ADV))
                    for csx, c in seg)
            finite = 0
            for sx, v in verbs:
                base = (v.deprel or "").split(":")[0]
                if base not in ("root", "parataxis", "advcl", "conj"):
                    continue
                if is_aictp(sx, v) or frame_advcl(sx, v) or not real_subj(sx, v):
                    continue
                finite += 1
            if finite >= 2:
                cls = "over-merge-multi-clause"
        results.append(cls)
    return results


def audit_chapter(book, chap):
    verses = G.read_v0(book)
    parsed = G.parse_book(book)
    rows = []
    for (c, v) in sorted(verses):
        if c != chap:
            continue
        lines = G.deployed_atu_lines(book, c, v, verses[(c, v)], parsed.get((c, v), []))
        lt = map_lines_to_tokens(verses[(c, v)], parsed.get((c, v), []), lines)
        cls = classify(lt)
        for (ln, _seg), cl in zip(lt, cls):
            rows.append((v, ln, cl))
    return rows


def audit_book(book):
    verses = G.read_v0(book)
    parsed = G.parse_book(book)
    rows = []
    for (c, v) in sorted(verses):
        lines = G.deployed_atu_lines(book, c, v, verses[(c, v)], parsed.get((c, v), []))
        lt = map_lines_to_tokens(verses[(c, v)], parsed.get((c, v), []), lines)
        for (ln, _seg), cl in zip(lt, classify(lt)):
            rows.append((c, v, ln, cl))
    return rows


# agent ground-truth (2026-05-22 5-genre bidirectional audit)
GROUND = {
    ("enos", 1): (101, 37), ("1nephi", 1): (74, 35), ("2nephi", 8): (107, 47),
    ("alma", 5): (267, 146), ("moroni", 7): (178, 109),
}


def calibrate():
    print(f"{'sample':<14} {'lines':>6} {'detector-fail':>14} {'agent-fail':>11} {'det%':>6} {'agent%':>7}")
    print("-" * 64)
    from collections import Counter
    allcls = Counter()
    for (book, chap), (a_lines, a_fail) in GROUND.items():
        rows = audit_chapter(book, chap)
        nlines = len(rows)
        fails = [r for r in rows if r[2] is not None]
        for _, _, cl in fails:
            allcls[cl] += 1
        dpc = 100 * len(fails) / nlines if nlines else 0
        apc = 100 * a_fail / a_lines if a_lines else 0
        print(f"{book+' '+str(chap):<14} {nlines:>6} {len(fails):>14} {a_fail:>11} {dpc:>5.0f}% {apc:>6.0f}%")
    print("\nDetector failure classes across the 5 calibration chapters:")
    for cl, n in allcls.most_common():
        print(f"  {cl:<26} {n}")


def main():
    if "--calibrate" in sys.argv:
        calibrate(); return
    show = "--show" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) >= 2:
        rows = audit_chapter(args[0], int(args[1]))
        fails = [r for r in rows if r[2]]
        print(f"{args[0]} {args[1]}: {len(rows)} lines, {len(fails)} fail "
              f"({100*len(fails)/max(len(rows),1):.0f}%)")
        if show:
            for v, ln, cl in rows:
                if cl:
                    print(f"  {v:>3} [{cl}] {ln}")
        return
    # whole corpus
    from collections import Counter
    total = fail = 0
    cls = Counter()
    for book in G.BOOKFILE:
        rows = audit_book(book)
        total += len(rows)
        for _, _, _, cl in rows:
            if cl:
                fail += 1; cls[cl] += 1
    print(f"CORPUS: {total} lines, {fail} bidirectional-fail "
          f"({100*fail/max(total,1):.1f}%)  ->  {100*(1-fail/max(total,1)):.1f}% pass")
    for cl, n in cls.most_common():
        print(f"  {cl:<26} {n}")


if __name__ == "__main__":
    main()
