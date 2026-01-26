"""
Configuration settings for AI Whiteboard
All constants and settings in one place
"""

# ============================================
# CAMERA SETTINGS
# ============================================
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# ============================================
# MEDIAPIPE HAND TRACKING SETTINGS
# ============================================
MAX_NUM_HANDS = 1  # Track only one hand
MIN_DETECTION_CONFIDENCE = 0.7  # Higher = more strict detection
MIN_TRACKING_CONFIDENCE = 0.7   # Higher = smoother tracking

# ============================================
# DRAWING SETTINGS
# ============================================
BRUSH_THICKNESS_MIN = 2
BRUSH_THICKNESS_MAX = 30
BRUSH_THICKNESS_DEFAULT = 5

ERASER_THICKNESS = 70

# ============================================
# COLOR PALETTE (BGR format for OpenCV)
# ============================================
COLORS = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'purple': (255, 0, 255),
    'white': (255, 255, 255)
}

# Color cycling order
COLOR_ORDER = ['red', 'blue', 'green', 'yellow', 'purple', 'white']

# ============================================
# GESTURE SETTINGS
# ============================================
# Time to hold gesture before triggering (seconds)
GESTURE_HOLD_TIME = 1.5  # Hold for 1.5 seconds to prevent accidental triggers

# Gesture definitions
GESTURE_DRAW = 1        # 1 finger
GESTURE_STOP = 2        # 2 fingers
GESTURE_NEXT_COLOR = 3  # 3 fingers
GESTURE_PREV_COLOR = 4  # 4 fingers
GESTURE_ERASE = 0       # Fist (0 fingers)
GESTURE_PAUSE = 5       # 5 fingers (all)

# ============================================
# SHAPE RECOGNITION SETTINGS
# ============================================
MIN_POINTS_FOR_SHAPE = 10  # Minimum points needed to recognize a shape

# Circle detection
CIRCLE_STD_THRESHOLD = 0.25  # Stricter: 25% variance allowed (was 30%)

# Line detection
LINE_ERROR_THRESHOLD = 20  # pixels

# Polygon approximation
POLYGON_EPSILON = 0.03  # More accurate (was 0.04)

# Square detection
SQUARE_SIDE_VARIANCE = 0.2  # 20% variance allowed

# ============================================
# UNDO/REDO SETTINGS
# ============================================
MAX_HISTORY_SIZE = 10  # Store last 10 strokes

# ============================================
# FILE EXPORT SETTINGS
# ============================================
EXPORT_FOLDER = "exports"  # Where to save PNG files
EXPORT_FORMAT = "air-canvas_%Y-%m-%d_%H-%M-%S.png"

# ============================================
# UI SETTINGS
# ============================================
UI_COLOR_PALETTE_Y = 20
UI_COLOR_PALETTE_X = 20
UI_BUTTON_SIZE = 50
UI_BUTTON_GAP = 60

STATUS_TEXT_SIZE = 0.6
STATUS_TEXT_COLOR = (255, 255, 255)
STATUS_TEXT_THICKNESS = 2

# ============================================
# WEBSOCKET SETTINGS
# ============================================
FRAME_ENCODE_QUALITY = 80  # JPEG quality (1-100)
