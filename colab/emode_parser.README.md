# EModE parser — Colab run guide

`emode_parser.ipynb` trains an Early-Modern-English dependency parser on the PCEEC→UD data
(2.3M tokens) and re-parses the Book of Mormon, producing the good syntax layer for **TF v0.2**
(replacing the weak Stanza modern-English parse — the root cause of the bulk over-split classes).

## To run

1. Open `emode_parser.ipynb` in Colab → **Runtime → Change runtime type → GPU**.
2. Run cells top to bottom. When cell 2 prompts, upload **`train-package.zip`** —
   it's at `readers-bofm/private/substrate/emode-substrate/train-package/train-package.zip`
   (23 MB: train/dev/test.conllu + bofm_toparse.conllu).
3. Training is ~30–60 min on a T4 (watch dev LAS climb). Cell 4 reports held-out LAS/UAS.
4. Cells 5–6 re-parse the BoFM and download **`bofm_parsed.conllu`** + the trained parser zip.
5. Send `bofm_parsed.conllu` back to Claude → it rewrites the TF `deprel`/`head` → **v0.2** and
   runs the binding rules on the good syntax.

## Why MacBERTh

The encoder is `emanjavacas/MacBERTh` — BERT pretrained on historical English (1450–1950). It
sees EModE complementation/relativization (the `that`/`which`/`whom` structures Stanza mis-parses)
as in-domain, not as noise to normalize away. Register caveat: PCEEC is *letters*, the BoFM is
*scripture-register* EModE — close, not identical; the LAS on the test split bounds the claim.
