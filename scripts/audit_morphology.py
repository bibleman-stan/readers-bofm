#!/usr/bin/env python3
"""Morphology-coverage AUDIT -- the hardened replacement for archaic_normalize.gaps().

gaps() only inspected -eth/-est SUFFIXES, so it was structurally blind to irregular
EME forms with no such suffix ("art", "dost", "wilt") -- the exact gap that let
"thou art" mis-tag as a NOUN and silently fracture 27 verses' parses. This audit
finds the ACTIVE DAMAGE instead of guessing from spelling: a token that
archaic_normalize leaves UNCHANGED, that stanza tags as a NON-VERB (NOUN/ADJ/PROPN/
ADP), yet sits in a VERB SLOT (it heads a clause or has a subject/aux/object child).
Those are verbs the tagger missed -- the holes that corrupt the parse and cascade
into the binding rules.

Run AFTER a parse so it reads real tags:
  PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe -m scripts.audit_morphology
"""
from collections import Counter
import scripts.bofm_generate as G
from scripts.archaic_normalize import normalize

BOOKS = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
         'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']

# genuine EME-looking nouns/adjs that legitimately tag non-verb -- not gaps
_GENUINE = {
    "manifest", "earnest", "honest", "harvest", "tempest", "request", "interest",
    "forest", "modest", "midst", "amidst", "behest", "conquest", "rest", "priest",
    "beast", "least", "best", "most", "west", "east", "feast", "breast", "wrist",
    "list", "mist", "fist", "trust", "thirst", "athirst", "rust", "must", "lest",
    "christ", "ghost", "host", "dust", "against", "almost", "steadfast", "fast",
    "past", "nest", "unjust", "frost", "boast", "coast", "roast", "toast",
    "eldest", "greatest", "youngest", "strongest", "weakest", "darkest", "chiefest",
    "highest", "lowest", "nethermost", "uttermost", "foremost", "vilest", "poorest",
    "choicest", "wickedest", "humblest", "holiest", "mightiest",
    "teeth", "death", "breath", "faith", "wrath", "mouth", "forth", "earth", "worth",
    "nazareth", "seth", "heth", "japheth",
    "twentieth", "thirtieth", "fortieth", "fiftieth", "ninetieth", "eightieth",
    "first", "last", "fastest", "whilst", "amongst", "betwixt", "next", "midst",
}


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def audit():
    by_form = Counter()
    examples = {}
    for b in BOOKS:
        for (c, vs), sents in G.parse_book(b).items():
            for sent in sents:
                by = {_i(t.id): t for t in sent if _i(t.id) is not None}
                for t in sent:
                    f = (t.form or "")
                    lw = f.lower()
                    if not lw or lw in _GENUINE:
                        continue
                    if normalize(f) != f:                       # already normalized
                        continue
                    if t.upos not in ("NOUN", "ADJ", "PROPN", "ADP"):
                        continue
                    if not (lw.endswith(("st", "eth")) or lw in ("art", "doth", "hath")):
                        continue
                    # in a VERB SLOT? heads a clause, or has subject/aux/obj children
                    kids = [x for x in by.values() if _i(x.head) == _i(t.id)]
                    verby = (t.deprel or "").split(":")[0] in (
                        "root", "ccomp", "advcl", "conj", "parataxis", "acl") or any(
                        (k.deprel or "").split(":")[0] in ("nsubj", "csubj", "aux", "obj", "obl")
                        for k in kids)
                    if verby:
                        by_form[lw] += 1
                        examples.setdefault(lw, f"{b} {c}:{vs}")
    return by_form, examples


def main():
    by_form, examples = audit()
    if not by_form:
        print("Morphology audit: 0 active mis-tags. Coverage clean.")
        return 0
    print(f"Morphology audit -- archaic verbs mis-tagged as non-verbs in a verb slot "
          f"(coverage holes): {sum(by_form.values())} tokens, {len(by_form)} forms\n")
    for form, n in by_form.most_common():
        print(f"  {form:<12} {n:>4}   e.g. {examples[form]}")
    print("\nEach is a verb stanza missed -> add to archaic_normalize._IRREGULAR "
          "(or the lexicon) and re-parse.")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
