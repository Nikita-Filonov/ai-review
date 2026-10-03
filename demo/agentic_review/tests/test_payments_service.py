from demo.agentic_review.payments.service import build_invoice_line
from demo.agentic_review.payments.service import calculate_discounted_total


def test_build_invoice_line() -> None:
    line = build_invoice_line("Pro plan", 1299)
    assert line == "Pro plan: USD 12.99"


def test_calculate_discounted_total() -> None:
    total = calculate_discounted_total(1000, 10)
    assert total == 9.0
