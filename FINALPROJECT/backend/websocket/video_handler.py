"""
WebSocket Video Handler
Streams video frames with hand tracking and canvas overlay
"""

import cv2
import numpy as np
import base64
from flask_socketio import emit
import config

class VideoHandler:
    def __init__(self, socketio, whiteboard_state):
        """
        Initialize video handler
        
        Args:
            socketio: Flask-SocketIO instance
            whiteboard_state: Shared whiteboard state dictionary
        """
        self.socketio = socketio
        self.state = whiteboard_state
        self.running = False
        
        # Camera
        self.cap = None
        
        # Drawing state
        self.prev_point = None
    
    def start_camera(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, config.CAMERA_WIDTH)
        self.cap.set(4, config.CAMERA_HEIGHT)
        self.running = True
        print("📹 Camera started")
    
    def stop_camera(self):
        """Stop camera capture"""
        self.running = False
        if self.cap:
            self.cap.release()
        print("📹 Camera stopped")
    
    def process_frame(self):
        """
        Process single frame:
        1. Read from camera
        2. Detect hand
        3. Recognize gesture
        4. Update canvas
        5. Combine and send to client
        
        Returns:
            bool: True if successful, False if failed
        """
        if not self.cap or not self.cap.isOpened():
            return False
        
        # Read frame
        success, frame = self.cap.read()
        if not success:
            return False
        
        # Flip frame (mirror effect)
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Get whiteboard components
        hand_tracker = self.state['hand_tracker']
        gesture_recognizer = self.state['gesture_recognizer']
        canvas = self.state['canvas']
        brush_thickness = self.state['brush_thickness']
        
        # Detect hand
        hand_detected = hand_tracker.detect_hand(frame)
        self.state['hand_detected'] = hand_detected
        
        if hand_detected:
            # Get finger tip position
            finger_pos = hand_tracker.get_index_finger_tip(w, h)
            
            # Count fingers for gesture
            finger_count = hand_tracker.count_fingers()
            
            # Recognize gesture
            gesture_result = gesture_recognizer.recognize_gesture(finger_count)
            mode = gesture_result['mode']
            
            # Get current color
            current_color = gesture_recognizer.get_current_color_bgr()
            
            # Handle drawing based on mode
            if mode == 'draw' and finger_pos:
                x, y = finger_pos
                
                if self.prev_point is None:
                    canvas.start_drawing(x, y, current_color, brush_thickness, mode)
                else:
                    canvas.continue_drawing(x, y, current_color, brush_thickness, mode)
                
                self.prev_point = (x, y)
                
                # Visual feedback
                cv2.circle(frame, (x, y), 10, current_color, -1)
            
            elif mode == 'erase' and finger_pos:
                x, y = finger_pos
                
                if self.prev_point is None:
                    canvas.start_drawing(x, y, (0, 0, 0), config.ERASER_THICKNESS, mode)
                else:
                    canvas.continue_drawing(x, y, (0, 0, 0), config.ERASER_THICKNESS, mode)
                
                self.prev_point = (x, y)
                
                # Visual feedback
                cv2.circle(frame, (x, y), config.ERASER_THICKNESS//2, (100, 100, 100), 2)
            
            else:
                # Stop drawing
                if self.prev_point is not None:
                    canvas.stop_drawing()
                self.prev_point = None
                
                # Visual feedback for idle
                if finger_pos:
                    cv2.circle(frame, finger_pos, 10, (0, 255, 0), 2)
            
            # Draw hand skeleton
            frame = hand_tracker.draw_hand_skeleton(frame)
        
        else:
            # No hand detected - stop drawing
            if self.prev_point is not None:
                canvas.stop_drawing()
            self.prev_point = None
        
        # Combine frame and canvas
        canvas_img = canvas.get_canvas()
        result = cv2.addWeighted(frame, 0.5, canvas_img, 0.5, 0)
        
        # Draw UI
        self._draw_ui(result, gesture_recognizer, canvas, brush_thickness)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, config.FRAME_ENCODE_QUALITY])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send frame to client
        self.socketio.emit('video_frame', {'frame': frame_base64})
        
        return True
    
    def _draw_ui(self, frame, gesture_recognizer, canvas, brush_thickness):
        """Draw UI elements on frame"""
        h, w = frame.shape[:2]
        
        # Color Palette
        palette_y = config.UI_COLOR_PALETTE_Y
        palette_x = config.UI_COLOR_PALETTE_X
        
        for i, color_name in enumerate(config.COLOR_ORDER):
            x_pos = palette_x + (i * config.UI_BUTTON_GAP)
            color_bgr = config.COLORS[color_name]
            
            # Draw color box
            cv2.rectangle(frame, 
                         (x_pos, palette_y), 
                         (x_pos + config.UI_BUTTON_SIZE, palette_y + config.UI_BUTTON_SIZE), 
                         color_bgr, -1)
            cv2.rectangle(frame, 
                         (x_pos, palette_y), 
                         (x_pos + config.UI_BUTTON_SIZE, palette_y + config.UI_BUTTON_SIZE), 
                         (255, 255, 255), 2)
            
            # Highlight current color
            if color_name == gesture_recognizer.get_current_color_name():
                cv2.rectangle(frame, 
                             (x_pos - 3, palette_y - 3), 
                             (x_pos + config.UI_BUTTON_SIZE + 3, palette_y + config.UI_BUTTON_SIZE + 3), 
                             (0, 255, 0), 3)
        
        # Status text
        status_y = 100
        mode_text = gesture_recognizer.get_mode_display_text()
        color_text = gesture_recognizer.get_current_color_name().upper()
        
        cv2.putText(frame, f"Mode: {mode_text}", 
                   (palette_x, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Color: {color_text}", 
                   (palette_x, status_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Brush: {brush_thickness}px", 
                   (palette_x, status_y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Undo/Redo status
        undo_status = "✓" if canvas.can_undo() else "✗"
        redo_status = "✓" if canvas.can_redo() else "✗"
        cv2.putText(frame, f"Undo: {undo_status} | Redo: {redo_status}", 
                   (palette_x, status_y + 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
