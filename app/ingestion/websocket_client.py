"""
Binance WebSocket Client for Live Data Ingestion

This module connects to the Binance Futures WebSocket API to receive real-time trade data.
It handles connection management, subscription to multiple symbols, and normalization of
trade messages into a standard format.

Key Features:
- Asynchronous connection handling using `websockets`
- Automatic reconnection logic
- Message normalization to standard dictionary format
- thread-safe logging of trade ticks
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timezone
import websockets

from app.sampling.sampler import Sampler

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class BinanceWebsocketClient:
    def __init__(self, symbols):
        """
        Initialize the WebSocket client.
        
        Args:
            symbols (list): List of symbols to subscribe to (e.g., ['btcusdt', 'ethusdt'])
        """
        self.symbols = [s.lower() for s in symbols]
        self.base_url = "wss://fstream.binance.com/ws"
        self.running = False
        self.sampler = Sampler()
        
    def normalize(self, message):
        """
        Normalize the raw Binance trade message into a standard format.
        
        Args:
            message (dict): Raw message from Binance WebSocket
            
        Returns:
            dict: Normalized trade data or None if invalid
        """
        try:
            # Binance trade message format checks
            if 'e' in message and message['e'] == 'trade':
                return {
                    'timestamp': datetime.fromtimestamp(message['T'] / 1000, tz=timezone.utc).isoformat(),
                    'symbol': message['s'],
                    'price': float(message['p']),
                    'quantity': float(message['q'])
                }
            # Handle other message types or return None
            return None
        except Exception as e:
            logger.error(f"Error normalizing message: {e}")
            return None

    def log_trade(self, trade):
        """
        Log the normalized trade data in a clean format.
        DEPRECATED in Phase 2: Sampler handles logging.
        """
        pass

    async def subscribe(self, ws):
        """
        Send subscription message to the WebSocket.
        """
        params = [f"{s}@trade" for s in self.symbols]
        sub_msg = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": 1
        }
        await ws.send(json.dumps(sub_msg))
        logger.info(f"Subscribed to: {', '.join(params)}")

    async def connect(self):
        """
        Main connection loop with reconnection logic.
        """
        self.running = True
        while self.running:
            try:
                logger.info(f"Connecting to {self.base_url}...")
                async with websockets.connect(self.base_url) as ws:
                    await self.subscribe(ws)
                    
                    async for message in ws:
                        if not self.running:
                            break
                            
                        try:
                            data = json.loads(message)
                            
                            # Process trade data
                            trade = self.normalize(data)
                            if trade:
                                # Phase 2: Pass to sampler
                                self.sampler.process_tick(trade)
                                
                        except json.JSONDecodeError:
                            logger.error("Failed to decode message")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
            except (websockets.ConnectionClosed, asyncio.TimeoutError) as e:
                logger.warning(f"Connection lost: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the client."""
        logger.info("Stopping WebSocket client...")
        self.running = False

async def main():
    # Define symbols to monitor
    symbols = ['btcusdt', 'ethusdt']
    
    client = BinanceWebsocketClient(symbols)
    
    # Run the client
    try:
        await client.connect()
    except asyncio.CancelledError:
        pass
    finally:
        await shutdown(client)

async def shutdown(client):
    client.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    if sys.platform == 'win32':
        # Windows-specific event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        # Windows signal handling workaround for asyncio
        # Run main() directly
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
