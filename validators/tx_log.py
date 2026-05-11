"""Transaction log for readers-bofm corpus appliers.

Thin BoFM-specific wrapper around `atu_method.infrastructure.tx_log.TxLog`
that fixes the per-repo TX_DIR to `<readers-bofm>/validators/.tx/`. Callers
construct the log the same way as before -- e.g., `TxLog("rule_name")` --
without needing to pass the directory.

Usage inside an applier::

    from validators.tx_log import TxLog
    tx = TxLog("polysyndetic_verb_chain")
    tx.record_split(str(v2_path), line_idx, original_line, left, right)
    tx.commit()   # writes <readers-bofm>/validators/.tx/<rule>_YYYYMMDD-HHMMSS.json

For rollback::

    python validators/rollback.py --latest
    python validators/rollback.py --tx validators/.tx/polysyndetic_verb_chain_20260510-143022.json
"""

from __future__ import annotations

from pathlib import Path

from atu_method.infrastructure.tx_log import TxLog as _UniversalTxLog


REPO = Path(__file__).resolve().parent.parent
TX_DIR = REPO / "validators" / ".tx"


class TxLog(_UniversalTxLog):
    """BoFM-fixed-tx-dir variant of the universal TxLog."""

    def __init__(self, rule_name: str) -> None:
        super().__init__(rule_name=rule_name, tx_dir=TX_DIR)
