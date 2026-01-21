"""
Hand Tracking Module
Uses MediaPipe to detect hand landmarks and count fingers
"""

import cv2
import mediapipe as mp
from typing import Optional, Tuple
import config

class HandTracker:
    def __init__(self):
        """Initialize MediaPipe hand tracking"""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize hand detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        
        self.hand_detected = False
        self.landmarks = None
    
    def detect_hand(self, frame):
        """
        Detect hand in frame and extract landmarks
        
        Args:
            frame: BGR image from webcam
            
        Returns:
            bool: True if hand detected, False otherwise
        """
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.hands.process(rgb_frame)
        
        # Check if hand detected
        if results.multi_hand_landmarks:
            self.hand_detected = True
            self.landmarks = results.multi_hand_landmarks[0]
            return True
        else:
            self.hand_detected = False
            self.landmarks = None
            return False
    
    def get_index_finger_tip(self, frame_width: int, frame_height: int) -> Optional[Tuple[int, int]]:
        """
        Get the position of index finger tip
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
            
        Returns:
            (x, y) coordinates or None if no hand detected
        """
        if not self.hand_detected or self.landmarks is None:
            return None
        
        # Index finger tip is landmark 8
        index_tip = self.landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Convert normalized coordinates to pixel coordinates
        x = int(index_tip.x * frame_width)
        y = int(index_tip.y * frame_height)
        
        return (x, y)
    
    def count_fingers(self) -> int:
        """
        Count number of extended fingers (0-5)
        
        Returns:
            int: Number of fingers up
        """
        if not self.hand_detected or self.landmarks is None:
            return 0
        
        fingers = []
        
        # Thumb: Check if tip is to the left of IP joint (for right hand)
        # This is a simplified check - works for most cases
        thumb_tip = self.landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = self.landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        
        if thumb_tip.x < thumb_ip.x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other four fingers: Check if tip is above PIP joint
        finger_tips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        finger_pips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        for tip, pip in zip(finger_tips, finger_pips):
            tip_landmark = self.landmarks.landmark[tip]
            pip_landmark = self.landmarks.landmark[pip]
            
            # If tip is above PIP (lower y value), finger is up
            if tip_landmark.y < pip_landmark.y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return sum(fingers)
    
    def draw_hand_skeleton(self, frame):
        """
        Draw hand skeleton on frame for visualization
        
        Args:
            frame: BGR image to draw on
            
        Returns:
            frame with hand skeleton drawn
        """
        if self.hand_detected and self.landmarks is not None:
            self.mp_drawing.draw_landmarks(
                frame,
                self.landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2)
            )
        
        return frame
    
    def release(self):
        """Release MediaPipe resources"""
        if self.hands:
            self.hands.close()