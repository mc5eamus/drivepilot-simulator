#!/usr/bin/env python3
"""
Basic example demonstrating the DrivePilot Simulator SDK.

This example shows how to:
1. Create a simulation environment
2. Initialize a car with all features enabled
3. Run simulation scenarios for each DP requirement
4. Monitor events and vehicle status
"""

import time
from drivepilot_simulator import Car, SimulationEnvironment, EventType


def print_event(event):
    """Print simulation events for monitoring."""
    print(f"[{event.timestamp:.2f}] {event.event_type.value}: {event.data}")


def main():
    """Run basic simulation example."""
    print("=== DrivePilot Simulator - Basic Example ===\n")
    
    # Create simulation environment
    print("1. Creating simulation environment...")
    env = SimulationEnvironment()
    
    # Subscribe to all events for monitoring
    for event_type in EventType:
        env.subscribe_to_event(event_type, print_event)
    
    # Create and configure car
    print("2. Creating and configuring car...")
    car = Car(environment=env, car_id="demo_car")
    
    # Enable all features
    car.enable_driver_monitoring(alert_threshold=5.0)
    car.enable_adaptive_speed(weather_factor=True)
    car.enable_ota_updates()
    car.enable_obstacle_detection(sensors=['radar', 'ir', 'ultrasonic'])
    car.enable_regulatory_mode()
    
    # Start simulation
    print("3. Starting simulation...\n")
    car.start_simulation()
    
    # Scenario 1: Driver Monitoring (DP-601)
    print("=== Scenario 1: Driver Monitoring (DP-601) ===")
    print("Testing driver attention monitoring...")
    
    # Simulate driver looking away
    car.update_driver_attention(is_attentive=False)
    time.sleep(1)  # Wait for events to process
    
    # Simulate extended inattention (should trigger alerts)
    for i in range(6):
        car.update_driver_attention(is_attentive=False)
        time.sleep(0.5)
    
    # Driver regains attention
    car.update_driver_attention(is_attentive=True)
    print("Driver attention regained.\\n")
    
    # Scenario 2: Adaptive Speed Limiting (DP-602)
    print("=== Scenario 2: Adaptive Speed Limiting (DP-602) ===")
    print("Testing adaptive speed control...")
    
    # Start driving
    car.drive_to("Test Location", speed=60.0)
    time.sleep(0.5)
    
    # Enter speed zone (TC-602.1)
    print("Entering 30 km/h speed zone...")
    car.set_speed_limit(30.0)
    time.sleep(1)
    
    # Weather change (TC-602.2)
    print("Weather change: Rain starting...")
    env.set_weather_conditions({
        "precipitation": 5.0,  # 5mm/hour rain
        "visibility": 800      # Reduced visibility
    })
    time.sleep(1)
    print()
    
    # Scenario 3: OTA Updates (DP-603)
    print("=== Scenario 3: OTA Updates (DP-603) ===")
    print("Testing OTA update system...")
    
    # TC-603.1: Valid update
    print("Attempting valid update...")
    success = car.simulate_ota_update("1.1.0", is_valid=True)
    print(f"Update success: {success}")
    
    # TC-603.2: Invalid signature
    print("Attempting update with invalid signature...")
    success = car.simulate_ota_update("1.2.0", is_valid=False)
    print(f"Update success: {success}")
    time.sleep(1)
    print()
    
    # Scenario 4: Obstacle Detection (DP-604)
    print("=== Scenario 4: Obstacle Detection (DP-604) ===")
    print("Testing obstacle detection...")
    
    # TC-604.1: Pedestrian detection
    print("Detecting pedestrian ahead...")
    car.detect_obstacle("pedestrian", distance=8.0, confidence=0.95)
    time.sleep(0.5)
    
    # TC-604.2: Animal at night
    print("Detecting animal at night...")
    car.detect_obstacle("animal", distance=15.0, confidence=0.8)
    time.sleep(0.5)
    
    # TC-604.3: Static object
    print("Detecting static object...")
    car.detect_obstacle("static_object", distance=4.0, confidence=0.9)
    time.sleep(1)
    print()
    
    # Scenario 5: Regulatory Mode Switching (DP-605)
    print("=== Scenario 5: Regulatory Mode Switching (DP-605) ===")
    print("Testing regulatory compliance...")
    
    # TC-605.1: Cross border (simulate location change)
    print("Crossing border from EU to US...")
    env.set_location({
        "latitude": 40.7128,   # New York
        "longitude": -74.0060,
        "altitude": 10.0
    })
    time.sleep(1)
    
    print("Crossing border from US to China...")
    env.set_location({
        "latitude": 39.9042,   # Beijing
        "longitude": 116.4074,
        "altitude": 44.0
    })
    time.sleep(1)
    print()
    
    # Show final status
    print("=== Final Vehicle Status ===")
    status = car.get_status()
    print(f"State: {status.state.value}")
    print(f"Speed: {status.speed:.1f} km/h")
    print(f"Current Region: {status.current_region}")
    print(f"Compliance Mode: {status.compliance_mode}")
    print(f"Software Version: {status.software_version}")
    print(f"Enabled Features: {', '.join(status.enabled_features)}")
    print(f"Driver State: {status.driver_state.value}")
    
    # Show event log summary
    events = env.get_event_log()
    print(f"\\nTotal events recorded: {len(events)}")
    
    # Stop simulation
    print("\\n=== Stopping Simulation ===")
    car.stop_simulation()
    env.stop()
    
    print("Simulation completed successfully!")


if __name__ == "__main__":
    main()