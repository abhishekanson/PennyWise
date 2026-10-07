from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Transaction, Budget, SavingsGoal
from ..ai.insights import generate_financial_insights
from ..ai.financial_health import calculate_financial_health


router = APIRouter(
    prefix="/ai",
    tags=["AI Insights"]
)


# =================================================
# AI FINANCIAL INSIGHTS
# =================================================

@router.get("/insights")
def get_financial_insights(
    month: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    transaction_query = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
    )

    if month:
        transaction_query = transaction_query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

    transactions = transaction_query.all()

    budget_query = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id
        )
    )

    if month:
        budget_query = budget_query.filter(
            Budget.month == month
        )

    budgets = budget_query.all()

    savings_goals = (
        db.query(SavingsGoal)
        .filter(
            SavingsGoal.user_id == current_user.id
        )
        .all()
    )

    # -------------------------------------------------
    # Income / expense totals
    # -------------------------------------------------

    total_income = sum(
        float(t.amount)
        for t in transactions
        if t.type.lower() == "income"
    )

    total_expenses = sum(
        float(t.amount)
        for t in transactions
        if t.type.lower() == "expense"
    )

    # -------------------------------------------------
    # Category spending
    # -------------------------------------------------

    category_totals = {}

    for transaction in transactions:

        if transaction.type.lower() != "expense":
            continue

        category = (
            transaction.category
            or "Uncategorized"
        )

        category_totals[category] = (
            category_totals.get(category, 0)
            + float(transaction.amount)
        )

    category_spending = [
        {
            "category": category,
            "amount": amount,
        }
        for category, amount
        in category_totals.items()
    ]

    # -------------------------------------------------
    # Budget usage
    # -------------------------------------------------

    budget_usage = []

    for budget in budgets:

        spent = sum(
            float(t.amount)
            for t in transactions
            if (
                t.type.lower() == "expense"
                and (t.category or "").lower()
                == budget.category.lower()
                and t.date.strftime("%Y-%m")
                == budget.month
            )
        )

        budget_amount = float(
            budget.amount
        )

        percentage = (
            (spent / budget_amount) * 100
            if budget_amount > 0
            else 0
        )

        budget_usage.append({
            "category": budget.category,
            "percentage_used": percentage,
        })

    # -------------------------------------------------
    # Savings progress
    # -------------------------------------------------

    savings_progress = []

    for goal in savings_goals:

        target = float(
            goal.target_amount
        )

        current = float(
            goal.current_amount or 0
        )

        percentage = (
            (current / target) * 100
            if target > 0
            else 0
        )

        savings_progress.append({
            "goal_name": goal.goal_name,
            "percentage_completed": percentage,
        })

    # -------------------------------------------------
    # Generate insights
    # -------------------------------------------------

    result = generate_financial_insights(
        total_income=total_income,
        total_expenses=total_expenses,
        category_spending=category_spending,
        budget_usage=budget_usage,
        savings_progress=savings_progress,
        db=db,
        user_id=current_user.id,
    )

    return result


# =================================================
# FINANCIAL HEALTH SCORE
# =================================================

@router.get("/health-score")
def get_financial_health_score(
    month: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    transaction_query = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
    )

    if month:
        transaction_query = transaction_query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

    transactions = transaction_query.all()

    budget_query = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id
        )
    )

    if month:
        budget_query = budget_query.filter(
            Budget.month == month
        )

    budgets = budget_query.all()

    savings_goals = (
        db.query(SavingsGoal)
        .filter(
            SavingsGoal.user_id == current_user.id
        )
        .all()
    )

    # ---------------------------------------------
    # Income / expenses
    # ---------------------------------------------

    total_income = sum(
        float(t.amount)
        for t in transactions
        if t.type.lower() == "income"
    )

    total_expenses = sum(
        float(t.amount)
        for t in transactions
        if t.type.lower() == "expense"
    )

    # ---------------------------------------------
    # Budget usage
    # ---------------------------------------------

    budget_usage = []

    for budget in budgets:

        spent = sum(
            float(t.amount)
            for t in transactions
            if (
                t.type.lower() == "expense"
                and (t.category or "").lower()
                == budget.category.lower()
                and t.date.strftime("%Y-%m")
                == budget.month
            )
        )

        budget_amount = float(
            budget.amount
        )

        percentage = (
            (spent / budget_amount) * 100
            if budget_amount > 0
            else 0
        )

        budget_usage.append({
            "category": budget.category,
            "percentage_used": percentage,
        })

    # ---------------------------------------------
    # Savings goals
    # ---------------------------------------------

    savings_progress = []

    for goal in savings_goals:

        target = float(
            goal.target_amount
        )

        current = float(
            goal.current_amount or 0
        )

        percentage = (
            (current / target) * 100
            if target > 0
            else 0
        )

        savings_progress.append({
            "goal_name": goal.goal_name,
            "percentage_completed": percentage,
        })

    # ---------------------------------------------
    # Calculate health score
    # ---------------------------------------------

    result = calculate_financial_health(
        total_income=total_income,
        total_expenses=total_expenses,
        budget_usage=budget_usage,
        savings_progress=savings_progress,
    )

    return result