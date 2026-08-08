"""Sentence-merging UD applier for PUNCTUATION_DRIVEN_SPLIT proposals.

Standard ud_apply_to_scratch.py edits tokens within a single sentence. PDS
proposals routinely require CROSS-SENTENCE reattachment — Stanza split a
verse at a punctuation mark (period/semicolon) mid-coordinate-stack, and
Sonnet proposes attaching s1's root as conj of an s0 token (and similar
patterns across s2, s3).

Operation per PDS-affected verse:
  1. Concatenate all sentences of the verse into ONE sentence.
  2. Renumber tokens: s_k's token i becomes merged token (offset_k + i),
     where offset_k = total token count of s_0..s_{k-1}.
  3. Translate intra-sentence head references in s_k>0 by the same offset.
  4. Apply Sonnet's proposed edits to the merged sentence. HEAD values in
     the proposals are assumed to be in s0's numbering (Sonnet's
     cross-sentence reattachments cite "s0 token N" in rationales), which
     equals merged numbering since s0 is first. Within-sentence HEAD edits
     (s_k>0 → s_k>0) are rare in PDS and treated as same-sentence — the
     edit value (e.g. local id 5 in s1) needs the same offset_k applied.

The Sonnet proposal format doesn't carry an explicit `target_sentence`
field, so for HEAD edits we apply this heuristic: if the new HEAD value
equals 0, it's a root assignment; otherwise treat it as already
referencing a token in the merged tree (no further translation). This
works for the cross-sentence pattern (s_k>0 token → s0 token) which
dominates PDS proposals.

Run:  py -3 5-machinery/scripts/ud_apply_pds.py <survivors_json> <scratch_dir>
"""
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROD_CACHE = REPO / "data" / "parses" / "v0-cache"

sys.path.insert(0, str(REPO / "5-machinery" / "scripts"))
from ud_pilot_extract_baseline import emit_sentence, ID, HEAD, DEPREL, UPOS, LEMMA, FORM

COL_TO_IDX = {"ID": ID, "HEAD": HEAD, "DEPREL": DEPREL, "UPOS": UPOS,
              "LEMMA": LEMMA, "FORM": FORM}


def _sent_index(sent_id):
    """`book_ch_v_sN` -> (book, ch, v, si)"""
    parts = sent_id.rsplit("_s", 1)
    si = int(parts[1])
    rest = parts[0].rsplit("_", 2)
    book, ch, v = rest[0], int(rest[1]), int(rest[2])
    return book, ch, v, si


def merge_verse_sentences(sents):
    """[[tok,...,sent], ...] → ([merged_tok,...], [offsets per sent]).
    Each tok is [id, head, deprel, upos, lemma, form, start, end].
    Offsets: max original id in sentences 0..k-1, so sent_k's token id i
    becomes merged id (offset_k + i)."""
    merged = []
    offsets = []
    for sent in sents:
        offsets.append(max((t[ID] for t in merged), default=0))
        max_orig_in_sent = max((t[ID] for t in sent), default=0)
        for t in sent:
            new_t = list(t)
            new_t[ID] = t[ID] + offsets[-1]
            if t[HEAD] and t[HEAD] > 0:
                new_t[HEAD] = t[HEAD] + offsets[-1]
            merged.append(new_t)
    return merged, offsets


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    survivors_path = Path(sys.argv[1])
    scratch_dir = Path(sys.argv[2])
    scratch_dir.mkdir(parents=True, exist_ok=True)

    for book_file in PROD_CACHE.glob("*.json"):
        shutil.copy(book_file, scratch_dir / book_file.name)

    survivors = json.loads(survivors_path.read_text(encoding="utf-8"))
    if "result" in survivors and isinstance(survivors.get("result"), dict):
        survivors = survivors["result"]
    survivors = survivors.get("survivors", [])

    # Group proposals by verse
    by_verse = {}
    for sv in survivors:
        ref = sv["ref"]
        by_verse.setdefault(ref, []).append(sv)

    by_book_cache = {}
    applied, skipped = 0, 0
    merged_count = 0

    for ref, props in by_verse.items():
        book, cv = ref.rsplit(" ", 1)
        ch, v = (int(x) for x in cv.split(":"))
        if book not in by_book_cache:
            by_book_cache[book] = json.loads(
                (scratch_dir / f"{book}.json").read_text(encoding="utf-8"))
        key = f"{ch}:{v}"
        original_sents = by_book_cache[book].get(key) or []
        if not original_sents:
            skipped += len(props); continue

        # Merge ALL sentences of the verse (PDS premise: punctuation-driven
        # split should be reunified).
        merged, offsets = merge_verse_sentences(original_sents)
        if len(original_sents) > 1:
            merged_count += 1

        # Apply all proposals' edits to the merged sentence
        ok_for_verse = True
        for sv in props:
            for edit in sv["edit_groups"][0]["edits"]:
                _, _, _, si = _sent_index(edit["sent_id"])
                tok_orig_id = edit["token"]
                tok_merged_id = tok_orig_id + offsets[si] if si < len(offsets) else None
                if tok_merged_id is None:
                    ok_for_verse = False; break
                target = next((t for t in merged if t[ID] == tok_merged_id), None)
                if target is None:
                    ok_for_verse = False; break
                col_idx = COL_TO_IDX.get(edit["column"].upper())
                if col_idx is None:
                    ok_for_verse = False; break
                new_val = edit["new"]
                if edit["column"].upper() == "HEAD":
                    try: new_val = int(new_val)
                    except (TypeError, ValueError):
                        ok_for_verse = False; break
                target[col_idx] = new_val
            if not ok_for_verse:
                break

        if ok_for_verse:
            # Replace the verse's sentence list with the single merged sentence
            by_book_cache[book][key] = [merged]
            applied += len(props)
        else:
            skipped += len(props)

    for book, data in by_book_cache.items():
        (scratch_dir / f"{book}.json").write_text(
            json.dumps(data), encoding="utf-8")

    # Emit corrected CoNLL-U for validate-gating
    blocks = []
    for sv in survivors:
        ref = sv["ref"]
        book, cv = ref.rsplit(" ", 1)
        ch, v = (int(x) for x in cv.split(":"))
        if book not in by_book_cache: continue
        sents = by_book_cache[book].get(f"{ch}:{v}", [])
        for si, sent in enumerate(sents):
            sid = f"{book}_{ch}_{v}_s{si}"
            text = " ".join((t[FORM] or "") for t in sent)
            blocks.append(emit_sentence(sid, text, sent))
    out_conllu = scratch_dir / "ud-pilot-corrected.conllu"
    out_conllu.write_text("\n\n".join(blocks) + "\n\n", encoding="utf-8")

    print(f"Applied {applied} edits across {len(by_verse)} verses ({merged_count} merged multi-sent).")
    print(f"Skipped {skipped} (token-resolve fail).")
    print(f"Scratch cache: {scratch_dir}")
    print(f"Corrected CoNLL-U: {out_conllu}")


if __name__ == "__main__":
    main()
