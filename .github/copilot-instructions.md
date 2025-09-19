# CarPort SDK - Automotive Simulator Repository

**ALWAYS follow these instructions first and only search for additional context if the information provided here is incomplete or found to be in error.**

This repository hosts the CarPort SDK, a Python-based automotive simulator designed for testing and validating autonomous driving features. The SDK provides simulation capabilities for driver monitoring, adaptive speed limiting, OTA updates, obstacle detection, and regulatory compliance based on the Drive Pilot project requirements.

## Repository Structure

**VALIDATED REPOSITORY CONTENTS:**
```
drivepilot-simulator/
├── .gitignore              # Python-focused gitignore with development exclusions
├── .github/
│   └── copilot-instructions.md  # This file
├── content/
│   └── transcript.md       # OEMagic Teams call transcript for Drive Pilot project (reference)
├── carport_sdk/            # Main SDK package
│   ├── __init__.py
│   ├── core/               # Core simulation components
│   ├── features/           # Feature-specific simulators
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── examples/               # Usage examples
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── setup.py               # Package installation
└── README.md              # Project overview and usage
```

## Working Effectively

### Prerequisites
- **Python 3.8+**: Required for running the CarPort SDK
- **Virtual Environment**: Recommended for isolated development (venv, conda, etc.)
- **pip**: For installing dependencies from requirements.txt
- **pytest**: For running the test suite (installed via requirements.txt)

### Key Project Information
Based on `content/transcript.md`, the CarPort SDK implements simulation capabilities for Drive Pilot autonomous vehicle features:
- **DP-601**: Real-Time Driver Monitoring (camera-based gaze tracking simulation)
- **DP-602**: Adaptive Speed Limiting (maps, weather, traffic integration simulation)  
- **DP-603**: OTA Update Support (secure updates with rollback simulation)
- **DP-604**: Enhanced Obstacle Detection (sensor fusion simulation)
- **DP-605**: Regulatory Mode Switching (geofencing compliance simulation)

### Common Operations

#### Setup Development Environment
```bash
# Create virtual environment (RECOMMENDED)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SDK in development mode
pip install -e .
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_driver_monitoring.py

# Run with coverage
pytest --cov=carport_sdk tests/
```

#### Using the SDK
```bash
# Run example simulations
python examples/basic_simulation.py

# Import in Python code
from carport_sdk import CarPortSimulator
```

## Validation

### Build and Test Commands
- **pip install -e .**: Install SDK in development mode
- **pytest**: Run the full test suite  
- **pytest --cov=carport_sdk**: Run tests with coverage reporting
- **python -m flake8 carport_sdk/**: Code style linting
- **python -m mypy carport_sdk/**: Type checking (if configured)

### Development Workflow
When making changes to the SDK:
1. **SETUP ENVIRONMENT**: Create virtual environment and install dependencies
2. **RUN EXISTING TESTS**: Ensure current functionality works (`pytest`)
3. **IMPLEMENT CHANGES**: Make surgical modifications to SDK code
4. **ADD/UPDATE TESTS**: Write tests for new functionality
5. **VALIDATE**: Run tests and linting to ensure quality
6. **DOCUMENTATION**: Update docstrings and README as needed

### Expected Timings
- **Environment setup**: 30-60 seconds (dependency installation)
- **Test suite execution**: 5-30 seconds (depending on scope)
- **SDK import/usage**: &lt; 1 second (lightweight simulator)

## Project Context

### CarPort SDK Features (implementing Drive Pilot requirements)
The SDK provides simulation capabilities for automotive autonomous driving systems:
- **Driver Monitoring**: Simulated camera-based gaze tracking with configurable alert thresholds
- **Speed Control**: Virtual speed limiting simulation based on environmental conditions
- **Update System**: Mock OTA update system with rollback simulation
- **Obstacle Detection**: Simulated multi-sensor fusion (IR, radar, ultrasonic)
- **Regulatory Compliance**: Virtual GPS-based geofencing for testing regional requirements

### SDK Architecture
- **Core Simulator**: Main simulation engine and state management
- **Feature Modules**: Individual simulators for each Drive Pilot feature
- **Event System**: Publisher-subscriber pattern for component communication
- **Data Models**: Standardized data structures for sensor data, vehicle state, etc.
- **Testing Framework**: Comprehensive test coverage for all simulation components

## Important Notes

### What This Repository IS:
- **Python SDK**: CarPort automotive simulator for testing autonomous driving features
- **Development Framework**: Tools and APIs for creating automotive test scenarios
- **Reference Implementation**: Simulated versions of real Drive Pilot features
- **Testing Platform**: Comprehensive test suite for validation and verification

### What This Repository IS NOT:
- **NOT production automotive software** - this is a simulator/testing tool
- **NOT a real-time system** - simulated timing and responses
- **NOT hardware-dependent** - pure software simulation
- **NOT safety-critical** - intended for development and testing only

### Working with Changes
- Follow Python development best practices (PEP 8, type hints, docstrings)
- Maintain comprehensive test coverage for all new features
- Update documentation when adding new simulation capabilities
- Ensure backwards compatibility when modifying existing APIs
- Reference the original Drive Pilot requirements in `content/transcript.md`

## Quick Reference Commands

```bash
# Essential development commands:
python --version           # Check Python version (3.8+ required)
python -m venv venv       # Create virtual environment
source venv/bin/activate  # Activate environment (Linux/Mac)
pip install -r requirements.txt  # Install dependencies
pip install -e .          # Install SDK in development mode
pytest                    # Run test suite
python examples/basic_simulation.py  # Run example
git status                # Check repository state
```

## CarPort SDK Quick Start

```python
# Basic usage example:
from carport_sdk import CarPortSimulator

# Create simulator instance
simulator = CarPortSimulator()

# Configure driver monitoring
simulator.driver_monitoring.set_alert_threshold(5.0)  # 5 second threshold

# Start simulation
simulator.start()

# Simulate driver looking away
simulator.driver_monitoring.simulate_gaze_away(6.0)  # 6 seconds

# Check for alerts
alerts = simulator.get_alerts()
```

**Remember**: This is a Python SDK for automotive simulation. Use virtual environments, run tests frequently, and maintain comprehensive test coverage.