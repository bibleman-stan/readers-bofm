"""Run UD tools validate.py on a CoNLL-U file, return {sent_id: error_count}.

Used as the per-sentence delta gate: a UD correction must not introduce
NEW validation errors beyond what the baseline parse already had.

Run standalone:  py -3 5-machinery/scripts/ud_validate_helper.py <conllu_path>
Import:          from ud_validate_helper import validate_per_sent
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CLI = REPO.parent / "ud-tools" / "udtools" / "src" / "udtools" / "cli.py"

# Validator output line: "[Line N Sent <sent_id>]: [LEVEL CLASS test-id] message"
RE_INC = re.compile(r"^\[Line \d+ Sent ([^\]]+)\]:\s*\[")


def validate_per_sent(conllu_path):
    """Returns ({sent_id: error_count}, total_errors)."""
    proc = subprocess.run(
        ["py", "-3", str(CLI), "--lang", "en", "--max-err", "0",
         "--no-warnings", str(conllu_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    counts = {}
    for line in out.splitlines():
        m = RE_INC.match(line)
        if m:
            sid = m.group(1)
            counts[sid] = counts.get(sid, 0) + 1
    total = sum(counts.values())
    return counts, total, out


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    counts, total, _ = validate_per_sent(sys.argv[1])
    print(f"Total errors: {total}")
    print(f"Sentences with errors: {len(counts)}")
    for sid in sorted(counts):
        print(f"  {sid}: {counts[sid]}")


if __name__ == "__main__":
    main()
