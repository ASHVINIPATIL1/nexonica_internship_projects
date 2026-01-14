from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time
import math

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Text-to-speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Global variables
current_sign = ""
recognized_text = ""
last_spoken_sign = ""
last_speak_time = 0

def speak_sign(text):
    """Speak the recognized sign"""
    global last_spoken_sign, last_speak_time
    current_time = time.time()
        
    if True:  # Always speak!
        def speak_thread():
            tts_engine.say(text)
            tts_engine.runAndWait()
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def is_finger_extended(tip, pip, mcp):
    """Check if finger is extended"""
    return tip.y < pip.y < mcp.y

def recognize_asl_sign(hand_landmarks):
    """
    Recognize ASL numbers (0-9) and some letters
    Based on finger positions and hand shape
    """
    landmarks = hand_landmarks.landmark
    
    # Key landmarks
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
    
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    middle_mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]
    ring_mcp = landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
    
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]
    
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    
    # Check which fingers are extended
    index_extended = is_finger_extended(index_tip, index_pip, index_mcp)
    middle_extended = is_finger_extended(middle_tip, middle_pip, middle_mcp)
    ring_extended = is_finger_extended(ring_tip, ring_pip, ring_mcp)
    pinky_extended = is_finger_extended(pinky_tip, pinky_pip, pinky_mcp)
    
    # Thumb extension (horizontal check)
    thumb_extended = thumb_tip.x < thumb_mcp.x - 0.05 or thumb_tip.x > thumb_mcp.x + 0.05
    
    # Count extended fingers
    extended_fingers = sum([index_extended, middle_extended, ring_extended, pinky_extended])
    
    # === NUMBERS (0-9) ===
    
    # Number 0 - Closed fist with thumb across
    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        dist_thumb_index = calculate_distance(thumb_tip, index_tip)
        if dist_thumb_index < 0.05:
            return "0 (Zero)"
    
    # Number 1 - Only index finger up
    if index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "1 (One)"
    
    # Number 2 - Index and middle fingers up
    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        return "2 (Two)"
    
    # Number 3 - Index, middle, and ring fingers up
    if index_extended and middle_extended and ring_extended and not pinky_extended:
        return "3 (Three)"
    
    # Number 4 - All four fingers up, thumb folded
    if index_extended and middle_extended and ring_extended and pinky_extended and not thumb_extended:
        return "4 (Four)"
    
    # Number 5 - All fingers extended (open palm)
    if index_extended and middle_extended and ring_extended and pinky_extended and thumb_extended:
        return "5 (Five)"
    
    # Number 6 - Thumb and pinky touching, others extended
    if index_extended and middle_extended and ring_extended and not pinky_extended:
        dist_thumb_pinky = calculate_distance(thumb_tip, pinky_tip)
        if dist_thumb_pinky < 0.08:
            return "6 (Six)"
    
    # Number 7 - Thumb and ring touching, others extended
    if index_extended and middle_extended and not ring_extended and pinky_extended:
        dist_thumb_ring = calculate_distance(thumb_tip, ring_tip)
        if dist_thumb_ring < 0.08:
            return "7 (Seven)"
    
    # Number 8 - Thumb and middle touching, others extended
    if index_extended and not middle_extended and ring_extended and pinky_extended:
        dist_thumb_middle = calculate_distance(thumb_tip, middle_tip)
        if dist_thumb_middle < 0.08:
            return "8 (Eight)"
    
    # Number 9 - Thumb and index touching, others extended
    if not index_extended and middle_extended and ring_extended and pinky_extended:
        dist_thumb_index = calculate_distance(thumb_tip, index_tip)
        if dist_thumb_index < 0.08:
            return "9 (Nine)"
    
    # === LETTERS ===
    
    # Letter A - Closed fist with thumb on side
    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        if thumb_tip.y > thumb_mcp.y:
            return "A (Letter)"
    
    # Letter B - Four fingers up, thumb across palm
    if index_extended and middle_extended and ring_extended and pinky_extended:
        if thumb_tip.x > index_mcp.x - 0.05 and thumb_tip.x < index_mcp.x + 0.05:
            return "B (Letter)"
    
    # Letter C - Curved hand shape
    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        if thumb_tip.x > wrist.x + 0.1:
            return "C (Letter)"
    
    # Letter D - Index up, others touching thumb
    if index_extended and not middle_extended and not ring_extended and not pinky_extended:
        dist_thumb_middle = calculate_distance(thumb_tip, middle_tip)
        if dist_thumb_middle < 0.06:
            return "D (Letter)"
    
    # Letter L - Index and thumb extended at 90 degrees
    if index_extended and not middle_extended and not ring_extended and not pinky_extended:
        if thumb_extended and abs(thumb_tip.y - index_tip.y) > 0.1:
            return "L (Letter)"
    
    # Letter O - All fingers curved touching thumb
    dist_thumb_index = calculate_distance(thumb_tip, index_tip)
    if dist_thumb_index < 0.05 and not index_extended:
        return "O (Letter)"
    
    # Letter V - Index and middle fingers extended and separated (peace sign)
    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        finger_distance = calculate_distance(index_tip, middle_tip)
        if finger_distance > 0.08:
            return "V (Letter)"
    
    # Letter Y - Thumb and pinky extended
    if not index_extended and not middle_extended and not ring_extended and pinky_extended and thumb_extended:
        return "Y (Letter)"
    
    # Thumbs Up - Gesture
    if thumb_tip.y < wrist.y and not index_extended and not middle_extended:
        return "👍 Thumbs Up"
    
    # Thumbs Down - Gesture
    if thumb_tip.y > wrist.y + 0.15 and not index_extended and not middle_extended:
        return "👎 Thumbs Down"
    
    # OK Sign - Thumb and index touching, others extended
    dist_thumb_index = calculate_distance(thumb_tip, index_tip)
    if dist_thumb_index < 0.05 and middle_extended and ring_extended and pinky_extended:
        return "👌 OK Sign"
    
    return "Unknown"

def generate_frames():
    """Generate video frames with hand detection"""
    camera = cv2.VideoCapture(0)
    
    global current_sign, recognized_text
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip frame horizontally
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = hands.process(rgb_frame)
        
        # Draw and recognize
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2)
                )
                
                # Recognize sign
                sign = recognize_asl_sign(hand_landmarks)
                current_sign = sign
                
                # Speak if not unknown
                if sign != "Unknown":
                    speak_sign(sign)
                    if sign not in recognized_text:
                        recognized_text += sign.split()[0] + " "
        else:
            current_sign = "No hand detected"
        
        # Display sign on frame
        cv2.rectangle(frame, (10, 10), (w-10, 70), (0, 0, 0), -1)
        cv2.putText(frame, f"Sign: {current_sign}", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_sign')
def get_sign():
    """Get current recognized sign"""
    return jsonify({
        'sign': current_sign,
        'text': recognized_text
    })

@app.route('/clear_text', methods=['POST'])
def clear_text():
    """Clear recognized text"""
    global recognized_text
    recognized_text = ""
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)