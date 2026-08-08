---
name: bofm-rebreak-at-scale
description: Apply a segmentation change to the whole Book of Mormon corpus and ship it to bomreader.com. Use whenever the task is a mass re-break, a v2-spray, applying a new structural class corpus-wide, a UD-correction sweep, or deploying re-segmentation live — anything of the form "change how the text breaks, everywhere, and put it on the site." Encodes the existing script chain and its mandatory gates in order.
---

# Re-breaking BoFM at scale

**This skill invents nothing.** Every step below is an existing, working script in `scripts/`. What was missing was a written record of the *order* and *which gates are not optional* — that knowledge lived in ~70 script filenames and in the git history of how they were chained, which is why it is easy to have built this and not recall it.

**The invariant:** the mechanism is the same for every structural class. Only the candidate-generator changes. "Apply Marschall-style re-breaks" and "sweep the and-that UD class" are the same pipeline with a different step 1.

## The chain

### 1. Generate candidates for the class

Scanners already exist per class — `scan_aictp.py`, `scan_participle_chain.py`, `scan_inverted_conditionals.py`, `yea_spray_candidates.py`, `extract_bare_relcl.py`, `extract_isaiah_aclrelcl.py`, `colometric_analysis.py`, `marschall_view.py`. A new class means a new scanner, and that is the ONLY bespoke part.

Normalize the output through `audit_to_candidates.py` → a candidate JSON in `data/parses/audit/`. Optionally enrich with `enrich_class_candidates.py`.

### 2. Build the adjudication workflow

```
py -3 scripts/build_spray_workflow.py <CLASS> --pilot
```

Writes a self-contained Workflow script to `scripts/workflows/`. The generated shape is fixed and is the canonical v2-spray: **Sonnet adjudicates per verse → 2 parallel Opus audits (over-merge lens + atomicity lens) → survivors of BOTH returned.** For book-scale work, chunked variants already exist (`bofm-book-audit-1nephi-chunk0of5.js` and siblings).

**The workflow HALTS at survivors. Deploy is a separate gated decision and must never be folded into the script.**

### 3. Apply survivors

```
py -3 scripts/apply_spray_survivors.py <spray-output.json>
```

Revalidates parity against the v0 master (text-identical, breaks moved only), writes to `data/text-files/v2-adjudicated/overrides.json` — currently **911 entries**, this is the deployed override layer — and to the gold yardstick as regression substrate with genre auto-tagging, then runs the twin-flag scan.

### 4. Regenerate

```
PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_generate.py <book> <chapter>
```

Live parse is `data/parses/v0-cache-conllu/<book>.conllu` (lever-2 LLM-corrected) — **never** `data/parses/ensemble/stanza/`, which is superseded reference only.

### 5. The gate that actually decides — quality_meter

```
py -3 scripts/quality_meter.py --candidate <v2dir> --baseline git:HEAD --out package.json
```

Read its docstring; it states the problem precisely: *"The canon validators catch canon-conformance but NOT over-merge, and the bidir gate is Stanza-circular."* It diffs candidate against baseline, isolates only verses whose segmentation changed, and emits an adjudication package. An LLM pass classifies each change improvement / regression / neutral; `tally()` returns net and by-genre.

**The gate is "candidate measurably BEATS baseline" — never "candidate is different."** Over-merge is Stan's red line and the validators are blind to it, which is the entire reason this gate exists.

Supporting gates: `bofm_bidir_gate.py`, `validate_stack_rule.py`, `fullclass_validate_gate.py`, `detect_residuals.py`, `prune_redundant_overrides.py`.

### 6. Ship and verify live

Commit, push, wait out the GitHub Pages window, then **fetch bomreader.com and confirm the user-visible change**. A successful commit is not a shipped change. For client-side-rendered output, verify the rendered DOM, not the raw HTML.

## What is NOT mechanizable here

The skill sequences the machinery; it does not make the editorial call. Do not let it become a way to skip step 5. If a class cannot produce candidates mechanically, it is not a spray — it is editorial work, and the three-lever framework says take what each lever reaches and accept the ceiling on what none does.

## Where the levers sit

1. Binding-rule additions in the fabric (`bofm_v1_fabric.py`) — permanent, try first for any structural class.
2. LLM-adjudicated UD corrections to `v0-cache/` — silver-tier substrate; workflows via `build_ud_correction_workflow*.py`, `build_ud_fullclass_workflow.py`, merged by `merge_fullclass_proposals.py`, gated by `fullclass_validate_gate.py`. **781 full-class candidates remain** in `data/parses/audit/ud-correction-fullclass-candidates.json`.
3. `overrides.json` v2-spray — judgment residuals neither rule nor UD-correction reaches. This chain.
