# API Documentation

## CarPort SDK API Reference

### Core Classes

#### CarPortSimulator

Main simulation engine that orchestrates all Drive Pilot feature simulators.

```python
from carport_sdk import CarPortSimulator

simulator = CarPortSimulator()
simulator.start()
# ... use simulator
simulator.stop()
```

**Methods:**
- `start()` - Start the simulation
- `stop()` - Stop the simulation
- `set_vehicle_position(lat, lon)` - Set GPS coordinates
- `set_vehicle_speed(speed)` - Set vehicle speed in km/h
- `get_alerts(clear=False)` - Get current alerts
- `get_status()` - Get comprehensive simulation status

#### EventBus

Central event system for component communication.

```python
from carport_sdk.core.events import EventBus, Event

event_bus = EventBus()
event_bus.subscribe("event_type", callback_function)
event_bus.publish(Event("event_type", data="event_data"))
```

### Feature Simulators

#### DriverMonitoringSimulator (DP-601)

Simulates camera-based driver monitoring with gaze tracking.

```python
# Configure alert threshold
simulator.driver_monitoring.set_alert_threshold(5.0)

# Simulate gaze directions
simulator.driver_monitoring.simulate_gaze_direction("away")
simulator.driver_monitoring.simulate_gaze_away(6.0)  # 6 seconds
```

#### SpeedLimitingSimulator (DP-602)

Simulates adaptive speed limiting based on environmental conditions.

```python
# Set speed zones
simulator.speed_limiting.set_speed_zone("city")  # 50 km/h

# Weather conditions
simulator.speed_limiting.set_weather_condition("rain")  # Reduces speed

# Traffic density
simulator.speed_limiting.set_traffic_density(0.7)  # 70% traffic
```

#### OTAUpdateSimulator (DP-603)

Simulates over-the-air update system with security and rollback.

```python
# Check for updates
update_info = simulator.ota_updates.check_for_updates()

# Start update
simulator.ota_updates.start_update("2.0.0", "sha256:abc123def456")

# Simulate failures
simulator.ota_updates.simulate_network_failure()
```

#### ObstacleDetectionSimulator (DP-604)

Simulates multi-sensor obstacle detection with fusion algorithms.

```python
# Add obstacles
simulator.obstacle_detection.simulate_pedestrian(15.0, crossing=True)
simulator.obstacle_detection.simulate_animal(30.0, is_night=True)
simulator.obstacle_detection.simulate_static_object(25.0, size="large")

# Get detected obstacles
obstacles = simulator.obstacle_detection.get_detected_obstacles()
```

#### RegulatoryModeSimulator (DP-605)

Simulates GPS-based regulatory compliance switching.

```python
# Simulate border crossing
simulator.regulatory_mode.simulate_border_crossing("US", "EU")

# Check feature availability
allowed = simulator.regulatory_mode.check_feature_allowed("highway_autopilot")

# Attempt feature activation
success = simulator.regulatory_mode.attempt_feature_activation("ota_updates")
```

### Data Models

#### VehicleState

```python
from carport_sdk.core.models import VehicleState

state = VehicleState(
    speed=50.0,
    position={"lat": 40.7128, "lon": -74.0060},
    heading=90.0,
    is_stationary=False
)
```

#### AlertData

```python
from carport_sdk.core.models import AlertData

alert = AlertData(
    alert_type="driver_attention",
    severity="warning",
    message="Driver attention required",
    source_component="DriverMonitoringSimulator"
)
```

### Event Types

- `simulation_started` - Simulation has started
- `simulation_stopped` - Simulation has stopped
- `vehicle_state_update` - Vehicle state changed
- `driver_state_update` - Driver state changed
- `obstacles_detected` - Obstacles detected
- `alert` - Alert generated
- `speed_adjusted` - Speed automatically adjusted
- `region_change` - Regulatory region changed

### Test Cases Implementation

All Drive Pilot test cases are implemented:

- **TC-601.1**: Driver looks away >5 sec → escalating alerts
- **TC-602.1**: Enter lower speed zone → reduce speed in ≤3 sec
- **TC-602.2**: Weather change → reduce speed + notify driver
- **TC-603.1**: Valid update → success
- **TC-603.2**: Invalid signature → reject + log
- **TC-603.3**: Simulate failure → rollback
- **TC-604.1**: Pedestrian → emergency stop
- **TC-604.2**: Animal at night → slow + alert
- **TC-604.3**: Static object → navigate around
- **TC-605.1**: Cross border → switch mode + notify
- **TC-605.2**: Engage disallowed feature → block + feedback