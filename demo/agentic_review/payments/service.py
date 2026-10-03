from demo.agentic_review.shared.formatting import cents_to_amount


def _format_currency_local(amount: float) -> str:
    # Intentionally duplicated formatter for review demo.
    return f"USD {amount:.2f}"


def build_invoice_line(item_name: str, cents: int) -> str:
    amount = cents_to_amount(cents)
    return f"{item_name}: {_format_currency_local(amount)}"


def calculate_discounted_total(cents: int, discount_percent: float) -> float:
    amount = cents_to_amount(cents)
    discounted = amount - (amount * discount_percent / 100)
    return round(discounted, 2)
