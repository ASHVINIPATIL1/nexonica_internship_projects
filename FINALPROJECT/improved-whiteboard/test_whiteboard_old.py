"""
Test Script - AI Whiteboard
Tests all features implemented so far
"""

import cv2
import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from core.hand_tracker import HandTracker
from core.gesture_recognizer import GestureRecognizer
from core.canvas import Canvas
from utils.file_handler import FileHandler
from utils.text_recognizer import TextRecognizer

def main():
    print("=" * 60)
    print("🎨 AI WHITEBOARD - TEST MODE")
    print("=" * 60)
    print("\nControls:")
    print("  ✌️  1 finger = Draw")
    print("  ✊  Fist = Erase")
    print("  ✋  2 fingers = Stop/Navigate")
    print("  🤟  3 fingers = Next Color")
    print("  🖖  4 fingers = Previous Color")
    print("\nKeyboard:")
    print("  's' = Convert last stroke to perfect shape")
    print("  'a' = Convert last stroke to arrow ➡️")
    print("  't' = Recognize text (OCR) 📝")
    print("  'u' = Undo")
    print("  'r' = Redo")
    print("  'c' = Clear canvas")
    print("  'Ctrl+S' = Save as PNG")
    print("  'q' = Quit")
    print("=" * 60)
    
    # Initialize components
    cap = cv2.VideoCapture(0)
    cap.set(3, config.CAMERA_WIDTH)
    cap.set(4, config.CAMERA_HEIGHT)
    
    hand_tracker = HandTracker()
    gesture_recognizer = GestureRecognizer()
    canvas = Canvas(config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    file_handler = FileHandler()
    text_recognizer = TextRecognizer()
    
    # Drawing state
    prev_x, prev_y = None, None
    brush_thickness = config.BRUSH_THICKNESS_DEFAULT
    
    print("\n✅ Whiteboard ready! Show your hand to the camera.\n")
    
    while True:
        success, frame = cap.read()
        if not success:
            print("❌ Failed to read from camera")
            break
        
        # Flip frame (mirror effect)
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Detect hand
        hand_detected = hand_tracker.detect_hand(frame)
        
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
                
                if prev_x is None:
                    canvas.start_drawing(x, y, current_color, brush_thickness, mode)
                else:
                    canvas.continue_drawing(x, y, current_color, brush_thickness, mode)
                
                prev_x, prev_y = x, y
                
                # Visual feedback
                cv2.circle(frame, (x, y), 10, current_color, -1)
            
            elif mode == 'erase' and finger_pos:
                x, y = finger_pos
                
                if prev_x is None:
                    canvas.start_drawing(x, y, (0, 0, 0), config.ERASER_THICKNESS, mode)
                else:
                    canvas.continue_drawing(x, y, (0, 0, 0), config.ERASER_THICKNESS, mode)
                
                prev_x, prev_y = x, y
                
                # Visual feedback
                cv2.circle(frame, (x, y), config.ERASER_THICKNESS//2, (100, 100, 100), 2)
            
            else:
                # Stop drawing
                if prev_x is not None:
                    canvas.stop_drawing()
                prev_x, prev_y = None, None
                
                # Visual feedback for idle
                if finger_pos:
                    cv2.circle(frame, finger_pos, 10, (0, 255, 0), 2)
            
            # Draw hand skeleton
            frame = hand_tracker.draw_hand_skeleton(frame)
        
        else:
            # No hand detected - stop drawing
            if prev_x is not None:
                canvas.stop_drawing()
            prev_x, prev_y = None, None
        
        # Combine frame and canvas
        canvas_img = canvas.get_canvas()
        result = cv2.addWeighted(frame, 0.5, canvas_img, 0.5, 0)
        
        # Draw UI - Color Palette
        palette_y = config.UI_COLOR_PALETTE_Y
        palette_x = config.UI_COLOR_PALETTE_X
        
        for i, color_name in enumerate(config.COLOR_ORDER):
            x_pos = palette_x + (i * config.UI_BUTTON_GAP)
            color_bgr = config.COLORS[color_name]
            
            # Draw color box
            cv2.rectangle(result, 
                         (x_pos, palette_y), 
                         (x_pos + config.UI_BUTTON_SIZE, palette_y + config.UI_BUTTON_SIZE), 
                         color_bgr, -1)
            cv2.rectangle(result, 
                         (x_pos, palette_y), 
                         (x_pos + config.UI_BUTTON_SIZE, palette_y + config.UI_BUTTON_SIZE), 
                         (255, 255, 255), 2)
            
            # Highlight current color
            if color_name == gesture_recognizer.get_current_color_name():
                cv2.rectangle(result, 
                             (x_pos - 3, palette_y - 3), 
                             (x_pos + config.UI_BUTTON_SIZE + 3, palette_y + config.UI_BUTTON_SIZE + 3), 
                             (0, 255, 0), 3)
        
        # Draw status
        status_y = 100
        mode_text = gesture_recognizer.get_mode_display_text()
        color_text = gesture_recognizer.get_current_color_name().upper()
        
        cv2.putText(result, f"Mode: {mode_text}", 
                   (palette_x, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(result, f"Color: {color_text}", 
                   (palette_x, status_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(result, f"Brush: {brush_thickness}px", 
                   (palette_x, status_y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Undo/Redo status
        undo_text = "YES" if canvas.can_undo() else "NO"
        redo_text = "YES" if canvas.can_redo() else "NO"
        cv2.putText(result, f"Undo: {undo_text} | Redo: {redo_text}", 
                   (palette_x, status_y + 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(result, "Press 's' for shape | 'a' for arrow | 'u' undo | 'r' redo | 'c' clear | 'q' quit", 
                   (palette_x, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show result
        cv2.imshow("AI Whiteboard - Test Mode", result)
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n👋 Quitting...")
            break
        
        elif key == ord('s'):
            print("\n🔍 Applying shape recognition...")
            if canvas.apply_shape_recognition():
                print("✨ Shape converted to perfect geometry!")
            else:
                print("⚠️ Could not recognize shape")
        
        elif key == ord('a'):
            # Convert last stroke to arrow manually
            print("\n➡️ Converting last stroke to arrow...")
            last_stroke = canvas.stroke_manager.get_last_completed_stroke()
            if last_stroke and len(last_stroke.points) >= 2:
                # Create arrow from start to end
                points = np.array(last_stroke.points)
                arrow_info = {
                    'type': 'arrow',
                    'tail': tuple(points[0].astype(int)),
                    'head': tuple(points[-1].astype(int)),
                    'points': points
                }
                
                # Create arrow stroke
                from core.stroke_manager import Stroke
                arrow_stroke = Stroke(last_stroke.color, last_stroke.thickness, 'shape')
                arrow_stroke.shape_info = arrow_info
                arrow_stroke.complete()
                
                # Replace last stroke
                canvas.stroke_manager.replace_last_stroke_with_shape(arrow_stroke)
                canvas._redraw_canvas()
                print("✨ Arrow created!")
            else:
                print("⚠️ Draw a line first, then press 'a'")
        
        elif key == ord('t'):
            # Text recognition
            print("\n📝 Recognizing text from canvas...")
            try:
                # Get ONLY the canvas (not the video overlay)
                canvas_only = canvas.get_canvas()
                
                # Run OCR
                result = text_recognizer.recognize_with_confidence(canvas_only)
                
                if result['text']:
                    print(f"✨ Recognized: '{result['text']}'")
                    print(f"📊 Confidence: {result['confidence']:.1f}%")
                else:
                    print("⚠️ No text recognized. Try writing clearer/bigger.")
                    print("💡 Tip: Use white/yellow color for better recognition")
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Make sure Tesseract is installed:")
                print("   Mac: brew install tesseract")
                print("   Linux: sudo apt-get install tesseract-ocr")
                print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        
        elif key == ord('u'):
            canvas.undo()
        
        elif key == ord('r'):
            canvas.redo()
        
        elif key == ord('c'):
            canvas.clear()
        
        elif key == 19:  # Ctrl+S
            export_path = file_handler.get_export_path()
            if canvas.save_as_png(export_path):
                print(f"💾 Saved to: {export_path}")
        
        elif key == ord('+') or key == ord('='):
            brush_thickness = min(brush_thickness + 2, config.BRUSH_THICKNESS_MAX)
            print(f"📏 Brush size increased: {brush_thickness}px")
        
        elif key == ord('-') or key == ord('_'):
            brush_thickness = max(brush_thickness - 2, config.BRUSH_THICKNESS_MIN)
            print(f"📏 Brush size decreased: {brush_thickness}px")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hand_tracker.release()
    
    print("\n✅ Whiteboard closed. Thank you!")

if __name__ == "__main__":
    main()
