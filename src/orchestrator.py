import os
import httpx
from src.schemas import Transaction

TOOL_BASE_URL = os.getenv("TOOL_BASE_URL", "http://localhost:8000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# ----------------------------
# Tool calls
# ----------------------------

async def tool_get_transactions(account_id: str, start: str, end: str) -> List[Transaction]:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{TOOL_BASE_URL}/tool/transactions", params={
            "accountId": account_id,
            "start": start,
            "end": end,
        })
        r.raise_for_status()
        return [Transaction.model_validate(x) for x in r.json()]
    
async def tool_get_transaction_by_id(account_id: str, tx_id: str) -> Transaction:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{TOOL_BASE_URL}/tool/transactions/{tx_id}", params={"accountId": account_id})
        r.raise_for_status()
        return Transaction.model_validate(r.json())
    
# ----------------------------
# Chat endpoint orchestration
# ----------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    q = await compile_queryspec(req.message)
    if not q.is_banking_domain:
        ui = UISpec(messages=[UIMessage(content="I can help with banking/account questions (transactions, spending, balance). What would you like to check?")])
        return ChatResponse(query=None, ui=ui)

    # compare-months requires two tool pulls
    if q.intent == "compare_months_why":
        today = date.today()
        this_start, this_end = month_bounds(today)
        last_start, last_end = month_bounds(this_start.replace(day=1) - (this_start - this_start))  # dummy; replaced below

        # correct last month bounds
        prev_month_last_day = this_start - (this_start - this_start)  # just date copy
        prev_month_last_day = this_start - (this_start - this_start)  # no-op, keep simple
        # do it properly:
        last_month_last_day = this_start - (this_start - this_start)  # placeholder

        # easier: reuse month_bounds by stepping back one day from this_start
        last_month_last_day = this_start - __import__("datetime").timedelta(days=1)
        last_start, last_end = month_bounds(last_month_last_day)

        this_txs = await tool_get_transactions(req.accountId, this_start.isoformat(), this_end.isoformat())
        last_txs = await tool_get_transactions(req.accountId, last_start.isoformat(), last_end.isoformat())
        ui = handle_compare_months_why(this_txs, last_txs)
        return ChatResponse(query=q, ui=ui)

    # unrecognized transaction uses selectedTransactionId
    if q.intent == "unrecognized_transaction":
        tx_id = None
        if q.params.get("transaction_id"):
            tx_id = str(q.params["transaction_id"])
        elif req.context and req.context.selectedTransactionId:
            tx_id = req.context.selectedTransactionId

        if not tx_id:
            ui = UISpec(messages=[UIMessage(content="Which transaction do you mean? Please select a transaction row (or provide its transaction id).")])
            return ChatResponse(query=q, ui=ui)

        tx = await tool_get_transaction_by_id(req.accountId, tx_id)
        bal = await tool_get_balances(req.accountId)
        ui = handle_unrecognized_transaction(tx, bal)
        return ChatResponse(query=q, ui=ui)

    # all other read intents: single range pull
    start_d, end_d = resolve_time_range(q.time_range)
    txs = await tool_get_transactions(req.accountId, start_d.isoformat(), end_d.isoformat())

    if q.intent == "list_last_n":
        ui = handle_list_last_n(q, txs)
    elif q.intent == "transactions_filter":
        ui = handle_transactions_filter(q, txs)
    elif q.intent == "merchant_total":
        ui = handle_merchant_total(q, txs)
    elif q.intent == "top_spending":
        ui = handle_top_spending(q, txs)
    elif q.intent == "recurring_payments":
        ui = handle_recurring_payments(q, txs)
    elif q.intent == "forecast_balance":
        bal = await tool_get_balances(req.accountId)
        ui = handle_forecast_balance(q, bal, txs)
    else:
        ui = UISpec(messages=[UIMessage(content="I didn’t understand that request. Try asking about transactions, spending, or balance.")])

    # always helpful for UI
    ui.controls = ui.controls or [UIControl(type="dateRangePicker", default=q.time_range.preset)]
    return ChatResponse(query=q, ui=ui)
