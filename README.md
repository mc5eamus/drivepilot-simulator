# DrivePilot Simulator

A comprehensive car simulator for autonomous driving software development and testing, implementing the core features required for modern autonomous vehicles.

## Features

Based on the OEMagic Drive Pilot project requirements, this simulator implements:

- **DP-601**: Real-Time Driver Monitoring (gaze tracking, alerts)
- **DP-602**: Adaptive Speed Limiting (maps, weather, traffic awareness)
- **DP-603**: OTA Update Support (secure updates, rollback capability)
- **DP-604**: Enhanced Obstacle Detection (sensor fusion)
- **DP-605**: Regulatory Mode Switching (geofencing, compliance)

## Quick Start

```python
from drivepilot_simulator import Car, SimulationEnvironment

# Initialize simulation
env = SimulationEnvironment()
car = Car(environment=env)

# Configure features
car.enable_driver_monitoring(alert_threshold=5.0)
car.enable_adaptive_speed(weather_factor=True)
car.enable_obstacle_detection(sensors=['radar', 'ir', 'ultrasonic'])

# Run simulation
car.start_simulation()
car.drive_to(destination="Test Location")
```

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Testing

```bash
pytest tests/
```

## Architecture

See `content/ideas.md` for detailed architectural concepts and implementation strategy.

## Requirements Implementation

All features are implemented according to the specifications in `content/transcript.md`, including:

- Test cases TC-601.1 through TC-605.2
- Risk mitigation strategies
- Regulatory compliance (UNECE R79, GDPR)
- Security requirements (TLS 1.3, signed packages)

## License

MIT License - see LICENSE file for details.