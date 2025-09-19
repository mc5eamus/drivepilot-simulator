"""Event system for the DrivePilot Simulator."""

from enum import Enum
from typing import Any, Dict
from dataclasses import dataclass
import time


class EventType(Enum):
    """Types of events in the simulation."""
    
    # Driver monitoring events (DP-601)
    DRIVER_ATTENTION_LOST = "driver_attention_lost"
    DRIVER_ATTENTION_REGAINED = "driver_attention_regained"
    DRIVER_ALERT_VISUAL = "driver_alert_visual"
    DRIVER_ALERT_AUDIBLE = "driver_alert_audible"
    DRIVER_ALERT_HAPTIC = "driver_alert_haptic"
    
    # Speed limiting events (DP-602)
    SPEED_ZONE_ENTERED = "speed_zone_entered"
    SPEED_ADJUSTED = "speed_adjusted"
    WEATHER_CHANGE = "weather_change"
    
    # OTA update events (DP-603)
    OTA_UPDATE_AVAILABLE = "ota_update_available"
    OTA_UPDATE_STARTED = "ota_update_started"
    OTA_UPDATE_SUCCESS = "ota_update_success"
    OTA_UPDATE_FAILED = "ota_update_failed"
    OTA_ROLLBACK = "ota_rollback"
    
    # Obstacle detection events (DP-604)
    OBSTACLE_DETECTED = "obstacle_detected"
    EMERGENCY_STOP = "emergency_stop"
    OBSTACLE_CLEARED = "obstacle_cleared"
    
    # Regulatory events (DP-605)
    REGION_CHANGED = "region_changed"
    COMPLIANCE_MODE_CHANGED = "compliance_mode_changed"
    FEATURE_BLOCKED = "feature_blocked"
    
    # General simulation events
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_STOPPED = "simulation_stopped"
    VEHICLE_STATE_CHANGED = "vehicle_state_changed"


@dataclass
class Event:
    """Represents an event in the simulation."""
    
    event_type: EventType
    data: Dict[str, Any]
    source: str = "simulation"
    timestamp: float = 0.0
    
    def __post_init__(self) -> None:
        """Initialize event with current timestamp if not provided."""
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "source": self.source,
        }