"""
Spread Calculation Module.

This module calculates the spread between two price series given a hedge ratio.
Spread = Y - (Hedge Ratio * X)
"""

import numpy as np
import pandas as pd

def compute_spread(x, y, hedge_ratio):
    """
    Compute the spread series given two assets and a hedge ratio.
    
    Formula: Spread = y - (hedge_ratio * x)
    
    Args:
        x (array-like): Independent asset prices.
        y (array-like): Dependent asset prices.
        hedge_ratio (float): The calculated hedge ratio (beta).
        
    Returns:
        np.ndarray: Array containing the spread values.
        
    Raises:
        ValueError: If x and y have different lengths or hedge_ratio is invalid.
    """
    if hedge_ratio is None:
        raise ValueError("Hedge ratio cannot be None.")
        
    # Convert to numpy arrays for vectorized operation
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    
    if len(x_arr) != len(y_arr):
        raise ValueError("Input arrays x and y must have the same length.")
        
    # Compute spread
    spread = y_arr - (hedge_ratio * x_arr)
    
    return spread
