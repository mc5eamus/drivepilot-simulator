"""Core Car class for the DrivePilot Simulator."""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import threading

from .environment import SimulationEnvironment
from .events import Event, EventType


class VehicleState(Enum):
    """States of the vehicle."""
    PARKED = "parked"
    STATIONARY = "stationary"
    MOVING = "moving"
    EMERGENCY_STOP = "emergency_stop"
    MAINTENANCE = "maintenance"


class DriverState(Enum):
    """States of the driver."""
    ATTENTIVE = "attentive"
    DISTRACTED = "distracted"
    ALERT_LEVEL_1 = "alert_level_1"  # Visual alert
    ALERT_LEVEL_2 = "alert_level_2"  # Audible alert
    ALERT_LEVEL_3 = "alert_level_3"  # Haptic alert


@dataclass
class VehicleStatus:
    """Current status of the vehicle."""
    state: VehicleState = VehicleState.PARKED
    speed: float = 0.0  # km/h
    target_speed: float = 0.0  # km/h
    position: Dict[str, float] = field(default_factory=lambda: {
        "latitude": 52.520008,
        "longitude": 13.404954,
        "altitude": 34.0,
        "heading": 0.0
    })
    
    # DP-601: Driver monitoring
    driver_state: DriverState = DriverState.ATTENTIVE
    attention_time: float = 0.0  # Time since last attention check
    
    # DP-602: Speed limiting
    speed_limit: float = 50.0  # Current speed limit
    weather_factor: float = 1.0  # Speed adjustment factor for weather
    
    # DP-603: OTA updates
    software_version: str = "1.0.0"
    update_available: bool = False
    update_in_progress: bool = False
    
    # DP-604: Obstacle detection
    obstacles_detected: List[Dict[str, Any]] = field(default_factory=list)
    sensors_active: Set[str] = field(default_factory=lambda: {"radar", "ir", "ultrasonic"})
    
    # DP-605: Regulatory compliance
    current_region: str = "EU"
    compliance_mode: str = "standard"
    enabled_features: Set[str] = field(default_factory=lambda: {
        "driver_monitoring", "adaptive_speed", "obstacle_detection"
    })


