#!/usr/bin/env python3
"""Deterministic parse repairs for systematic stanza mis-parses of Early-Modern
English. Applied at parse load-time (idempotent), BEFORE the binding rules run --
the same architectural slot as archaic_normalize (which repairs morphology); this
repairs ATTACHMENT. Each repair targets a NAMED, structurally-detectable mis-parse
class, never a single verse.

R-INV  Inverted speech-attribution ("thus saith THE LORD, I have led...", "said HE,
       I have seen..."). stanza puts the POSTPOSED speech-subject ("the Lord", "he")
       as a non-subject (obj/nmod) of the QUOTED verb instead of the subject of the
       verbum dicendi, so the subject lands inside the quote and any speech-release
       strands it. Repair: re-attach that postposed nominal to the speech verb as its
       nsubj. After this, the M2 direct-speech release renders "thus saith the Lord,"
       as the frame line and the quotation as its own ATU(s).
"""
import sys
import scripts.bofm_generate  # noqa: F401 (ensures package import path)
from scripts.bofm_v1_fabric import _VERBA_DICENDI


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _repair_inverted_speech(sent):
    """R-INV. Returns count of re-attachments made in this sentence."""
    n = 0
    for v in sent:
        if (v.lemma or "").lower() not in _VERBA_DICENDI:
            continue
        # the verbum dicendi must NOT already have its own subject (the inverted
        # mis-parse is precisely the case where stanza failed to give it one).
        if any(_i(c.head) == _i(v.id) and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
               for c in sent):
            continue
        # its quoted complement
        ccomp = next((c for c in sent if _i(c.head) == _i(v.id)
                      and (c.deprel or "").split(":")[0] == "ccomp"), None)
        if ccomp is None:
            continue
        # postposed subject: a PROPN/PRON bound to the QUOTED verb as a NON-subject,
        # sitting immediately after the speech verb (the mis-grabbed attribution).
        for s in sent:
            if s.upos == "PROPN" and _i(s.head) == _i(ccomp.id) \
               and (s.deprel or "").split(":")[0] not in ("nsubj", "csubj", "vocative") \
               and 0 < (_i(s.id) - _i(v.id)) <= 3:
                s.head = v.id
                s.deprel = "nsubj"
                n += 1
                break
    return n


def repair(parsed):
    """Apply all repairs to a {(c,v): [[Tok,...], ...]} parse map, in place.
    Returns {repair_name: count}."""
    counts = {"R-INV": 0}
    for sents in parsed.values():
        for sent in sents:
            counts["R-INV"] += _repair_inverted_speech(sent)
    return counts


def _main():
    """Size the repair classes corpus-wide (read-only report)."""
    import scripts.bofm_generate as G
    books = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
             'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']
    total = {"R-INV": 0}
    affected = []
    for b in books:
        p = G.parse_book(b)  # NOTE: if wired into parse_book, this is already repaired;
        for (c, v), sents in p.items():
            before = sum(_count_inverted(s) for s in sents)
            if before:
                affected.append((b, c, v, before))
                total["R-INV"] += before
    print(f"R-INV inverted-speech mis-parses detectable: {total['R-INV']} in {len(affected)} verses")
    for r in affected[:30]:
        print(f"   {r[0]:<14} {r[1]}:{r[2]:<3} x{r[3]}")
    if len(affected) > 30:
        print(f"   ... +{len(affected)-30} more")


def _count_inverted(sent):
    """Detection-only twin of _repair_inverted_speech (does not mutate)."""
    n = 0
    for v in sent:
        if (v.lemma or "").lower() not in _VERBA_DICENDI:
            continue
        if any(_i(c.head) == _i(v.id) and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
               for c in sent):
            continue
        ccomp = next((c for c in sent if _i(c.head) == _i(v.id)
                      and (c.deprel or "").split(":")[0] == "ccomp"), None)
        if ccomp is None:
            continue
        for s in sent:
            if s.upos == "PROPN" and _i(s.head) == _i(ccomp.id) \
               and (s.deprel or "").split(":")[0] not in ("nsubj", "csubj", "vocative") \
               and 0 < (_i(s.id) - _i(v.id)) <= 3:
                n += 1
                break
    return n


if __name__ == "__main__":
    _main()
