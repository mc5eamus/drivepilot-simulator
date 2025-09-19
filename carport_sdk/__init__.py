"""
CarPort SDK - Automotive Simulator for Drive Pilot Features

A Python-based simulation framework for testing autonomous driving features
including driver monitoring, adaptive speed limiting, OTA updates, obstacle
detection, and regulatory compliance.
"""

__version__ = "0.1.0"
__author__ = "Drive Pilot Team"

from .core.simulator import CarPortSimulator
from .core.events import Event, EventBus
from .core.models import VehicleState, SensorData

__all__ = [
    "CarPortSimulator",
    "Event", 
    "EventBus",
    "VehicleState",
    "SensorData",
]