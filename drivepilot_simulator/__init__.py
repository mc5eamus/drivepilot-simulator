"""
DrivePilot Simulator - A comprehensive car simulator for autonomous driving software development.

This package provides a simulation environment for testing and developing autonomous
driving features including driver monitoring, adaptive speed limiting, OTA updates,
obstacle detection, and regulatory compliance.
"""

from .core.car import Car
from .core.environment import SimulationEnvironment
from .core.events import Event, EventType

__version__ = "0.1.0"
__all__ = ["Car", "SimulationEnvironment", "Event", "EventType"]