class Car:
    """
    Main Car class representing a simulated vehicle with autonomous driving capabilities.
    
    This class implements all the core features required by the DrivePilot project:
    - DP-601: Real-Time Driver Monitoring
    - DP-602: Adaptive Speed Limiting  
    - DP-603: OTA Update Support
    - DP-604: Enhanced Obstacle Detection
    - DP-605: Regulatory Mode Switching
    """
    
    def __init__(self, environment: SimulationEnvironment, car_id: str = "sim_car_001") -> None:
        """Initialize the car with the given simulation environment."""
        self.car_id = car_id
        self.environment = environment
        self.status = VehicleStatus()
        self._lock = threading.Lock()
        
        # Feature enablement flags
        self._driver_monitoring_enabled = False
        self._adaptive_speed_enabled = False
        self._ota_updates_enabled = False
        self._obstacle_detection_enabled = False
        self._regulatory_mode_enabled = False
        
        # Configuration parameters
        self._driver_attention_threshold = 5.0  # seconds
        self._speed_adjustment_time = 3.0       # seconds for speed changes
        
        # Subscribe to environment events
        self._subscribe_to_environment_events()
        
        # Internal timers and state
        self._last_attention_check = time.time()
        self._last_speed_update = time.time()
    
    def _get_timestamp(self) -> float:
        """Get current timestamp, using simulation time if available."""
        if self.environment.is_running():
            return self.environment.get_simulation_time()
        else:
            return time.time()
        
    def _subscribe_to_environment_events(self) -> None:
        """Subscribe to relevant environment events."""
        self.environment.subscribe_to_event(
            EventType.WEATHER_CHANGE, 
            self._handle_weather_change
        )
        self.environment.subscribe_to_event(
            EventType.REGION_CHANGED, 
            self._handle_region_change
        )
    
    # DP-601: Driver Monitoring Implementation
    def enable_driver_monitoring(self, alert_threshold: float = 5.0) -> None:
        """Enable driver monitoring system (DP-601)."""
        with self._lock:
            self._driver_monitoring_enabled = True
            self._driver_attention_threshold = alert_threshold
            self.status.enabled_features.add("driver_monitoring")
            
        self.environment.publish_event(Event(
            event_type=EventType.VEHICLE_STATE_CHANGED,
            timestamp=self._get_timestamp(),
            data={
                "feature": "driver_monitoring",
                "enabled": True,
                "threshold": alert_threshold
            },
            source=self.car_id
        ))
    
    def disable_driver_monitoring(self) -> None:
        """Disable driver monitoring system."""
        with self._lock:
            self._driver_monitoring_enabled = False
            self.status.enabled_features.discard("driver_monitoring")
            self.status.driver_state = DriverState.ATTENTIVE
    
    def update_driver_attention(self, is_attentive: bool) -> None:
        """Update driver attention state and trigger alerts if necessary."""
        if not self._driver_monitoring_enabled:
            return
            
        current_time = self._get_timestamp()
        
        with self._lock:
            if is_attentive:
                self.status.driver_state = DriverState.ATTENTIVE
                self.status.attention_time = 0.0
                self._last_attention_check = current_time
                
                self.environment.publish_event(Event(
                    event_type=EventType.DRIVER_ATTENTION_REGAINED,
                    timestamp=current_time,
                    data={"car_id": self.car_id},
                    source=self.car_id
                ))
            else:
                # Update attention time
                time_since_last_check = current_time - self._last_attention_check
                self.status.attention_time += time_since_last_check
                self._last_attention_check = current_time
                
                # Check if attention threshold exceeded (TC-601.1)
                if self.status.attention_time > self._driver_attention_threshold:
                    self._escalate_driver_alerts()
    
    def _escalate_driver_alerts(self) -> None:
        """Escalate driver alerts based on attention time (TC-601.1)."""
        current_time = self._get_timestamp()
        attention_time = self.status.attention_time
        
        if attention_time > self._driver_attention_threshold * 3:
            # Level 3: Haptic alert
            self.status.driver_state = DriverState.ALERT_LEVEL_3
            self.environment.publish_event(Event(
                event_type=EventType.DRIVER_ALERT_HAPTIC,
                timestamp=current_time,
                data={"car_id": self.car_id, "attention_time": attention_time},
                source=self.car_id
            ))
        elif attention_time > self._driver_attention_threshold * 2:
            # Level 2: Audible alert
            self.status.driver_state = DriverState.ALERT_LEVEL_2
            self.environment.publish_event(Event(
                event_type=EventType.DRIVER_ALERT_AUDIBLE,
                timestamp=current_time,
                data={"car_id": self.car_id, "attention_time": attention_time},
                source=self.car_id
            ))
        elif attention_time > self._driver_attention_threshold:
            # Level 1: Visual alert
            self.status.driver_state = DriverState.ALERT_LEVEL_1
            self.environment.publish_event(Event(
                event_type=EventType.DRIVER_ALERT_VISUAL,
                timestamp=current_time,
                data={"car_id": self.car_id, "attention_time": attention_time},
                source=self.car_id
            ))
    
    # DP-602: Adaptive Speed Limiting Implementation
    def enable_adaptive_speed(self, weather_factor: bool = True) -> None:
        """Enable adaptive speed limiting system (DP-602)."""
        with self._lock:
            self._adaptive_speed_enabled = True
            self.status.enabled_features.add("adaptive_speed")
    
    def disable_adaptive_speed(self) -> None:
        """Disable adaptive speed limiting system."""
        with self._lock:
            self._adaptive_speed_enabled = False
            self.status.enabled_features.discard("adaptive_speed")
    
    def set_speed_limit(self, speed_limit: float) -> None:
        """Set the current speed limit (from map/sign recognition)."""
        if not self._adaptive_speed_enabled:
            return
            
        old_limit = self.status.speed_limit
        self.status.speed_limit = speed_limit
        
        # Adjust speed if necessary (TC-602.1: ≤3 sec)
        if speed_limit < self.status.speed:
            self._adjust_speed_gradually(speed_limit)
        
        self.environment.publish_event(Event(
            event_type=EventType.SPEED_ZONE_ENTERED,
            timestamp=self._get_timestamp(),
            data={
                "car_id": self.car_id,
                "old_limit": old_limit,
                "new_limit": speed_limit
            },
            source=self.car_id
        ))
    
    def _adjust_speed_gradually(self, target_speed: float) -> None:
        """Gradually adjust speed to target (within 3 seconds)."""
        if not self._adaptive_speed_enabled:
            return
            
        self.status.target_speed = target_speed
        current_time = self._get_timestamp()
        
        # Apply weather factor
        adjusted_target = target_speed * self.status.weather_factor
        
        # Simulate gradual speed change
        speed_diff = abs(self.status.speed - adjusted_target)
        if speed_diff > 0.1:  # Only adjust if significant difference
            self.status.speed = adjusted_target
            self._last_speed_update = current_time
            
            self.environment.publish_event(Event(
                event_type=EventType.SPEED_ADJUSTED,
                timestamp=current_time,
                data={
                    "car_id": self.car_id,
                    "new_speed": self.status.speed,
                    "target_speed": target_speed,
                    "weather_factor": self.status.weather_factor
                },
                source=self.car_id
            ))
    
    def _handle_weather_change(self, event: Event) -> None:
        """Handle weather changes and adjust speed accordingly (TC-602.2)."""
        if not self._adaptive_speed_enabled:
            return
            
        weather = event.data.get("new_conditions", {})
        
        # Calculate weather factor based on conditions
        weather_factor = 1.0
        
        # Reduce speed for precipitation
        precipitation = weather.get("precipitation", 0.0)
        if precipitation > 0:
            weather_factor *= max(0.7, 1.0 - precipitation / 10.0)
        
        # Reduce speed for low visibility
        visibility = weather.get("visibility", 10000)
        if visibility < 1000:
            weather_factor *= max(0.5, visibility / 1000.0)
        
        # Reduce speed for high wind
        wind_speed = weather.get("wind_speed", 0.0)
        if wind_speed > 50:  # km/h
            weather_factor *= max(0.8, 1.0 - (wind_speed - 50) / 100.0)
        
        old_factor = self.status.weather_factor
        self.status.weather_factor = weather_factor
        
        # Adjust speed if weather factor changed significantly
        if abs(weather_factor - old_factor) > 0.05:
            new_target = self.status.speed_limit * weather_factor
            self._adjust_speed_gradually(new_target)
    
    # DP-603: OTA Update Support Implementation
    def enable_ota_updates(self) -> None:
        """Enable OTA update system (DP-603)."""
        with self._lock:
            self._ota_updates_enabled = True
            self.status.enabled_features.add("ota_updates")
    
    def disable_ota_updates(self) -> None:
        """Disable OTA update system."""
        with self._lock:
            self._ota_updates_enabled = False
            self.status.enabled_features.discard("ota_updates")
    
    def simulate_ota_update(self, new_version: str, is_valid: bool = True) -> bool:
        """Simulate an OTA update process with validation and rollback capability."""
        if not self._ota_updates_enabled:
            return False
            
        current_time = self._get_timestamp()
        
        # TC-603.1 & TC-603.2: Update validation
        if not is_valid:
            self.environment.publish_event(Event(
                event_type=EventType.OTA_UPDATE_FAILED,
                timestamp=current_time,
                data={
                    "car_id": self.car_id,
                    "reason": "invalid_signature",
                    "version": new_version
                },
                source=self.car_id
            ))
            return False
        
        # Start update process
        self.status.update_in_progress = True
        self.environment.publish_event(Event(
            event_type=EventType.OTA_UPDATE_STARTED,
            timestamp=current_time,
            data={
                "car_id": self.car_id,
                "from_version": self.status.software_version,
                "to_version": new_version
            },
            source=self.car_id
        ))
        
        # Simulate update success/failure (TC-603.3)
        import random
        update_success = random.random() > 0.1  # 90% success rate
        
        if update_success:
            old_version = self.status.software_version
            self.status.software_version = new_version
            self.status.update_in_progress = False
            
            self.environment.publish_event(Event(
                event_type=EventType.OTA_UPDATE_SUCCESS,
                timestamp=current_time,
                data={
                    "car_id": self.car_id,
                    "from_version": old_version,
                    "to_version": new_version
                },
                source=self.car_id
            ))
            return True
        else:
            # Rollback on failure
            self.status.update_in_progress = False
            self.environment.publish_event(Event(
                event_type=EventType.OTA_ROLLBACK,
                timestamp=current_time,
                data={
                    "car_id": self.car_id,
                    "failed_version": new_version,
                    "current_version": self.status.software_version
                },
                source=self.car_id
            ))
            return False
    
    # DP-604: Enhanced Obstacle Detection Implementation
    def enable_obstacle_detection(self, sensors: Optional[List[str]] = None) -> None:
        """Enable obstacle detection system (DP-604)."""
        if sensors is None:
            sensors = ["radar", "ir", "ultrasonic"]
            
        with self._lock:
            self._obstacle_detection_enabled = True
            self.status.sensors_active = set(sensors)
            self.status.enabled_features.add("obstacle_detection")
    
    def disable_obstacle_detection(self) -> None:
        """Disable obstacle detection system."""
        with self._lock:
            self._obstacle_detection_enabled = False
            self.status.enabled_features.discard("obstacle_detection")
            self.status.obstacles_detected.clear()
    
    def detect_obstacle(self, obstacle_type: str, distance: float, confidence: float = 0.9) -> None:
        """Simulate obstacle detection and appropriate response."""
        if not self._obstacle_detection_enabled:
            return
            
        current_time = self._get_timestamp()
        
        obstacle = {
            "type": obstacle_type,
            "distance": distance,
            "confidence": confidence,
            "detected_at": current_time
        }
        
        self.status.obstacles_detected.append(obstacle)
        
        self.environment.publish_event(Event(
            event_type=EventType.OBSTACLE_DETECTED,
            timestamp=current_time,
            data={
                "car_id": self.car_id,
                "obstacle": obstacle
            },
            source=self.car_id
        ))
        
        # Determine response based on obstacle type and distance
        self._handle_obstacle_response(obstacle_type, distance)
    
    def _handle_obstacle_response(self, obstacle_type: str, distance: float) -> None:
        """Handle appropriate response to detected obstacles."""
        current_time = self.environment.get_simulation_time()
        
        # TC-604.1: Pedestrian → emergency stop
        if obstacle_type == "pedestrian" and distance < 10.0:
            self.emergency_stop()
            
        # TC-604.2: Animal at night → slow + alert
        elif obstacle_type == "animal" and distance < 20.0:
            self._adjust_speed_gradually(max(20.0, self.status.speed * 0.5))
            
        # TC-604.3: Static object → navigate around
        elif obstacle_type == "static_object" and distance < 5.0:
            # In simulation, we just slow down instead of actual navigation
            self._adjust_speed_gradually(max(10.0, self.status.speed * 0.3))
    
    def emergency_stop(self) -> None:
        """Perform emergency stop."""
        current_time = self._get_timestamp()
        
        with self._lock:
            old_state = self.status.state
            self.status.state = VehicleState.EMERGENCY_STOP
            self.status.speed = 0.0
            self.status.target_speed = 0.0
        
        self.environment.publish_event(Event(
            event_type=EventType.EMERGENCY_STOP,
            timestamp=current_time,
            data={
                "car_id": self.car_id,
                "previous_state": old_state.value,
                "reason": "obstacle_detected"
            },
            source=self.car_id
        ))
    
    # DP-605: Regulatory Mode Switching Implementation
    def enable_regulatory_mode(self) -> None:
        """Enable regulatory mode switching (DP-605)."""
        with self._lock:
            self._regulatory_mode_enabled = True
            self.status.enabled_features.add("regulatory_mode")
    
    def disable_regulatory_mode(self) -> None:
        """Disable regulatory mode switching."""
        with self._lock:
            self._regulatory_mode_enabled = False
            self.status.enabled_features.discard("regulatory_mode")
    
    def _handle_region_change(self, event: Event) -> None:
        """Handle region changes and update compliance mode (TC-605.1)."""
        if not self._regulatory_mode_enabled:
            return
            
        new_region = event.data.get("new_region")
        old_region = event.data.get("old_region")
        
        if new_region:
            self.status.current_region = new_region
            
            # Update compliance mode based on region
            old_mode = self.status.compliance_mode
            self.status.compliance_mode = self._get_compliance_mode(new_region)
            
            # Update enabled features based on regional requirements
            self._update_regional_features(new_region)
            
            self.environment.publish_event(Event(
                event_type=EventType.COMPLIANCE_MODE_CHANGED,
                timestamp=self._get_timestamp(),
                data={
                    "car_id": self.car_id,
                    "old_region": old_region,
                    "new_region": new_region,
                    "old_mode": old_mode,
                    "new_mode": self.status.compliance_mode
                },
                source=self.car_id
            ))
    
    def _get_compliance_mode(self, region: str) -> str:
        """Get compliance mode for a specific region."""
        compliance_modes = {
            "EU": "eu_standard",
            "US": "fmvss",
            "CN": "gb_standard",
            "JP": "jis_standard",
        }
        return compliance_modes.get(region, "international")
    
    def _update_regional_features(self, region: str) -> None:
        """Update available features based on regional regulations."""
        # Example: Some features might be restricted in certain regions
        restricted_features = {
            "US": [],  # No restrictions
            "EU": [],  # No restrictions  
            "CN": ["driver_monitoring"],  # Example restriction
            "JP": [],  # No restrictions
        }
        
        restrictions = restricted_features.get(region, [])
        
        for feature in restrictions:
            if feature in self.status.enabled_features:
                self.status.enabled_features.remove(feature)
                
                # TC-605.2: Block disallowed feature
                self.environment.publish_event(Event(
                    event_type=EventType.FEATURE_BLOCKED,
                    timestamp=self._get_timestamp(),
                    data={
                        "car_id": self.car_id,
                        "feature": feature,
                        "region": region,
                        "reason": "regulatory_restriction"
                    },
                    source=self.car_id
                ))
    
    # General vehicle control methods
    def start_simulation(self) -> None:
        """Start the vehicle simulation."""
        with self._lock:
            if self.status.state == VehicleState.PARKED:
                self.status.state = VehicleState.STATIONARY
        
        if not self.environment.is_running():
            self.environment.start()
    
    def stop_simulation(self) -> None:
        """Stop the vehicle simulation."""
        with self._lock:
            self.status.state = VehicleState.PARKED
            self.status.speed = 0.0
            self.status.target_speed = 0.0
    
    def drive_to(self, destination: str, speed: float = 50.0) -> None:
        """Simulate driving to a destination."""
        with self._lock:
            if self.status.state != VehicleState.EMERGENCY_STOP:
                self.status.state = VehicleState.MOVING
                self.status.target_speed = min(speed, self.status.speed_limit)
                self._adjust_speed_gradually(self.status.target_speed)
    
    def get_status(self) -> VehicleStatus:
        """Get current vehicle status."""
        with self._lock:
            # Return a copy to prevent external modification
            import copy
            return copy.deepcopy(self.status)