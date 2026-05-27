# Book of Mormon — Text-Fabric

A queryable [Text-Fabric](https://annotation.github.io/text-fabric/) representation of the Book of
Mormon, in the same ecosystem format as BHSA (Hebrew), Macula, and the LXX/Vulgate fabrics — so
BoFM can be queried structurally and compared cross-corpus (the ATU-convergence thesis).

Built by [`scripts/build_tf.py`](../../scripts/build_tf.py). Regenerate: `python scripts/build_tf.py`.

## Load

```python
from tf.fabric import Fabric
api = Fabric(locations="data/tf", modules="0.1").load("form lemma pos deprel atu_seq atu_text ref book chapter verse")
F, L, T = api.F, api.L, api.T
```

## Structure (version 0.1)

| node type | count | what |
|---|---|---|
| `book` | 15 | book (feature `book` = display name, `book_id` = slug) |
| `chapter` | 239 | chapter |
| `verse` | 6,604 | verse (`ref` = "c:v") |
| `atu` | 16,004 | **one deployed ATU line** — the colometric unit shipped to bomreader.com (`atu_seq`, `atu_text`) |
| `word` (slot) | 302,624 | token (`form`, `lemma`, `pos`, `deprel`) + a `head` dependency edge |

The `atu` layer is the distinctive one: word-membership of each ATU node matches the deployed
segmentation exactly (punctuation included), so you can query the corpus **by atomic-thought-unit**,
not just by verse.

## Provenance + the syntax caveat

- `form` / `lemma` / `pos` — from the cached **Stanza** UD parse of the v0 text. Solid.
- `deprel` / `head` — **PROVISIONAL.** This is the weak Stanza *modern-English* dependency parse —
  the very layer the **PCEEC-trained Early-Modern-English parser** will replace. It is included so
  the fabric is syntactically queryable now; the syntax layer upgrades in place when the EModE
  parser lands (see `private/substrate/emode-substrate/BUILD-PLAN.md`). Treat `head`/`deprel` as a
  draft, `form`/`pos`/`atu_*` as sound.
- The ATU layer = the deployed `data/text-files/v2/` segmentation (mechanical-first + the
  discourse-voice v2 adjudication).

Version bumps when the syntax layer is regenerated from the EModE parser.
