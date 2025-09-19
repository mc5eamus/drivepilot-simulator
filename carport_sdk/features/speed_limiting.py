"""
DP-602: Adaptive Speed Limiting Simulator

Simulates dynamic speed limiting based on maps, weather, and traffic data.
Implements the test cases from the Drive Pilot specification:
- TC-602.1: Enter lower speed zone → reduce speed in ≤3 sec
- TC-602.2: Weather change → reduce speed + notify driver
"""

import time
from typing import Dict, Any, Optional
from ..core.events import EventBus, Event
from ..core.models import VehicleState, AlertData


class SpeedLimitingSimulator:
    """
    Simulates adaptive speed limiting with environmental integration.
    
    Features:
    - Map-based speed limits
    - Weather condition adjustments
    - Traffic-based speed recommendations
    - Smooth speed transitions
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.enabled = True
        self.current_speed_limit = 50.0  # km/h
        self.weather_adjustment = 1.0  # multiplier (0.5-1.0)
        self.traffic_adjustment = 1.0  # multiplier (0.5-1.0)
        self._target_speed = 50.0
        self._speed_change_rate = 10.0  # km/h per second
        self._last_update_time = time.time()
        
        # Simulated zones and conditions
        self._speed_zones = {
            "city": 50.0,
            "highway": 120.0,
            "school": 30.0,
            "construction": 40.0
        }
        
        self._weather_conditions = {
            "clear": 1.0,
            "rain": 0.8,
            "heavy_rain": 0.6,
            "snow": 0.5,
            "fog": 0.7
        }
        
    def enable(self):
        """Enable adaptive speed limiting."""
        self.enabled = True
        
    def disable(self):
        """Disable adaptive speed limiting."""
        self.enabled = False
        
    def set_speed_zone(self, zone_type: str):
        """
        Set the current speed zone type.
        
        Args:
            zone_type: One of 'city', 'highway', 'school', 'construction'
        """
        if zone_type in self._speed_zones:
            old_limit = self.current_speed_limit
            self.current_speed_limit = self._speed_zones[zone_type]
            
            if old_limit != self.current_speed_limit:
                self._calculate_target_speed()
                self._notify_speed_limit_change(old_limit, self.current_speed_limit)
                
    def set_weather_condition(self, condition: str):
        """
        Set the current weather condition.
        
        Args:
            condition: One of 'clear', 'rain', 'heavy_rain', 'snow', 'fog'
        """
        if condition in self._weather_conditions:
            old_adjustment = self.weather_adjustment
            self.weather_adjustment = self._weather_conditions[condition]
            
            if old_adjustment != self.weather_adjustment:
                self._calculate_target_speed()
                self._notify_weather_change(condition)
                
    def set_traffic_density(self, density: float):
        """
        Set traffic density adjustment factor.
        
        Args:
            density: Traffic density factor (0.5-1.0, where 0.5 is heavy traffic)
        """
        density = max(0.5, min(1.0, density))
        if abs(self.traffic_adjustment - density) > 0.1:
            self.traffic_adjustment = density
            self._calculate_target_speed()
            
    def simulate_speed_zone_entry(self, new_limit: float):
        """
        Simulate entering a new speed zone.
        
        Args:
            new_limit: New speed limit in km/h
        """
        old_limit = self.current_speed_limit
        self.current_speed_limit = new_limit
        self._calculate_target_speed()
        self._notify_speed_limit_change(old_limit, new_limit)
        
    def update(self, vehicle_state: VehicleState):
        """Update speed limiting simulation."""
        if not self.enabled:
            return
            
        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time
        
        # Apply smooth speed adjustment toward target
        speed_diff = self._target_speed - vehicle_state.speed
        max_change = self._speed_change_rate * delta_time
        
        if abs(speed_diff) > max_change:
            speed_change = max_change if speed_diff > 0 else -max_change
        else:
            speed_change = speed_diff
            
        # Update vehicle speed (simulated)
        if abs(speed_change) > 0.1:  # Only update if significant change
            new_speed = vehicle_state.speed + speed_change
            vehicle_state.speed = max(0.0, new_speed)
            vehicle_state.is_stationary = vehicle_state.speed < 1.0
            
            # Publish speed change event
            self.event_bus.publish(Event(
                "speed_adjusted",
                data={
                    "old_speed": vehicle_state.speed - speed_change,
                    "new_speed": vehicle_state.speed,
                    "target_speed": self._target_speed
                },
                source="SpeedLimitingSimulator"
            ))
    
    def _calculate_target_speed(self):
        """Calculate target speed based on all factors."""
        base_speed = self.current_speed_limit
        adjusted_speed = base_speed * self.weather_adjustment * self.traffic_adjustment
        self._target_speed = max(0.0, adjusted_speed)
        
    def _notify_speed_limit_change(self, old_limit: float, new_limit: float):
        """Notify about speed limit change."""
        direction = "reduced" if new_limit < old_limit else "increased"
        alert = AlertData(
            alert_type="speed_limit_change",
            severity="info",
            message=f"Speed limit {direction} from {old_limit} to {new_limit} km/h",
            source_component="SpeedLimitingSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="SpeedLimitingSimulator"))
        
    def _notify_weather_change(self, condition: str):
        """Notify about weather-based speed adjustment."""
        alert = AlertData(
            alert_type="weather_speed_adjustment",
            severity="info",
            message=f"Speed adjusted for {condition} weather conditions",
            source_component="SpeedLimitingSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="SpeedLimitingSimulator"))
        
    def get_current_speed_limit(self) -> float:
        """Get the current base speed limit."""
        return self.current_speed_limit
        
    def get_target_speed(self) -> float:
        """Get the current target speed after adjustments."""
        return self._target_speed
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status of speed limiting."""
        return {
            "enabled": self.enabled,
            "current_speed_limit": self.current_speed_limit,
            "target_speed": self._target_speed,
            "weather_adjustment": self.weather_adjustment,
            "traffic_adjustment": self.traffic_adjustment,
            "speed_change_rate": self._speed_change_rate
        }