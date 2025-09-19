"""
Test configuration and utilities.
"""

import pytest
from carport_sdk import CarPortSimulator

@pytest.fixture
def simulator():
    """Create a CarPort simulator instance for testing."""
    sim = CarPortSimulator()
    yield sim
    sim.stop()

@pytest.fixture  
def running_simulator():
    """Create a running CarPort simulator instance for testing."""
    sim = CarPortSimulator()
    sim.start()
    yield sim
    sim.stop()