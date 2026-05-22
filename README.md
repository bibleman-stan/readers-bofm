# Book of Mormon Reading Edition

> A web-based reading edition of the Book of Mormon designed for ESL readers,
> children, and newcomers. Live at **[bomreader.com](https://bomreader.com)**.

The text is presented as **atomic thought units (ATUs)** — one ATU per line —
so the reader can take in each line as a single, complete unit of meaning
before moving on. Archaic words can be toggled to modern equivalents.
Multiple study layers (deity references, biblical quotations, geography,
Hebrew poetry) can be overlaid. Audio narration is available per chapter.

---

## What this repository contains

| Path | Purpose |
|------|---------|
| `index.html` | Main single-page app (HTML/CSS/JS, all inline). |
| `books/*.html` | Generated HTML fragments, one per book of scripture. |
| `narration.js` | Audio playback module. |
| `sw.js` | Service worker (offline support; bump cache version on every CSS/JS/HTML change). |
| `build_book.py` | Converts ATU-formatted `.txt` sources -> HTML fragments. |
| `data/text-files/v2/` | Canonical source text files (one ATU per line). |
| `data/parses/llm-direct/` | CoNLL-U Universal-Dependencies parses, used by validators. |
| `data/syntax-reference/` | UD-taxonomy and other rule-reference tables. |
| `validators/` | Python rule-detector and applier suite (see Method section). |
| `private/01-method/colometry-canon.md` | Operational rule canon (BoFM-specific §5). |
| `audio/` | Narration MP3 files. |

The site is deployed via GitHub Pages from `main`; pushes go live in ~30s.

## How the editorial method works

The reading edition's distinctive feature is the **atomic thought unit (ATU)**:
each line on the page is calibrated to be readable as one complete unit of
meaning. Splitting and merging decisions are governed by a settled,
auditable rule canon that combines:

- A **universal framework** — generative principle, structural justifications,
  merge-overrides, decision procedure — codified in the sibling
  [`atu-method`](https://github.com/bibleman-stan/atu-method) repository at
  [`docs/framework.md`](https://github.com/bibleman-stan/atu-method/blob/main/docs/framework.md).
- A **BoFM-specific rule §5** with ~26 rules, each documented in MISRA-style
  operational form (Status / Category / Decidability / Layer / Rule / UD
  signature / Closed lists / Scope / Exclusions / Precedence / Examples /
  Implementation). Lives at `private/01-method/colometry-canon.md` (also
  available as a single tracked file in this repo despite the `private/`
  directory name).
- **Per-rule scholarship companions** — rationale, grammatical grounding,
  empirical evidence, intellectual lineage, adversarial history — at
  [`atu-method/scholarship/bofm/`](https://github.com/bibleman-stan/atu-method/tree/main/scholarship/bofm).

The validator suite (`validators/`) implements each rule as a UD-query or
surface-pattern detector. The pre-commit hook runs `validators/run_all.py`
in `--baseline-check` mode to prevent regressions.

## Local development

### Sibling-checkout convention

readers-bofm imports universal parsing/infrastructure primitives from the
sibling `atu-method` repository. Clone both alongside each other:

```
~/repos/
├── readers-bofm/      <-- this repo
└── atu-method/        <-- sibling
```

Then install `atu-method` as an editable Python package into your env (one
command, one time per env):

```bash
git clone git@github.com:bibleman-stan/atu-method.git
cd atu-method
python -m pip install -e .
```

After that, every Python process in this env can `from atu_method.parsing
import ...` and changes to atu-method are picked up automatically.

### Running the app locally

The site is a static SPA but `file://` won't work for the service worker
or fetch calls. Serve over HTTP:

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

### Rebuilding after source text edits

After editing files in `data/text-files/v2/`:

```bash
python build_book.py --all
```

Then bump the service-worker cache version in `sw.js` (find
`bomreader-vNN` and increment).

### Running validators

```bash
python validators/run_all.py
python validators/run_all.py --baseline-check     # what the pre-commit hook runs
python validators/run_all.py --update-baseline    # after intentional changes
```

Install the pre-commit hook once:

```bash
bash validators/hooks/install.sh
```

## Related work

| Repo | Purpose |
|------|---------|
| [`atu-method`](https://github.com/bibleman-stan/atu-method) | Universal framework, scholarship companions, Python infrastructure shared across reader editions. |
| [`readers-gnt`](https://github.com/bibleman-stan/readers-gnt) | Greek New Testament reader edition (in development). |
| [`readers-tanakh`](https://github.com/bibleman-stan/readers-tanakh) | Hebrew Bible reader edition (in development). |
| [`readers-gnt-morph`](https://github.com/bibleman-stan/readers-gnt-morph) | Morphological-annotation experiments for the GNT pipeline. |

## License

- **Code** (`*.py`, `*.js`, `*.html`, `*.css`): MIT — see [LICENSE](LICENSE).
- **Editorial method, canon, scholarship** (`private/01-method/`, prose docs):
  the methodology is shared work between this repository and `atu-method`;
  see [`atu-method/LICENSE-DOCS`](https://github.com/bibleman-stan/atu-method/blob/main/LICENSE-DOCS)
  (CC-BY-4.0).
- **Source text** (Book of Mormon): public-domain canonical text (1830/2020
  LDS editions); editorial layer (ATU line-break positions) is original to
  this project.

If you use the methodology or the editorial approach in your own work,
please cite per [`atu-method`'s CITATION.cff](https://github.com/bibleman-stan/atu-method/blob/main/CITATION.cff).

## Contact

`thebibleman77@gmail.com`
