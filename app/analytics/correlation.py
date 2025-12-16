"""
Correlation Calculation Module.

This module computes the rolling Pearson correlation variance between two time series.
Essential for monitoring the stability of the relationship between pairs.
"""

import numpy as np
import pandas as pd

def compute_rolling_correlation(x, y, window):
    """
    Compute the rolling Pearson correlation coefficient between two series.
    
    Args:
        x (array-like): First time series.
        y (array-like): Second time series.
        window (int): Rolling window size.
        
    Returns:
        np.ndarray: Array of rolling correlation values.
        
    Raises:
        ValueError: If input lengths mismatch or window is invalid.
    """
    if window <= 1:
        raise ValueError("Window size must be greater than 1.")
        
    s1 = pd.Series(x)
    s2 = pd.Series(y)
    
    if len(s1) != len(s2):
        raise ValueError("Input series x and y must have the same length.")
        
    # Compute rolling correlation
    rolling_corr = s1.rolling(window=window).corr(s2)
    
    return rolling_corr.to_numpy()
