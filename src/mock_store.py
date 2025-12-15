from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .schemas import Transaction

_DATA_DIR = Path(__file__).resolve().parents[1]
_CACHE: Dict[str, List[Transaction]] = {}

def get_transactions(account_id: str) -> List[Transaction]:
    if account_id in _CACHE:
        return _CACHE[account_id]
    file_path = _DATA_DIR / f"data/txns_{account_id}.json"
    if not file_path.exists():
        return []
    with open(file_path, "r") as f:
        tx_list = json.load(f)
    transactions = [Transaction.model_validate(tx) for tx in tx_list]
    _CACHE[account_id] = transactions
    return transactions

def find_transaction(account_id: str, tx_id: str) -> Optional[Transaction]:
    transactions = get_transactions(account_id)
    for tx in transactions:
        if tx.id == tx_id:
            return tx
    return None

if __name__ == "__main__":
    txns = get_transactions("A123")
    print(f"Loaded {len(txns)} transactions for account A123")
    tx = find_transaction("A123", "t002")