from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..models import User
from ..ai.categorizer import predict_category
from ..ai.behavior import analyze_spending_behavior
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


# ---------------------------------------------------------
# Expense Categorization
# ---------------------------------------------------------

class CategorizationRequest(BaseModel):
    description: str


@router.post("/categorize")
def categorize_expense(
    request: CategorizationRequest,
    current_user: User = Depends(get_current_user)
):
    result = predict_category(
        request.description
    )

    return result


# ---------------------------------------------------------
# Spending Behaviour Analysis
# ---------------------------------------------------------

@router.get("/spending-behaviour")
def spending_behaviour(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Keep the analysis period within a sensible range
    if months < 1:
        months = 1

    if months > 12:
        months = 12

    result = analyze_spending_behavior(
        db=db,
        user_id=current_user.id,
        months=months
    )

    return result