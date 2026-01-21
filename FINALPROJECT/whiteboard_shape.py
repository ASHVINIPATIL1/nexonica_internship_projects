import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Create blank canvas
canvas = None

# Drawing settings
draw_color = (0, 0, 255)  # Red
brush_thickness = 5
eraser_thickness = 50

# Shape recognition variables
shape_buffer = []  # Store points for shape recognition
shape_recognition_enabled = True

# Colors
colors = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'purple': (255, 0, 255),
    'white': (255, 255, 255)
}

current_color = 'red'
eraser_mode = False
drawing_mode = False

# Previous point
prev_x, prev_y = None, None

print("=" * 60)
print("🎨 HAND TRACKING WHITEBOARD - AI ENHANCED")
print("=" * 60)
print("How to use:")
print("  ✌️  Index finger UP only = DRAW")
print("  ✋  All fingers UP = STOP drawing (move without drawing)")
print("  ✊  Fist = ERASE")
print("\nKeyboard controls:")
print("  'r' - Red   | 'b' - Blue  | 'g' - Green")
print("  'y' - Yellow | 'p' - Purple | 'w' - White")
print("  's' - Convert last shape to perfect shape ✨")
print("  'c' - Clear canvas | 'q' - Quit")
print("  '+' - Increase size | '-' - Decrease size")
print("=" * 60)
print("\n💡 Draw a circle, rectangle, triangle, or line, then press 's'!")
print("=" * 60)

def count_fingers(hand_landmarks):
    """Count number of extended fingers"""
    fingers = []
    
    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    
    # Other fingers
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return sum(fingers)


def recognize_shape(points):
    """Recognize what shape was drawn"""
    if len(points) < 10:
        return None
    
    points = np.array(points)
    
    # 1. Check if it's a CIRCLE
    center = points.mean(axis=0)
    distances = np.linalg.norm(points - center, axis=1)
    avg_distance = distances.mean()
    std_distance = distances.std()
    
    if std_distance < avg_distance * 0.3:  # Pretty circular
        return {
            'type': 'circle',
            'center': tuple(center.astype(int)),
            'radius': int(avg_distance)
        }
    
    # 2. Check if it's a LINE
    if len(points) > 2:
        x = points[:, 0]
        y = points[:, 1]
        
        try:
            slope, intercept = np.polyfit(x, y, 1)
            predicted_y = slope * x + intercept
            error = np.abs(y - predicted_y).mean()
            
            if error < 20:  # Pretty straight
                return {
                    'type': 'line',
                    'start': tuple(points[0].astype(int)),
                    'end': tuple(points[-1].astype(int))
                }
        except:
            pass
    
    # 3. Check for RECTANGLE or TRIANGLE
    hull = cv2.convexHull(points)
    epsilon = 0.04 * cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, epsilon, True)
    
    if len(approx) == 4:
        return {
            'type': 'rectangle',
            'points': approx.reshape(-1, 2).astype(int)
        }
    
    if len(approx) == 3:
        return {
            'type': 'triangle',
            'points': approx.reshape(-1, 2).astype(int)
        }
    
    # 4. Check for SQUARE (special rectangle)
    if len(approx) == 4:
        # Calculate side lengths
        sides = []
        for i in range(4):
            p1 = approx[i][0]
            p2 = approx[(i + 1) % 4][0]
            length = np.linalg.norm(p1 - p2)
            sides.append(length)
        
        # Check if all sides are roughly equal
        sides = np.array(sides)
        if sides.std() < sides.mean() * 0.2:
            return {
                'type': 'square',
                'points': approx.reshape(-1, 2).astype(int)
            }
    
    return None


def draw_perfect_shape(canvas, shape_info, color, thickness):
    """Draw the recognized shape cleanly"""
    if shape_info['type'] == 'circle':
        cv2.circle(canvas, shape_info['center'], shape_info['radius'], color, thickness)
        print(f"✨ Perfect CIRCLE - Center: {shape_info['center']}, Radius: {shape_info['radius']}")
    
    elif shape_info['type'] == 'line':
        cv2.line(canvas, shape_info['start'], shape_info['end'], color, thickness)
        print(f"✨ Perfect LINE - From {shape_info['start']} to {shape_info['end']}")
    
    elif shape_info['type'] == 'rectangle':
        pts = shape_info['points'].reshape((-1, 1, 2))
        cv2.polylines(canvas, [pts], True, color, thickness)
        print("✨ Perfect RECTANGLE")
    
    elif shape_info['type'] == 'square':
        pts = shape_info['points'].reshape((-1, 1, 2))
        cv2.polylines(canvas, [pts], True, color, thickness)
        print("✨ Perfect SQUARE")
    
    elif shape_info['type'] == 'triangle':
        pts = shape_info['points'].reshape((-1, 1, 2))
        cv2.polylines(canvas, [pts], True, color, thickness)
        print("✨ Perfect TRIANGLE")


