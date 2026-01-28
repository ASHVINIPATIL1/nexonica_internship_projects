"""
Configuration settings for AI Whiteboard - IMPROVED VERSION
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

ERASER_THICKNESS = 50

# ============================================
# BRUSH STYLES (NEW!)
# ============================================
BRUSH_STYLES = {
    'solid': 'solid',      # Normal continuous line
    'dotted': 'dotted',    # Dotted line
    'dashed': 'dashed',    # Dashed line
    'spray': 'spray'       # Spray paint effect
}

BRUSH_STYLE_DEFAULT = 'spray'

# Dotted/Dashed parameters
DOT_SPACING = 10           # Pixels between dots
DASH_LENGTH = 15           # Pixels per dash
DASH_GAP = 10              # Pixels between dashes
SPRAY_RADIUS = 15          # Radius of spray effect
SPRAY_DENSITY = 5          # Number of dots per spray

# ============================================
# COLOR PALETTE (BGR format for OpenCV) - EXPANDED TO 12 COLORS!
# ============================================
COLORS = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'purple': (255, 0, 255),
    'white': (255, 255, 255),
    'orange': (0, 165, 255),      # NEW
    'pink': (203, 192, 255),      # NEW
    'cyan': (255, 255, 0),        # NEW
    'lime': (0, 255, 128),        # NEW
    'brown': (42, 42, 165),       # NEW
    'gray': (128, 128, 128)       # NEW
}

# Color cycling order (12 colors now!)
COLOR_ORDER = ['red', 'blue', 'green', 'yellow', 'purple', 'white', 
               'orange', 'pink', 'cyan', 'lime', 'brown', 'gray']

# ============================================
# BACKGROUND TEMPLATES (NEW!)
# ============================================
BACKGROUNDS = {
    'blank': 'blank',           # Plain black background
    'white': 'white',           # Plain white background
    'grid': 'grid',             # Grid lines
    'dots': 'dots',             # Dotted paper
    'lines': 'lines'            # Ruled lines
}

BACKGROUND_DEFAULT = 'blank'

# Grid/Dots parameters
GRID_SIZE = 50                  # Pixels between grid lines
GRID_COLOR = (40, 40, 40)       # Dark gray
DOT_SIZE = 2                    # Size of dots in dotted background
LINE_SPACING = 40               # Spacing for ruled lines

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
# SHAPE RECOGNITION SETTINGS - MORE SHAPES!
# ============================================
MIN_POINTS_FOR_SHAPE = 10  # Minimum points needed to recognize a shape

# Circle detection
CIRCLE_STD_THRESHOLD = 0.25  # Stricter: 25% variance allowed

# Line detection
LINE_ERROR_THRESHOLD = 20  # pixels

# Polygon approximation
POLYGON_EPSILON = 0.03  # More accurate

# Square detection
SQUARE_SIDE_VARIANCE = 0.2  # 20% variance allowed

# Pentagon detection (NEW!)
PENTAGON_SIDE_VARIANCE = 0.25  # 25% variance allowed

# Hexagon detection (NEW!)
HEXAGON_SIDE_VARIANCE = 0.25  # 25% variance allowed

# Star detection (NEW!)
STAR_INNER_OUTER_RATIO = 0.4   # Ratio of inner to outer radius
STAR_RATIO_VARIANCE = 0.3      # Allowed variance

# ============================================
# FILL TOOL SETTINGS (NEW!)
# ============================================
FILL_TOLERANCE = 30            # Color tolerance for flood fill
FILL_ENABLED = True            # Enable/disable fill tool

# ============================================
# IMAGE IMPORT SETTINGS (NEW!)
# ============================================
IMAGE_IMPORT_ENABLED = True    # Enable/disable image import
IMAGE_MAX_WIDTH = 800          # Max width for imported images
IMAGE_MAX_HEIGHT = 600         # Max height for imported images
IMAGE_OPACITY = 0.7            # Opacity when overlaying image (0-1)

# ============================================
# UNDO/REDO SETTINGS
# ============================================
MAX_HISTORY_SIZE = 10  # Store last 10 strokes

# ============================================
# FILE EXPORT SETTINGS
# ============================================
EXPORT_FOLDER = "exports"  # Where to save PNG files
EXPORT_FORMAT = "whiteboard_%Y-%m-%d_%H-%M-%S.png"

# ============================================
# UI SETTINGS - IMPROVED!
# ============================================
UI_COLOR_PALETTE_Y = 20
UI_COLOR_PALETTE_X = 20
UI_BUTTON_SIZE = 50
UI_BUTTON_GAP = 60

STATUS_TEXT_SIZE = 0.8  # Larger! (was 0.6)
STATUS_TEXT_COLOR = (255, 255, 255)
STATUS_TEXT_THICKNESS = 2
STATUS_FONT = 1  # FONT_HERSHEY_SIMPLEX

# Instructions text (NEW!)
INSTRUCTIONS_TEXT_SIZE = 0.9  # Large, clear instructions
INSTRUCTIONS_TEXT_COLOR = (0, 255, 255)  # Cyan for visibility
INSTRUCTIONS_TEXT_THICKNESS = 2
INSTRUCTIONS_FONT = 1

# ============================================
# KEYBOARD SHORTCUTS - MANY MORE!
# ============================================
KEY_SHORTCUTS = {
    # Direct color selection (1-9)
    '1': ('color', 'red'),
    '2': ('color', 'blue'),
    '3': ('color', 'green'),
    '4': ('color', 'yellow'),
    '5': ('color', 'purple'),
    '6': ('color', 'white'),
    '7': ('color', 'orange'),
    '8': ('color', 'pink'),
    '9': ('color', 'cyan'),
    
    # Brush styles (z, x, v, b)
    'z': ('brush_style', 'solid'),
    'x': ('brush_style', 'dotted'),
    'v': ('brush_style', 'dashed'),
    'b': ('brush_style', 'spray'),
    
    # Backgrounds (n, m, comma, period, slash)
    'n': ('background', 'blank'),
    'm': ('background', 'white'),
    ',': ('background', 'grid'),
    '.': ('background', 'dots'),
    '/': ('background', 'lines'),
    
    # Tools
    'f': ('tool', 'fill'),
    'i': ('tool', 'import_image'),
    
    # Existing
    's': ('action', 'shape'),
    'a': ('action', 'arrow'),
    't': ('action', 'text'),
    'u': ('action', 'undo'),
    'r': ('action', 'redo'),
    'c': ('action', 'clear'),
    'q': ('action', 'quit'),
    '+': ('brush', 'increase'),
    '-': ('brush', 'decrease')
}

# ============================================
# WEBSOCKET SETTINGS
# ============================================
FRAME_ENCODE_QUALITY = 80  # JPEG quality (1-100)
