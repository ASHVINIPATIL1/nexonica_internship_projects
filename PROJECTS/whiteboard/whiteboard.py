import cv2
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1180)  # Width
cap.set(4, 620)   # Height

# Create a blank canvas for drawing
canvas = None

# Drawing settings
draw_color = (0, 0, 255)  # Red (BGR format)
brush_thickness = 5
eraser_thickness = 50

# Color ranges for detection (HSV format)
# You can use your finger with a colored cap or marker
colors = {
    'red': {
        'lower': np.array([0, 120, 70]),
        'upper': np.array([10, 255, 255]),
        'bgr': (0, 0, 255)
    },
    'blue': {
        'lower': np.array([100, 150, 0]),
        'upper': np.array([140, 255, 255]),
        'bgr': (255, 0, 0)
    },
    'green': {
        'lower': np.array([40, 70, 80]),
        'upper': np.array([80, 255, 255]),
        'bgr': (0, 255, 0)
    },
    'yellow': {
        'lower': np.array([20, 100, 100]),
        'upper': np.array([30, 255, 255]),
        'bgr': (0, 255, 255)
    }
}

# Previous point for drawing lines
prev_x, prev_y = 0, 0

print("=" * 60)
print("🎨 VIRTUAL WHITEBOARD - CONTROLS")
print("=" * 60)
print("Keys:")
print("  'r' - Red pen")
print("  'b' - Blue pen")
print("  'g' - Green pen")
print("  'y' - Yellow pen")
print("  'e' - Eraser")
print("  'c' - Clear canvas")
print("  '+' - Increase brush size")
print("  '-' - Decrease brush size")
print("  'q' - Quit")
print("=" * 60)
print("\nHold a RED colored object in front of camera to draw!")
print("(You can use red marker cap, red cloth, or anything red)\n")

# Current selected color
current_color = 'red'

while True:
    # Read frame from webcam
    success, frame = cap.read()
    if not success:
        break
    
    # Flip frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)
    
    # Initialize canvas on first frame
    if canvas is None:
        canvas = np.zeros_like(frame)
    
    # Convert frame to HSV for color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Detect the selected color
    lower = colors[current_color]['lower']
    upper = colors[current_color]['upper']
    mask = cv2.inRange(hsv, lower, upper)
    
    # Clean up the mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw on canvas if color is detected
    if len(contours) > 0:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get the center point
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        
        # Only draw if the detected object is big enough
        if radius > 10:
            # Convert to integer
            center = (int(x), int(y))
            
            # Draw a circle to show detected point
            cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            # Draw line from previous point to current point
            if prev_x != 0 and prev_y != 0:
                if current_color == 'eraser':
                    cv2.line(canvas, (prev_x, prev_y), center, (0, 0, 0), eraser_thickness)
                else:
                    cv2.line(canvas, (prev_x, prev_y), center, draw_color, brush_thickness)
            
            # Update previous point
            prev_x, prev_y = center
    else:
        # Reset previous point when color is not detected
        prev_x, prev_y = 0, 0
    
    # Combine frame and canvas
    result = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)
    
    # Add UI elements
    # Draw color palette
    palette_y = 20
    palette_x = 20
    for i, (color_name, color_data) in enumerate(colors.items()):
        x_pos = palette_x + (i * 60)
        cv2.rectangle(result, (x_pos, palette_y), (x_pos + 50, palette_y + 50), color_data['bgr'], -1)
        cv2.rectangle(result, (x_pos, palette_y), (x_pos + 50, palette_y + 50), (255, 255, 255), 2)
        
        # Highlight selected color
        if color_name == current_color:
            cv2.rectangle(result, (x_pos - 3, palette_y - 3), (x_pos + 53, palette_y + 53), (255, 255, 255), 3)
    
    # Draw eraser button
    eraser_x = palette_x + (len(colors) * 60)
    cv2.rectangle(result, (eraser_x, palette_y), (eraser_x + 50, palette_y + 50), (50, 50, 50), -1)
    cv2.putText(result, "E", (eraser_x + 15, palette_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if current_color == 'eraser':
        cv2.rectangle(result, (eraser_x - 3, palette_y - 3), (eraser_x + 53, palette_y + 53), (255, 255, 255), 3)
    
    # Draw clear button
    clear_x = eraser_x + 60
    cv2.rectangle(result, (clear_x, palette_y), (clear_x + 50, palette_y + 50), (200, 200, 200), -1)
    cv2.putText(result, "C", (clear_x + 15, palette_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Display brush size
    cv2.putText(result, f"Brush: {brush_thickness}px", (palette_x, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Display instructions
    cv2.putText(result, "Hold RED object to draw | Press 'q' to quit", 
                (palette_x, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Show the result
    cv2.imshow("Virtual Whiteboard", result)
    
    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('r'):
        current_color = 'red'
        draw_color = colors['red']['bgr']
        print("🔴 Selected: Red")
    elif key == ord('b'):
        current_color = 'blue'
        draw_color = colors['blue']['bgr']
        print("🔵 Selected: Blue")
    elif key == ord('g'):
        current_color = 'green'
        draw_color = colors['green']['bgr']
        print("🟢 Selected: Green")
    elif key == ord('y'):
        current_color = 'yellow'
        draw_color = colors['yellow']['bgr']
        print("🟡 Selected: Yellow")
    elif key == ord('e'):
        current_color = 'eraser'
        print("🧹 Selected: Eraser")
    elif key == ord('c'):
        canvas = np.zeros_like(frame)
        print("🗑️ Canvas cleared!")
    elif key == ord('+') or key == ord('='):
        brush_thickness = min(brush_thickness + 2, 30)
        print(f"📏 Brush size: {brush_thickness}px")
    elif key == ord('-') or key == ord('_'):
        brush_thickness = max(brush_thickness - 2, 2)
        print(f"📏 Brush size: {brush_thickness}px")

# Release resources
cap.release()
cv2.destroyAllWindows()

print("\n✅ Whiteboard closed. Thank you!")