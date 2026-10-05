from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Budget, User
from ..schemas import BudgetCreate, BudgetResponse
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


@router.post(
    "/",
    response_model=BudgetResponse
)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if budget.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Budget amount must be greater than zero"
        )

    new_budget = Budget(
        user_id=current_user.id,
        category=budget.category,
        amount=budget.amount,
        month=budget.month
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@router.get(
    "/",
    response_model=list[BudgetResponse]
)
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id
    ).all()

    return budgets


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return budget


@router.put(
    "/{budget_id}",
    response_model=BudgetResponse
)
def update_budget(
    budget_id: int,
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    if budget_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Budget amount must be greater than zero"
        )

    budget.category = budget_data.category
    budget.amount = budget_data.amount
    budget.month = budget_data.month

    db.commit()
    db.refresh(budget)

    return budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Budget deleted successfully"
    }