# from __future__ import annotations

from datetime import date
from fastapi import APIRouter, HTTPException, Query

from src.schemas import Transaction
from src.mock_store import find_transaction, get_transactions
router = APIRouter(prefix="/tool", tags=["tool-api"])   

@router.get("/transactions", response_model=list[Transaction])
@router.get("/transactions")
def list_transactions(
    accountId: str = Query(..., description="Bank account id"),
    start: date = Query(..., description="YYYY-MM-DD inclusive"),
    end: date = Query(..., description="YYYY-MM-DD inclusive"),
    includePending: bool = Query(True, description="Include pending transactions"),
    limit: int = Query(500, ge=1, le=5000),
):
    """
    Sequence:
    1) Validate accountId is non-empty.
    2) Load all transactions for accountId from JSON via mock_store.get_transactions(accountId).
    3) Filter to date range (inclusive):
       - tx.postedAt.date() >= start AND tx.postedAt.date() <= end
    4) Filter out pending if includePending is False.
    5) Sort by postedAt.
    6) Apply limit.
    7) Return list[Transaction].
    """
    if not accountId:
        raise HTTPException(status_code=400, detail="accountId is required")
    all_txs = get_transactions(accountId)
    # Filter by date range
    filtered_txs = [
        tx for tx in all_txs
        if start <= tx.postedAt.date() <= end
    ]
    # Filter out pending if needed
    if not includePending:
        filtered_txs = [tx for tx in filtered_txs if not tx.isPending]
    # Sort newest first
    sorted_txs = sorted(filtered_txs, key=lambda tx: tx.postedAt, reverse=True)
    # Apply limit
    limited_txs = sorted_txs[:limit]
    return limited_txs

@router.get("/transactions/{txId}", response_model=Transaction)
def get_transaction_by_id(
    txId: str,
    accountId: str = Query(..., description="Bank account id"),
):
    """
    Sequence:
    1) Validate accountId and txId are non-empty.
    2) Load transaction via mock_store.find_transaction(accountId, txId).
    3) If not found, raise HTTP 404.
    4) Return Transaction (Pydantic model or dict).
    """

    if not accountId or not txId:
        raise HTTPException(status_code=400, detail="accountId and txId are required")
    tx = find_transaction(accountId, txId)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx