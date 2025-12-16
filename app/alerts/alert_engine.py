"""
Alert Engine Module.

This module is responsible for converting raw analytics metrics (Z-Score, Correlation, Stationarity)
into actionable trading alerts. It implements a state machine to prevent signal spamming
and ensures that signals are only generated when specific criteria are met.
"""

class AlertEngine:
    def __init__(self, threshold=2.0, reset_threshold=0.5, min_correlation=0.7):
        """
        Initialize the Alert Engine.
        
        Args:
            threshold (float): Z-Score threshold for triggering signals (default: 2.0).
            reset_threshold (float): Z-Score threshold for resetting alert state (default: 0.5).
            min_correlation (float): Minimum correlation required to trigger a signal (default: 0.7).
        """
        self.threshold = threshold
        self.reset_threshold = reset_threshold
        self.min_correlation = min_correlation
        
        # State tracking: None, 'LONG', or 'SHORT'
        self.current_state = None

    def evaluate(self, z_score, rolling_correlation, adf_result, timestamp):
        """
        Evaluate market metrics to generate trade alerts.
        
        Args:
            z_score (float): Current Z-Score value.
            rolling_correlation (float): Current rolling correlation value.
            adf_result (dict): Result from ADF test {'is_stationary': bool, ...}.
            timestamp (str): ISO 8601 timestamp string.
            
        Returns:
            dict or None: Alert dictionary if triggered, else None.
        """
        if z_score is None or rolling_correlation is None or adf_result is None:
            return None

        # 1. State Reset Logic
        # We only reset state if we are currently holding a position/signal state
        if self.current_state is not None:
            if abs(z_score) < self.reset_threshold:
                self.current_state = None
                # Optionally logs could go here via a logger, but requirements say no printing/side-effects.
                # We just silently reset internal state.
                return None
            
            # If we are in a state and Z-score hasn't neutralized, we simply hold.
            # No new alert is generated (Anti-Spam).
            return None

        # 2. Trigger Logic (Only if State is None)
        
        # Filter 1: Correlation
        if rolling_correlation < self.min_correlation:
            return None
            
        # Filter 2: Stationarity
        if not adf_result.get('is_stationary', False):
            return None
            
        # Filter 3: Z-Score Thresholds
        signal = None
        reason = ""
        
        if z_score >= self.threshold:
            signal = "SHORT"
            reason = f"Z-Score ({z_score:.2f}) >= Threshold ({self.threshold}) [Overbought]"
            
        elif z_score <= -self.threshold:
            signal = "LONG"
            reason = f"Z-Score ({z_score:.2f}) <= -Threshold (-{self.threshold}) [Oversold]"
            
        if signal:
            # Update State
            self.current_state = signal
            
            # Construct Alert
            return {
                "timestamp": timestamp,
                "signal": signal,
                "z_score": z_score,
                "correlation": rolling_correlation,
                "reason": reason
            }
            
        return None
