from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Float, nullable=False)

    type = Column(String, nullable=False)
    # income or expense

    description = Column(String, nullable=True)

    merchant = Column(String, nullable=True)

    category = Column(String, nullable=True)

    date = Column(Date, nullable=False)

    payment_method = Column(String, nullable=True)

    source = Column(String, nullable=False, default="manual")
    # manual or pdf

    reference_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    source = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    date = Column(Date, nullable=False)

    description = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Float, nullable=False)

    category = Column(String, nullable=True)

    date = Column(Date, nullable=False)

    description = Column(String, nullable=True)

    payment_method = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    month = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    goal_name = Column(String, nullable=False)

    target_amount = Column(Float, nullable=False)

    current_amount = Column(Float, default=0)

    target_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)