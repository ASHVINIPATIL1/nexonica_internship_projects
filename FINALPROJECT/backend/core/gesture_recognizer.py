"""
Gesture Recognition Module
Converts finger counts into specific actions/modes
"""

import time
import config

class GestureRecognizer:
    def __init__(self):
        """Initialize gesture recognizer"""
        self.current_mode = 'idle'
        self.current_color_index = 0  # Start with first color (red)
        
        # Gesture timing
        self.last_gesture = None
        self.gesture_start_time = None
        self.gesture_confirmed = False
        self.last_color_change_time = 0  # Cooldown for color changes
    
    def recognize_gesture(self, finger_count: int) -> dict:
        """
        Convert finger count to action
        
        Args:
            finger_count: Number of fingers detected (0-5)
            
        Returns:
            dict with 'mode' and 'action' keys
        """
        result = {
            'mode': self.current_mode,
            'action': None,
            'color_changed': False
        }
        
        # Track gesture timing for color changes
        current_time = time.time()
        
        # Check if gesture changed
        if finger_count != self.last_gesture:
            self.last_gesture = finger_count
            self.gesture_start_time = current_time
            self.gesture_confirmed = False
        
        # Check if gesture held long enough
        if self.gesture_start_time:
            hold_duration = current_time - self.gesture_start_time
            if hold_duration >= config.GESTURE_HOLD_TIME and not self.gesture_confirmed:
                self.gesture_confirmed = True
        
        # Map finger counts to modes/actions
        if finger_count == config.GESTURE_ERASE:  # 0 fingers (fist)
            self.current_mode = 'erase'
            result['mode'] = 'erase'
        
        elif finger_count == config.GESTURE_DRAW:  # 1 finger
            self.current_mode = 'draw'
            result['mode'] = 'draw'
        
        elif finger_count == config.GESTURE_STOP:  # 2 fingers
            self.current_mode = 'idle'
            result['mode'] = 'idle'
        
        elif finger_count == config.GESTURE_NEXT_COLOR:  # 3 fingers
            if self.gesture_confirmed:
                # Check cooldown (prevent continuous changing)
                if current_time - self.last_color_change_time > 2.0:  # 2 second cooldown
                    self._next_color()
                    result['action'] = 'next_color'
                    result['color_changed'] = True
                    self.last_color_change_time = current_time
                self.gesture_confirmed = False  # Prevent continuous triggering
        
        elif finger_count == config.GESTURE_PREV_COLOR:  # 4 fingers
            if self.gesture_confirmed:
                # Check cooldown (prevent continuous changing)
                if current_time - self.last_color_change_time > 2.0:  # 2 second cooldown
                    self._prev_color()
                    result['action'] = 'prev_color'
                    result['color_changed'] = True
                    self.last_color_change_time = current_time
                self.gesture_confirmed = False
        
        elif finger_count == config.GESTURE_PAUSE:  # 5 fingers (palm)
            self.current_mode = 'pause'
            result['mode'] = 'pause'
        
        return result
    
    def _next_color(self):
        """Cycle to next color"""
        self.current_color_index = (self.current_color_index + 1) % len(config.COLOR_ORDER)
        print(f"🎨 Color changed to: {self.get_current_color_name()}")
    
    def _prev_color(self):
        """Cycle to previous color"""
        self.current_color_index = (self.current_color_index - 1) % len(config.COLOR_ORDER)
        print(f"🎨 Color changed to: {self.get_current_color_name()}")
    
    def get_current_color_name(self) -> str:
        """Get current color name"""
        return config.COLOR_ORDER[self.current_color_index]
    
    def get_current_color_bgr(self) -> tuple:
        """Get current color in BGR format"""
        color_name = self.get_current_color_name()
        return config.COLORS[color_name]
    
    def set_color_by_name(self, color_name: str):
        """Set color by name (for keyboard shortcuts)"""
        if color_name in config.COLOR_ORDER:
            self.current_color_index = config.COLOR_ORDER.index(color_name)
            print(f"🎨 Color set to: {color_name}")
    
    def get_mode_display_text(self) -> str:
        """Get human-readable mode text for UI"""
        mode_map = {
            'draw': 'DRAWING',
            'erase': 'ERASING',
            'idle': 'IDLE',
            'pause': 'PAUSED'
        }
        return mode_map.get(self.current_mode, 'UNKNOWN')