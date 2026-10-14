from collections import defaultdict
from datetime import date, datetime
from statistics import mean


def get_month_key(value):
    """Convert a transaction date into YYYY-MM."""
    if isinstance(value, datetime):
        value = value.date()

    if isinstance(value, date):
        return value.strftime("%Y-%m")

    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10]).strftime("%Y-%m")
        except ValueError:
            return None

    return None


def previous_months(current_date, count=3):
    """Return the latest calendar months, including the current month."""
    year = current_date.year
    month = current_date.month
    months = []

    for _ in range(count):
        months.append(f"{year:04d}-{month:02d}")
        month -= 1

        if month == 0:
            month = 12
            year -= 1

    return list(reversed(months))


def predict_future_expenses(transactions):
    """
    Estimate next month's expenses from the latest three calendar months.
    Transfers and non-expense transactions are excluded.
    """

    today = date.today()
    analysis_months = previous_months(today, 3)
    analysis_month_set = set(analysis_months)

    monthly_totals = defaultdict(lambda: defaultdict(float))
    all_categories = set()
    valid_transaction_count = 0

    for transaction in transactions:
        transaction_type = (
            getattr(transaction, "type", None) or ""
        ).strip().lower()

        category = (
            getattr(transaction, "category", None) or "Uncategorized"
        ).strip()

        normalized_category = category.casefold()

        # Only genuine expenses
        if transaction_type != "expense":
            continue

        # Exclude transfers and deposits from expense prediction
        if normalized_category in {
            "transfers",
            "cash deposit",
            "salary",
        }:
            continue

        transaction_date = getattr(transaction, "date", None)
        month_key = get_month_key(transaction_date)

        if month_key not in analysis_month_set:
            continue

        try:
            amount = float(getattr(transaction, "amount", 0) or 0)
        except (TypeError, ValueError):
            continue

        if amount <= 0:
            continue

        monthly_totals[month_key][category] += amount
        all_categories.add(category)
        valid_transaction_count += 1

    if valid_transaction_count == 0:
        return {
            "status": "insufficient_data",
            "message": (
                "No expense transactions found in the latest "
                "three calendar months."
            ),
            "predicted_total": 0,
            "categories": [],
            "months_analyzed": 0,
        }

    predictions = []

    for category in all_categories:
        # Include months with zero spending for this category.
        amounts = [
            monthly_totals[month].get(category, 0.0)
            for month in analysis_months
        ]

        predicted_amount = mean(amounts)
        months_with_spending = sum(amount > 0 for amount in amounts)

        if months_with_spending >= 3:
            confidence = "High"
        elif months_with_spending == 2:
            confidence = "Medium"
        else:
            confidence = "Low"

        predictions.append({
            "category": category,
            "predicted_amount": round(predicted_amount, 2),
            "months_with_spending": months_with_spending,
            "months_included": len(analysis_months),
            "confidence": confidence,
        })

    predictions.sort(
        key=lambda item: item["predicted_amount"],
        reverse=True,
    )

    predicted_total = sum(
        item["predicted_amount"] for item in predictions
    )

    return {
        "status": "success",
        "message": (
            "Expense estimates use the latest three calendar months, "
            "including zero-spending months."
        ),
        "predicted_total": round(predicted_total, 2),
        "categories": predictions,
        "months_analyzed": len(analysis_months),
        "analysis_months": analysis_months,
    }