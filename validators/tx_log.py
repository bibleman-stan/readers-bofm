"""Transaction log for corpus appliers.

Each apply session writes a JSON log of {file, line, action, before, after}
entries. rollback.py reads the log and reverses entries whose current state
still matches `after`.

Usage inside an applier::

    from validators.tx_log import TxLog
    tx = TxLog("polysyndetic_verb_chain")
    tx.record_split(str(v2_path), line_idx, original_line, left, right)
    tx.commit()   # writes .tx/<rule>_YYYYMMDD-HHMMSS.json

Then to roll back::

    python validators/rollback.py --latest
    python validators/rollback.py --tx validators/.tx/polysyndetic_verb_chain_20260510-143022.json
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

REPO = Path(__file__).resolve().parent.parent
TX_DIR = REPO / "validators" / ".tx"


class TxLog:
    def __init__(self, rule_name: str) -> None:
        TX_DIR.mkdir(parents=True, exist_ok=True)
        self.rule_name = rule_name
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = TX_DIR / f"{rule_name}_{ts}.json"
        self.entries: list[dict] = []

    def record_split(
        self,
        file: str,
        line_idx: int,
        before_text: str,
        after_left: str,
        after_right: str,
    ) -> None:
        """Record a split: one line → two lines.

        line_idx is 0-based.  after_left is the new content of line_idx,
        after_right is the newly-inserted line at line_idx+1.
        """
        self.entries.append(
            {
                "action": "split",
                "file": file,
                "line_idx": line_idx,
                "before": before_text,
                "after_left": after_left,
                "after_right": after_right,
            }
        )

    def record_merge(
        self,
        file: str,
        line_idx: int,
        before_a: str,
        before_b: str,
        after: str,
    ) -> None:
        """Record a merge: two lines → one line.

        line_idx is 0-based; it is the line that absorbs the next.
        before_a is the original content of line_idx, before_b of line_idx+1,
        after is the merged content now at line_idx.
        """
        self.entries.append(
            {
                "action": "merge",
                "file": file,
                "line_idx": line_idx,
                "before_a": before_a,
                "before_b": before_b,
                "after": after,
            }
        )

    def commit(self) -> Path:
        """Write the log to disk.  Returns the path written."""
        # Timestamp is the trailing YYYYMMDD-HHMMSS portion: last 15 chars of stem
        # (format: <rule_name>_YYYYMMDD-HHMMSS  →  stem ends with _20260510-143022)
        stem = self.path.stem
        ts = stem[stem.rfind("_") + 1:]
        payload = {
            "rule": self.rule_name,
            "timestamp": ts,
            "entries": self.entries,
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return self.path

    def __len__(self) -> int:
        return len(self.entries)
