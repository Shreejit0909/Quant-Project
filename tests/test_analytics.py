"""
Test script for verifying analytics modules.
"""
import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.analytics.hedge_ratio import compute_hedge_ratio
from app.analytics.spread import compute_spread
from app.analytics.zscore import compute_zscore
from app.analytics.correlation import compute_rolling_correlation
from app.analytics.adf_test import run_adf_test

def test_analytics():
    print("Verifying Analytics Modules...")

    # 1. Hedge Ratio
    # y = 2 * x + noise
    x = np.linspace(0, 10, 100)
    y = 2 * x + np.random.normal(0, 0.1, 100)
    beta = compute_hedge_ratio(x, y)
    print(f"Computed Hedge Ratio (Expected ~2.0): {beta:.4f}")
    assert 1.9 <= beta <= 2.1, "Hedge ratio calculation failed"

    # 2. Spread
    spread = compute_spread(x, y, beta)
    print(f"Spread Mean (Expected ~0): {np.mean(spread):.4f}")
    assert abs(np.mean(spread)) < 0.2, "Spread calculation failed"

    # 3. Z-Score
    # Create a series with a spike
    series = np.ones(50) * 10
    series[25] = 20 # Spike
    z = compute_zscore(series, window=10)
    print(f"Z-Score at spike (index 25): {z[25]:.4f}")
    # At index 25, value is 20. Previous 9 are 10. Mean of 10 items (9*10 + 20) / 10 = 11.
    # Std dev of [10, 10, ..., 20]. 
    # This should be a significant positive z-score
    assert z[25] > 2, "Z-Score calculation failed"
    assert np.isnan(z[0]), "Z-Score should be NaN for first element"

    # 4. Correlation
    x_corr = np.sin(np.linspace(0, 10, 100))
    y_corr = np.sin(np.linspace(0, 10, 100)) # Perfect correlation
    corr = compute_rolling_correlation(x_corr, y_corr, window=20)
    print(f"Correlation at end (Expected ~1.0): {corr[-1]:.4f}")
    assert corr[-1] > 0.99, "Correlation calculation failed"

    # 5. ADF Test
    # Mean reverting series (noise)
    stationary = np.random.normal(0, 1, 100)
    res = run_adf_test(stationary)
    print(f"ADF P-Value (Stationary): {res['p_value']:.4f}")
    assert res['is_stationary'] == True, "ADF test failed for stationary series"

    # Random walk (non-stationary)
    random_walk = np.cumsum(np.random.normal(0, 1, 100))
    res_rw = run_adf_test(random_walk)
    print(f"ADF P-Value (Random Walk): {res_rw['p_value']:.4f}")
    assert res_rw['is_stationary'] == False, "ADF test failed for random walk"

    print("\nALL ANALYTICS TESTS PASSED ✅")

if __name__ == "__main__":
    try:
        test_analytics()
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ unexpected error: {e}")
        sys.exit(1)
