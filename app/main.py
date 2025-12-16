"""
Main Application Entry Point.

This module initializes the FastAPI application and includes the API routes.
"""

from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Quant Analytics API",
    description="Real-time trading analytics system API",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    import asyncio
    from app.ingestion.binance_ws import start_binance_ws
    # Launch WebSocket collector as a background task
    asyncio.create_task(start_binance_ws())

if __name__ == "__main__":
    import uvicorn
    # In production, run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
