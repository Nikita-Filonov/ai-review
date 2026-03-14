def format_currency(amount: float, currency: str = "USD") -> str:
    normalized = round(amount, 2)
    return f"{currency} {normalized:,.2f}"


def cents_to_amount(cents: int) -> float:
    return cents / 100
