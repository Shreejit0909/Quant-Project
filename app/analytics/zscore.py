"""
Z-Score Calculation Module.

This module calculates the rolling Z-Score of a time series.
Z-Score measures how many standard deviations a data point is from the mean.
"""

import numpy as np
import pandas as pd

def compute_zscore(series, window):
    """
    Compute the rolling Z-Score of a series.
    
    Z = (Value - Rolling Mean) / Rolling Std
    
    Args:
        series (array-like): Input time series data.
        window (int): Size of the rolling window.
        
    Returns:
        np.ndarray: Array of Z-Scores. First (window-1) elements will be NaN.
        
    Raises:
        ValueError: If input series is empty or window is invalid.
    """
    if window <= 1:
        raise ValueError("Window size must be greater than 1.")
        
    # Convert to pandas Series for efficient rolling operations
    s = pd.Series(series)
    
    if len(s) == 0:
        return np.array([])
        
    rolling = s.rolling(window=window)
    r_mean = rolling.mean()
    r_std = rolling.std(ddof=1) # Sample standard deviation
    
    # Compute Z-Score
    # We use numpy to handle division by zero (resulting in inf) or 0/0 (resulting in NaN) gracefully if needed
    # But generally pandas handles this well.
    z_score = (s - r_mean) / r_std
    
    # Fill infinite values with NaN to be safe? 
    # Or keep them as is. Standard behavior is to return what calc gives.
    # The requirement says "Protect against divide-by-zero".
    
    # Replace infinite values with NaN to ensure safety
    z_score = z_score.replace([np.inf, -np.inf], np.nan)
    
    return z_score.to_numpy()
