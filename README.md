# CarPort SDK - Automotive Simulator

CarPort SDK is a Python-based automotive simulator designed for testing and validating autonomous driving features. It provides comprehensive simulation capabilities for the Drive Pilot project requirements including driver monitoring, adaptive speed limiting, OTA updates, obstacle detection, and regulatory compliance.

## Features

### Core Simulation Components

- **🚗 Driver Monitoring (DP-601)**: Camera-based gaze tracking simulation with configurable alert thresholds
- **⚡ Adaptive Speed Limiting (DP-602)**: Dynamic speed control based on environmental conditions 
- **📦 OTA Updates (DP-603)**: Secure over-the-air update simulation with rollback capability
- **🔍 Obstacle Detection (DP-604)**: Multi-sensor fusion simulation (IR, radar, ultrasonic)
- **🌍 Regulatory Mode (DP-605)**: GPS-based geofencing for regional compliance testing

### Key Benefits

- **Comprehensive Testing**: Test all Drive Pilot features in a controlled environment
- **Event-Driven Architecture**: Publisher-subscriber pattern for component communication
- **Configurable Scenarios**: Create custom test scenarios for specific requirements
- **Real-time Simulation**: Simulate sensor data, vehicle state, and environmental conditions
- **Test Case Coverage**: Implements all test cases from Drive Pilot specification

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mc5eamus/drivepilot-simulator.git
cd drivepilot-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SDK in development mode
pip install -e .
```

### Basic Usage

```python
from carport_sdk import CarPortSimulator

# Create simulator instance
simulator = CarPortSimulator()

# Configure driver monitoring
simulator.driver_monitoring.set_alert_threshold(5.0)

# Start simulation
simulator.start()

# Simulate driver looking away for 6 seconds
simulator.driver_monitoring.simulate_gaze_away(6.0)

# Check for alerts
alerts = simulator.get_alerts()
for alert in alerts:
    print(f"Alert: {alert.message}")

# Stop simulation
simulator.stop()
```

### Running Examples

```bash
# Run basic simulation example
python examples/basic_simulation.py

# Run driver monitoring test
python examples/driver_monitoring_test.py

# Run obstacle detection scenarios
python examples/obstacle_scenarios.py
```

## Testing

Run the test suite to validate all components:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=carport_sdk tests/

# Run specific test module
pytest tests/test_driver_monitoring.py
```

## Development

### Code Quality

```bash
# Code formatting
black carport_sdk/

# Linting
flake8 carport_sdk/

# Type checking
mypy carport_sdk/
```

### Project Structure

```
carport_sdk/
├── core/                   # Core simulation engine
│   ├── simulator.py       # Main simulator class
│   ├── events.py          # Event system
│   └── models.py          # Data models
├── features/              # Feature-specific simulators
│   ├── driver_monitoring.py
│   ├── speed_limiting.py
│   ├── ota_updates.py
│   ├── obstacle_detection.py
│   └── regulatory_mode.py
└── utils/                 # Utility functions
    ├── logging.py
    ├── validation.py
    └── time_utils.py
```

## Test Cases Implementation

The SDK implements all test cases from the Drive Pilot specification:

### Driver Monitoring (DP-601)
- **TC-601.1**: Driver looks away >5 sec → escalating alerts (visual, audible, haptic)

### Adaptive Speed Limiting (DP-602)  
- **TC-602.1**: Enter lower speed zone → reduce speed in ≤3 sec
- **TC-602.2**: Weather change → reduce speed + notify driver

### OTA Updates (DP-603)
- **TC-603.1**: Valid update → success
- **TC-603.2**: Invalid signature → reject + log
- **TC-603.3**: Simulate failure → rollback

### Obstacle Detection (DP-604)
- **TC-604.1**: Pedestrian → emergency stop
- **TC-604.2**: Animal at night → slow + alert  
- **TC-604.3**: Static object → navigate around

### Regulatory Mode (DP-605)
- **TC-605.1**: Cross border → switch mode + notify
- **TC-605.2**: Engage disallowed feature → block + feedback

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Reference

This SDK is based on the Drive Pilot project requirements documented in `content/transcript.md`. The original project team includes:

- **Sherry**: Project Manager
- **Fu**: Requirements Engineer  
- **Tanvi**: Software Engineer
- **Dennis**: Test Engineer
- **Pavan**: Homologation Engineer

## Documentation

For detailed API documentation and advanced usage examples, see the `docs/` directory or visit our [online documentation](https://mc5eamus.github.io/drivepilot-simulator).