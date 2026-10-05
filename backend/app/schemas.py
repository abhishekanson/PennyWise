from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionCreate(BaseModel):
    amount: float
    type: str
    description: Optional[str] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    date: date
    payment_method: Optional[str] = None
    source: str = "manual"
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    description: Optional[str]
    merchant: Optional[str]
    category: Optional[str]
    date: date
    payment_method: Optional[str]
    source: str
    reference_id: Optional[str]

    class Config:
        from_attributes = True

class BudgetCreate(BaseModel):
    category: str
    amount: float
    month: str


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    month: str

    class Config:
        from_attributes = True


class SavingsGoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: float = 0
    target_date: Optional[date] = None


class SavingsGoalResponse(BaseModel):
    id: int
    user_id: int
    goal_name: str
    target_amount: float
    current_amount: float
    target_date: Optional[date]

    class Config:
        from_attributes = True