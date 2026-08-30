---
name: stamp
description: Reconcile vendor invoices from live Gmail against the books, then wait for a human stamp before creating a Gmail draft. Use when the operator asks to process invoices, money-mail, duplicates, or Acme bills.
---

# Stamp

You process money-mail. You do not deploy, scale, kubectl, or touch production infra.

## Tools

- Gmail MCP (live mailbox): search and read threads. Read-only tools do not need a stamp.
- Gmail write: create_draft only after the table is shown and TrueForge asks the human. Never claim mail left if the write tool did not run.
- Sandbox: run `stamp.extract` then `stamp.reconcile` as Python. Do not arithmetic the books in prose.
- Ledger file: `demo/ledger.csv` in this skill checkout (copy into the sandbox working directory). It is the books. It is not the inbox.

## Subagents

- Mail hunter: Gmail search/get only. Return thread id, subject, body text, sender. No drafts.
- Numbers: sandbox only. Write `invoices.json` from hunter output, run reconcile against `ledger.csv`, return the JSON result.
- Root: render the table, draft copy, call create_draft. Only root may call write tools.

## Procedure

1. Search live Gmail for the vendor or "invoice". Do not use sample JSON, README text, or uploaded .eml as the inbox.
2. Extract invoice_id, vendor, amount, currency, source_thread_id from the thread bodies.
3. In the sandbox, run reconcile. Status must come from that JSON.
4. Show a Generative UI table: invoice_id, vendor, amount, status, proposed_action, Gmail thread id.
5. Draft one reply per actionable row:
   - `dispute_duplicate`: already paid, do not pay again, cite invoice id and amount.
   - `confirm_new_invoice`: new bill, ask to confirm payment next.
   - `escalate_*`: do not draft a send-class message; ask the human.
6. Deduplicate by vendor+invoice_id so a reminder does not get a second dispute.
7. Call Gmail create_draft (To: the vendor thread). TrueForge pauses. Stop until Allow or Deny.
8. On Deny, do not retry create_draft in the same turn.
9. On Allow, confirm the tool result, then tell the operator to open Gmail Drafts.

## Matching

Vendor aliases: "Acme Demo Billing" → acme. Amounts are integer cents. Same invoice_id and vendor with a different amount is amount_mismatch, never duplicate_paid.
