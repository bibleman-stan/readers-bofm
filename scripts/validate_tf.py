#!/usr/bin/env python3
"""TF validation suite — the release gate from atu-method/docs/03-implementation/substrate.md §9 (the Opus red-team).

A built TF must pass ALL of these before deploy, not merely "it loads". Run against any version dir:
    python scripts/validate_tf.py 0.1
Reports PASS/FAIL/GAP per check. GAP = the fabric lacks the feature needed to even run the check
(i.e. an audit flaw that is still open in that version); the v0.2 build closes the GAPs.

Checks:
  1. round-trip      — concatenated `form` per verse == NFC v0 source (mod whitespace)
  2. atu-count       — `atu` node count per verse == deployed v2 segmentation line count (fail loud)
  3. edge-integrity  — every non-root token has exactly one `head` edge; edge-less count == #sentence-roots
                       (needs `is_root` + a `sentence` node; GAP until v0.2)
  4. provenance      — every `atu` carries `boundary_source`; every word carries `syn_source` (GAP until v0.2)
  5. cross-corpus    — one canonical UD query returns comparable hits here + on a gold corpus
                       (N/A until the harmonization layer exists; reported, not enforced yet)
"""
import sys, re, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")
import bofm_generate as B
from tf.fabric import Fabric

REPO = Path(__file__).resolve().parent.parent
VERSION = sys.argv[1] if len(sys.argv) > 1 else "0.1"
_REF = re.compile(r"^\d+:\d+$")
def nfc(s): return unicodedata.normalize("NFC", s)
def squash(s): return re.sub(r"\s+", "", nfc(s))

BOOK_NAME = {"1nephi":"1 Nephi","2nephi":"2 Nephi","jacob":"Jacob","enos":"Enos","jarom":"Jarom",
    "omni":"Omni","words-of-mormon":"Words of Mormon","mosiah":"Mosiah","alma":"Alma",
    "helaman":"Helaman","3nephi":"3 Nephi","4nephi":"4 Nephi","mormon":"Mormon","ether":"Ether","moroni":"Moroni"}
NAME_BOOK = {v: k for k, v in BOOK_NAME.items()}


def v2_line_counts():
    out = {}
    for book in B.BOOKFILE:
        cur = None
        for ln in B._v2_target(book).read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if _REF.match(s):
                c, v = s.split(":"); cur = (book, int(c), int(v)); out[cur] = 0
            elif cur and s:
                out[cur] += 1
    return out


def main():
    vdir = REPO/"data"/"tf"/VERSION
    has = lambda f: (vdir/f"{f}.tf").exists()
    optional = [f for f in ("is_root", "boundary_source", "syn_source", "head") if has(f)]
    api = Fabric(locations=str(REPO/"data"/"tf"), modules=VERSION, silent="deep").load(
        "form atu_seq atu_text ref book chapter verse " + " ".join(optional), silent="deep")
    if api is False:
        print(f"FAIL: TF v{VERSION} did not load"); return 1
    F, L = api.F, api.L
    Es = (lambda w: getattr(api.E, "head").f(w)) if has("head") else (lambda n: [])
    feats = {f for f in ("is_root", "boundary_source", "syn_source", "head") if has(f)}
    print(f"=== TF v{VERSION} validation suite ===")
    results = {}

    # 1. round-trip
    v0 = {(b, c, v): t for b in B.BOOKFILE for (c, v), t in B.read_v0(b).items()}
    bad_rt = []
    for vnode in F.otype.s("verse"):
        bk = NAME_BOOK.get(F.book.v(vnode)); c, v = F.chapter.v(vnode), F.verse.v(vnode)
        forms = " ".join(F.form.v(w) for w in L.d(vnode, "word"))
        src = v0.get((bk, c, v), "")
        if squash(forms) != squash(src):
            bad_rt.append(f"{bk} {c}:{v}")
    results["1 round-trip (form==NFC v0)"] = ("PASS" if not bad_rt else f"FAIL ({len(bad_rt)}; e.g. {bad_rt[:3]})")

    # 2. atu-count identity
    want = v2_line_counts(); bad_ct = []
    for vnode in F.otype.s("verse"):
        bk = NAME_BOOK.get(F.book.v(vnode)); c, v = F.chapter.v(vnode), F.verse.v(vnode)
        got = len(L.d(vnode, "atu")); exp = want.get((bk, c, v))
        if exp is not None and got != exp:
            bad_ct.append(f"{bk} {c}:{v} (tf={got} v2={exp})")
    results["2 atu-count identity"] = ("PASS" if not bad_ct else f"FAIL ({len(bad_ct)}; e.g. {bad_ct[:3]})")

    # 3. edge-integrity (needs is_root + sentence node)
    if "is_root" not in feats or "sentence" not in F.otype.all:
        results["3 edge-integrity"] = "GAP (no is_root / sentence node — open audit flaw #1; closes in v0.2)"
    else:
        edgeless = sum(1 for w in F.otype.s("word") if not Es(w))
        roots = sum(1 for w in F.otype.s("word") if F.is_root.v(w))
        results["3 edge-integrity"] = ("PASS" if edgeless == roots else f"FAIL (edgeless={edgeless} roots={roots})")

    # 4. provenance completeness
    if "boundary_source" not in feats or "syn_source" not in feats:
        results["4 provenance completeness"] = "GAP (no boundary_source/syn_source — open audit flaw #5; closes in v0.2)"
    else:
        miss_a = sum(1 for a in F.otype.s("atu") if not F.boundary_source.v(a))
        miss_w = sum(1 for w in F.otype.s("word") if not F.syn_source.v(w))
        results["4 provenance completeness"] = ("PASS" if not (miss_a or miss_w) else f"FAIL (atu={miss_a} word={miss_w})")

    # 5. cross-corpus golden query
    results["5 cross-corpus golden query"] = "N/A (pending harmonization layer — audit flaw #2; convergence track)"

    for k, v in results.items():
        print(f"  [{v.split()[0]:4}] {k}: {v}")
    hard_fail = any(r.startswith("FAIL") for r in results.values())
    print("\nRESULT:", "FAIL — do not deploy" if hard_fail else "OK on enforceable checks (GAPs tracked for v0.2)")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
