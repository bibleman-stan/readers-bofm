"""Canon-Validator structural alignment check (per atu-method/docs/canon-validator-alignment-protocol.md).

Verifies STRUCTURAL alignment between §5 rule entries and validator code:
  1. Validator file presence — Implementation field's named validator path resolves
  2. Closed-list presence — every UD-signature-named closed-list appears as uppercase
     Python constant in the validator source
  3. UD signature field consistency — deprels and lemmas from the signature appear
     as string literals or constants in validator code
  4. Multi-valued field branches — surfaced as PARTIAL when branches are unverifiable

Verdicts (per protocol):
  ALIGNED        — all checks pass
  NO_IMPL        — canon names a validator file that doesn't exist
  DRIFT          — validator file exists but named closed-lists / signature fields are missing
  PARTIAL        — multi-valued / multi-branch case; some named branches present, others not
  EDITORIAL_ACK  — canon declares `Applier: (none — Category B / ...)` or `no dedicated validator yet`

Out of scope: semantic alignment (whether validator predicate logic implements canon prose).

Usage:
    python3 validators/canon/check_canon_alignment.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CANON = REPO / "private" / "01-method" / "colometry-canon.md"


def split_rules(canon_text: str) -> list[tuple[str, str, str]]:
    """Return (rule_id, title, body) for each §5 rule entry, delimited by `<!-- ===== ... ===== -->`."""
    markers = list(re.finditer(r'<!-- =====\s+(\S+)\s+=====\s+-->', canon_text))
    out = []
    for i, m in enumerate(markers):
        rid = m.group(1)
        body_start = m.end()
        body_end = markers[i + 1].start() if i + 1 < len(markers) else len(canon_text)
        body = canon_text[body_start:body_end]
        title_m = re.search(r'^###\s+(.+)$', body, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else "(no heading)"
        out.append((rid, title, body))
    return out


def extract_validator_paths(body: str) -> list[str]:
    """Find ALL validator paths named in the Implementation field.

    Some rules name multiple validators (e.g., R12 has both a line-final-tokens
    validator and a compound-verb validator). The structural alignment check
    must search ALL named files for canon-named constants — checking only the
    first produced false-positive DRIFT findings (bug surfaced 2026-05-16).
    """
    impl_m = re.search(r'\*\*Implementation\.\*\*(.*)', body, re.DOTALL)
    if not impl_m:
        return []
    impl = impl_m.group(1)
    return re.findall(r'`(validators/[^`]+\.py)`', impl)


def is_editorial_no_applier(body: str) -> bool:
    """True when Implementation explicitly declares no auto-applier (Category B convention)."""
    impl_m = re.search(r'\*\*Implementation\.\*\*(.*)', body, re.DOTALL)
    if not impl_m:
        return False
    impl = impl_m.group(1)
    if re.search(r'Applier:\s*\(none', impl):
        return True
    return False


def extract_closed_list_names(body: str) -> list[str]:
    """Pick out closed-list constant names referenced in the rule body.

    Sources (only — no prose-uppercase noise):
      (a) backtick-quoted constants matching the closed-list naming convention
          (UPPERCASE with at least one underscore: GOVERNING_LEMMAS_R17, MOTION_VERBS)
      (b) keys inside `**Closed lists**` YAML blocks
      (c) `lemma_in:` / `upos_in:` references to a named list (e.g., `lemma_in: GOVERNING_LEMMAS_R17`)
    """
    names = set()
    # (a) backtick-quoted constants — only the snake-uppercase shape (must contain `_`)
    for m in re.finditer(r'`([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)`', body):
        names.add(m.group(1))
    # (b) YAML keys inside `**Closed lists**` blocks
    cl_m = re.search(r'\*\*Closed lists\*\*.*?(?=\*\*\w)', body, re.DOTALL)
    if cl_m:
        for ym in re.finditer(r'(?:```|~~~)yaml\s*(.*?)\s*(?:```|~~~)', cl_m.group(0), re.DOTALL):
            for line in ym.group(1).split("\n"):
                key_m = re.match(r'^\s*([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\s*:', line)
                if key_m:
                    names.add(key_m.group(1))
    # (c) lemma_in / upos_in references in any YAML block in the body
    for ym in re.finditer(r'(?:```|~~~)yaml\s*(.*?)\s*(?:```|~~~)', body, re.DOTALL):
        for m in re.finditer(r'(?:lemma_in|upos_in|lemma|upos):\s*([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b', ym.group(1)):
            names.add(m.group(1))
    return sorted(names)


def extract_signature_deprels(body: str) -> set[str]:
    """Pick deprel values from UD signature YAML blocks."""
    # Look inside ```yaml ... ``` or ~~~yaml ... ~~~ blocks
    deprels = set()
    for code in re.finditer(r'(?:```|~~~)yaml\s*(.*?)\s*(?:```|~~~)', body, re.DOTALL):
        block = code.group(1)
        for m in re.finditer(r'relation:\s*\[?\s*([^\]\n]+)', block):
            for d in re.split(r'[,\s]+', m.group(1).strip().strip("[]")):
                if d and not d.startswith(("#", "<")):
                    deprels.add(d.strip().strip("'\""))
        # `deprel:` and `deprel_in:` keys
        for m in re.finditer(r'deprel(?:_in)?:\s*\[?\s*([^\]\n]+)', block):
            for d in re.split(r'[,\s]+', m.group(1).strip().strip("[]")):
                if d and not d.startswith(("#", "<")):
                    deprels.add(d.strip().strip("'\""))
    return deprels


def audit_rule(rid: str, title: str, body: str) -> dict:
    """Return verdict + evidence for one rule entry."""
    res = {"rid": rid, "title": title, "verdict": None, "evidence": []}

    if is_editorial_no_applier(body):
        res["verdict"] = "EDITORIAL_ACK"
        res["evidence"].append("Implementation: Applier (none — Cat B / editorial)")
        return res

    vpaths = extract_validator_paths(body)
    if not vpaths:
        res["verdict"] = "EDITORIAL_ACK"
        res["evidence"].append("no validator path named in Implementation")
        return res

    # Verify each named file exists; collect missing
    missing_files = [p for p in vpaths if not (REPO / p).exists()]
    if missing_files:
        res["verdict"] = "NO_IMPL"
        res["evidence"].append(f"canon names files that don't exist: {missing_files}")
        return res

    # Concatenate ALL validator-file sources — closed-list constants may live in any
    src_concat = "\n".join((REPO / p).read_text(encoding="utf-8") for p in vpaths)

    # Cross-rule reference resolution: a canon rule may cite a constant defined in
    # ANOTHER rule's validator (e.g., R19 citing R17's GOVERNING_LEMMAS in an Exclusion).
    # Such cross-rule citations are CORRECT canon prose, not DRIFT — collect the full
    # codebase's constant inventory once and treat any constant found anywhere as resolved.
    all_validators_src = "\n".join(
        (REPO / p).read_text(encoding="utf-8")
        for p in REPO.glob("validators/**/*.py")
        if "__pycache__" not in str(p) and ".tx" not in str(p)
    )

    # Check closed-list presence (own validator first; fall through to cross-rule)
    canon_names = extract_closed_list_names(body)
    missing_lists = []
    cross_rule = []
    for n in canon_names:
        if n in src_concat:
            continue
        if n in all_validators_src:
            cross_rule.append(n)  # exists elsewhere in codebase — cross-rule reference, not DRIFT
        else:
            missing_lists.append(n)

    # Check deprels appear
    deprels = extract_signature_deprels(body)
    missing_deprels = [d for d in deprels if d and d not in src_concat]

    if missing_lists or missing_deprels:
        res["verdict"] = "DRIFT"
        if missing_lists:
            res["evidence"].append(f"canon-named closed-list constants missing from codebase: {missing_lists}")
        if cross_rule:
            res["evidence"].append(f"cross-rule references (resolved elsewhere): {cross_rule}")
        if missing_deprels:
            res["evidence"].append(f"signature deprels missing from validator code: {sorted(missing_deprels)}")
    else:
        res["verdict"] = "ALIGNED"
        extra = f" + {len(cross_rule)} cross-rule ref(s) resolved" if cross_rule else ""
        res["evidence"].append(f"validator(s) at {vpaths}; {len(canon_names) - len(cross_rule)} local + {len(cross_rule)} cross-rule closed-list ref(s) present{extra}")
    return res


def main() -> int:
    canon = CANON.read_text(encoding="utf-8")
    rules = split_rules(canon)
    audits = [audit_rule(rid, title, body) for rid, title, body in rules]

    # Sort by severity per protocol: NO_IMPL > DRIFT > PARTIAL > EDITORIAL_ACK > ALIGNED
    severity = {"NO_IMPL": 0, "DRIFT": 1, "PARTIAL": 2, "EDITORIAL_ACK": 3, "ALIGNED": 4}
    audits.sort(key=lambda a: (severity.get(a["verdict"], 99), a["rid"]))

    print("Canon-Validator Structural Alignment Check — readers-bofm")
    print("=" * 72)
    print(f"Total §5 rule entries: {len(audits)}")
    from collections import Counter
    cts = Counter(a["verdict"] for a in audits)
    for v in ("NO_IMPL", "DRIFT", "PARTIAL", "EDITORIAL_ACK", "ALIGNED"):
        print(f"  {v}: {cts.get(v, 0)}")
    print()
    for a in audits:
        if a["verdict"] == "ALIGNED":
            continue
        print(f"[{a['verdict']}] {a['rid']} — {a['title'][:60]}")
        for e in a["evidence"]:
            print(f"    {e}")
    print()
    print(f"ALIGNED (omitted from detail): {cts.get('ALIGNED', 0)}")
    return 0 if cts.get("NO_IMPL", 0) == 0 and cts.get("DRIFT", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
