"""
Resilient ATS Backend — FastAPI Application
Main entry point for the resume analysis engine.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.analysis import router as analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 Resilient ATS Engine starting...")
    print("📦 Pre-loading NLP model (first time may take a moment)...")

    # Skip model pre-loading for faster startup - load on demand
    print("🟢 Resilient ATS Engine is ready!")
    yield
    print("👋 Resilient ATS Engine shutting down...")


app = FastAPI(
    title="Resilient ATS Engine",
    description="Intelligent resume analysis with adversarial detection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(analysis_router)


@app.get("/")
async def root():
    return {
        "name": "Resilient ATS Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }
