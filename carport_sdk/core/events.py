"""
Event system for CarPort SDK simulation components.
"""

from typing import Any, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Base event class for the simulation system."""
    
    event_type: str
    data: Any = None
    timestamp: datetime = None
    source: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """Central event bus for component communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._event_history: List[Event] = []
        
    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        """Subscribe to events of a specific type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]):
        """Unsubscribe from events of a specific type."""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
    
    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    # Log error but continue with other subscribers
                    print(f"Error in event callback: {e}")
    
    def get_event_history(self, event_type: str = None) -> List[Event]:
        """Get history of events, optionally filtered by type."""
        if event_type is None:
            return self._event_history.copy()
        return [e for e in self._event_history if e.event_type == event_type]
    
    def clear_history(self):
        """Clear the event history."""
        self._event_history.clear()