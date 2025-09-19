#!/usr/bin/env python3
"""
Driver Monitoring Test Example.

Demonstrates the driver monitoring feature (DP-601) with various test scenarios
including TC-601.1: Driver looks away >5 sec → escalating alerts.
"""

import time
from carport_sdk import CarPortSimulator

def test_driver_monitoring():
    """Test driver monitoring scenarios."""
    print("CarPort SDK - Driver Monitoring Test")
    print("=" * 40)
    
    simulator = CarPortSimulator()
    
    # Configure driver monitoring with 5-second threshold (per specification)
    simulator.driver_monitoring.set_alert_threshold(5.0)
    
    print("Starting simulation...")
    simulator.start()
    
    try:
        # Test Case 1: Normal attention
        print("\nTest 1: Normal driving with forward gaze")
        simulator.driver_monitoring.simulate_gaze_direction("forward")
        time.sleep(2)
        
        alerts = simulator.get_alerts(clear=True)
        print(f"Alerts: {len(alerts)} (expected: 0)")
        
        # Test Case 2: Brief distraction (< threshold)
        print("\nTest 2: Brief distraction (3 seconds)")
        simulator.driver_monitoring.simulate_gaze_away(3.0)
        time.sleep(1)
        
        alerts = simulator.get_alerts(clear=True)
        print(f"Alerts: {len(alerts)} (expected: 0)")
        
        # Test Case 3: TC-601.1 - Extended distraction (> threshold)
        print("\nTest 3: TC-601.1 - Extended distraction (6 seconds)")
        simulator.driver_monitoring.simulate_gaze_away(6.0)
        time.sleep(1)
        
        alerts = simulator.get_alerts(clear=True)
        print(f"Alerts: {len(alerts)} (expected: 1+)")
        for alert in alerts:
            print(f"  - {alert.severity}: {alert.message}")
        
        # Test Case 4: Different gaze directions
        print("\nTest 4: Different gaze directions")
        directions = ["left", "right", "down", "away"]
        
        for direction in directions:
            print(f"  Testing gaze direction: {direction}")
            simulator.driver_monitoring.simulate_gaze_direction(direction)
            time.sleep(1.5)  # 1.5 seconds each
            
        # Check cumulative effect
        status = simulator.driver_monitoring.get_status()
        print(f"  Time looking away: {status['time_looking_away']:.1f}s")
        print(f"  Alert level: {status['alert_level']}")
        
        alerts = simulator.get_alerts(clear=True)
        if alerts:
            print(f"  Generated alerts: {len(alerts)}")
            for alert in alerts:
                print(f"    - {alert.severity}: {alert.message}")
        
        # Test Case 5: Eyes closed simulation
        print("\nTest 5: Eyes closed scenario")
        simulator.driver_monitoring.simulate_eyes_closed(True)
        time.sleep(2)
        simulator.driver_monitoring.simulate_eyes_closed(False)
        
        alerts = simulator.get_alerts(clear=True)
        print(f"Alerts: {len(alerts)}")
        
        # Test Case 6: Recovery scenario
        print("\nTest 6: Recovery - return to forward gaze")
        simulator.driver_monitoring.simulate_gaze_direction("forward")
        time.sleep(2)
        
        status = simulator.driver_monitoring.get_status()
        print(f"  Time looking away after recovery: {status['time_looking_away']:.1f}s")
        print(f"  Alert level after recovery: {status['alert_level']}")
        
        print("\nDriver monitoring test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    finally:
        simulator.stop()

if __name__ == "__main__":
    test_driver_monitoring()