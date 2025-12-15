QUERY_SPEC_SYSTEM_PROMPT = """
Output ONLY JSON. No markdown. No extra keys.

Return this JSON shape:

{
  "is_banking": true | false | null,
  "clarification_needed": false,
  "clarification_question": null,
  "confidence": 0.0,
  "query": {
    "intent": "top_spending_ytd" | "transactions_list" | "recurring_payments" | "unrecognized_transaction",
    "time_range": {
      "mode": "preset" | "relative" | "custom",
      "preset": "ytd" | "last_month" | null,
      "last": null,
      "unit": null,
      "start": null,
      "end": null
    },
    "params": {}
  }
}

Rules:
1) Set is_banking:
- true: clearly a banking request about transactions/spending/recurring/unrecognized/dispute.
- false: clearly not about banking.
- null: unclear OR gibberish/nonsensical even if it contains banking words.
  Example: "what is the third transaction from the sun" => is_banking=null and ask a clarification question.

2) If is_banking is false or null:
- clarification_needed=true
- clarification_question: short, helpful question.
- query should be a safe default (transactions_list, last 30 days, limit 10), but it will NOT be executed unless is_banking=true.

3) If is_banking is true:
- clarification_needed=false unless required info is missing.
- For unrecognized_transaction:
  - if tx id like t016 appears => params.transaction_id="t016"
  - else params.transaction_id=null and clarification_needed=true (ask user to select one).

Time rules:
- "this year" / "ytd" => preset ytd
- "last month" => preset last_month
- "last N days/weeks/months/years" => relative last=N unit=...
- "recent 10 transactions" => params.limit=10 (default time_range last 30 days)

Defaults:
- transactions_list => relative 30 days, params.limit=50
- recurring_payments => relative 3 months, params.min_occurrences=3
- top_spending_ytd => preset ytd, params.top_k=5

Output ONLY JSON.
"""
