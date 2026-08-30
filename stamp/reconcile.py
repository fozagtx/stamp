"""Books check: match extracted invoices to ledger rows. Stdlib only (Daytona)."""

from __future__ import annotations

import csv
import json
import sys
from typing import Any

VENDOR_ALIASES = {
    "acme": "acme",
    "acme demo billing": "acme",
    "acme billing": "acme",
}

STATUSES = frozenset(
    {
        "duplicate_paid",
        "new_unpaid",
        "amount_mismatch",
        "unknown_vendor",
        "partial",
        "unreadable",
    }
)

ACTIONS = {
    "duplicate_paid": "dispute_duplicate",
    "new_unpaid": "confirm_new_invoice",
    "amount_mismatch": "escalate_mismatch",
    "unknown_vendor": "escalate_unreadable",
    "partial": "escalate_mismatch",
    "unreadable": "escalate_unreadable",
}


def normalize_vendor(raw: str | None) -> str:
    if raw is None:
        return ""
    key = " ".join(str(raw).strip().lower().split())
    return VENDOR_ALIASES.get(key, key)


def _int_cents(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text:
        return None
    try:
        if "." in text:
            return int(round(float(text) * 100)) if abs(float(text)) < 10_000_000 else int(float(text))
        return int(text)
    except ValueError:
        return None


def _currency(raw: Any) -> str:
    if raw is None or str(raw).strip() == "":
        return "usd"
    return str(raw).strip().lower()


def _invoice_id(raw: Any) -> str:
    if raw is None:
        return ""
    return str(raw).strip().lstrip("#")


def _load_ledger(path: str) -> list[dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _index_ledger(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for i, row in enumerate(rows):
        vendor = normalize_vendor(row.get("vendor"))
        invoice_id = _invoice_id(row.get("invoice_id"))
        if not vendor or not invoice_id:
            continue
        indexed = dict(row)
        indexed["_row"] = i
        index[(vendor, invoice_id)] = indexed
    return index


def reconcile(
    invoices: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Classify each invoice against the ledger. Idempotent per invoice_id+vendor."""
    ledger = _index_ledger(ledger_rows)
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []

    for inv in invoices:
        invoice_id = _invoice_id(inv.get("invoice_id"))
        vendor = normalize_vendor(inv.get("vendor"))
        amount = _int_cents(inv.get("amount_cents") if inv.get("amount_cents") not in (None, "") else inv.get("amount"))
        currency = _currency(inv.get("currency"))
        thread_id = inv.get("source_thread_id") or ""

        if not invoice_id or amount is None:
            out.append(
                _result(
                    invoice_id or "",
                    "unreadable",
                    reasons=["missing invoice_id or amount"],
                    thread_id=thread_id,
                    vendor=vendor,
                    amount_cents=amount,
                    currency=currency,
                )
            )
            continue

        key = (vendor, invoice_id)
        if key in seen:
            continue
        seen.add(key)

        row = ledger.get(key)
        if row is None:
            if not _vendor_known(vendor, ledger):
                status = "unknown_vendor"
                reasons = ["vendor not on ledger"]
            else:
                status = "new_unpaid"
                reasons = ["no ledger row for vendor+invoice_id"]
            out.append(
                _result(
                    invoice_id,
                    status,
                    reasons=reasons,
                    thread_id=thread_id,
                    vendor=vendor,
                    amount_cents=amount,
                    currency=currency,
                    ledger_row_id=None,
                )
            )
            continue

        ledger_amount = _int_cents(row.get("amount_cents"))
        ledger_currency = _currency(row.get("currency"))
        ledger_status = (row.get("status") or "").strip().lower()
        row_id = row.get("_row")

        if ledger_currency != currency:
            out.append(
                _result(
                    invoice_id,
                    "amount_mismatch",
                    reasons=[f"currency {currency} != ledger {ledger_currency}"],
                    thread_id=thread_id,
                    vendor=vendor,
                    amount_cents=amount,
                    currency=currency,
                    ledger_row_id=row_id,
                )
            )
            continue

        if ledger_amount is None or ledger_amount != amount:
            out.append(
                _result(
                    invoice_id,
                    "amount_mismatch",
                    reasons=[f"amount {amount} != ledger {ledger_amount}"],
                    thread_id=thread_id,
                    vendor=vendor,
                    amount_cents=amount,
                    currency=currency,
                    ledger_row_id=row_id,
                )
            )
            continue

        if ledger_status == "partial":
            status = "partial"
            reasons = ["ledger marks partial payment"]
        elif ledger_status == "paid":
            status = "duplicate_paid"
            reasons = ["ledger already paid"]
        else:
            status = "new_unpaid"
            reasons = [f"ledger status {ledger_status or 'empty'}"]

        out.append(
            _result(
                invoice_id,
                status,
                reasons=reasons,
                thread_id=thread_id,
                vendor=vendor,
                amount_cents=amount,
                currency=currency,
                ledger_row_id=row_id,
            )
        )

    return out


def _vendor_known(vendor: str, ledger: dict[tuple[str, str], dict[str, Any]]) -> bool:
    return any(k[0] == vendor for k in ledger)


def _result(
    invoice_id: str,
    status: str,
    *,
    reasons: list[str],
    thread_id: str,
    vendor: str,
    amount_cents: int | None,
    currency: str,
    ledger_row_id: int | None = None,
) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(status)
    return {
        "invoice_id": invoice_id,
        "vendor": vendor,
        "amount_cents": amount_cents,
        "currency": currency,
        "status": status,
        "proposed_action": ACTIONS[status],
        "reasons": reasons,
        "source_thread_id": thread_id,
        "ledger_row_id": ledger_row_id,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write("usage: python -m stamp.reconcile invoices.json ledger.csv\n")
        return 2
    with open(argv[1], encoding="utf-8") as handle:
        invoices = json.load(handle)
    ledger_rows = _load_ledger(argv[2])
    json.dump(reconcile(invoices, ledger_rows), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
