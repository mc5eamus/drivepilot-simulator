"""
Validation utilities for CarPort SDK.
"""


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate GPS coordinates.
    
    Args:
        latitude: Latitude in degrees (-90 to 90)
        longitude: Longitude in degrees (-180 to 180)
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return (-90.0 <= latitude <= 90.0) and (-180.0 <= longitude <= 180.0)


def validate_speed(speed: float) -> bool:
    """
    Validate vehicle speed.
    
    Args:
        speed: Speed in km/h
        
    Returns:
        True if speed is valid (>= 0), False otherwise
    """
    return speed >= 0.0


def validate_distance(distance: float) -> bool:
    """
    Validate distance measurement.
    
    Args:
        distance: Distance in meters
        
    Returns:
        True if distance is valid (>= 0), False otherwise
    """
    return distance >= 0.0


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence value.
    
    Args:
        confidence: Confidence value (0.0 to 1.0)
        
    Returns:
        True if confidence is valid, False otherwise
    """
    return 0.0 <= confidence <= 1.0