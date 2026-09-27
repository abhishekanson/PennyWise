from fastapi import FastAPI

from .database import Base, engine
from . import models


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PennyWise API",
    description="AI Personal Finance Advisor API",
    version="1.0.0"
)


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