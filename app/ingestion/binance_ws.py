
import asyncio
import json
import logging
import time
from collections import deque
from datetime import datetime, timezone
import websockets
import numpy as np
from app.api.routes import history_data, latest_alert, CURRENT_CONFIG

# Configuration
# Using Futures stream as requested: fstream.binance.com
# Stream names are lowercase: btcusdt@trade / ethusdt@trade
URI = "wss://fstream.binance.com/ws/btcusdt@trade/ethusdt@trade"
WINDOW_SIZE = 50 

# State Buffers
btc_prices = deque(maxlen=WINDOW_SIZE)
eth_prices = deque(maxlen=WINDOW_SIZE)
spread_history = deque(maxlen=WINDOW_SIZE)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BinanceWS")

async def start_binance_ws():
    """
    Connects to Binance WebSocket and ingests live market data.
    """
    while True:
        try:
            async with websockets.connect(URI) as websocket:
                logger.info("Connected to Binance WebSocket")
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    process_message(data)
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

def process_message(data):
    """
    Normalizes message and updates analytics.
    Payload Example: {"e":"trade", "s":"BTCUSDT", "p":"98000.50", "T":1678900000000, ...}
    """
    try:
        symbol = data.get('s')
        price = float(data.get('p', 0))
        
        # Use ingestion time with high precision as requested
        # 'T' is trade time, but user requested time.time() (float, includes milliseconds)
        # We allow isoformat() to include the fractional seconds by default
        timestamp_str = datetime.fromtimestamp(time.time(), timezone.utc).isoformat()
        
        
        # Update Price Buffers
        if symbol == 'BTCUSDT':
            btc_prices.append(price)
        elif symbol == 'ETHUSDT':
            eth_prices.append(price)
        else:
            return

        # Trigger Analytics Update
        # We update if we have at least minimal data for both
        if len(btc_prices) > 1 and len(eth_prices) > 1:
            update_analytics(timestamp_str)
            
    except Exception as e:
        logger.warning(f"Error processing message: {e}")

def update_analytics(timestamp):
    # 1. Fetch latest prices
    current_btc = btc_prices[-1]
    current_eth = eth_prices[-1]
    
    # 2. Compute Spread
    # Using a simple fixed ratio for stability in this demo context, 
    # or we could calculate meaningful ratio dynamically.
    # Given we want "Correlation responds better to volatility", 
    # let's assume a simplified stationary relationship expectation:
    # Spread = BTC - Ratio * ETH. 
    # Current Market: BTC ~100k, ETH ~4k. Ratio ~25.
    HEDGE_RATIO = 25.0 
    spread = current_btc - (HEDGE_RATIO * current_eth)
    
    spread_history.append(spread)
    
    if len(spread_history) < 5:
        return

    # 3. Compute Z-Score
    spreads_arr = np.array(spread_history)
    mean_spread = np.mean(spreads_arr)
    std_spread = np.std(spreads_arr)
    
    zscore = 0.0
    if std_spread > 1e-6:
        zscore = (spread - mean_spread) / std_spread
        
    # 4. Compute Correlation
    # We take the aligned tail of both queues
    min_len = min(len(btc_prices), len(eth_prices))
    
    btc_arr = np.array(list(btc_prices)[-min_len:])
    eth_arr = np.array(list(eth_prices)[-min_len:])

    if len(btc_arr) < 20 or np.std(btc_arr) < 1e-6 or np.std(eth_arr) < 1e-6:
        corr = None
    else:
        corr = float(np.corrcoef(btc_arr, eth_arr)[0, 1])
    
    correlation = corr

    # 5. Stationarity Check
    is_stationary = abs(zscore) < CURRENT_CONFIG.zscore_entry_threshold
    
    # 6. Update Shared Runtime State
    new_data_point = {
        "timestamp": timestamp,
        "zscore": float(zscore),
        "spread": float(spread),
        "correlation": correlation,
        "hedge_ratio": float(HEDGE_RATIO)
    }
    
    # Atomic List Update (GIL protected)
    history_data.append(new_data_point)
    if len(history_data) > WINDOW_SIZE:
        history_data.pop(0)
        
    # 7. Check Alerts
    update_alerts(new_data_point)

def update_alerts(data):
    z = data['zscore']
    threshold = CURRENT_CONFIG.zscore_entry_threshold
    min_corr = CURRENT_CONFIG.min_correlation
    corr = data.get('correlation')
    
    # Filter by Correlation
    if corr is not None and corr < min_corr:
        return # Skip alert if correlation is too weak
        
    alert_signal = "NONE"
    if z > threshold:
        alert_signal = "SHORT"
    elif z < -threshold:
        alert_signal = "LONG"
        
    if alert_signal != "NONE":
        latest_alert.update({
             "timestamp": data['timestamp'],
             "type": "SIGNAL",
             "signal": alert_signal,
             "z_score": z,
             "reason": f"Z-Score ({z:.2f}) crossed {alert_signal} threshold (Corr: {corr if corr else 'N/A'})"
        })
