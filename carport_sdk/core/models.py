"""
Core data models for the CarPort SDK simulator.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class VehicleState:
    """Represents the current state of the simulated vehicle."""
    
    speed: float = 0.0  # km/h
    position: Dict[str, float] = None  # {"lat": 0.0, "lon": 0.0}
    heading: float = 0.0  # degrees
    is_stationary: bool = True
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = {"lat": 0.0, "lon": 0.0}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass 
class SensorData:
    """Generic sensor data structure."""
    
    sensor_type: str
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DriverState:
    """Driver monitoring state data."""
    
    gaze_direction: str = "forward"  # forward, left, right, down, away
    attention_level: float = 1.0  # 0.0 to 1.0
    eyes_closed: bool = False
    time_looking_away: float = 0.0  # seconds
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ObstacleData:
    """Obstacle detection data."""
    
    object_type: str  # pedestrian, vehicle, animal, static_object
    distance: float  # meters
    bearing: float  # degrees relative to vehicle heading
    velocity: float = 0.0  # m/s
    confidence: float = 1.0  # 0.0 to 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AlertData:
    """Alert/notification data structure."""
    
    alert_type: str
    severity: str  # info, warning, critical
    message: str
    source_component: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()