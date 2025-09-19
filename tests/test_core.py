"""
Tests for CarPort SDK core functionality.
"""

import pytest
import time
from carport_sdk import CarPortSimulator, Event, EventBus
from carport_sdk.core.models import VehicleState, AlertData

def test_simulator_creation():
    """Test CarPort simulator can be created."""
    simulator = CarPortSimulator()
    assert simulator is not None
    assert simulator.event_bus is not None
    assert simulator.vehicle_state is not None

def test_simulator_start_stop(simulator):
    """Test simulator start and stop functionality."""
    # Initially not running
    assert not simulator._running
    
    # Start simulator
    simulator.start()
    assert simulator._running
    
    # Stop simulator
    simulator.stop()
    assert not simulator._running

def test_vehicle_state_updates(simulator):
    """Test vehicle state can be updated."""
    # Test position update
    simulator.set_vehicle_position(40.7128, -74.0060)  # NYC coordinates
    assert simulator.vehicle_state.position["lat"] == 40.7128
    assert simulator.vehicle_state.position["lon"] == -74.0060
    
    # Test speed update
    simulator.set_vehicle_speed(50.0)
    assert simulator.vehicle_state.speed == 50.0
    assert not simulator.vehicle_state.is_stationary
    
    # Test stationary detection
    simulator.set_vehicle_speed(0.5)
    assert simulator.vehicle_state.is_stationary

def test_event_bus():
    """Test event bus functionality."""
    event_bus = EventBus()
    received_events = []
    
    def event_handler(event):
        received_events.append(event)
    
    # Subscribe to events
    event_bus.subscribe("test_event", event_handler)
    
    # Publish event
    test_event = Event("test_event", data="test_data")
    event_bus.publish(test_event)
    
    # Verify event received
    assert len(received_events) == 1
    assert received_events[0].event_type == "test_event"
    assert received_events[0].data == "test_data"

def test_alert_handling(simulator):
    """Test alert handling functionality."""
    # Create test alert
    alert = AlertData(
        alert_type="test_alert",
        severity="warning",
        message="Test alert message",
        source_component="TestComponent"
    )
    
    # Publish alert event
    event = Event("alert", data=alert)
    simulator.event_bus.publish(event)
    
    # Check alert was recorded
    alerts = simulator.get_alerts()
    assert len(alerts) == 1
    assert alerts[0].alert_type == "test_alert"
    assert alerts[0].severity == "warning"

def test_status_reporting(simulator):
    """Test comprehensive status reporting."""
    status = simulator.get_status()
    
    # Check required status fields
    assert "running" in status
    assert "vehicle_state" in status
    assert "alert_count" in status
    assert "features" in status
    
    # Check feature status
    features = status["features"]
    expected_features = [
        "driver_monitoring",
        "speed_limiting", 
        "ota_updates",
        "obstacle_detection",
        "regulatory_mode"
    ]
    
    for feature in expected_features:
        assert feature in features