
from .categorizer import is_transfer


def get_transfer_category(
    description=None,
    merchant=None,
    existing_category=None
):
    """
    Return 'Transfers' when a transaction is explicitly
    identified as a transfer; otherwise preserve its
    existing category.
    """

    if (
        isinstance(existing_category, str)
        and existing_category.strip().casefold() == "transfers"
    ):
        return "Transfers"

    parts = []

    for value in (description, merchant):
        if value is None:
            continue

        text = str(value).strip()

        if text and text.casefold() not in {"nan", "none"}:
            parts.append(text)

    combined_text = " ".join(parts)

    if combined_text and is_transfer(combined_text):
        return "Transfers"

    return None
