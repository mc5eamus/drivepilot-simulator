"""Tests for the DrivePilot Simulator core functionality."""

import pytest
import time
from drivepilot_simulator import Car, SimulationEnvironment, EventType
from drivepilot_simulator.core.car import VehicleState, DriverState


class TestSimulationEnvironment:
    """Test cases for SimulationEnvironment."""
    
    def test_environment_creation(self):
        """Test environment can be created and started."""
        env = SimulationEnvironment()
        assert not env.is_running()
        
        env.start()
        assert env.is_running()
        
        env.stop()
        assert not env.is_running()
    
    def test_event_publishing(self):
        """Test event publishing and subscription."""
        env = SimulationEnvironment()
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        env.subscribe_to_event(EventType.SIMULATION_STARTED, event_handler)
        env.start()
        
        assert len(events_received) == 1
        assert events_received[0].event_type == EventType.SIMULATION_STARTED
    
    def test_weather_conditions(self):
        """Test weather condition management."""
        env = SimulationEnvironment()
        
        initial_weather = env.get_weather_conditions()
        assert "temperature" in initial_weather
        
        new_weather = {"temperature": 25.0, "precipitation": 2.0}
        env.set_weather_conditions(new_weather)
        
        updated_weather = env.get_weather_conditions()
        assert updated_weather["temperature"] == 25.0
        assert updated_weather["precipitation"] == 2.0
    
    def test_location_and_region_detection(self):
        """Test location setting and region detection."""
        env = SimulationEnvironment()
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        env.subscribe_to_event(EventType.REGION_CHANGED, event_handler)
        
        # Set location in US
        env.set_location({"latitude": 40.7128, "longitude": -74.0060})
        assert env.get_current_region() == "US"
        
        # Should have triggered region change event
        assert len(events_received) == 1
        assert events_received[0].event_type == EventType.REGION_CHANGED


