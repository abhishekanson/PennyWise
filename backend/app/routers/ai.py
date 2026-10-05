from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..models import User
from ..ai.categorizer import predict_category


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


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