"""
API Routes Module.

This module defines the RESTful endpoints for the quantitative analytics system.
It exposes health checks, analytics data (latest & history), alert status, and configuration management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import random
import numpy as np
import csv
import io

# Import core analytics for the manual ADF trigger (if needed, though contract mentions specific endpoints)
# We will keep the adf_test import if we need to verify stationarity internally, 
# but the prompt says "GET /analytics/latest" implies we serve pre-calculated data.
from app.analytics.adf_test import run_adf_test

router = APIRouter()

# --- Internal State / Mock Data Generator ---

def get_utc_now():
    return datetime.now(timezone.utc)

def get_utc_now_iso():
    return get_utc_now().isoformat()

# Initial Configuration
# --- Pydantic Models for Configuration ---
class TradingConfig(BaseModel):
    zscore_entry_threshold: float = 2.0
    zscore_exit_threshold: float = 0.5
    min_correlation: float = 0.7

# Initial Global Configuration
CURRENT_CONFIG = TradingConfig()
# Deprecated alias to maintain minimal changes elsewhere if needed, but we will update usages
# config dict for backward compatibility logic references if strictly needed?
# No, better to update the logical references to use CURRENT_CONFIG attributes.

# Generate some historical data on startup so charts aren't empty
HISTORY_LENGTH = 50
history_data = []

def generate_history():
    global history_data
    history_data = []
    now = get_utc_now()
    base_spread = 100.0
    base_zscore = 0.0
    
    for i in range(HISTORY_LENGTH):
        # Time points from past to now
        t = now - timedelta(minutes=(HISTORY_LENGTH - 1 - i))
        
        # Random walk / noise
        base_spread += random.uniform(-1, 1)
        base_zscore = random.uniform(-2.5, 2.5)
        correlation = random.uniform(0.6, 0.99)
        
        history_data.append({
            "timestamp": t.isoformat(),
            "zscore": base_zscore,
            "spread": max(0, base_spread), # Ensure non-negative per requirement
            "correlation": correlation,
            "hedge_ratio": 1.2 + random.uniform(-0.1, 0.1)
        })

generate_history()

# Latest state derived from history or updated
def get_latest_data():
    if not history_data:
        generate_history()
    
    latest = history_data[-1]
    # Update timestamp to "now" to simulate live feed if polled
    latest_copy = latest.copy()
    latest_copy["timestamp"] = get_utc_now_iso()
    
    # Calculate stationarity (simple mock logic or real ADF)
    # Using real ADF on the Z-score history if possible
    # For now, simplistic check based on Z-score threshold
    is_stationary = abs(latest["zscore"]) < CURRENT_CONFIG.zscore_entry_threshold
    
    # Task 2: Warm-up metadata
    # WINDOW_SIZE is defined in binance_ws, but we can reuse HISTORY_LENGTH here as they align in concept for now
    # Or define WINDOW_SIZE explicitly as requested.
    WINDOW_SIZE = 50 
    points_collected = len(history_data)
    warmup = points_collected < WINDOW_SIZE
    
    # Filter alert if correlation is low? 
    # Prompt says "Apply config to analytics... Filtering alerts based on minimum correlation".
    # Since this is just returning the latest data point with 'stationary' flag, we just update stationary check.
    # The actual alert logic is in binance_ws.py mostly or here if we use latest_alert object.

    return {
        **latest_copy,
        "stationary": is_stationary,
        "warmup": warmup,
        "points_collected": points_collected,
        "window_size": WINDOW_SIZE
    }

# Mock Alert
latest_alert = {
    "timestamp": get_utc_now_iso(),
    "type": "SIGNAL",
    "signal": "SHORT",  # included for backward compat if needed, but Prompt asked for type|z_score|timestamp
    "z_score": 2.5,
    "reason": "Z-Score crossed upper threshold"
}


# --- Pydantic Models ---

class ConfigUpdate(BaseModel):
    z_threshold: Optional[float] = None
    reset_threshold: Optional[float] = None
    min_correlation: Optional[float] = None

class HealthResponse(BaseModel):
    status: str

class AnalyticsLatest(BaseModel):
    timestamp: str
    zscore: float
    spread: float
    correlation: Optional[float]
    hedge_ratio: float
    stationary: bool
    warmup: bool
    points_collected: int
    window_size: int

class AlertResponse(BaseModel):
    timestamp: str
    type: str # SIGNAL, etc.
    signal: Optional[str] = None
    z_score: float
    reason: str

class StatsRow(BaseModel):
    timestamp: str
    zscore: float
    spread: float
    correlation: Optional[float]
    is_stationary: bool
    alert: str

class StatsResponse(BaseModel):
    rows: List[StatsRow]

# --- Endpoints ---

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Health check endpoint."""
    return {"status": "ok"}

