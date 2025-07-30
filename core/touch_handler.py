"""
Touch input and gesture recognition for the Raspberry Pi Dashboard.
"""

import time
from typing import Tuple, Optional, Dict, Any


class TouchHandler:
    """Handle touch input and swipe gesture detection with configurable parameters."""
    
    def __init__(self, config_manager=None, swipe_threshold: int = 100):
        """
        Initialize touch handler.
        
        Args:
            config_manager: Configuration manager for dynamic settings
            swipe_threshold: Fallback swipe threshold if config not available
        """
        # Get swipe threshold from config or use default
        if config_manager:
            self.swipe_threshold = config_manager.get('app.touch_swipe_threshold', swipe_threshold)
        else:
            self.swipe_threshold = swipe_threshold
            
        self.touch_start: Optional[Tuple[int, int]] = None
        self.touch_start_time: Optional[float] = None
        self.is_touching = False
        self.max_swipe_time = 1.0  # Maximum time for a valid swipe
        self.min_swipe_ratio = 2.0  # Minimum horizontal:vertical ratio for swipe
        
        # Store config manager for potential runtime updates
        self.config_manager = config_manager
    
    def update_config(self, config_manager) -> None:
        """
        Update configuration from config manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        if config_manager:
            new_threshold = config_manager.get('app.touch_swipe_threshold', self.swipe_threshold)
            if new_threshold != self.swipe_threshold:
                print(f"Updated swipe threshold: {self.swipe_threshold} -> {new_threshold}")
                self.swipe_threshold = new_threshold
    
    def handle_touch_start(self, pos: Tuple[int, int]) -> None:
        """
        Handle touch start event.
        
        Args:
            pos: Touch position (x, y)
        """
        self.touch_start = pos
        self.touch_start_time = time.time()
        self.is_touching = True
        
        # Debug logging if enabled
        if self.config_manager and self.config_manager.get('app.debug_mode', False):
            print(f"Touch start at {pos}")
    
    def handle_touch_end(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Handle touch end event and detect swipe gesture.
        
        Args:
            pos: Touch end position (x, y)
            
        Returns:
            Swipe direction ('swipe_left', 'swipe_right') or None
        """
        if not self.touch_start or not self.is_touching or not self.touch_start_time:
            self._reset_touch()
            return None
        
        # Calculate swipe parameters
        dx = pos[0] - self.touch_start[0]
        dy = pos[1] - self.touch_start[1]
        dt = time.time() - self.touch_start_time
        distance = (dx**2 + dy**2)**0.5
        
        # Debug logging if enabled
        if self.config_manager and self.config_manager.get('app.debug_mode', False):
            print(f"Touch end at {pos}, dx={dx}, dy={dy}, dt={dt:.2f}s, distance={distance:.1f}")
        
        # Reset touch state
        swipe_result = None
        
        # Check for valid horizontal swipe
        if self._is_valid_swipe(dx, dy, dt):
            swipe_result = 'swipe_right' if dx > 0 else 'swipe_left'
            if self.config_manager and self.config_manager.get('app.debug_mode', False):
                print(f"Detected {swipe_result}")
        
        self._reset_touch()
        return swipe_result
    
    def handle_touch_move(self, pos: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """
        Handle touch move event for real-time feedback.
        
        Args:
            pos: Current touch position (x, y)
            
        Returns:
            Dictionary with move information or None
        """
        if not self.touch_start or not self.is_touching:
            return None
        
        dx = pos[0] - self.touch_start[0]
        dy = pos[1] - self.touch_start[1]
        
        return {
            'delta_x': dx,
            'delta_y': dy,
            'distance': (dx**2 + dy**2)**0.5,
            'is_horizontal': abs(dx) > abs(dy) * self.min_swipe_ratio,
            'touch_duration': time.time() - self.touch_start_time if self.touch_start_time else 0
        }
    
    def _is_valid_swipe(self, dx: float, dy: float, dt: float) -> bool:
        """
        Check if movement qualifies as a valid swipe.
        
        Args:
            dx: Horizontal distance
            dy: Vertical distance  
            dt: Time duration
            
        Returns:
            True if valid swipe, False otherwise
        """
        # Check minimum distance
        if abs(dx) < self.swipe_threshold:
            return False
        
        # Check time constraint
        if dt > self.max_swipe_time:
            return False
        
        # Check if predominantly horizontal
        if abs(dx) < abs(dy) * self.min_swipe_ratio:
            return False
        
        return True
    
    def _reset_touch(self) -> None:
        """Reset touch state."""
        self.touch_start = None
        self.touch_start_time = None
        self.is_touching = False
    
    def cancel_touch(self) -> None:
        """Cancel current touch interaction."""
        if self.config_manager and self.config_manager.get('app.debug_mode', False):
            print("Touch cancelled")
        self._reset_touch()
    
    def get_touch_info(self) -> Dict[str, Any]:
        """
        Get current touch state information.
        
        Returns:
            Dictionary with touch state information
        """
        return {
            'is_touching': self.is_touching,
            'touch_start': self.touch_start,
            'touch_duration': time.time() - self.touch_start_time if self.touch_start_time else 0,
            'swipe_threshold': self.swipe_threshold,
            'max_swipe_time': self.max_swipe_time,
            'min_swipe_ratio': self.min_swipe_ratio
        }
    
    def get_gesture_settings(self) -> Dict[str, Any]:
        """
        Get current gesture recognition settings.
        
        Returns:
            Dictionary with gesture settings
        """
        return {
            'swipe_threshold': self.swipe_threshold,
            'max_swipe_time': self.max_swipe_time,
            'min_swipe_ratio': self.min_swipe_ratio
        }
    
    def set_gesture_settings(self, **kwargs) -> None:
        """
        Update gesture recognition settings.
        
        Args:
            swipe_threshold: Minimum pixels for swipe detection
            max_swipe_time: Maximum time for valid swipe
            min_swipe_ratio: Minimum horizontal:vertical ratio
        """
        if 'swipe_threshold' in kwargs:
            self.swipe_threshold = kwargs['swipe_threshold']
        if 'max_swipe_time' in kwargs:
            self.max_swipe_time = kwargs['max_swipe_time']
        if 'min_swipe_ratio' in kwargs:
            self.min_swipe_ratio = kwargs['min_swipe_ratio']
        
        if self.config_manager and self.config_manager.get('app.debug_mode', False):
            print(f"Updated gesture settings: {self.get_gesture_settings()}") 