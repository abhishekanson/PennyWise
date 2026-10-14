
def is_transfer_transaction(transaction) -> bool:
    """Return True if a transaction is categorized as a transfer."""
    category = (getattr(transaction, "category", None) or "").strip()
    return category.casefold() == "transfers"


def is_financial_transaction(transaction) -> bool:
    """Transfers remain visible but are excluded from financial totals."""
    return not is_transfer_transaction(transaction)
