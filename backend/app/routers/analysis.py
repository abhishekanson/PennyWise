from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Transaction, Budget, SavingsGoal, User
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/analysis",
    tags=["Financial Analysis"]
)


@router.get("/summary")
def get_financial_summary(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income_query = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income"
    )

    expense_query = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    )

    if month:
        income_query = income_query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

        expense_query = expense_query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

    total_income = income_query.scalar()
    total_expenses = expense_query.scalar()

    balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance
    }

@router.get("/category-spending")
def get_category_spending(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    )

    if month:
        query = query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

    results = query.group_by(
        Transaction.category
    ).all()

    return [
        {
            "category": category or "Uncategorized",
            "total": total
        }
        for category, total in results
    ]

@router.get("/monthly-spending")
def get_monthly_spending(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        func.to_char(
            Transaction.date,
            "YYYY-MM"
        ).label("month"),
        func.sum(
            Transaction.amount
        ).label("total")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    )

    if month:
        query = query.filter(
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == month
        )

    results = query.group_by(
        func.to_char(
            Transaction.date,
            "YYYY-MM"
        )
    ).order_by(
        func.to_char(
            Transaction.date,
            "YYYY-MM"
        )
    ).all()

    return [
        {
            "month": month,
            "total": total
        }
        for month, total in results
    ]

@router.get("/budget-usage")
def get_budget_usage(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets_query = db.query(Budget).filter(
        Budget.user_id == current_user.id
    )

    if month:
        budgets_query = budgets_query.filter(
            Budget.month == month
        )

    budgets = budgets_query.all()

    result = []

    for budget in budgets:

        spent = db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0
            )
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.category == budget.category,
            func.to_char(
                Transaction.date,
                "YYYY-MM"
            ) == budget.month
        ).scalar()

        remaining = budget.amount - spent

        if budget.amount > 0:
            percentage_used = (
                spent / budget.amount
            ) * 100
        else:
            percentage_used = 0

        result.append({
            "budget_id": budget.id,
            "category": budget.category,
            "month": budget.month,
            "budget_amount": budget.amount,
            "spent": spent,
            "remaining": remaining,
            "percentage_used": round(
                percentage_used,
                2
            )
        })

    return result

@router.get("/savings-progress")
def get_savings_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == current_user.id
    ).all()

    result = []

    for goal in goals:

        if goal.target_amount > 0:
            percentage = (
                goal.current_amount / goal.target_amount
            ) * 100
        else:
            percentage = 0

        remaining = goal.target_amount - goal.current_amount

        result.append({
            "goal_id": goal.id,
            "goal_name": goal.goal_name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "remaining_amount": remaining,
            "percentage_completed": round(percentage, 2),
            "target_date": goal.target_date
        })

    return result