class TestCar:
    """Test cases for Car class."""
    
    def setup_method(self):
        """Set up test environment and car for each test."""
        self.env = SimulationEnvironment()
        self.car = Car(environment=self.env, car_id="test_car")
        self.events_received = []
        
        def event_handler(event):
            self.events_received.append(event)
        
        # Subscribe to all events
        for event_type in EventType:
            self.env.subscribe_to_event(event_type, event_handler)
    
    def test_car_creation(self):
        """Test car can be created with default state."""
        status = self.car.get_status()
        assert status.state == VehicleState.PARKED
        assert status.speed == 0.0
        assert status.driver_state == DriverState.ATTENTIVE
    
    def test_driver_monitoring_enable_disable(self):
        """Test driver monitoring can be enabled and disabled."""
        # Initially disabled
        status = self.car.get_status()
        assert "driver_monitoring" not in status.enabled_features
        
        # Enable driver monitoring
        self.car.enable_driver_monitoring(alert_threshold=3.0)
        status = self.car.get_status()
        assert "driver_monitoring" in status.enabled_features
        
        # Disable driver monitoring
        self.car.disable_driver_monitoring()
        status = self.car.get_status()
        assert "driver_monitoring" not in status.enabled_features
    
    def test_driver_attention_monitoring(self):
        """Test driver attention monitoring and alerts."""
        self.car.enable_driver_monitoring(alert_threshold=2.0)
        self.car.start_simulation()
        
        # Simulate driver inattention
        for i in range(5):
            self.car.update_driver_attention(is_attentive=False)
            time.sleep(0.1)
        
        # Should have triggered alert events
        alert_events = [e for e in self.events_received 
                       if e.event_type in [EventType.DRIVER_ALERT_VISUAL, 
                                          EventType.DRIVER_ALERT_AUDIBLE,
                                          EventType.DRIVER_ALERT_HAPTIC]]
        assert len(alert_events) > 0
    
    def test_adaptive_speed_limiting(self):
        """Test adaptive speed limiting functionality."""
        self.car.enable_adaptive_speed()
        self.car.start_simulation()
        
        # Set initial driving state
        self.car.drive_to("Test Location", speed=60.0)
        
        # Change speed limit
        self.car.set_speed_limit(30.0)
        
        # Should trigger speed zone and adjustment events
        speed_events = [e for e in self.events_received 
                       if e.event_type in [EventType.SPEED_ZONE_ENTERED,
                                          EventType.SPEED_ADJUSTED]]
        assert len(speed_events) > 0
    
    def test_obstacle_detection(self):
        """Test obstacle detection functionality."""
        self.car.enable_obstacle_detection()
        self.car.start_simulation()
        
        # Detect pedestrian (should trigger emergency stop)
        self.car.detect_obstacle("pedestrian", distance=5.0, confidence=0.9)
        
        # Check for obstacle detection event
        obstacle_events = [e for e in self.events_received 
                          if e.event_type == EventType.OBSTACLE_DETECTED]
        assert len(obstacle_events) == 1
        
        # Check for emergency stop
        emergency_events = [e for e in self.events_received 
                           if e.event_type == EventType.EMERGENCY_STOP]
        assert len(emergency_events) == 1
        
        # Car should be stopped
        status = self.car.get_status()
        assert status.state == VehicleState.EMERGENCY_STOP
        assert status.speed == 0.0
    
    def test_ota_updates(self):
        """Test OTA update functionality."""
        self.car.enable_ota_updates()
        
        # Test valid update
        initial_version = self.car.get_status().software_version
        success = self.car.simulate_ota_update("2.0.0", is_valid=True)
        
        # Should succeed (with some probability due to random failure simulation)
        # We'll test the event generation regardless of success
        update_events = [e for e in self.events_received 
                        if e.event_type in [EventType.OTA_UPDATE_STARTED,
                                           EventType.OTA_UPDATE_SUCCESS,
                                           EventType.OTA_UPDATE_FAILED,
                                           EventType.OTA_ROLLBACK]]
        assert len(update_events) > 0
        
        # Test invalid update
        self.events_received.clear()
        success = self.car.simulate_ota_update("2.1.0", is_valid=False)
        assert not success
        
        failed_events = [e for e in self.events_received 
                        if e.event_type == EventType.OTA_UPDATE_FAILED]
        assert len(failed_events) == 1
    
    def test_regulatory_mode_switching(self):
        """Test regulatory mode switching."""
        self.car.enable_regulatory_mode()
        self.car.start_simulation()
        
        # Change environment location to trigger region change
        self.env.set_location({"latitude": 35.6762, "longitude": 139.6503})  # Tokyo
        
        # Should trigger region and compliance mode change
        region_events = [e for e in self.events_received 
                        if e.event_type == EventType.REGION_CHANGED]
        compliance_events = [e for e in self.events_received 
                           if e.event_type == EventType.COMPLIANCE_MODE_CHANGED]
        
        assert len(region_events) > 0
        assert len(compliance_events) > 0
        
        # Car should update its region
        status = self.car.get_status()
        assert status.current_region == "JP"
    
    def test_simulation_lifecycle(self):
        """Test simulation start/stop lifecycle."""
        assert not self.env.is_running()
        
        self.car.start_simulation()
        assert self.env.is_running()
        
        status = self.car.get_status()
        assert status.state == VehicleState.STATIONARY
        
        self.car.stop_simulation()
        status = self.car.get_status()
        assert status.state == VehicleState.PARKED
    
    def test_feature_integration(self):
        """Test multiple features working together."""
        # Enable all features
        self.car.enable_driver_monitoring()
        self.car.enable_adaptive_speed()
        self.car.enable_ota_updates()
        self.car.enable_obstacle_detection()
        self.car.enable_regulatory_mode()
        
        status = self.car.get_status()
        expected_features = {
            "driver_monitoring", "adaptive_speed", "ota_updates", 
            "obstacle_detection", "regulatory_mode"
        }
        assert expected_features.issubset(status.enabled_features)
        
        self.car.start_simulation()
        
        # Simulate complex scenario
        self.car.drive_to("Test", speed=50.0)
        self.car.set_speed_limit(30.0)
        self.car.detect_obstacle("animal", distance=20.0)
        
        # Should have generated multiple events
        assert len(self.events_received) > 5


if __name__ == "__main__":
    pytest.main([__file__])