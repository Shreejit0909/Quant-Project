"""
Sampler Module

This module is responsible for aggregating individual trade ticks into OHLCV
(Open, High, Low, Close, Volume) bars for specified time intervals.
It maintains in-memory buffers and handles time-alignment logic.
"""

import sys
import logging
from datetime import datetime, timedelta, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class Sampler:
    def __init__(self):
        """
        Initialize the Sampler.
        Maintains active bars for multiple timeframes.
        """
        # Timeframes in seconds: 1s, 1m (60s), 5m (300s)
        self.timeframes = [1, 60, 300]
        
        # Structure: {(symbol, timeframe_sec): current_bar_dict}
        self.active_bars = {}

    def _get_period_start(self, timestamp: datetime, period_seconds: int) -> datetime:
        """
        Align timestamp to the start of the period (wall-clock time).
        """
        timestamp_sec = timestamp.timestamp()
        aligned_sec = (timestamp_sec // period_seconds) * period_seconds
        return datetime.fromtimestamp(aligned_sec, tz=timezone.utc)

    def _create_bar(self, symbol: str, start_time: datetime, period_seconds: int, price: float, qty: float) -> dict:
        """
        Create a new OHLCV bar with explicit start and end times.
        """
        return {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': start_time + timedelta(seconds=period_seconds),
            'open': price,
            'high': price,
            'low': price,
            'close': price,
            'volume': qty,
            'count': 1
        }

    def _update_bar(self, bar: dict, price: float, qty: float):
        """
        Update an existing OHLCV bar with new tick data.
        """
        bar['high'] = max(bar['high'], price)
        bar['low'] = min(bar['low'], price)
        bar['close'] = price
        bar['volume'] += qty
        bar['count'] += 1

    def _finalize_bar(self, timeframe_sec: int, bar: dict):
        """
        Log the finalized bar.
        Only emit bars with valid data (volume > 0).
        """
        # Discard empty bars or bars with invalid data
        if bar['volume'] <= 0 or bar['close'] <= 0:
            return

        tf_label = f"{timeframe_sec}S"
        if timeframe_sec >= 60:
            tf_label = f"{timeframe_sec // 60}M"

        log_msg = (
            f"[{tf_label:<3}] [{bar['symbol']}] [{bar['start_time'].isoformat()}] "
            f"O={bar['open']:.2f} H={bar['high']:.2f} L={bar['low']:.2f} "
            f"C={bar['close']:.2f} V={bar['volume']:.3f}"
        )
        logger.info(log_msg)

    def _check_buffer_closures(self):
        """
        Check all active bars and finalize those that have passed their end_time.
        This provides time-driven closure piggybacking on tick events.
        """
        now = datetime.now(timezone.utc)
        
        # Create a list of keys to allow modification of dictionary during iteration
        for key in list(self.active_bars.keys()):
            bar = self.active_bars[key]
            timeframe_sec = key[1]
            
            # If current time exceeds the bar's end time, finalize it
            if now > bar['end_time']:
                self._finalize_bar(timeframe_sec, bar)
                del self.active_bars[key]

    def process_tick(self, tick: dict):
        """
        Process a normalized tick and update bars.
        
        Args:
            tick (dict): Expects {'timestamp': ISO_str, 'symbol': str, 'price': float, 'quantity': float}
        """
        # Always run the time-driven closure check first
        self._check_buffer_closures()
        
        if not tick:
            return

        try:
            # Parse timestamp explicitly to UTC datetime
            ts = datetime.fromisoformat(tick['timestamp'])
            price = tick['price']
            qty = tick['quantity']
            symbol = tick['symbol']
            
            now = datetime.now(timezone.utc)

            for tf in self.timeframes:
                key = (symbol, tf)
                period_start = self._get_period_start(ts, tf)
                period_end = period_start + timedelta(seconds=tf)

                # Check if this tick belongs to a period that is already over in wall-clock time
                # If the period end is in the past, it's a late tick that shouldn't re-open a bar
                if period_end < now:
                    continue

                # Check if we have an active bar for this symbol & timeframe
                if key in self.active_bars:
                    current_bar = self.active_bars[key]
                    
                    if period_start == current_bar['start_time']:
                        # Same period, update bar
                        self._update_bar(current_bar, price, qty)
                    else:
                        # Since we ran _check_buffer_closures, stale bars should be gone.
                        # If a bar exists but mismatch start_time, it might be a future bar? 
                        # Or specific edge case. Safest to handle strict match.
                        # If start time doesn't match, and we passed closure check, 
                        # it means the existing bar is valid (future/current) but different? 
                        # With strict wall clock, this implies we might have jumped periods?
                        # In that case, we should finalize the old one (if valid) and start new.
                        # But active_bars should only contain VALID current bars after check.
                        
                        # Just in case: finalize old, start new
                        self._finalize_bar(tf, current_bar)
                        self.active_bars[key] = self._create_bar(symbol, period_start, tf, price, qty)
                        
                else:
                    # No active bar, start one
                    self.active_bars[key] = self._create_bar(symbol, period_start, tf, price, qty)
                    
        except Exception as e:
            logger.error(f"Error processing tick in Sampler: {e}")
