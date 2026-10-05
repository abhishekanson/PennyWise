from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routers import auth, transactions, budgets, savings_goals

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PennyWise API",
    description="AI Personal Finance Advisor API",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(savings_goals.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to PennyWise API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }