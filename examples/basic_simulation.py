#!/usr/bin/env python3
"""
Basic CarPort SDK simulation example.

This example demonstrates the core functionality of the CarPort SDK
by running a simple simulation with driver monitoring and obstacle detection.
"""

import time
from carport_sdk import CarPortSimulator

def main():
    """Run basic simulation example."""
    print("CarPort SDK - Basic Simulation Example")
    print("=" * 40)
    
    # Create simulator instance
    simulator = CarPortSimulator()
    
    # Configure components
    simulator.driver_monitoring.set_alert_threshold(3.0)  # 3 second threshold
    simulator.speed_limiting.set_speed_zone("city")  # 50 km/h limit
    
    print("Starting simulation...")
    simulator.start()
    
    try:
        # Simulate normal driving for 2 seconds
        print("Simulating normal driving...")
        simulator.set_vehicle_speed(45.0)  # 45 km/h
        time.sleep(2)
        
        # Simulate driver looking away
        print("Simulating driver looking away...")
        simulator.driver_monitoring.simulate_gaze_away(4.0)  # 4 seconds
        time.sleep(1)
        
        # Check for alerts
        alerts = simulator.get_alerts()
        if alerts:
            print(f"\nAlerts generated ({len(alerts)}):")
            for alert in alerts:
                print(f"  - {alert.severity.upper()}: {alert.message}")
        
        # Add an obstacle
        print("\nAdding pedestrian obstacle...")
        simulator.obstacle_detection.simulate_pedestrian(15.0, crossing=True)
        time.sleep(1)
        
        # Check for more alerts
        new_alerts = simulator.get_alerts(clear=True)
        if new_alerts:
            print(f"\nNew alerts generated ({len(new_alerts)}):")
            for alert in new_alerts:
                print(f"  - {alert.severity.upper()}: {alert.message}")
        
        # Simulate weather change
        print("\nChanging weather to rain...")
        simulator.speed_limiting.set_weather_condition("rain")
        time.sleep(1)
        
        # Show final status
        print("\nFinal simulation status:")
        status = simulator.get_status()
        print(f"  Vehicle speed: {status['vehicle_state'].speed:.1f} km/h")
        print(f"  Driver monitoring enabled: {status['features']['driver_monitoring']['enabled']}")
        print(f"  Obstacles detected: {status['features']['obstacle_detection']['obstacles_count']}")
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    
    finally:
        print("\nStopping simulation...")
        simulator.stop()
        print("Simulation completed!")

if __name__ == "__main__":
    main()