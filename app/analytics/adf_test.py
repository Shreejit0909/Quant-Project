"""
Stationarity Test Module.

This module performs the Augmented Dickey-Fuller (ADF) test to check for stationarity
in a time series. Stationarity is a key assumption for mean-reverting strategies.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def run_adf_test(series):
    """
    Run Augmented Dickey-Fuller test on a time series.
    
    Args:
        series (array-like): Input time series.
        
    Returns:
        dict: {
            "adf_statistic": float,
            "p_value": float,
            "is_stationary": bool
        }
        
    Raises:
        ValueError: If input series is too short for the test.
    """
    # Clean input: remove NaNs/Infs
    s = pd.Series(series).dropna()
    s = s[np.isfinite(s)]
    
    # ADF test requires some data length. Statsmodels usually handles small samples but
    # it's good to check. 
    if len(s) < 10: 
        # Very short series might cause errors or return garbage
        return {
            "adf_statistic": np.nan,
            "p_value": np.nan,
            "is_stationary": False
        }
        
    try:
        # Perform ADF test
        # autolag='AIC' chooses the optimal number of lags to minimize AIC
        result = adfuller(s, autolag='AIC')
        
        adf_stat = result[0]
        p_val = result[1]
        
        # Determine stationarity (common threshold is 0.05)
        is_stationary = p_val < 0.05
        
        return {
            "adf_statistic": float(adf_stat),
            "p_value": float(p_val),
            "is_stationary": bool(is_stationary)
        }
        
    except Exception:
        # Graceful failure for edge cases (e.g. constant series)
        return {
            "adf_statistic": np.nan,
            "p_value": np.nan,
            "is_stationary": False
        }
