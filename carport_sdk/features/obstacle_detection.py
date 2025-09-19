"""
DP-604: Enhanced Obstacle Detection Simulator

Simulates multi-sensor fusion for obstacle detection with IR, radar, and ultrasonic.
Implements the test cases from the Drive Pilot specification:
- TC-604.1: Pedestrian → emergency stop
- TC-604.2: Animal at night → slow + alert
- TC-604.3: Static object → navigate around
"""

import time
import math
import random
from typing import Dict, Any, List
from ..core.events import EventBus, Event
from ..core.models import VehicleState, ObstacleData, AlertData


class ObstacleDetectionSimulator:
    """
    Simulates enhanced obstacle detection with sensor fusion.

    Features:
    - Multi-sensor fusion (IR, radar, ultrasonic)
    - Kalman filter simulation
    - CNN classification simulation
    - Emergency response triggers
    - Performance benchmarking
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.enabled = True
        self.detection_range = 100.0  # meters
        self.confidence_threshold = 0.7
        self._obstacles: List[ObstacleData] = []
        self._sensor_fusion_enabled = True

        # Sensor characteristics
        self._sensor_ranges = {
            "radar": 150.0,  # meters
            "ir": 80.0,  # meters
            "ultrasonic": 10.0,  # meters
        }

        self._sensor_accuracies = {"radar": 0.95, "ir": 0.85, "ultrasonic": 0.75}

    def enable(self):
        """Enable obstacle detection."""
        self.enabled = True

    def disable(self):
        """Disable obstacle detection."""
        self.enabled = False
        self._obstacles.clear()

    def set_detection_range(self, range_meters: float):
        """Set maximum detection range."""
        self.detection_range = range_meters

    def set_confidence_threshold(self, threshold: float):
        """Set minimum confidence threshold for detections."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))

    def add_obstacle(
        self, object_type: str, distance: float, bearing: float, velocity: float = 0.0
    ):
        """
        Add a simulated obstacle for testing.

        Args:
            object_type: Type of obstacle ('pedestrian', 'vehicle', 'animal', 'static_object')
            distance: Distance in meters
            bearing: Bearing in degrees relative to vehicle heading
            velocity: Object velocity in m/s
        """
        # Simulate sensor fusion confidence
        confidence = self._calculate_fusion_confidence(distance, object_type)

        if confidence >= self.confidence_threshold:
            obstacle = ObstacleData(
                object_type=object_type,
                distance=distance,
                bearing=bearing,
                velocity=velocity,
                confidence=confidence,
            )

            self._obstacles.append(obstacle)
            self._process_obstacle_detection(obstacle)

    def simulate_pedestrian(self, distance: float, crossing: bool = False):
        """
        Simulate pedestrian detection scenario.

        Args:
            distance: Distance to pedestrian in meters
            crossing: Whether pedestrian is crossing the road
        """
        velocity = 1.4 if crossing else 0.0  # m/s walking speed
        bearing = 0.0 if crossing else random.uniform(-45, 45)

        self.add_obstacle("pedestrian", distance, bearing, velocity)

    def simulate_animal(self, distance: float, is_night: bool = False):
        """
        Simulate animal detection scenario.

        Args:
            distance: Distance to animal in meters
            is_night: Whether it's nighttime (affects IR sensor performance)
        """
        # Animals are harder to detect at night
        confidence_modifier = 0.8 if is_night else 1.0

        obstacle = ObstacleData(
            object_type="animal",
            distance=distance,
            bearing=random.uniform(-30, 30),
            velocity=random.uniform(0.5, 3.0),  # Variable animal movement
            confidence=self._calculate_fusion_confidence(distance, "animal") * confidence_modifier,
        )

        if obstacle.confidence >= self.confidence_threshold:
            self._obstacles.append(obstacle)
            self._process_obstacle_detection(obstacle, is_night)

    def simulate_static_object(self, distance: float, size: str = "medium"):
        """
        Simulate static object detection.

        Args:
            distance: Distance to object in meters
            size: Object size ('small', 'medium', 'large')
        """
        confidence_modifiers = {"small": 0.7, "medium": 1.0, "large": 1.2}
        modifier = confidence_modifiers.get(size, 1.0)

        self.add_obstacle("static_object", distance, 0.0, 0.0)

    def update(self, vehicle_state: VehicleState):
        """Update obstacle detection simulation."""
        if not self.enabled:
            return

        # Update obstacle positions based on relative movement
        self._update_obstacle_positions(vehicle_state)

        # Remove obstacles that are out of range
        self._cleanup_old_obstacles()

        # Publish obstacle detection data
        if self._obstacles:
            self.event_bus.publish(
                Event(
                    "obstacles_detected",
                    data=self._obstacles.copy(),
                    source="ObstacleDetectionSimulator",
                )
            )

    def _update_obstacle_positions(self, vehicle_state: VehicleState):
        """Update obstacle positions based on vehicle movement."""
        # Simplified position update - in reality this would use Kalman filtering
        for obstacle in self._obstacles:
            # Simulate relative movement
            time_delta = 0.1  # 100ms simulation step

            # Update distance based on relative velocities
            relative_velocity = vehicle_state.speed / 3.6 - obstacle.velocity  # Convert km/h to m/s
            obstacle.distance += relative_velocity * time_delta

    def _cleanup_old_obstacles(self):
        """Remove obstacles that are out of detection range."""
        self._obstacles = [
            obs
            for obs in self._obstacles
            if obs.distance <= self.detection_range and obs.distance > 0
        ]

    def _calculate_fusion_confidence(self, distance: float, object_type: str) -> float:
        """
        Calculate sensor fusion confidence based on distance and object type.

        Simulates Kalman filter + CNN classification confidence.
        """
        base_confidence = 0.9

        # Distance affects confidence
        if distance > 50:
            base_confidence *= 0.8
        elif distance > 100:
            base_confidence *= 0.6

        # Object type affects detectability
        type_modifiers = {"vehicle": 1.0, "pedestrian": 0.85, "animal": 0.75, "static_object": 0.9}

        base_confidence *= type_modifiers.get(object_type, 0.7)

        # Add some sensor fusion noise
        noise = random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, base_confidence + noise))

    def _process_obstacle_detection(self, obstacle: ObstacleData, is_night: bool = False):
        """Process obstacle detection and trigger appropriate responses."""
        # Determine response based on obstacle type and distance
        if obstacle.object_type == "pedestrian":
            if obstacle.distance < 20 and obstacle.velocity > 0:
                # TC-604.1: Pedestrian crossing → emergency stop
                self._trigger_emergency_stop(obstacle)
            elif obstacle.distance < 50:
                self._trigger_warning(obstacle, "Pedestrian detected ahead")

        elif obstacle.object_type == "animal":
            if obstacle.distance < 30:
                # TC-604.2: Animal → slow + alert
                severity = "warning" if not is_night else "critical"
                self._trigger_slow_down(obstacle, is_night)

        elif obstacle.object_type == "static_object":
            if obstacle.distance < 25:
                # TC-604.3: Static object → navigate around
                self._trigger_navigation_alert(obstacle)

    def _trigger_emergency_stop(self, obstacle: ObstacleData):
        """Trigger emergency stop response."""
        alert = AlertData(
            alert_type="emergency_stop",
            severity="critical",
            message=f"Emergency stop triggered - {obstacle.object_type} at {obstacle.distance:.1f}m",
            source_component="ObstacleDetectionSimulator",
        )
        self.event_bus.publish(Event("alert", data=alert, source="ObstacleDetectionSimulator"))

    def _trigger_slow_down(self, obstacle: ObstacleData, is_night: bool = False):
        """Trigger slow down response."""
        night_msg = " (night conditions)" if is_night else ""
        alert = AlertData(
            alert_type="slow_down",
            severity="warning",
            message=f"Reducing speed - {obstacle.object_type} detected{night_msg}",
            source_component="ObstacleDetectionSimulator",
        )
        self.event_bus.publish(Event("alert", data=alert, source="ObstacleDetectionSimulator"))

    def _trigger_navigation_alert(self, obstacle: ObstacleData):
        """Trigger navigation alert for static obstacles."""
        alert = AlertData(
            alert_type="navigation_required",
            severity="info",
            message=f"Navigation adjustment needed - {obstacle.object_type} ahead",
            source_component="ObstacleDetectionSimulator",
        )
        self.event_bus.publish(Event("alert", data=alert, source="ObstacleDetectionSimulator"))

    def _trigger_warning(self, obstacle: ObstacleData, message: str):
        """Trigger general warning alert."""
        alert = AlertData(
            alert_type="obstacle_warning",
            severity="warning",
            message=message,
            source_component="ObstacleDetectionSimulator",
        )
        self.event_bus.publish(Event("alert", data=alert, source="ObstacleDetectionSimulator"))

    def get_detected_obstacles(self) -> List[ObstacleData]:
        """Get list of currently detected obstacles."""
        return self._obstacles.copy()

    def clear_obstacles(self):
        """Clear all detected obstacles."""
        self._obstacles.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get current obstacle detection status."""
        return {
            "enabled": self.enabled,
            "detection_range": self.detection_range,
            "confidence_threshold": self.confidence_threshold,
            "obstacles_count": len(self._obstacles),
            "sensor_fusion_enabled": self._sensor_fusion_enabled,
            "sensor_ranges": self._sensor_ranges,
        }
