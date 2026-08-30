from stamp.extract import extract_invoices


def test_extracts_canonical_bodies():
    threads = [
        {
            "id": "a",
            "subject": "Invoice #4412",
            "body": "Invoice #4412 Amount: $4,200.00 USD from Acme Demo Billing. Please remit.",
            "sender": "billing@acme.example",
        },
        {
            "id": "b",
            "subject": "Reminder Invoice #4412",
            "body": "Reminder: Invoice #4412 Amount: $4,200.00 USD is still showing as open.",
            "sender": "billing@acme.example",
        },
        {
            "id": "c",
            "subject": "Invoice #4419",
            "body": "Invoice #4419 Amount: $890.00 USD from Acme Demo Billing. New workstream.",
            "sender": "billing@acme.example",
        },
    ]
    rows = extract_invoices(threads)
    assert [r["invoice_id"] for r in rows] == ["4412", "4412", "4419"]
    assert rows[0]["amount_cents"] == 420000
    assert rows[2]["amount_cents"] == 89000
    assert rows[0]["vendor"] == "acme"
    assert rows[1]["vendor"] == "acme"
    assert rows[0]["source_thread_id"] == "a"
