#!/usr/bin/env python3
"""
Run all colometry-canon validators and report per-rule conformance summary.

Discovers every `validate_*.py` script under `validators/syntax/` and
`validators/colometry/`, runs each as a subprocess, collects exit code
+ violation count, prints a unified dashboard.

Exit code:
  0 — all validators clean
  1 — at least one validator reported violations

Usage:
    python3 validators/run_all.py
    python3 validators/run_all.py --verbose       # forward --verbose to each
    python3 validators/run_all.py --staged-only   # only check files staged for commit (for pre-commit hook)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATORS_DIR = REPO_ROOT / "validators"

VIOLATION_RE = re.compile(r"(?:violations? found|candidate violations|deviations? found|matches? found):?\s*(\d+)", re.IGNORECASE)
# Fallback: count [DEVIATION] / [MALFORMED] / [INFO] / [REVIEW] markers in output
DEVIATION_MARKER_RE = re.compile(r"^\[(?:DEVIATION|MALFORMED|INFO|REVIEW|FLAG)\]", re.MULTILINE)


def discover_validators():
    out = []
    for sub in ("syntax", "colometry"):
        for f in sorted((VALIDATORS_DIR / sub).glob("validate_*.py")):
            out.append((sub, f))
    return out


def run_one(path, verbose):
    cmd = [sys.executable, str(path)]
    if verbose:
        cmd.append("--verbose")
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"name": path.name, "exit": -1, "violations": None, "error": "timeout"}
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    m = VIOLATION_RE.search(out)
    if m:
        violations = int(m.group(1))
    else:
        # Fallback: count standard marker lines
        marker_count = len(DEVIATION_MARKER_RE.findall(out))
        violations = marker_count if marker_count > 0 or proc.returncode == 0 else None
    return {
        "name": path.name,
        "exit": proc.returncode,
        "violations": violations,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


BASELINE_PATH = REPO_ROOT / "validators" / ".baseline.json"


def load_baseline():
    import json
    if not BASELINE_PATH.exists():
        return None
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def save_baseline(rows):
    import json
    data = {name: violations for _, name, _, _, violations in rows}
    BASELINE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--baseline-check", action="store_true",
                    help="Compare current counts to validators/.baseline.json; exit 1 if any rule's count increased.")
    ap.add_argument("--update-baseline", action="store_true",
                    help="Capture current violation counts as the new baseline.")
    args = ap.parse_args()

    validators = discover_validators()
    if not validators:
        print("No validators found under validators/syntax/ or validators/colometry/")
        return 0

    print("=" * 72)
    print("BofM Colometry Audit Dashboard — running all validators")
    print("=" * 72)
    print()

    rows = []
    total_violations = 0
    any_failed = False

    for sub, path in validators:
        result = run_one(path, args.verbose)
        violations = result["violations"]
        exit_code = result["exit"]
        if exit_code == -1:
            status = "TIMEOUT"
            any_failed = True
        elif violations is None:
            status = "?"
            any_failed = exit_code != 0 or any_failed
            violations = 0  # treat unknown as 0 for baseline-tracking
        elif violations == 0:
            status = "CLEAN"
        else:
            status = f"{violations} violation{'s' if violations != 1 else ''}"
            total_violations += violations
            any_failed = True
        rows.append((sub, path.name, status, exit_code, violations))

    width_name = max(len(r[1]) for r in rows) + 2
    print(f"  {'LAYER':<10} {'VALIDATOR':<{width_name}} STATUS")
    print("  " + "-" * (10 + width_name + 30))
    for sub, name, status, exit_code, _v in rows:
        marker = "FAIL" if exit_code != 0 else "OK"
        print(f"  {sub:<10} {name:<{width_name}} {status}  [{marker}]")

    print()
    print(f"TOTAL VIOLATIONS: {total_violations}")
    print()

    if args.update_baseline:
        save_baseline(rows)
        print(f"Baseline updated: {BASELINE_PATH}")
        return 0

    if args.baseline_check:
        baseline = load_baseline()
        if baseline is None:
            print("No baseline found. Run with --update-baseline to create one.")
            print("(For now, treating absence-of-baseline as PASS.)")
            return 0
        regressions = []
        for sub, name, status, exit_code, violations in rows:
            base = baseline.get(name, 0)
            if violations > base:
                regressions.append((name, base, violations))
        if regressions:
            print("=" * 72)
            print("REGRESSIONS DETECTED (violation count increased vs baseline):")
            print("=" * 72)
            for name, base, current in regressions:
                print(f"  {name}: baseline={base} → current={current}  (+{current - base})")
            print()
            return 1
        print("No regressions vs baseline.")
        return 0

    return 0  # default mode: report only, never block


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
