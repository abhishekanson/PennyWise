from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Transaction, Budget
from ..ai.financial_health import calculate_financial_health

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/monthly")
def get_monthly_report(
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

        start_date = date(
            year,
            month_number,
            1
        )

        if month_number == 12:
            end_date = date(
                year + 1,
                1,
                1
            )
        else:
            end_date = date(
                year,
                month_number + 1,
                1
            )

    except ValueError:
        return {
            "error": "Invalid month format. Use YYYY-MM."
        }

    # ---------------------------------------------
    # Get transactions
    # ---------------------------------------------

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        .order_by(
            Transaction.date.desc()
        )
        .all()
    )

    # ---------------------------------------------
    # Calculate income and expenses
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

    savings = (
        total_income - total_expenses
    )

    if total_income > 0:
        savings_rate = (
            savings / total_income
        ) * 100
    else:
        savings_rate = 0

    if total_income > 0:
        expense_ratio = (
            total_expenses / total_income
        ) * 100
    else:
        expense_ratio = 100

    # ---------------------------------------------
    # Category-wise spending
    # ---------------------------------------------

    category_spending = {}

    for transaction in transactions:

        if transaction.type.lower() == "expense":

            category = (
                transaction.category
                or "Other"
            )

            category_spending[category] = (
                category_spending.get(
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
        in category_spending.items()
    ]

    category_data.sort(
        key=lambda item: item["amount"],
        reverse=True
    )

    # ---------------------------------------------
    # Highest spending category
    # ---------------------------------------------

    highest_category = (
        category_data[0]["category"]
        if category_data
        else None
    )

    # ---------------------------------------------
    # Get budgets for selected month
    # ---------------------------------------------

    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.month == month
        )
        .all()
    )

    # ---------------------------------------------
    # Prepare budget usage
    # ---------------------------------------------

    budget_usage = []

    for budget in budgets:

        category_expenses = sum(
            transaction.amount
            for transaction in transactions
            if (
                transaction.type.lower()
                == "expense"
                and (
                    transaction.category
                    or "Other"
                ) == budget.category
            )
        )

        if budget.amount > 0:
            percentage_used = (
                category_expenses
                / budget.amount
            ) * 100
        else:
            percentage_used = 0

        budget_usage.append(
            {
                "category": budget.category,
                "budget_amount": round(
                    budget.amount,
                    2
                ),
                "spent_amount": round(
                    category_expenses,
                    2
                ),
                "percentage_used": round(
                    percentage_used,
                    2
                )
            }
        )

    total_budget = sum(
        budget.amount
        for budget in budgets
    )

    if total_budget > 0:
        overall_budget_usage = (
            total_expenses
            / total_budget
        ) * 100
    else:
        overall_budget_usage = 0

    # ---------------------------------------------
    # Savings progress
    # ---------------------------------------------
    # Monthly report does not yet calculate
    # savings-goal progress separately.
    #
    # We pass an empty list for now.
    # This keeps the report compatible with
    # the existing 8Q health-score function.

    savings_progress = []

    # ---------------------------------------------
    # Financial Health Score
    # ---------------------------------------------

    health = calculate_financial_health(
        total_income=total_income,
        total_expenses=total_expenses,
        budget_usage=budget_usage,
        savings_progress=savings_progress
    )

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
            "savings_rate": round(
                savings_rate,
                2
            ),
            "expense_ratio": round(
                expense_ratio,
                2
            ),
            "transaction_count": len(
                transactions
            )
        },

        "category_spending": category_data,

        "highest_spending_category":
            highest_category,

        "budget": {
            "total_budget": round(
                total_budget,
                2
            ),
            "total_expenses": round(
                total_expenses,
                2
            ),
            "usage_percentage": round(
                overall_budget_usage,
                2
            ),
            "categories": budget_usage
        },

        "financial_health": health
    }