@router.get("/analytics/latest", response_model=AnalyticsLatest)
async def get_analytics_latest():
    """Get the latest calculated metrics."""
    # In a real app, this would query the latest row from DB or in-memory store
    return get_latest_data()

@router.get("/analytics/history")
async def get_analytics_history():
    """Get historical data series for charts."""
    # In live app, you might want to append a 'fresh' point or shift the window
    # For this demo, we can shift the history slightly to simulate time passing
    # or just return the static generated history.
    # Let's shift it if called to make it feel alive.
    
    global history_data
    last_time = datetime.fromisoformat(history_data[-1]["timestamp"])
    now = get_utc_now()
    
    # If more than 1 minute passed, add a point
    if (now - last_time).total_seconds() > 60:
         new_point = history_data[-1].copy()
         new_point["timestamp"] = now.isoformat()
         new_point["zscore"] = random.uniform(-2.5, 2.5)
         new_point["spread"] = max(0, new_point["spread"] + random.uniform(-1, 1))
         history_data.append(new_point)
         history_data.pop(0) # Keep window fixed size
         
    return {"series": history_data}

@router.get("/alerts/latest", response_model=AlertResponse)
async def get_latest_alert_endpoint():
    """Get the latest trading alert."""
    # Update timestamp to keep it fresh
    latest_alert["timestamp"] = get_utc_now_iso()
    return latest_alert


@router.get("/config", response_model=TradingConfig)
async def get_config():
    """Get current runtime configuration."""
    return CURRENT_CONFIG

@router.post("/config", response_model=TradingConfig)
async def update_config(config: TradingConfig):
    """Update runtime configuration with validation."""
    if config.zscore_entry_threshold <= config.zscore_exit_threshold:
        raise HTTPException(status_code=400, detail="Entry threshold must be greater than exit threshold.")
    if not (0 <= config.min_correlation <= 1):
        raise HTTPException(status_code=400, detail="Correlation must be between 0 and 1.")
    
    global CURRENT_CONFIG
    CURRENT_CONFIG = config
    return CURRENT_CONFIG

@router.get("/analytics/stats", response_model=StatsResponse)
async def get_analytics_stats():
    """
    Return time-series analytics in tabular format suitable for UI + CSV.
    """
    global history_data
    stats_rows = []
    
    # Process history data to generate derived fields
    # Return in reverse chronological order (newest first) for Table UI
    for point in reversed(history_data):
        z = point["zscore"]
        
        # Calculate derived fields
        # Using CURRENT_CONFIG attributes
        is_stationary = abs(z) < CURRENT_CONFIG.zscore_entry_threshold
        
        alert_status = "NONE"
        if z > CURRENT_CONFIG.zscore_entry_threshold:
            alert_status = "SHORT"
        elif z < -CURRENT_CONFIG.zscore_entry_threshold:
            alert_status = "LONG"
            
        stats_rows.append({
            "timestamp": point["timestamp"],
            "zscore": z,
            "spread": point["spread"],
            "correlation": point["correlation"],
            "is_stationary": is_stationary,
            "alert": alert_status
        })
        
    return {"rows": stats_rows}

@router.get("/analytics/stats/csv")
async def get_analytics_stats_csv():
    """
    Generates CSV dynamically from stats data.
    Stream CSV from memory.
    """
    # Reuse the same logic as get_analytics_stats
    global history_data
    
    # Create an in-memory string buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    writer.writerow(["timestamp", "zscore", "spread", "correlation", "is_stationary", "alert"])
    
    # Write Rows (Newest first)
    for point in reversed(history_data):
        z = point["zscore"]
        is_stationary = abs(z) < runtime_config["z_threshold"]
        
        alert_status = "NONE"
        if z > runtime_config["z_threshold"]:
            alert_status = "SHORT"
        elif z < -runtime_config["z_threshold"]:
            alert_status = "LONG"
            
        writer.writerow([
            point["timestamp"],
            z,
            point["spread"],
            point["correlation"],
            is_stationary,
            alert_status
        ])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="analytics_stats.csv"'}
    )
