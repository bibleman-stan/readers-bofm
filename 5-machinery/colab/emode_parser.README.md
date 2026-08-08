# EModE parser v2 (MacBERTh) — Colab run guide

`emode_parser.ipynb` is the **GPU keystone re-try**. The CPU parser (PCEEC→UD, spaCy) lost to Stanza
**21–6** on a blind head-to-head over BoFM scripture (the register gap, letters→scripture, ate the
gains). This notebook trains a **biaffine + MacBERTh** transformer (BERT pretrained on historical
English 1450–1950; graph-based, handles non-projectivity) on the **fixed-converter** (clause-type
error 6.6%, down from 38.7%), **author-held-out** data — the two things wrong with the first run.

## To run
1. Open `emode_parser.ipynb` in Colab → **Runtime → Change runtime type → T4 GPU**.
2. **Run all.** At cell 2, upload `train-package-v2.zip` —
   `readers-bofm/private/substrate/emode-substrate/train-package/train-package-v2.zip` (21 MB).
3. ~30–50 min on a T4. Cells 5–6 produce and download **two** files.

## Send BOTH back to Claude
- `test2_macberth.conllu` → per-label F (ccomp/advcl/acl:relcl/conj) on held-out authors.
- `bofm_macberth.conllu` → the **same blind 30-sentence gate vs Stanza** the CPU parser failed.

## The verdict rule (decided up front, so the test is honest)
- **MacBERTh beats Stanza on the gate →** keystone alive; build BoFM TF v0.2 on it.
- **MacBERTh does not beat Stanza →** close the parser track; BoFM rests on Stanza + the proven
  v2-adjudication sprays. (The register gap may persist regardless of model size, since the dependency
  *supervision* is still PCEEC letters — this bet tests whether a stronger encoder overcomes that.)
