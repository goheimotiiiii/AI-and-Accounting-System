from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import Ledger


def load_ledger(path: str) -> Ledger:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return Ledger()

    with ledger_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return Ledger.from_dict(data)


def save_ledger(ledger: Ledger, path: str) -> None:
    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as handle:
        json.dump(ledger.to_dict(), handle, ensure_ascii=False, indent=2)
