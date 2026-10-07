from datetime import date
from calendar import monthrange

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Transaction


router = APIRouter(
    prefix="/analytics",
    tags=["Advanced Analytics"]
)


def get_month_dates(year: int, month: int):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    return start_date, end_date


@router.get("/advanced")
def get_advanced_analytics(
    month: str = Query(
        ...,
        description="Month in YYYY-MM format"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ---------------------------------------------
    # Validate month
    # ---------------------------------------------

    try:
        year, month_number = map(
            int,
            month.split("-")
        )

        if month_number < 1 or month_number > 12:
            raise ValueError

        start_date, end_date = get_month_dates(
            year,
            month_number
        )

    except ValueError:
        return {
            "error": "Invalid month format. Use YYYY-MM."
        }

    # ---------------------------------------------
    # Previous month
    # ---------------------------------------------

    if month_number == 1:
        previous_year = year - 1
        previous_month = 12
    else:
        previous_year = year
        previous_month = month_number - 1

    previous_start, previous_end = get_month_dates(
        previous_year,
        previous_month
    )

    # ---------------------------------------------
    # Current month transactions
    # ---------------------------------------------

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        .order_by(Transaction.date.asc())
        .all()
    )

    # ---------------------------------------------
    # Previous month transactions
    # ---------------------------------------------

    previous_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= previous_start,
            Transaction.date < previous_end
        )
        .all()
    )

    # ---------------------------------------------
    # Current month income / expenses
    # ---------------------------------------------

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type.lower() == "income"
    )

    total_expenses = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type.lower() == "expense"
    )

    savings = total_income - total_expenses

    # ---------------------------------------------
    # Previous month income / expenses
    # ---------------------------------------------

    previous_income = sum(
        transaction.amount
        for transaction in previous_transactions
        if transaction.type.lower() == "income"
    )

    previous_expenses = sum(
        transaction.amount
        for transaction in previous_transactions
        if transaction.type.lower() == "expense"
    )

    previous_savings = (
        previous_income - previous_expenses
    )

    # ---------------------------------------------
    # Month-to-month percentage change
    # ---------------------------------------------

    if previous_expenses > 0:
        expense_change = (
            (total_expenses - previous_expenses)
            / previous_expenses
        ) * 100
    else:
        expense_change = 0

    if previous_income > 0:
        income_change = (
            (total_income - previous_income)
            / previous_income
        ) * 100
    else:
        income_change = 0

    if previous_savings != 0:
        savings_change = (
            (savings - previous_savings)
            / abs(previous_savings)
        ) * 100
    else:
        savings_change = 0

    # ---------------------------------------------
    # Category analysis
    # ---------------------------------------------

    category_totals = {}

    for transaction in transactions:

        if transaction.type.lower() != "expense":
            continue

        category = (
            transaction.category
            or "Other"
        )

        category_totals[category] = (
            category_totals.get(
                category,
                0
            )
            + transaction.amount
        )

    category_data = [
        {
            "category": category,
            "amount": round(
                amount,
                2
            )
        }
        for category, amount
        in category_totals.items()
    ]

    category_data.sort(
        key=lambda item: item["amount"],
        reverse=True
    )

    # ---------------------------------------------
    # Top merchants
    # ---------------------------------------------

    merchant_totals = {}

    for transaction in transactions:

        if transaction.type.lower() != "expense":
            continue

        merchant = (
            transaction.merchant
            or "Unknown"
        )

        merchant_totals[merchant] = (
            merchant_totals.get(
                merchant,
                0
            )
            + transaction.amount
        )

    merchant_data = [
        {
            "merchant": merchant,
            "amount": round(
                amount,
                2
            )
        }
        for merchant, amount
        in merchant_totals.items()
    ]

    merchant_data.sort(
        key=lambda item: item["amount"],
        reverse=True
    )

    # Keep top 10
    merchant_data = merchant_data[:10]

    # ---------------------------------------------
    # Payment method analysis
    # ---------------------------------------------

    payment_totals = {}

    for transaction in transactions:

        if transaction.type.lower() != "expense":
            continue

        payment_method = (
            transaction.payment_method
            or "Unknown"
        )

        payment_totals[payment_method] = (
            payment_totals.get(
                payment_method,
                0
            )
            + transaction.amount
        )

    payment_data = [
        {
            "payment_method": payment_method,
            "amount": round(
                amount,
                2
            )
        }
        for payment_method, amount
        in payment_totals.items()
    ]

    payment_data.sort(
        key=lambda item: item["amount"],
        reverse=True
    )

    # ---------------------------------------------
    # Daily spending
    # ---------------------------------------------

    daily_totals = {}

    for transaction in transactions:

        if transaction.type.lower() != "expense":
            continue

        day = transaction.date.isoformat()

        daily_totals[day] = (
            daily_totals.get(
                day,
                0
            )
            + transaction.amount
        )

    daily_data = [
        {
            "date": day,
            "amount": round(
                amount,
                2
            )
        }
        for day, amount
        in daily_totals.items()
    ]

    daily_data.sort(
        key=lambda item: item["date"]
    )

    # ---------------------------------------------
    # Highest spending day
    # ---------------------------------------------

    highest_spending_day = None

    if daily_data:
        highest_spending_day = max(
            daily_data,
            key=lambda item: item["amount"]
        )

    # ---------------------------------------------
    # Average daily spending
    # ---------------------------------------------

    days_with_expenses = len(
        daily_data
    )

    if days_with_expenses > 0:
        average_daily_spending = (
            total_expenses
            / days_with_expenses
        )
    else:
        average_daily_spending = 0

    # ---------------------------------------------
    # Final response
    # ---------------------------------------------

    return {

        "month": month,

        "summary": {
            "income": round(
                total_income,
                2
            ),
            "expenses": round(
                total_expenses,
                2
            ),
            "savings": round(
                savings,
                2
            ),
            "transaction_count": len(
                transactions
            )
        },

        "previous_month": {
            "month": (
                f"{previous_year:04d}-"
                f"{previous_month:02d}"
            ),
            "income": round(
                previous_income,
                2
            ),
            "expenses": round(
                previous_expenses,
                2
            ),
            "savings": round(
                previous_savings,
                2
            )
        },

        "month_comparison": {
            "income_change_percentage":
                round(
                    income_change,
                    2
                ),
            "expense_change_percentage":
                round(
                    expense_change,
                    2
                ),
            "savings_change_percentage":
                round(
                    savings_change,
                    2
                )
        },

        "category_spending": category_data,

        "top_merchants": merchant_data,

        "payment_methods": payment_data,

        "daily_spending": daily_data,

        "spending_pattern": {
            "average_daily_spending":
                round(
                    average_daily_spending,
                    2
                ),
            "highest_spending_day":
                highest_spending_day
        }
    }