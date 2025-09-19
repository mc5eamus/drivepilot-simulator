"""
Main CarPort Simulator class that orchestrates all simulation components.
"""

import time
from typing import List, Dict, Any
from threading import Thread, Event as ThreadEvent

from .events import EventBus, Event
from .models import VehicleState, AlertData
from ..features.driver_monitoring import DriverMonitoringSimulator
from ..features.speed_limiting import SpeedLimitingSimulator  
from ..features.ota_updates import OTAUpdateSimulator
from ..features.obstacle_detection import ObstacleDetectionSimulator
from ..features.regulatory_mode import RegulatoryModeSimulator


class CarPortSimulator:
    """
    Main simulation engine for the CarPort SDK.
    
    Orchestrates all Drive Pilot feature simulators and provides
    a unified interface for testing autonomous driving features.
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.vehicle_state = VehicleState()
        self._running = False
        self._stop_event = ThreadEvent()
        self._simulation_thread = None
        
        # Initialize feature simulators
        self.driver_monitoring = DriverMonitoringSimulator(self.event_bus)
        self.speed_limiting = SpeedLimitingSimulator(self.event_bus)
        self.ota_updates = OTAUpdateSimulator(self.event_bus)
        self.obstacle_detection = ObstacleDetectionSimulator(self.event_bus)
        self.regulatory_mode = RegulatoryModeSimulator(self.event_bus)
        
        # Track alerts
        self._alerts: List[AlertData] = []
        
        # Subscribe to alert events
        self.event_bus.subscribe("alert", self._handle_alert)
    
    def start(self):
        """Start the simulation."""
        if self._running:
            return
            
        self._running = True
        self._stop_event.clear()
        self._simulation_thread = Thread(target=self._simulation_loop, daemon=True)
        self._simulation_thread.start()
        
        # Publish simulation start event
        self.event_bus.publish(Event("simulation_started", source="CarPortSimulator"))
    
    def stop(self):
        """Stop the simulation."""
        if not self._running:
            return
            
        self._running = False
        self._stop_event.set()
        
        if self._simulation_thread:
            self._simulation_thread.join(timeout=1.0)
        
        # Publish simulation stop event
        self.event_bus.publish(Event("simulation_stopped", source="CarPortSimulator"))
    
    def _simulation_loop(self):
        """Main simulation loop running in a separate thread."""
        while self._running and not self._stop_event.is_set():
            # Update simulation state
            self._update_simulation()
            
            # Sleep for simulation timestep (100ms)
            time.sleep(0.1)
    
    def _update_simulation(self):
        """Update simulation state and publish vehicle state event."""
        # Publish current vehicle state
        self.event_bus.publish(Event(
            "vehicle_state_update", 
            data=self.vehicle_state,
            source="CarPortSimulator"
        ))
        
        # Update all feature simulators
        self.driver_monitoring.update(self.vehicle_state)
        self.speed_limiting.update(self.vehicle_state)
        self.ota_updates.update(self.vehicle_state)
        self.obstacle_detection.update(self.vehicle_state)
        self.regulatory_mode.update(self.vehicle_state)
    
    def _handle_alert(self, event: Event):
        """Handle alert events from feature simulators."""
        if isinstance(event.data, AlertData):
            self._alerts.append(event.data)
    
    def get_alerts(self, clear: bool = False) -> List[AlertData]:
        """Get current alerts, optionally clearing them."""
        alerts = self._alerts.copy()
        if clear:
            self._alerts.clear()
        return alerts
    
    def clear_alerts(self):
        """Clear all current alerts."""
        self._alerts.clear()
    
    def set_vehicle_position(self, latitude: float, longitude: float):
        """Set vehicle position for testing geofencing features."""
        self.vehicle_state.position = {"lat": latitude, "lon": longitude}
    
    def set_vehicle_speed(self, speed: float):
        """Set vehicle speed in km/h."""
        self.vehicle_state.speed = speed
        self.vehicle_state.is_stationary = speed < 1.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive simulation status."""
        return {
            "running": self._running,
            "vehicle_state": self.vehicle_state,
            "alert_count": len(self._alerts),
            "features": {
                "driver_monitoring": self.driver_monitoring.get_status(),
                "speed_limiting": self.speed_limiting.get_status(),
                "ota_updates": self.ota_updates.get_status(),
                "obstacle_detection": self.obstacle_detection.get_status(),
                "regulatory_mode": self.regulatory_mode.get_status(),
            }
        }