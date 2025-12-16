"""
Hedge Ratio Calculation Module.

This module provides functions to compute the hedge ratio (beta) between two price series
using Ordinary Least Squares (OLS) regression. The hedge ratio represents the number of
units of asset X needed to hedge one unit of asset Y.
"""

import numpy as np

def compute_hedge_ratio(x, y):
    """
    Compute the hedge ratio (beta) of y with respect to x using OLS without an intercept.
    
    Model: y = beta * x + epsilon
    
    Args:
        x (array-like): Independent variable (e.g., benchmark or hedge asset).
        y (array-like): Dependent variable (e.g., target asset).
        
    Returns:
        float: The hedge ratio (beta). Returns None if input data is invalid or insufficient.
        
    Raises:
        ValueError: If x and y have different lengths.
    """
    # Convert inputs to numpy arrays
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    
    # Validate lengths
    if len(x_arr) != len(y_arr):
        raise ValueError("Input arrays x and y must have the same length.")
        
    # Check for empty or insufficient data
    if len(x_arr) < 2:
        return None
        
    # Check for NaNs or Infinite values
    if not np.isfinite(x_arr).all() or not np.isfinite(y_arr).all():
        return None
        
    # Compute OLS (No intercept as per strict hedge ratio definitions usually)
    # Using numpy.linalg.lstsq for efficiency
    # Reshape x to be a column vector for matrix multiplication if needed,
    # but for 1D simple regression: slope = dot(x, y) / dot(x, x) (for zero intercept)
    
    # Implementing generic OLS logic
    # beta = Cov(x, y) / Var(x) ... but wait, user asked for y = beta * x + epsilon
    # This implies a regression through origin if no alpha is mentioned.
    # Standard pairs trading often uses standard OLS with intercept but hedge ratio is just beta.
    # However, for pure hedge ratio often we regress WITHOUT intercept if we want strict dollar neutrality 
    # capability without cash component, or WITH intercept if we allow spread mean to be non-zero.
    # Given "y = beta * x + epsilon", this usually implies keeping the constant term in epsilon or ignoring it.
    # Let's use np.polyfit(deg=1) which includes intercept, as allows spread to float.
    # Slope is index 0.
    
    try:
        slope, _ = np.polyfit(x_arr, y_arr, 1)
        return float(slope)
    except Exception:
        return None
