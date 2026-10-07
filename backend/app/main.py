from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routers import (
    auth,
    transactions,
    budgets,
    savings_goals,
    analysis,
    ai,
    imports,
    insights,
    reports,
    analytics
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PennyWise API",
    description="AI Personal Finance Advisor API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(savings_goals.router)
app.include_router(analysis.router)
app.include_router(ai.router)
app.include_router(imports.router)
app.include_router(insights.router)
app.include_router(reports.router)
app.include_router(analytics.router)


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