"""
DP-601: Real-Time Driver Monitoring Simulator

Simulates camera-based gaze tracking with configurable alert thresholds.
Implements the test cases from the Drive Pilot specification:
- TC-601.1: Driver looks away >5 sec → escalating alerts
"""

import time
from typing import Dict, Any
from ..core.events import EventBus, Event
from ..core.models import VehicleState, DriverState, AlertData


class DriverMonitoringSimulator:
    """
    Simulates real-time driver monitoring with gaze tracking.

    Features:
    - Configurable alert threshold (default 5 seconds)
    - Escalating alert levels (visual, audible, haptic)
    - GDPR compliance simulation
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.driver_state = DriverState()
        self.alert_threshold = 5.0  # seconds
        self.enabled = True
        self._time_looking_away = 0.0
        self._last_update_time = time.time()
        self._alert_level = 0  # 0=none, 1=visual, 2=audible, 3=haptic

    def set_alert_threshold(self, threshold: float):
        """Set the alert threshold in seconds."""
        self.alert_threshold = threshold

    def enable(self):
        """Enable driver monitoring."""
        self.enabled = True

    def disable(self):
        """Disable driver monitoring."""
        self.enabled = False
        self._reset_alerts()

    def simulate_gaze_direction(self, direction: str):
        """
        Simulate driver gaze direction.

        Args:
            direction: One of 'forward', 'left', 'right', 'down', 'away'
        """
        self.driver_state.gaze_direction = direction

        if direction != "forward":
            self.driver_state.attention_level = max(0.0, self.driver_state.attention_level - 0.1)
        else:
            self.driver_state.attention_level = min(1.0, self.driver_state.attention_level + 0.2)
            self._time_looking_away = 0.0
            self._reset_alerts()

    def simulate_gaze_away(self, duration: float):
        """
        Simulate driver looking away for a specific duration.

        Args:
            duration: Time in seconds to simulate looking away
        """
        self._time_looking_away = duration
        self.driver_state.gaze_direction = "away"
        self.driver_state.time_looking_away = duration
        self._check_alert_conditions()

    def simulate_eyes_closed(self, closed: bool):
        """Simulate driver eyes closed state."""
        self.driver_state.eyes_closed = closed
        if closed:
            self.driver_state.attention_level = 0.0

    def update(self, vehicle_state: VehicleState):
        """Update driver monitoring simulation."""
        if not self.enabled:
            return

        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time

        # Update time looking away if not looking forward
        if self.driver_state.gaze_direction != "forward":
            self._time_looking_away += delta_time
            self.driver_state.time_looking_away = self._time_looking_away

        # Check for alert conditions
        self._check_alert_conditions()

        # Publish driver state update
        self.event_bus.publish(
            Event("driver_state_update", data=self.driver_state, source="DriverMonitoringSimulator")
        )

    def _check_alert_conditions(self):
        """Check if alert conditions are met and escalate accordingly."""
        if not self.enabled:
            return

        if self._time_looking_away >= self.alert_threshold:
            # Calculate alert level based on time
            if self._time_looking_away >= self.alert_threshold * 3:
                new_level = 3  # haptic
            elif self._time_looking_away >= self.alert_threshold * 2:
                new_level = 2  # audible
            else:
                new_level = 1  # visual

            # Only escalate, don't de-escalate
            if new_level > self._alert_level:
                self._alert_level = new_level
                self._trigger_alert(new_level)

    def _trigger_alert(self, level: int):
        """Trigger an alert with the specified level."""
        alert_types = {1: "visual", 2: "audible", 3: "haptic"}

        alert = AlertData(
            alert_type="driver_attention",
            severity="warning" if level < 3 else "critical",
            message=f"Driver attention required - {alert_types.get(level, 'unknown')} alert",
            source_component="DriverMonitoringSimulator",
        )

        self.event_bus.publish(Event("alert", data=alert, source="DriverMonitoringSimulator"))

    def _reset_alerts(self):
        """Reset alert state."""
        self._alert_level = 0

    def get_status(self) -> Dict[str, Any]:
        """Get current status of driver monitoring."""
        return {
            "enabled": self.enabled,
            "alert_threshold": self.alert_threshold,
            "time_looking_away": self._time_looking_away,
            "alert_level": self._alert_level,
            "driver_state": self.driver_state,
        }
