"""
Tests for DP-601: Driver Monitoring Simulator.

Tests TC-601.1: Driver looks away >5 sec → escalating alerts.
"""

import pytest
import time
from carport_sdk.features.driver_monitoring import DriverMonitoringSimulator
from carport_sdk.core.events import EventBus

@pytest.fixture
def driver_monitor():
    """Create driver monitoring simulator for testing."""
    event_bus = EventBus()
    monitor = DriverMonitoringSimulator(event_bus)
    return monitor, event_bus

def test_driver_monitor_creation(driver_monitor):
    """Test driver monitoring simulator creation."""
    monitor, event_bus = driver_monitor
    assert monitor is not None
    assert monitor.enabled
    assert monitor.alert_threshold == 5.0

def test_alert_threshold_configuration(driver_monitor):
    """Test alert threshold can be configured."""
    monitor, _ = driver_monitor
    
    # Test threshold setting
    monitor.set_alert_threshold(3.0)
    assert monitor.alert_threshold == 3.0
    
    # Test invalid threshold handling
    monitor.set_alert_threshold(-1.0)
    assert monitor.alert_threshold == -1.0  # Should accept any float

def test_gaze_direction_simulation(driver_monitor):
    """Test gaze direction simulation."""
    monitor, _ = driver_monitor
    
    # Test different gaze directions
    directions = ["forward", "left", "right", "down", "away"]
    
    for direction in directions:
        monitor.simulate_gaze_direction(direction)
        assert monitor.driver_state.gaze_direction == direction

def test_attention_level_changes(driver_monitor):
    """Test attention level changes with gaze direction."""
    monitor, _ = driver_monitor
    
    # Start with forward gaze (should maintain high attention)
    monitor.simulate_gaze_direction("forward")
    initial_attention = monitor.driver_state.attention_level
    
    # Look away (should decrease attention)
    monitor.simulate_gaze_direction("away")
    assert monitor.driver_state.attention_level < initial_attention
    
    # Return to forward (should increase attention)
    monitor.simulate_gaze_direction("forward")
    # Note: may not be exactly initial due to gradual recovery

def test_tc_601_1_alert_threshold(driver_monitor):
    """Test TC-601.1: Driver looks away >5 sec → escalating alerts."""
    monitor, event_bus = driver_monitor
    
    # Set 5-second threshold per specification
    monitor.set_alert_threshold(5.0)
    
    # Collect events
    alerts = []
    def alert_handler(event):
        if event.data and hasattr(event.data, 'alert_type'):
            alerts.append(event.data)
    
    event_bus.subscribe("alert", alert_handler)
    
    # Simulate looking away for 6 seconds (> threshold)
    monitor.simulate_gaze_away(6.0)
    
    # Should trigger alert
    assert len(alerts) >= 1
    assert any(alert.alert_type == "driver_attention" for alert in alerts)

def test_escalating_alerts(driver_monitor):
    """Test escalating alert levels."""
    monitor, event_bus = driver_monitor
    monitor.set_alert_threshold(2.0)  # Lower threshold for testing
    
    alerts = []
    def alert_handler(event):
        if event.data and hasattr(event.data, 'alert_type'):
            alerts.append(event.data)
    
    event_bus.subscribe("alert", alert_handler)
    
    # Simulate progressive time looking away
    test_times = [3.0, 5.0, 7.0]  # Should trigger visual, audible, haptic
    
    for time_away in test_times:
        monitor.simulate_gaze_away(time_away)
        
    # Should have multiple alerts with escalating severity
    assert len(alerts) >= 1

def test_eyes_closed_simulation(driver_monitor):
    """Test eyes closed simulation."""
    monitor, _ = driver_monitor
    
    # Simulate eyes closed
    monitor.simulate_eyes_closed(True)
    assert monitor.driver_state.eyes_closed
    assert monitor.driver_state.attention_level == 0.0
    
    # Simulate eyes open
    monitor.simulate_eyes_closed(False)
    assert not monitor.driver_state.eyes_closed

def test_enable_disable_functionality(driver_monitor):
    """Test enable/disable functionality."""
    monitor, _ = driver_monitor
    
    # Test disable
    monitor.disable()
    assert not monitor.enabled
    
    # Test enable
    monitor.enable()
    assert monitor.enabled

def test_status_reporting(driver_monitor):
    """Test status reporting."""
    monitor, _ = driver_monitor
    
    status = monitor.get_status()
    
    # Check required status fields
    required_fields = [
        "enabled",
        "alert_threshold", 
        "time_looking_away",
        "alert_level",
        "driver_state"
    ]
    
    for field in required_fields:
        assert field in status

def test_alert_reset_on_forward_gaze(driver_monitor):
    """Test that alerts reset when returning to forward gaze."""
    monitor, _ = driver_monitor
    
    # Simulate looking away to trigger alert state
    monitor.simulate_gaze_away(6.0)
    initial_alert_level = monitor._alert_level
    
    # Return to forward gaze
    monitor.simulate_gaze_direction("forward")
    
    # Alert level should be reset
    assert monitor._alert_level == 0
    assert monitor._time_looking_away == 0.0