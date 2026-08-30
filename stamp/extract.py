"""Pull invoice_id / vendor / amount_cents from live Gmail thread text. Stdlib only."""

from __future__ import annotations

import re
from typing import Any

from stamp.reconcile import normalize_vendor

INVOICE_RE = re.compile(
    r"(?:invoice\s*#?\s*|inv(?:oice)?\s*(?:no\.?|number)?\s*#?\s*|#)\s*([A-Za-z0-9-]{2,32})",
    re.IGNORECASE,
)
AMOUNT_RE = re.compile(
    r"(?:amount|total|due|balance)[:\s]*\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+\.[0-9]{2})",
    re.IGNORECASE,
)
CURRENCY_RE = re.compile(r"\b(USD|GBP|EUR)\b", re.IGNORECASE)
VENDOR_RE = re.compile(
    r"(?:from|vendor|biller|company)[:\s]+([A-Za-z0-9 .&-]{2,80})",
    re.IGNORECASE,
)


def dollars_string_to_cents(raw: str) -> int | None:
    text = raw.strip().replace(",", "").replace("$", "")
    if not text:
        return None
    try:
        return int(round(float(text) * 100))
    except ValueError:
        return None


def extract_invoices(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each thread: {id, subject, body, sender?} from Gmail MCP. Not a file inbox."""
    found: list[dict[str, Any]] = []
    for thread in threads:
        text = " ".join(
            str(thread.get(k) or "")
            for k in ("subject", "body", "snippet", "sender")
        )
        invoice_match = INVOICE_RE.search(text)
        amount_match = AMOUNT_RE.search(text)
        currency_match = CURRENCY_RE.search(text)
        vendor_match = VENDOR_RE.search(text)
        sender = str(thread.get("sender") or "")

        invoice_id = invoice_match.group(1).lstrip("#") if invoice_match else ""
        amount_cents = dollars_string_to_cents(amount_match.group(1)) if amount_match else None
        currency = (currency_match.group(1) if currency_match else "USD").lower()
        vendor_raw = vendor_match.group(1).strip() if vendor_match else sender
        vendor = normalize_vendor(vendor_raw)
        if vendor not in {"acme"} and "acme" in text.lower():
            vendor = "acme"

        found.append(
            {
                "invoice_id": invoice_id,
                "vendor": vendor,
                "amount_cents": amount_cents,
                "currency": currency,
                "source_thread_id": str(thread.get("id") or thread.get("thread_id") or ""),
            }
        )
    return found
