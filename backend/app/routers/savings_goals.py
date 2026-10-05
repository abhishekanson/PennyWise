from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SavingsGoal, User
from ..schemas import SavingsGoalCreate, SavingsGoalResponse
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/savings-goals",
    tags=["Savings Goals"]
)


@router.post(
    "/",
    response_model=SavingsGoalResponse
)
def create_savings_goal(
    goal: SavingsGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if goal.target_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Target amount must be greater than zero"
        )

    if goal.current_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Current amount cannot be negative"
        )

    if goal.current_amount > goal.target_amount:
        raise HTTPException(
            status_code=400,
            detail="Current amount cannot exceed target amount"
        )

    new_goal = SavingsGoal(
        user_id=current_user.id,
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


@router.get(
    "/",
    response_model=list[SavingsGoalResponse]
)
def get_savings_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    goals = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == current_user.id
    ).all()

    return goals


@router.get(
    "/{goal_id}",
    response_model=SavingsGoalResponse
)
def get_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    return goal


@router.put(
    "/{goal_id}",
    response_model=SavingsGoalResponse
)
def update_savings_goal(
    goal_id: int,
    goal_data: SavingsGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    if goal_data.target_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Target amount must be greater than zero"
        )

    if goal_data.current_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Current amount cannot be negative"
        )

    if goal_data.current_amount > goal_data.target_amount:
        raise HTTPException(
            status_code=400,
            detail="Current amount cannot exceed target amount"
        )

    goal.goal_name = goal_data.goal_name
    goal.target_amount = goal_data.target_amount
    goal.current_amount = goal_data.current_amount
    goal.target_date = goal_data.target_date

    db.commit()
    db.refresh(goal)

    return goal


@router.delete("/{goal_id}")
def delete_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    db.delete(goal)
    db.commit()

    return {
        "message": "Savings goal deleted successfully"
    }