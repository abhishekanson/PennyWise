from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Transaction
from ..dependencies import get_current_user
from ..ai.expense_predictor import predict_future_expenses


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


@router.get("/future-expenses")
def get_future_expenses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Predict the user's future expenses using historical transactions.
    """

    # Get only transactions belonging to the logged-in user
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
        .all()
    )

    # Generate prediction
    result = predict_future_expenses(transactions)

    return result