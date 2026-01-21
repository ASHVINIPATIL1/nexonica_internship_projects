"""
Main Flask Application
AI-Enhanced Hand Tracking Whiteboard Backend
"""

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time

import config
from core.hand_tracker import HandTracker
from core.gesture_recognizer import GestureRecognizer
from core.canvas import Canvas
from utils.file_handler import FileHandler
from api.routes import api_bp, init_routes
from websocket.video_handler import VideoHandler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production
CORS(app)  # Enable CORS for React frontend

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global whiteboard state
whiteboard_state = {
    'hand_tracker': HandTracker(),
    'gesture_recognizer': GestureRecognizer(),
    'canvas': Canvas(config.CAMERA_WIDTH, config.CAMERA_HEIGHT),
    'file_handler': FileHandler(),
    'brush_thickness': config.BRUSH_THICKNESS_DEFAULT,
    'hand_detected': False
}

# Initialize video handler
video_handler = VideoHandler(socketio, whiteboard_state)

# Initialize API routes with state
init_routes(whiteboard_state)
app.register_blueprint(api_bp)

# ============================================
# WEBSOCKET EVENTS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('✅ Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('❌ Client disconnected')

@socketio.on('start_video')
def handle_start_video():
    """Start video streaming"""
    print('📹 Starting video stream...')
    video_handler.start_camera()
    
    # Start video streaming thread
    def stream_video():
        while video_handler.running:
            video_handler.process_frame()
            time.sleep(0.033)  # ~30 FPS
    
    thread = threading.Thread(target=stream_video)
    thread.daemon = True
    thread.start()
    
    emit('video_started', {'status': 'streaming'})

@socketio.on('stop_video')
def handle_stop_video():
    """Stop video streaming"""
    print('📹 Stopping video stream...')
    video_handler.stop_camera()
    emit('video_stopped', {'status': 'stopped'})

# ============================================
# HTTP ROUTES
# ============================================

@app.route('/')
def index():
    """Root endpoint"""
    return {
        'name': 'AI Whiteboard Backend',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'api': '/api/*',
            'websocket': 'ws://localhost:5000'
        }
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 AI WHITEBOARD BACKEND")
    print("=" * 60)
    print(f"📡 Server: http://localhost:5000")
    print(f"🔌 WebSocket: ws://localhost:5000")
    print(f"📚 API Docs: http://localhost:5000/api/config")
    print("=" * 60)
    print("\n✅ Backend ready! Waiting for frontend connection...\n")
    
    # Run Flask app with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid issues with camera
    )
