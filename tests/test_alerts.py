"""
Test script for verifying Alert Engine behavior.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.alerts.alert_engine import AlertEngine

def test_alert_engine():
    print("Verifying Alert Engine...")
    
    engine = AlertEngine(threshold=2.0, reset_threshold=0.5, min_correlation=0.7)
    
    # Common dummy inputs
    ts = "2025-01-01T10:00:00"
    adf_stationary = {"is_stationary": True}
    adf_non_stationary = {"is_stationary": False}
    
    # 1. Test Normal Trigger (SHORT)
    # Z=2.5, Corr=0.9, Stationary=True -> Should Trigger SHORT
    alert = engine.evaluate(2.5, 0.9, adf_stationary, ts)
    print(f"Test 1 (Trigger SHORT): {alert['signal'] if alert else 'None'}")
    assert alert is not None
    assert alert['signal'] == "SHORT"
    assert engine.current_state == "SHORT"

    # 2. Test Anti-Spam (Same condition)
    # Z=2.6, Corr=0.9, Stationary=True -> Should return None (State is already SHORT)
    alert = engine.evaluate(2.6, 0.9, adf_stationary, ts)
    print(f"Test 2 (Anti-Spam): {alert}")
    assert alert is None
    
    # 3. Test Reset Condition
    # Z=0.1 (in 0.5 range), Corr=0.9, Stationary=True -> Should Reset State to None
    alert = engine.evaluate(0.1, 0.9, adf_stationary, ts)
    print(f"Test 3 (Reset State): State is now {engine.current_state}")
    assert alert is None
    assert engine.current_state is None
    
    # 4. Test Normal Trigger (LONG)
    # Z=-2.5 -> Should Trigger LONG
    alert = engine.evaluate(-2.5, 0.9, adf_stationary, ts)
    print(f"Test 4 (Trigger LONG): {alert['signal'] if alert else 'None'}")
    assert alert is not None
    assert alert['signal'] == "LONG"
    
    # 5. Test Filters (Correlation)
    # Reset first
    engine.evaluate(0.0, 0.9, adf_stationary, ts)
    
    # Z=2.5, Corr=0.4 (Low) -> Should NOT Trigger
    alert = engine.evaluate(2.5, 0.4, adf_stationary, ts)
    print(f"Test 5 (Filter - Low Corr): {alert}")
    assert alert is None
    
    # 6. Test Filters (Stationarity)
    # Z=2.5, Corr=0.9, Non-Stationary -> Should NOT Trigger
    alert = engine.evaluate(2.5, 0.9, adf_non_stationary, ts)
    print(f"Test 6 (Filter - Non Stationary): {alert}")
    assert alert is None
    
    print("\nALL ALERT TESTS PASSED ✅")

if __name__ == "__main__":
    try:
        test_alert_engine()
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
