from stamp.reconcile import reconcile

LEDGER = [
    {
        "invoice_id": "4412",
        "vendor": "acme",
        "amount_cents": "420000",
        "currency": "usd",
        "status": "paid",
    }
]


def test_duplicate_4412():
    invoices = [
        {
            "invoice_id": "4412",
            "vendor": "acme",
            "amount_cents": 420000,
            "currency": "usd",
            "source_thread_id": "t1",
        }
    ]
    rows = reconcile(invoices, LEDGER)
    assert len(rows) == 1
    assert rows[0]["status"] == "duplicate_paid"
    assert rows[0]["proposed_action"] == "dispute_duplicate"


def test_reminder_same_id_is_one_row():
    invoices = [
        {
            "invoice_id": "4412",
            "vendor": "Acme Demo Billing",
            "amount_cents": 420000,
            "currency": "usd",
            "source_thread_id": "t1",
        },
        {
            "invoice_id": "4412",
            "vendor": "acme",
            "amount_cents": 420000,
            "currency": "usd",
            "source_thread_id": "t2",
        },
    ]
    rows = reconcile(invoices, LEDGER)
    assert len(rows) == 1
    assert rows[0]["status"] == "duplicate_paid"


def test_new_4419():
    invoices = [
        {
            "invoice_id": "4419",
            "vendor": "acme",
            "amount_cents": 89000,
            "currency": "usd",
            "source_thread_id": "t3",
        }
    ]
    rows = reconcile(invoices, LEDGER)
    assert rows[0]["status"] == "new_unpaid"
    assert rows[0]["proposed_action"] == "confirm_new_invoice"


def test_amount_mismatch():
    invoices = [
        {
            "invoice_id": "4412",
            "vendor": "acme",
            "amount_cents": 419900,
            "currency": "usd",
            "source_thread_id": "t4",
        }
    ]
    rows = reconcile(invoices, LEDGER)
    assert rows[0]["status"] == "amount_mismatch"
    assert rows[0]["proposed_action"] == "escalate_mismatch"


def test_vendor_alias():
    invoices = [
        {
            "invoice_id": "4412",
            "vendor": "Acme Demo Billing",
            "amount_cents": 420000,
            "currency": "usd",
            "source_thread_id": "t5",
        }
    ]
    rows = reconcile(invoices, LEDGER)
    assert rows[0]["vendor"] == "acme"
    assert rows[0]["status"] == "duplicate_paid"


def test_currency_mismatch():
    invoices = [
        {
            "invoice_id": "4412",
            "vendor": "acme",
            "amount_cents": 420000,
            "currency": "gbp",
            "source_thread_id": "t6",
        }
    ]
    assert reconcile(invoices, LEDGER)[0]["status"] == "amount_mismatch"


def test_empty():
    assert reconcile([], LEDGER) == []


def test_unreadable():
    rows = reconcile([{"vendor": "acme", "source_thread_id": "t7"}], LEDGER)
    assert rows[0]["status"] == "unreadable"
    assert rows[0]["proposed_action"] == "escalate_unreadable"


def test_unknown_vendor():
    invoices = [
        {
            "invoice_id": "99",
            "vendor": "globex",
            "amount_cents": 100,
            "currency": "usd",
            "source_thread_id": "t8",
        }
    ]
    result = reconcile(invoices, LEDGER)[0]
    assert result["status"] == "unknown_vendor"
    # unknown_vendor escalates as mismatch (not unreadable) — bug fix: was escalate_unreadable
    assert result["proposed_action"] == "escalate_mismatch"


def test_large_invoice_cents_not_truncated():
    """Regression: invoices ≥ $100k were stored as raw dollars due to a bad guard."""
    ledger = [
        {
            "invoice_id": "BIG1",
            "vendor": "acme",
            "amount_cents": "10000000",  # $100,000.00 in cents
            "currency": "usd",
            "status": "paid",
        }
    ]
    invoices = [
        {
            "invoice_id": "BIG1",
            "vendor": "acme",
            "amount_cents": 10000000,  # $100,000.00 in cents
            "currency": "usd",
            "source_thread_id": "t_big",
        }
    ]
    result = reconcile(invoices, ledger)[0]
    assert result["status"] == "duplicate_paid", (
        f"Large invoice should match as duplicate_paid, got {result['status']}"
    )


def test_partial_ledger():
    ledger = [
        {
            "invoice_id": "10",
            "vendor": "acme",
            "amount_cents": "50000",
            "currency": "usd",
            "status": "partial",
        }
    ]
    invoices = [
        {
            "invoice_id": "10",
            "vendor": "acme",
            "amount_cents": 50000,
            "currency": "usd",
            "source_thread_id": "t9",
        }
    ]
    assert reconcile(invoices, ledger)[0]["status"] == "partial"