def clear_region(canvas, points):
    """Clear the rough drawing from canvas"""
    if len(points) < 2:
        return
    
    points = np.array(points)
    x_min, y_min = points.min(axis=0) - 30
    x_max, y_max = points.max(axis=0) + 30
    
    # Ensure within bounds
    x_min = max(0, int(x_min))
    y_min = max(0, int(y_min))
    x_max = min(canvas.shape[1], int(x_max))
    y_max = min(canvas.shape[0], int(y_max))
    
    # Clear that region
    canvas[y_min:y_max, x_min:x_max] = 0


while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Initialize canvas
    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    # Process hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand skeleton
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2)
            )
            
            # Get index finger tip position
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)
            
            # Count fingers
            fingers_up = count_fingers(hand_landmarks)
            
            # Determine mode based on fingers
            if fingers_up == 1:  # Only index finger up = DRAW
                drawing_mode = True
                eraser_mode = False
                cv2.circle(frame, (x, y), 10, draw_color, -1)
            elif fingers_up == 0:  # Fist = ERASE
                drawing_mode = True
                eraser_mode = True
                cv2.circle(frame, (x, y), eraser_thickness//2, (100, 100, 100), 2)
            else:  # Multiple fingers = STOP
                drawing_mode = False
                eraser_mode = False
                cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)
            
            # Draw on canvas
            if drawing_mode:
                if prev_x is not None and prev_y is not None:
                    if eraser_mode:
                        cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 0), eraser_thickness)
                        # Don't add to shape buffer when erasing
                    else:
                        cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, brush_thickness)
                        # Add to shape buffer for recognition
                        shape_buffer.append((x, y))
                
                prev_x, prev_y = x, y
            else:
                prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None
    
    # Combine frame and canvas
    result = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)
    
    # Draw UI - Color Palette
    palette_y = 20
    palette_x = 20
    i = 0
    for color_name, color_bgr in colors.items():
        x_pos = palette_x + (i * 60)
        cv2.rectangle(result, (x_pos, palette_y), (x_pos + 50, palette_y + 50), color_bgr, -1)
        cv2.rectangle(result, (x_pos, palette_y), (x_pos + 50, palette_y + 50), (255, 255, 255), 2)
        
        if color_name == current_color:
            cv2.rectangle(result, (x_pos - 3, palette_y - 3), (x_pos + 53, palette_y + 53), (0, 255, 0), 3)
        i += 1
    
    # Draw status
    status_y = 100
    cv2.putText(result, f"Brush: {brush_thickness}px", (palette_x, status_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    mode_text = "DRAWING" if drawing_mode and not eraser_mode else "ERASING" if eraser_mode else "IDLE"
    mode_color = (0, 0, 255) if drawing_mode and not eraser_mode else (0, 165, 255) if eraser_mode else (0, 255, 0)
    cv2.putText(result, f"Mode: {mode_text}", (palette_x, status_y + 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
    
    # Show shape buffer status
    if len(shape_buffer) > 10:
        cv2.putText(result, f"Shape ready! Press 's' to perfect it", (palette_x, status_y + 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Instructions
    cv2.putText(result, "1 finger=Draw | Fist=Erase | Many=Stop | 's'=Perfect shape", 
                (palette_x, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Show result
    cv2.imshow("Hand Tracking Whiteboard", result)
    
    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('r'):
        current_color = 'red'
        draw_color = colors['red']
        print("🔴 Color: RED")
    elif key == ord('b'):
        current_color = 'blue'
        draw_color = colors['blue']
        print("🔵 Color: BLUE")
    elif key == ord('g'):
        current_color = 'green'
        draw_color = colors['green']
        print("🟢 Color: GREEN")
    elif key == ord('y'):
        current_color = 'yellow'
        draw_color = colors['yellow']
        print("🟡 Color: YELLOW")
    elif key == ord('p'):
        current_color = 'purple'
        draw_color = colors['purple']
        print("🟣 Color: PURPLE")
    elif key == ord('w'):
        current_color = 'white'
        draw_color = colors['white']
        print("⚪ Color: WHITE")
    elif key == ord('c'):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        shape_buffer = []
        print("🗑️ Canvas cleared!")
    elif key == ord('s'):
        # SHAPE RECOGNITION!
        if len(shape_buffer) > 10:
            print(f"\n🔍 Analyzing shape with {len(shape_buffer)} points...")
            recognized = recognize_shape(shape_buffer)
            
            if recognized:
                # Clear the rough drawing
                clear_region(canvas, shape_buffer)
                # Draw perfect shape
                draw_perfect_shape(canvas, recognized, draw_color, brush_thickness)
                print("=" * 60)
            else:
                print("❌ Could not recognize shape. Try drawing clearer!")
            
            # Clear buffer
            shape_buffer = []
        else:
            print("⚠️ Not enough points. Draw something first!")
    elif key == ord('+') or key == ord('='):
        brush_thickness = min(brush_thickness + 2, 30)
        print(f"📏 Brush size: {brush_thickness}px")
    elif key == ord('-') or key == ord('_'):
        brush_thickness = max(brush_thickness - 2, 2)
        print(f"📏 Brush size: {brush_thickness}px")

cap.release()
cv2.destroyAllWindows()
print("\n✅ Whiteboard closed! Thank you!")