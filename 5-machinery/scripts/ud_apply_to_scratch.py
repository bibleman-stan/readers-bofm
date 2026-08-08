"""Apply UD-correction survivors to a scratch v0-cache (no production impact).

For each survivor's edit_groups: locate the verse's sentence in the scratch
v0-cache JSON, apply each edit to the matching token (column maps to JSON
field). Edits within a group apply atomically — group fails -> verse rolls
back (whole verse restored to baseline state).

Also writes the corrected CoNLL-U for validate-gate consumption.

Run:  py -3 5-machinery/scripts/ud_apply_to_scratch.py <survivors_json> <scratch_dir>
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

    by_book_cache = {}
    applied, rolled_back = 0, 0
    corrected_conllu_blocks = []
    for sv in survivors:
        ref = sv["ref"]
        for group in sv["edit_groups"]:
            touched_sents = set()
            for edit in group["edits"]:
                book, ch, v, si = _sent_index(edit["sent_id"])
                touched_sents.add((book, ch, v, si))
            backups = {}
            success = True
            for edit in group["edits"]:
                book, ch, v, si = _sent_index(edit["sent_id"])
                if book not in by_book_cache:
                    by_book_cache[book] = json.loads((scratch_dir / f"{book}.json").read_text(encoding="utf-8"))
                key = f"{ch}:{v}"
                sents_for_verse = by_book_cache[book].get(key, [])
                if si >= len(sents_for_verse):
                    success = False; break  # sentence index out of bounds (verse merged post-spray)
                sent = sents_for_verse[si]
                tok_idx = edit["token"] - 1
                if tok_idx < 0 or tok_idx >= len(sent):
                    success = False; break
                col_idx = COL_TO_IDX.get(edit["column"].upper())
                if col_idx is None:
                    success = False; break
                if (book, ch, v, si, tok_idx, col_idx) not in backups:
                    backups[(book, ch, v, si, tok_idx, col_idx)] = sent[tok_idx][col_idx]
                new_val = edit["new"]
                if edit["column"].upper() == "HEAD":
                    try: new_val = int(new_val)
                    except (TypeError, ValueError): success = False; break
                sent[tok_idx][col_idx] = new_val
            if not success:
                for (b, c, v_, si, ti, ci), val in backups.items():
                    by_book_cache[b][f"{c}:{v_}"][si][ti][ci] = val
                rolled_back += 1
            else:
                applied += 1

    for book, data in by_book_cache.items():
        (scratch_dir / f"{book}.json").write_text(json.dumps(data), encoding="utf-8")
    for sv in survivors:
        ref = sv["ref"]
        for sid in sv["sent_ids"]:
            book, ch, v, si = _sent_index(sid)
            if book not in by_book_cache:
                continue
            sents_for_verse = by_book_cache[book].get(f"{ch}:{v}", [])
            if si >= len(sents_for_verse):
                continue  # verse-merged post-spray; sentence index out of bounds
            sent = sents_for_verse[si]
            text = " ".join((t[FORM] or "") for t in sent)
            corrected_conllu_blocks.append(emit_sentence(sid, text, sent))

    out_conllu = scratch_dir / "ud-pilot-corrected.conllu"
    out_conllu.write_text("\n\n".join(corrected_conllu_blocks) + "\n\n", encoding="utf-8")
    print(f"Applied {applied} edit_groups, rolled back {rolled_back}.")
    print(f"Scratch cache: {scratch_dir}")
    print(f"Corrected CoNLL-U: {out_conllu}")


if __name__ == "__main__":
    main()
