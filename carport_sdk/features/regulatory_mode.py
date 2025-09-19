"""
DP-605: Regulatory Mode Switching Simulator

Simulates GPS-based geofencing for regional compliance switching.
Implements the test cases from the Drive Pilot specification:
- TC-605.1: Cross border → switch mode + notify
- TC-605.2: Engage disallowed feature → block + feedback
"""

from typing import Dict, Any, List, Optional
from ..core.events import EventBus, Event
from ..core.models import VehicleState, AlertData


class RegulatoryRegion:
    """Represents a regulatory region with specific compliance rules."""
    
    def __init__(self, name: str, code: str, allowed_features: List[str], 
                 speed_limit_max: float = None):
        self.name = name
        self.code = code
        self.allowed_features = allowed_features
        self.speed_limit_max = speed_limit_max


class RegulatoryModeSimulator:
    """
    Simulates regulatory mode switching with GPS-based geofencing.
    
    Features:
    - GPS-based region detection
    - Automatic compliance profile switching
    - Feature blocking/enabling
    - Cross-border notifications
    - Regulatory database simulation
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.enabled = True
        self.current_region = None
        self._initialize_regions()
        
        # Feature availability
        self._all_features = [
            "driver_monitoring",
            "adaptive_speed_limiting", 
            "ota_updates",
            "obstacle_detection",
            "autonomous_parking",
            "highway_autopilot",
            "traffic_light_detection"
        ]
        
    def enable(self):
        """Enable regulatory mode switching."""
        self.enabled = True
        
    def disable(self):
        """Disable regulatory mode switching."""
        self.enabled = False
        
    def _initialize_regions(self):
        """Initialize regulatory regions database."""
        self._regions = {
            "US": RegulatoryRegion(
                name="United States",
                code="US",
                allowed_features=[
                    "driver_monitoring", "adaptive_speed_limiting", 
                    "ota_updates", "obstacle_detection"
                ],
                speed_limit_max=130.0
            ),
            "EU": RegulatoryRegion(
                name="European Union", 
                code="EU",
                allowed_features=[
                    "driver_monitoring", "adaptive_speed_limiting",
                    "ota_updates", "obstacle_detection", "highway_autopilot"
                ],
                speed_limit_max=120.0
            ),
            "JP": RegulatoryRegion(
                name="Japan",
                code="JP", 
                allowed_features=[
                    "driver_monitoring", "adaptive_speed_limiting",
                    "obstacle_detection", "traffic_light_detection"
                ],
                speed_limit_max=100.0
            ),
            "CN": RegulatoryRegion(
                name="China",
                code="CN",
                allowed_features=[
                    "driver_monitoring", "obstacle_detection"
                ],
                speed_limit_max=120.0
            )
        }
        
        # Set default region
        self.current_region = self._regions["US"]
        
    def simulate_gps_position(self, latitude: float, longitude: float):
        """
        Simulate GPS position update and check for region changes.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
        """
        if not self.enabled:
            return
            
        # Simulate geofencing logic (simplified)
        new_region = self._determine_region_from_coordinates(latitude, longitude)
        
        if new_region != self.current_region:
            old_region = self.current_region
            self.current_region = new_region
            self._handle_region_change(old_region, new_region)
            
    def simulate_border_crossing(self, from_region: str, to_region: str):
        """
        Simulate crossing from one regulatory region to another.
        
        Args:
            from_region: Source region code (e.g., "US", "EU")
            to_region: Destination region code
        """
        if from_region in self._regions and to_region in self._regions:
            old_region = self._regions[from_region]
            new_region = self._regions[to_region]
            
            self.current_region = new_region
            self._handle_region_change(old_region, new_region)
            
    def check_feature_allowed(self, feature_name: str) -> bool:
        """
        Check if a feature is allowed in the current region.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            True if feature is allowed, False otherwise
        """
        if not self.enabled or not self.current_region:
            return True
            
        return feature_name in self.current_region.allowed_features
        
    def attempt_feature_activation(self, feature_name: str) -> bool:
        """
        Attempt to activate a feature, respecting regional restrictions.
        
        Args:
            feature_name: Name of the feature to activate
            
        Returns:
            True if activation succeeded, False if blocked
        """
        if not self.enabled:
            return True
            
        if self.check_feature_allowed(feature_name):
            self._notify_feature_activation(feature_name, True)
            return True
        else:
            # TC-605.2: Block disallowed feature + feedback
            self._notify_feature_blocked(feature_name)
            return False
            
    def get_allowed_features(self) -> List[str]:
        """Get list of features allowed in current region."""
        if not self.current_region:
            return self._all_features.copy()
        return self.current_region.allowed_features.copy()
        
    def get_blocked_features(self) -> List[str]:
        """Get list of features blocked in current region.""" 
        if not self.current_region:
            return []
        return [f for f in self._all_features if f not in self.current_region.allowed_features]
        
    def update(self, vehicle_state: VehicleState):
        """Update regulatory mode simulation."""
        if not self.enabled:
            return
            
        # Check current position if available
        if vehicle_state.position:
            lat = vehicle_state.position.get("lat", 0.0)
            lon = vehicle_state.position.get("lon", 0.0)
            
            # Only update if position is not zero (indicating valid GPS)
            if lat != 0.0 or lon != 0.0:
                self.simulate_gps_position(lat, lon)
                
    def _determine_region_from_coordinates(self, lat: float, lon: float) -> RegulatoryRegion:
        """
        Determine regulatory region from GPS coordinates.
        
        Simplified geofencing logic for simulation purposes.
        """
        # Simplified region detection based on rough geographic boundaries
        if 25.0 <= lat <= 49.0 and -125.0 <= lon <= -66.0:
            return self._regions["US"]
        elif 35.0 <= lat <= 71.0 and -10.0 <= lon <= 40.0:
            return self._regions["EU"]
        elif 30.0 <= lat <= 46.0 and 129.0 <= lon <= 146.0:
            return self._regions["JP"]
        elif 18.0 <= lat <= 54.0 and 73.0 <= lon <= 135.0:
            return self._regions["CN"]
        else:
            # Default to US for unknown regions
            return self._regions["US"]
            
    def _handle_region_change(self, old_region: RegulatoryRegion, 
                             new_region: RegulatoryRegion):
        """Handle transition between regulatory regions."""
        # TC-605.1: Cross border → switch mode + notify
        self._notify_region_change(old_region, new_region)
        
        # Check for newly blocked features
        newly_blocked = [
            f for f in old_region.allowed_features 
            if f not in new_region.allowed_features
        ]
        
        # Check for newly allowed features
        newly_allowed = [
            f for f in new_region.allowed_features
            if f not in old_region.allowed_features
        ]
        
        if newly_blocked:
            self._notify_features_disabled(newly_blocked)
            
        if newly_allowed:
            self._notify_features_enabled(newly_allowed)
            
    def _notify_region_change(self, old_region: RegulatoryRegion, 
                             new_region: RegulatoryRegion):
        """Notify about region change."""
        alert = AlertData(
            alert_type="region_change",
            severity="info",
            message=f"Regulatory region changed from {old_region.name} to {new_region.name}",
            source_component="RegulatoryModeSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="RegulatoryModeSimulator"))
        
    def _notify_feature_blocked(self, feature_name: str):
        """Notify about feature being blocked."""
        alert = AlertData(
            alert_type="feature_blocked",
            severity="warning", 
            message=f"Feature '{feature_name}' not available in {self.current_region.name}",
            source_component="RegulatoryModeSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="RegulatoryModeSimulator"))
        
    def _notify_feature_activation(self, feature_name: str, success: bool):
        """Notify about feature activation attempt."""
        status = "activated" if success else "blocked"
        alert = AlertData(
            alert_type="feature_activation",
            severity="info",
            message=f"Feature '{feature_name}' {status}",
            source_component="RegulatoryModeSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="RegulatoryModeSimulator"))
        
    def _notify_features_disabled(self, features: List[str]):
        """Notify about features being disabled due to region change."""
        alert = AlertData(
            alert_type="features_disabled",
            severity="warning",
            message=f"Features disabled in {self.current_region.name}: {', '.join(features)}",
            source_component="RegulatoryModeSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="RegulatoryModeSimulator"))
        
    def _notify_features_enabled(self, features: List[str]):
        """Notify about features being enabled due to region change."""
        alert = AlertData(
            alert_type="features_enabled",
            severity="info",
            message=f"Features enabled in {self.current_region.name}: {', '.join(features)}",
            source_component="RegulatoryModeSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="RegulatoryModeSimulator"))
        
    def get_current_region(self) -> Optional[RegulatoryRegion]:
        """Get current regulatory region."""
        return self.current_region
        
    def get_status(self) -> Dict[str, Any]:
        """Get current regulatory mode status."""
        return {
            "enabled": self.enabled,
            "current_region": {
                "name": self.current_region.name,
                "code": self.current_region.code,
                "allowed_features": self.current_region.allowed_features,
                "speed_limit_max": self.current_region.speed_limit_max
            } if self.current_region else None,
            "available_regions": list(self._regions.keys()),
            "blocked_features": self.get_blocked_features()
        }