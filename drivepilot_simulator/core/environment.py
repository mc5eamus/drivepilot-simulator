"""Simulation environment for the DrivePilot Simulator."""

from typing import List, Dict, Any, Optional, Callable
import time
import threading
from dataclasses import dataclass

from .events import Event, EventType


@dataclass
class SimulationConfig:
    """Configuration for the simulation environment."""
    
    time_scale: float = 1.0  # Speed multiplier for simulation time
    real_time: bool = True   # Whether to run in real-time or as fast as possible
    log_events: bool = True  # Whether to log all events
    max_log_size: int = 10000  # Maximum number of events to keep in log


class SimulationEnvironment:
    """
    Simulation environment that manages time, events, and environmental conditions.
    
    This class provides the foundation for all simulation activities including:
    - Time management and synchronization
    - Event publishing and subscription
    - Environmental condition simulation (weather, traffic, etc.)
    - Logging and telemetry
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None) -> None:
        """Initialize the simulation environment."""
        self.config = config or SimulationConfig()
        self._start_time = time.time()
        self._simulation_time = 0.0
        self._running = False
        self._event_log: List[Event] = []
        self._event_subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()
        
        # Environmental conditions
        self._weather_conditions = {
            "temperature": 20.0,  # Celsius
            "humidity": 50.0,     # Percentage
            "precipitation": 0.0,  # mm/hour
            "visibility": 10000,   # meters
            "wind_speed": 0.0,     # km/h
        }
        
        self._traffic_conditions = {
            "density": 0.3,        # 0.0 to 1.0
            "average_speed": 60.0, # km/h
            "congestion_level": 0.2, # 0.0 to 1.0
        }
        
        # GPS/Location simulation
        self._current_location = {
            "latitude": 52.520008,   # Berlin, Germany (default)
            "longitude": 13.404954,
            "altitude": 34.0,        # meters
            "heading": 0.0,          # degrees
            "speed": 0.0,            # km/h
        }
        
        # Regulatory region
        self._current_region = "EU"  # Default to European Union
        
    def start(self) -> None:
        """Start the simulation environment."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._start_time = time.time()
            self._simulation_time = 0.0
            
            # Publish simulation started event
            self.publish_event(Event(
                event_type=EventType.SIMULATION_STARTED,
                timestamp=self.get_simulation_time(),
                data={"config": self.config.__dict__},
                source="environment"
            ))
    
    def stop(self) -> None:
        """Stop the simulation environment."""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            
            # Publish simulation stopped event
            self.publish_event(Event(
                event_type=EventType.SIMULATION_STOPPED,
                timestamp=self.get_simulation_time(),
                data={"duration": self._simulation_time},
                source="environment"
            ))
    
    def get_simulation_time(self) -> float:
        """Get the current simulation time."""
        if not self._running:
            return self._simulation_time
        
        real_elapsed = time.time() - self._start_time
        self._simulation_time = real_elapsed * self.config.time_scale
        return self._simulation_time
    
    def is_running(self) -> bool:
        """Check if the simulation is currently running."""
        return self._running
    
    def publish_event(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            # Log the event
            if self.config.log_events:
                self._event_log.append(event)
                
                # Trim log if it exceeds maximum size
                if len(self._event_log) > self.config.max_log_size:
                    self._event_log = self._event_log[-self.config.max_log_size:]
            
            # Notify subscribers
            subscribers = self._event_subscribers.get(event.event_type, [])
            for callback in subscribers:
                try:
                    callback(event)
                except Exception as e:
                    # Log callback errors but don't stop simulation
                    print(f"Error in event callback: {e}")
    
    def subscribe_to_event(
        self, 
        event_type: EventType, 
        callback: Callable[[Event], None]
    ) -> None:
        """Subscribe to events of a specific type."""
        with self._lock:
            if event_type not in self._event_subscribers:
                self._event_subscribers[event_type] = []
            self._event_subscribers[event_type].append(callback)
    
    def unsubscribe_from_event(
        self, 
        event_type: EventType, 
        callback: Callable[[Event], None]
    ) -> None:
        """Unsubscribe from events of a specific type."""
        with self._lock:
            if event_type in self._event_subscribers:
                try:
                    self._event_subscribers[event_type].remove(callback)
                except ValueError:
                    pass  # Callback wasn't subscribed
    
    def get_event_log(self) -> List[Event]:
        """Get a copy of the event log."""
        with self._lock:
            return self._event_log.copy()
    
    def get_weather_conditions(self) -> Dict[str, float]:
        """Get current weather conditions."""
        return self._weather_conditions.copy()
    
    def set_weather_conditions(self, conditions: Dict[str, float]) -> None:
        """Update weather conditions and publish event."""
        old_conditions = self._weather_conditions.copy()
        self._weather_conditions.update(conditions)
        
        self.publish_event(Event(
            event_type=EventType.WEATHER_CHANGE,
            timestamp=self.get_simulation_time(),
            data={
                "old_conditions": old_conditions,
                "new_conditions": self._weather_conditions.copy()
            },
            source="environment"
        ))
    
    def get_traffic_conditions(self) -> Dict[str, float]:
        """Get current traffic conditions."""
        return self._traffic_conditions.copy()
    
    def set_traffic_conditions(self, conditions: Dict[str, float]) -> None:
        """Update traffic conditions."""
        self._traffic_conditions.update(conditions)
    
    def get_location(self) -> Dict[str, float]:
        """Get current GPS location."""
        return self._current_location.copy()
    
    def set_location(self, location: Dict[str, float]) -> None:
        """Update GPS location and check for region changes."""
        old_location = self._current_location.copy()
        self._current_location.update(location)
        
        # Simple region detection based on latitude/longitude
        old_region = self._current_region
        new_region = self._detect_region(
            self._current_location["latitude"], 
            self._current_location["longitude"]
        )
        
        if new_region != old_region:
            self._current_region = new_region
            self.publish_event(Event(
                event_type=EventType.REGION_CHANGED,
                timestamp=self.get_simulation_time(),
                data={
                    "old_region": old_region,
                    "new_region": new_region,
                    "old_location": old_location,
                    "new_location": self._current_location.copy()
                },
                source="environment"
            ))
    
    def get_current_region(self) -> str:
        """Get the current regulatory region."""
        return self._current_region
    
    def _detect_region(self, latitude: float, longitude: float) -> str:
        """Detect regulatory region based on GPS coordinates."""
        # Simplified region detection for simulation
        if 35.0 <= latitude <= 70.0 and -10.0 <= longitude <= 40.0:
            return "EU"  # Europe
        elif 25.0 <= latitude <= 49.0 and -125.0 <= longitude <= -66.0:
            return "US"  # United States
        elif 20.0 <= latitude <= 45.0 and 73.0 <= longitude <= 153.0:
            return "CN"  # China
        elif 31.0 <= latitude <= 46.0 and 129.0 <= longitude <= 146.0:
            return "JP"  # Japan
        else:
            return "OTHER"
    
    def simulate_sensor_noise(self, base_value: float, noise_level: float = 0.1) -> float:
        """Add realistic sensor noise to a measurement."""
        import random
        noise = random.uniform(-noise_level, noise_level) * base_value
        return base_value + noise