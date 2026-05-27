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

R-WLD  EME desiderative "would" ("I would THAT ye should remember ..." = "I wish/
       desire that ..."). stanza tags this volitional matrix "would" as a stranded
       modal AUX -- NOT as `aux` of a finite verb (the modal reading), but as a
       clause-level node (conj/parataxis/root/reparandum/acl/advcl/ccomp) with NO
       lexical verb of its own, its content sitting in the FOLLOWING `that`-clause.
       So the desiderative "would" surfaces as a stranded fragment ("...therefore I
       would" / "that ye should remember ..."). Repair: when "would" is a clause-level
       node (deprel != aux) whose IMMEDIATELY-following content token is a `that`
       SCONJ-mark heading a clause, re-tag "would" -> main VERB and re-attach that
       `that`-clause head as "would"'s `ccomp`. The existing complement-bind (fabric
       ccomp default) then reunites "I would that ye should remember ..." as one ATU.
       Discriminator is punctuation-invariant: "would" deprel (NOT aux = not a modal
       of a finite verb) + the `that` complementizer lexeme + clause-head attachment;
       the comma after "would" is never consulted. The 546 modal-AUX "would believe"/
       "would not give" cases (deprel == aux) are untouched -- only the small
       desiderative-matrix class re-tags. LOAD-BEARING: validated by Alma 32:22 render
       regression test -- disabling R-WLD strands "and I would" as its own line
       (verified 2026-05-26; the consistency audit's "output-inert" finding was
       incorrect for this verse).
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


def _repair_desiderative_would(sent):
    """R-WLD. Re-tag a stranded EME desiderative "would" to a main VERB governing its
    following `that`-clause as `ccomp`. Returns count of re-tags made."""
    n = 0
    toks = sorted(sent, key=lambda t: (_i(t.id) if _i(t.id) is not None else 0))
    for idx, w in enumerate(toks):
        if (w.form or "").lower() != "would":
            continue
        # MODAL guard: a `would` serving as `aux` of a finite verb ("would believe",
        # "would not give") is the 546-case modal reading -> never touched. Only a
        # CLAUSE-LEVEL `would` (it is a node in its own right, not an auxiliary) can
        # be the stranded desiderative matrix.
        wbase = (w.deprel or "").split(":")[0]
        if wbase == "aux":
            continue
        # REPARANDUM guard: stanza's `reparandum` (disfluency/restart) relation marks a
        # BROKEN sub-tree -- re-rooting a `that`-clause onto a reparandum-`would` shatters
        # the clause-atom grouping (the verse explodes into per-token lines). These
        # cases ALSO already render bound in the deployed edition (the `would that` is
        # glued within a larger clause), so there is nothing to repair. Restrict R-WLD
        # to genuine clause-node attachments (conj/parataxis/root/advcl/acl/ccomp/csubj),
        # where `would` is a real but DISCONNECTED node that strands at render.
        if wbase not in ("conj", "parataxis", "root", "advcl", "acl", "ccomp", "csubj"):
            continue
        # The immediately-following CONTENT token must be the `that` complementizer
        # (SCONJ `mark`) -- "would THAT ...". (Skip intervening punctuation only.)
        rest = [t for t in toks[idx + 1:] if (t.form or "").strip(",;:.!?—–’\"()")]
        nxt = rest[0] if rest else None
        if nxt is None or (nxt.form or "").lower() != "that" \
           or (nxt.deprel or "") != "mark" or nxt.upos != "SCONJ":
            continue
        # The `that`-clause head is the token `that` attaches to as its mark.
        clause_head = next((t for t in sent if _i(t.id) == _i(nxt.head)), None)
        if clause_head is None:
            continue
        # Re-tag: "would" becomes the desiderative main VERB; the that-clause head
        # becomes its `ccomp`. Keep "would"'s own deprel/head (its slot in the tree
        # is fine -- conj of the prior speech verb in Alma 32:22, etc.); we only give
        # it the complement so the complement-bind reunites the two segments.
        w.upos = "VERB"
        clause_head.head = w.id
        clause_head.deprel = "ccomp"
        n += 1
    return n


def repair(parsed):
    """Apply all repairs to a {(c,v): [[Tok,...], ...]} parse map, in place.
    Returns {repair_name: count}."""
    counts = {"R-INV": 0, "R-WLD": 0}
    for sents in parsed.values():
        for sent in sents:
            counts["R-INV"] += _repair_inverted_speech(sent)
            counts["R-WLD"] += _repair_desiderative_would(sent)
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
