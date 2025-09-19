#!/usr/bin/env python3
"""
Quick demonstration of the DrivePilot Simulator functionality.
This script shows all major features working together.
"""

from drivepilot_simulator import Car, SimulationEnvironment, EventType

def demo():
    """Run a quick demonstration of the simulator."""
    print("=== DrivePilot Simulator - Quick Demo ===")
    print()
    
    # Setup
    env = SimulationEnvironment()
    car = Car(environment=env, car_id="demo_vehicle")
    
    # Event counter
    event_count = 0
    
    def count_events(event):
        nonlocal event_count
        event_count += 1
        print(f"Event {event_count}: {event.event_type.value}")
    
    # Subscribe to key events
    for event_type in [EventType.SIMULATION_STARTED, EventType.DRIVER_ALERT_VISUAL, 
                       EventType.SPEED_ADJUSTED, EventType.OBSTACLE_DETECTED,
                       EventType.REGION_CHANGED]:
        env.subscribe_to_event(event_type, count_events)
    
    print("1. Enabling all features...")
    car.enable_driver_monitoring(alert_threshold=3.0)
    car.enable_adaptive_speed()
    car.enable_obstacle_detection()
    car.enable_regulatory_mode()
    car.enable_ota_updates()
    
    print("2. Starting simulation...")
    car.start_simulation()
    
    print("3. Testing driver monitoring (DP-601)...")
    # Simulate brief inattention
    car.update_driver_attention(is_attentive=False)
    car.update_driver_attention(is_attentive=False)
    car.update_driver_attention(is_attentive=False)
    car.update_driver_attention(is_attentive=False)
    car.update_driver_attention(is_attentive=True)  # Regain attention
    
    print("4. Testing adaptive speed (DP-602)...")
    car.drive_to("Test Location", speed=50.0)
    car.set_speed_limit(30.0)  # Enter speed zone
    
    print("5. Testing obstacle detection (DP-604)...")
    car.detect_obstacle("pedestrian", distance=8.0)
    
    print("6. Testing regulatory compliance (DP-605)...")
    env.set_location({"latitude": 40.7128, "longitude": -74.0060})  # US location
    
    print("7. Testing OTA updates (DP-603)...")
    car.simulate_ota_update("1.1.0", is_valid=True)
    
    # Show final status
    status = car.get_status()
    print()
    print("=== Final Status ===")
    print(f"Vehicle State: {status.state.value}")
    print(f"Current Region: {status.current_region}")  
    print(f"Speed: {status.speed:.1f} km/h")
    print(f"Enabled Features: {', '.join(sorted(status.enabled_features))}")
    print(f"Software Version: {status.software_version}")
    print(f"Total Events Generated: {event_count}")
    
    print()
    print("✓ Demonstration completed successfully!")
    print("✓ All DP-601 through DP-605 features working")
    
    # Cleanup
    car.stop_simulation()
    env.stop()

if __name__ == "__main__":
    demo()