"""
DP-603: OTA Update Support Simulator

Simulates secure over-the-air updates with rollback capability.
Implements the test cases from the Drive Pilot specification:
- TC-603.1: Valid update → success
- TC-603.2: Invalid signature → reject + log
- TC-603.3: Simulate failure → rollback
"""

import time
import hashlib
from enum import Enum
from typing import Dict, Any, Optional
from ..core.events import EventBus, Event
from ..core.models import VehicleState, AlertData


class UpdateStatus(Enum):
    IDLE = "idle"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class OTAUpdateSimulator:
    """
    Simulates OTA update system with security and rollback features.
    
    Features:
    - TLS 1.3 simulation
    - Package signature validation
    - Backup partition management
    - Automatic rollback on failure
    - Update progress tracking
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.enabled = True
        self.status = UpdateStatus.IDLE
        self.current_version = "1.0.0"
        self.backup_version = "1.0.0"
        self.progress = 0.0  # 0.0 to 1.0
        self._update_start_time = None
        self._simulated_bandwidth = 1.0  # MB/s
        self._package_size = 100.0  # MB
        
        # Simulated security keys
        self._valid_signatures = {
            "2.0.0": "sha256:abc123def456",
            "1.1.0": "sha256:fed456cba321"
        }
        
    def enable(self):
        """Enable OTA update system."""
        self.enabled = True
        
    def disable(self):
        """Disable OTA update system."""
        self.enabled = False
        
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Simulate checking for available updates.
        
        Returns:
            Update info dict if available, None otherwise
        """
        if not self.enabled or self.status != UpdateStatus.IDLE:
            return None
            
        # Simulate available update
        return {
            "version": "2.0.0",
            "size_mb": self._package_size,
            "description": "Bug fixes and performance improvements",
            "signature": "sha256:abc123def456",
            "download_url": "https://updates.example.com/v2.0.0.pkg"
        }
    
    def start_update(self, version: str, signature: str, simulate_failure: bool = False):
        """
        Start an OTA update process.
        
        Args:
            version: Target version to update to
            signature: Package signature for validation
            simulate_failure: If True, simulates update failure for testing
        """
        if not self.enabled or self.status != UpdateStatus.IDLE:
            self._notify_update_error("Update already in progress or system disabled")
            return False
            
        # Validate signature first
        if not self._validate_signature(version, signature):
            self.status = UpdateStatus.FAILED
            self._notify_update_error(f"Invalid signature for version {version}")
            return False
            
        # Start update process
        self.status = UpdateStatus.DOWNLOADING
        self.progress = 0.0
        self._update_start_time = time.time()
        self._simulate_failure = simulate_failure
        
        self._notify_update_status(f"Starting update to version {version}")
        return True
    
    def simulate_network_failure(self):
        """Simulate network failure during update."""
        if self.status in [UpdateStatus.DOWNLOADING, UpdateStatus.INSTALLING]:
            self._trigger_rollback("Network failure during update")
            
    def simulate_power_failure(self):
        """Simulate power failure during update."""
        if self.status == UpdateStatus.INSTALLING:
            self._trigger_rollback("Power failure during installation")
            
    def update(self, vehicle_state: VehicleState):
        """Update OTA simulation state."""
        if not self.enabled or self.status == UpdateStatus.IDLE:
            return
            
        if self.status == UpdateStatus.DOWNLOADING:
            self._update_download_progress()
        elif self.status == UpdateStatus.VALIDATING:
            self._update_validation()
        elif self.status == UpdateStatus.INSTALLING:
            self._update_installation()
            
    def _update_download_progress(self):
        """Update download progress simulation."""
        if self._update_start_time is None:
            return
            
        elapsed = time.time() - self._update_start_time
        download_time = self._package_size / self._simulated_bandwidth
        
        self.progress = min(1.0, elapsed / download_time)
        
        if self.progress >= 1.0:
            self.status = UpdateStatus.VALIDATING
            self.progress = 0.0
            self._notify_update_status("Download complete, validating package")
            
    def _update_validation(self):
        """Update package validation simulation."""
        # Simulate validation taking 2 seconds
        if self.progress == 0.0:
            self._validation_start = time.time()
            
        elapsed = time.time() - self._validation_start
        self.progress = min(1.0, elapsed / 2.0)
        
        if self.progress >= 1.0:
            if hasattr(self, '_simulate_failure') and self._simulate_failure:
                self._trigger_rollback("Package validation failed")
            else:
                self.status = UpdateStatus.INSTALLING
                self.progress = 0.0
                self._notify_update_status("Validation complete, installing update")
                
    def _update_installation(self):
        """Update installation progress simulation."""
        if not hasattr(self, '_install_start'):
            self._install_start = time.time()
            
        elapsed = time.time() - self._install_start
        install_time = 10.0  # 10 seconds to install
        
        self.progress = min(1.0, elapsed / install_time)
        
        if self.progress >= 1.0:
            if hasattr(self, '_simulate_failure') and self._simulate_failure:
                self._trigger_rollback("Installation failed")
            else:
                self._complete_update()
                
    def _complete_update(self):
        """Complete the update successfully."""
        self.backup_version = self.current_version
        self.current_version = "2.0.0"  # Simulated new version
        self.status = UpdateStatus.SUCCESS
        self.progress = 1.0
        
        self._notify_update_status(f"Update completed successfully to version {self.current_version}")
        
        # Reset to idle after notification
        self.status = UpdateStatus.IDLE
        self.progress = 0.0
        
    def _trigger_rollback(self, reason: str):
        """Trigger automatic rollback."""
        self.status = UpdateStatus.ROLLED_BACK
        self.progress = 1.0
        
        alert = AlertData(
            alert_type="ota_rollback",
            severity="warning",
            message=f"Update rolled back: {reason}",
            source_component="OTAUpdateSimulator"
        )
        
        self.event_bus.publish(Event("alert", data=alert, source="OTAUpdateSimulator"))
        
        # Reset to idle
        self.status = UpdateStatus.IDLE
        self.progress = 0.0
        
    def _validate_signature(self, version: str, signature: str) -> bool:
        """Validate package signature."""
        return signature in self._valid_signatures.get(version, [])
        
    def _notify_update_status(self, message: str):
        """Notify about update status change."""
        alert = AlertData(
            alert_type="ota_status",
            severity="info",
            message=message,
            source_component="OTAUpdateSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="OTAUpdateSimulator"))
        
    def _notify_update_error(self, message: str):
        """Notify about update error."""
        alert = AlertData(
            alert_type="ota_error",
            severity="critical",
            message=message,
            source_component="OTAUpdateSimulator"
        )
        self.event_bus.publish(Event("alert", data=alert, source="OTAUpdateSimulator"))
        
    def get_status(self) -> Dict[str, Any]:
        """Get current OTA update status."""
        return {
            "enabled": self.enabled,
            "status": self.status.value,
            "current_version": self.current_version,
            "backup_version": self.backup_version,
            "progress": self.progress,
            "bandwidth_mbps": self._simulated_bandwidth
        }