#!/usr/bin/env python3
"""Early-Modern-English verb-morphology normalizer for PARSING ONLY.

stanza's POS tagger is trained on modern English and mis-tags EME verb
morphology: 51% of -eth/-est forms (596/1160 corpus-wide) come back as NOUN/ADJ
("liveth", "seeketh", "standeth", "desirest"), which cascades into broken
dependency structure (wrong clause-heads, fractured noun phrases like "good /
works"). This maps each archaic form to a recognizable modern form so the parser
tags it correctly. Applied 1:1 per token (count + order preserved) so the parse
maps back onto the ORIGINAL surface exactly; the rendered edition NEVER shows a
normalized form — normalization touches the parse substrate only.

SINGLE SOURCE OF TRUTH: the archaic->modern mappings are SOURCED FROM the build's
swap lexicon (`build_book.SIMPLE_SWAPS` + `KNOWN_ETH`), the same audit-hardened
table the modern-mode reading toggle uses, so the parse layer and the display
layer cannot drift. We take only single-token->single-token entries (1:1
alignment) and add a productive -eth/-est morphological fallback (mirroring
build_book's eth_replace) for forms the lexicon doesn't enumerate. Spelling need
not be perfect: stanza only needs a recognizable modern verb.

Coverage gaps (corpus -eth/-est forms absent from the lexicon) are reported by
`gaps()` and fed BACK to extend the swap lexicon's modern-mode coverage.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo root
from build_book import SIMPLE_SWAPS, KNOWN_ETH  # noqa: E402  source of truth

# Single-token grammatical swaps from the source-of-truth lexicon: pronouns
# (thou/thee/thy/ye/mine), auxiliaries/copulas (hath/doth/shalt/art...), and the
# enumerated -eth/-est verbs. Restricted to 1:1 (single-token target) so the
# parse stays index-aligned to the original token stream.
_MAP = {}
for _src, _tgt in SIMPLE_SWAPS:
    if " " not in _src and " " not in _tgt:
        _MAP.setdefault(_src.lower(), _tgt)
for _src, _tgt in KNOWN_ETH.items():
    if " " not in _src and " " not in str(_tgt):
        _MAP.setdefault(_src.lower(), _tgt)

# Irregular EME 2nd-person verb/aux/modal forms that the -eth/-est fallback CANNOT
# reach (no -eth/-est suffix) and that the lexicon under-covers. Audited 2026-05-22:
# stanza mis-tags "art" as NOUN ("Blessed ART thou" -> noun-phrase, no clause; 27x),
# "beholdest" as ADP (3x), "mightest" as ADJ -- each destroying the clause and
# cascading into the binding rules. The rest (dost/wilt/couldst...) usually tag VERB
# but with a wrong lemma, which corrupts lemma-keyed rules (verba dicendi, AICTP);
# normalizing fixes both. Targets are modern finite forms stanza tags VERB/AUX.
_IRREGULAR = {
    "art": "are", "beest": "be",
    "dost": "do", "doest": "do",
    "wilt": "will", "couldst": "could", "wouldst": "would",
    "shouldst": "should", "mayest": "may", "mightest": "might",
    "beholdest": "behold",
}
for _src, _tgt in _IRREGULAR.items():
    _MAP.setdefault(_src, _tgt)

# -eth/-est words that are NOT verbs — never touched by the morphological fallback.
NONVERB = {
    "greatest", "eldest", "highest", "lowest", "utmost", "latest", "nearest",
    "meanest", "honest", "manifest", "earnest", "harvest", "tempest", "request",
    "interest", "conquest", "forest", "modest", "midst", "amidst", "behest",
    "wickedest", "humblest", "holiest", "mightiest", "strongest", "weakest",
    "rest", "priest", "beast", "least", "best", "most", "west", "east",
    "death", "breath", "wreath", "beneath", "underneath", "youth", "truth",
    "faith", "wrath", "mouth", "forth", "north", "south", "earth", "worth",
    "teeth", "cloth", "both", "sabbath", "behemoth", "twelfth",
}


def _morph_eth(w):
    """Productive -eth -> 3sg -s fallback (mirrors build_book.eth_replace)."""
    stem = w[:-3]
    sl = stem.lower()
    if sl.endswith("i"):
        return stem[:-1] + "ies"
    if sl.endswith(("s", "sh", "ch", "x", "z")):
        return stem + "es"
    return stem + "s"


def _case(form, out):
    return out.capitalize() if form[:1].isupper() else out


def normalize(form):
    """Modern parse-surrogate for one token (or the token itself if not archaic).

    The lexicon (_MAP) already enumerates the curated -eth AND -est verbs +
    pronouns/auxiliaries. Beyond it we apply ONLY a productive -eth fallback
    (3sg verbs), guarded against ordinals (-tieth) and proper nouns; there is no
    blind -est fallback because -est is dominated by superlatives ("youngest")
    that a morphological strip would mangle. The few genuinely-uncovered -est
    thou-verbs (mayest/mightest/beholdest...) are reported by gaps() for promotion
    into the lexicon rather than guessed at here."""
    lw = form.lower()
    if lw in _MAP:
        return _case(form, _MAP[lw])
    if (len(lw) >= 5 and lw not in NONVERB and lw.endswith("eth")
            and not lw.endswith("tieth")          # ordinals: thirtieth, fortieth
            and not form[:1].isupper()):           # proper nouns: Nazareth, Japheth
        return _morph_eth(form)
    return form


_ARCH = re.compile(r"(eth|est)$", re.I)


def gaps(words):
    """Given an iterable of corpus word-forms, return the -eth/-est forms that the
    lexicon does NOT cover (handled only by the morphological fallback) — the
    feedback list for extending the swap lexicon's modern-mode coverage."""
    out = {}
    for w in words:
        lw = w.lower()
        if (len(lw) >= 5 and lw not in NONVERB and _ARCH.search(lw)
                and lw not in _MAP):
            out[lw] = out.get(lw, 0) + 1
    return out
