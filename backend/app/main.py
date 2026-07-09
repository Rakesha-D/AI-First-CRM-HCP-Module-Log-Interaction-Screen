"""
AI-First CRM HCP Module - Main FastAPI Application

An AI-first CRM system for managing Healthcare Professional (HCP) interactions.
Built with FastAPI, LangGraph, Groq LLM, and MySQL.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine, Base
from app.routers import hcps, interactions, chat, ai, accounts

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-First CRM system for Healthcare Professional (HCP) management. "
        "Features LangGraph-powered AI agent with tools for logging interactions, "
        "editing records, searching HCPs, creating accounts, and generating insights."
    ),
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hcps.router)
app.include_router(interactions.router)
app.include_router(chat.router)
app.include_router(ai.router)
app.include_router(accounts.router)


@app.on_event("startup")
def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        print(f"Database initialization skipped: {exc}")


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
