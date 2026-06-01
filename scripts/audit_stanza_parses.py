"""Deterministic audit of the Stanza UD layer for the diagnosed failure classes.

Walks data/parses/v0-cache/*.json (the raw Stanza dependency parses) and flags
verses that exhibit known parser-mistake patterns. Output is a ranked candidate
list for downstream review (hand-jam or v2-spray). NOT a fix; only a finder.

The five patterns come straight from the 2026-05-31 hostile audit (wlwl37c70)
that killed a28deab. Each is a STRUCTURAL signal the Stanza parse is internally
inconsistent or punctuation-driven in a way that can't be patched downstream.

Token layout in v0-cache JSON: [id, head, deprel, upos, lemma, form, start, end]

Run:  py -3 scripts/audit_stanza_parses.py
Out:  data/parses/audit/stanza-anomalies.json
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "data" / "parses" / "v0-cache"
OUT = REPO / "data" / "parses" / "audit" / "stanza-anomalies.json"

ID, HEAD, DEPREL, UPOS, LEMMA, FORM, START, END = range(8)

SUBORD_OR_COORD = {
    "and", "but", "or", "nor", "for", "yet", "so",
    "that", "because", "when", "while", "if", "unless", "though",
    "although", "since", "after", "before", "until", "lest",
}
MODALS = {"may", "might", "shall", "will", "would", "could", "should",
          "can", "must", "do", "did", "doth", "dost"}


def _by_id(sent):
    return {t[ID]: t for t in sent}


def _parent(sent_idx, t):
    return sent_idx.get(t[HEAD])


def _first_content(sent):
    for t in sent:
        if t[UPOS] != "PUNCT":
            return t
    return None


def p1_parallel_that_asymmetry(sent, sent_idx):
    """Multiple 'that' markers in one sentence whose parent-clause deprels
    disagree (e.g., one parataxis, one advcl). The Moroni 4:3 smoking gun."""
    thats = [t for t in sent
             if (t[FORM] or "").lower() == "that"
             and ((t[DEPREL] or "") == "mark" or t[UPOS] == "SCONJ")]
    if len(thats) < 2:
        return None
    parent_deprels = []
    for t in thats:
        p = _parent(sent_idx, t)
        if p is None:
            continue
        parent_deprels.append((p[DEPREL] or "").split(":")[0])
    if len(set(parent_deprels)) >= 2:
        counts = Counter(parent_deprels)
        return f"{len(thats)} 'that' markers, parent deprels: " + \
               ", ".join(f"{k}×{v}" for k, v in counts.most_common())
    return None


def p2_punctuation_driven_split(sents):
    """Verse split into >1 Stanza sentence where a later sentence begins with
    a coordinator/subordinator — the parser broke on a punctuation mark mid-
    coordinate-stack. Direct §2.1 violation feeder."""
    if len(sents) < 2:
        return None
    flagged_leaders = []
    for s in sents[1:]:
        first = _first_content(s)
        if first is None:
            continue
        lex = (first[FORM] or "").lower()
        if lex in SUBORD_OR_COORD:
            flagged_leaders.append(lex)
    if flagged_leaders:
        return f"{len(flagged_leaders)} continuation sentence(s) led by: " + \
               ", ".join(flagged_leaders)
    return None


def p3_modal_acl_relcl(sent, sent_idx):
    """A verb tagged acl:relcl whose immediate predecessor is 'that' (deprel
    mark) AND whose aux child is a modal — almost certainly a purpose-that
    clause mis-tagged as a restrictive relative."""
    flagged = []
    for t in sent:
        if (t[DEPREL] or "") != "acl:relcl":
            continue
        prev = None
        for s in sent:
            if s[ID] == t[ID] - 1:
                prev = s
                break
        if prev is None or (prev[FORM] or "").lower() != "that":
            continue
        if (prev[DEPREL] or "") != "mark" and prev[UPOS] != "SCONJ":
            continue
        has_modal_aux = any(
            (a[HEAD] == t[ID])
            and (a[DEPREL] or "").startswith("aux")
            and (a[LEMMA] or "").lower() in MODALS
            for a in sent
        )
        if has_modal_aux:
            flagged.append((t[FORM] or "").lower())
    if flagged:
        return f"purpose-'that' mis-tagged acl:relcl on verb(s): " + ", ".join(flagged)
    return None


def p4_long_distance_attachment(sent):
    """advcl / parataxis attached >30 tokens away from its head — Stanza often
    chooses the wrong attachment when coordination chains are long."""
    flagged = []
    for t in sent:
        dep = (t[DEPREL] or "").split(":")[0]
        if dep in ("advcl", "parataxis") and t[HEAD] != 0:
            dist = abs(int(t[ID]) - int(t[HEAD]))
            if dist > 30:
                flagged.append(f"{(t[FORM] or '').lower()}({dep},Δ={dist})")
    if flagged:
        return f"long-distance attachment(s): " + ", ".join(flagged[:5])
    return None


def p5_bigram_inconsistency(sent):
    """Within a sentence, a subordinator/coordinator bigram appears 2+ times
    with different deprels on the lead token. Stronger version of P1 — works
    for 'and he', 'when he', etc. not just 'that'."""
    bigrams = defaultdict(list)
    by_pos = sorted(sent, key=lambda t: t[ID])
    for i, t in enumerate(by_pos[:-1]):
        nxt = by_pos[i + 1]
        if (t[FORM] or "").lower() not in SUBORD_OR_COORD:
            continue
        key = ((t[FORM] or "").lower(), (nxt[FORM] or "").lower())
        bigrams[key].append((t[DEPREL] or "").split(":")[0])
    flagged = []
    for bg, deps in bigrams.items():
        if len(deps) >= 2 and len(set(deps)) >= 2:
            counts = Counter(deps)
            flagged.append(f"'{bg[0]} {bg[1]}': " +
                           ", ".join(f"{k}×{v}" for k, v in counts.most_common()))
    if flagged:
        return "; ".join(flagged[:3])
    return None


PATTERNS = [
    ("PARALLEL_THAT_ASYMMETRY",   "p1", p1_parallel_that_asymmetry, "sent"),
    ("PUNCTUATION_DRIVEN_SPLIT",  "p2", p2_punctuation_driven_split, "verse"),
    ("PURPOSE_THAT_AS_ACL_RELCL", "p3", p3_modal_acl_relcl,          "sent"),
    ("LONG_DISTANCE_ATTACHMENT",  "p4", p4_long_distance_attachment, "sent"),
    ("BIGRAM_DEPREL_DIVERGENCE",  "p5", p5_bigram_inconsistency,     "sent"),
]


def audit_verse(verse_sents):
    """Run all five patterns over one verse's sentence list. Returns list of
    flag dicts: [{class, sentence_idx, detail}, ...]."""
    flags = []
    for cls, _tag, fn, scope in PATTERNS:
        if scope == "verse":
            det = fn(verse_sents)
            if det:
                flags.append({"class": cls, "detail": det})
        else:
            for si, sent in enumerate(verse_sents):
                sent_idx = _by_id(sent)
                if fn.__code__.co_argcount == 2:
                    det = fn(sent, sent_idx)
                else:
                    det = fn(sent)
                if det:
                    flags.append({"class": cls, "sentence": si, "detail": det})
    return flags


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    summary = Counter()
    by_verse = {}
    for cache_file in sorted(CACHE.glob("*.json")):
        book = cache_file.stem
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        for cv, sents in data.items():
            flags = audit_verse(sents)
            if not flags:
                continue
            ref = f"{book} {cv}"
            for f in flags:
                summary[f["class"]] += 1
            by_verse[ref] = {
                "n_sentences": len(sents),
                "n_tokens": sum(len(s) for s in sents),
                "flags": flags,
            }
    out = {
        "_summary": dict(summary.most_common()),
        "_n_verses_flagged": len(by_verse),
        "_n_verses_total": sum(
            len(json.loads(p.read_text(encoding="utf-8")))
            for p in CACHE.glob("*.json")
        ),
        "verses": by_verse,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}")
    print(f"Verses flagged: {out['_n_verses_flagged']} / {out['_n_verses_total']}")
    print(f"Class summary:")
    for cls, n in summary.most_common():
        print(f"  {cls:30s} {n:5d}")


if __name__ == "__main__":
    main()
