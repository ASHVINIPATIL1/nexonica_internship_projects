# 🚀 Flask Backend with WebSocket - Setup Guide

## ✅ Your Backend is READY!

The Flask backend with WebSocket support is already complete and includes:

- ✅ Flask web server
- ✅ SocketIO for WebSocket communication
- ✅ CORS enabled for React frontend
- ✅ Real-time video streaming
- ✅ Hand tracking & gesture recognition
- ✅ REST API endpoints
- ✅ Canvas management

---

## 📦 Installation Steps

### **STEP 1: Install Python Dependencies**

Navigate to your backend folder:

```bash
cd "C:\Users\acer\OneDrive\Desktop\Nexonica internship\FINALPROJECT\backend"
```

Install all required packages:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `flask` - Web framework
- `flask-socketio` - WebSocket support
- `flask-cors` - CORS headers
- `opencv-python` - Computer vision
- `mediapipe` - Hand tracking
- `numpy` - Array operations

---

### **STEP 2: Run the Backend**

```bash
python app.py
```

You should see:

```
============================================================
🎨 AI WHITEBOARD BACKEND
============================================================
📡 Server: http://localhost:5000
🔌 WebSocket: ws://localhost:5000
📚 API Docs: http://localhost:5000/api/config
============================================================

✅ Backend ready! Waiting for frontend connection...

 * Running on http://0.0.0.0:5000
```

**Keep this terminal running!**

---

## 🔌 WebSocket Events

The backend listens for these WebSocket events from the frontend:

### **Client → Server:**

1. **`connect`** - Client connects to server
   ```javascript
   socket.on('connect', () => {
     console.log('Connected to backend');
   });
   ```

2. **`start_video`** - Start camera and video streaming
   ```javascript
   socket.emit('start_video');
   ```

3. **`stop_video`** - Stop camera and video streaming
   ```javascript
   socket.emit('stop_video');
   ```

---

### **Server → Client:**

1. **`connection_response`** - Confirms connection
   ```javascript
   {
     status: 'connected'
   }
   ```

2. **`video_frame`** - Sends video frame (30 FPS)
   ```javascript
   {
     frame: 'base64_encoded_jpeg_image'
   }
   ```

3. **`video_started`** - Video streaming began
   ```javascript
   {
     status: 'streaming'
   }
   ```

4. **`video_stopped`** - Video streaming stopped
   ```javascript
   {
     status: 'stopped'
   }
   ```

---

## 🌐 REST API Endpoints

All endpoints are prefixed with `/api`:

### **GET Endpoints:**

#### **`GET /api/status`**
Get current whiteboard status

**Response:**
```json
{
  "mode": "DRAWING",
  "color": "red",
  "brush_size": 5,
  "can_undo": true,
  "can_redo": false,
  "hand_detected": true
}
```

---

#### **`GET /api/colors`**
Get available colors

**Response:**
```json
{
  "colors": ["red", "blue", "green", "yellow", "purple", "white"],
  "current": "red"
}
```

---

#### **`GET /api/config`**
Get whiteboard configuration

**Response:**
```json
{
  "camera_width": 640,
  "camera_height": 480,
  "brush_min": 2,
  "brush_max": 30,
  "brush_default": 5,
  "colors": ["red", "blue", "green", "yellow", "purple", "white"],
  "max_history": 10
}
```

---

### **POST Endpoints:**

#### **`POST /api/clear`**
Clear the canvas

**Response:**
```json
{
  "success": true,
  "message": "Canvas cleared"
}
```

---

#### **`POST /api/undo`**
Undo last stroke

**Response:**
```json
{
  "success": true
}
```

---

#### **`POST /api/redo`**
Redo last undone stroke

**Response:**
```json
{
  "success": true
}
```

---

#### **`POST /api/perfect-shape`**
Apply shape recognition to last stroke

**Response:**
```json
{
  "success": true,
  "message": "Shape converted"
}
```

---

#### **`POST /api/change-color`**
Change drawing color

**Request Body:**
```json
{
  "color": "blue"
}
```

**Response:**
```json
{
  "success": true,
  "color": "blue"
}
```

---

#### **`POST /api/brush-size`**
Change brush size

**Request Body:**
```json
{
  "size": 10
}
```

**Response:**
```json
{
  "success": true,
  "size": 10
}
```

---

#### **`POST /api/save`**
Save canvas as PNG

**Response:**
```json
{
  "success": true,
  "filename": "whiteboard_2026-01-27_10-40-30.png",
  "path": "backend/exports/whiteboard_2026-01-27_10-40-30.png"
}
```

---

## 📁 Backend File Structure

```
backend/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
│
├── api/
│   ├── __init__.py
│   └── routes.py            # REST API endpoints
│
├── core/
│   ├── __init__.py
│   ├── hand_tracker.py      # MediaPipe hand tracking
│   ├── gesture_recognizer.py # Gesture to action mapping
│   ├── canvas.py            # Drawing canvas
│   ├── stroke_manager.py    # Undo/redo management
│   └── shape_recognizer.py  # AI shape recognition
│
├── websocket/
│   ├── __init__.py
│   └── video_handler.py     # Video streaming logic
│
├── utils/
│   ├── __init__.py
│   ├── file_handler.py      # File save/export
│   └── text_recognizer.py  # OCR (optional)
│
└── exports/                 # Saved PNG files go here
```

---

## 🎯 How It Works

### **1. Frontend Connects**
```
React App → WebSocket → Backend
Status: Connected ✅
```

### **2. User Clicks "Start Whiteboard"**
```javascript
socket.emit('start_video');
```
- Backend starts camera
- Creates video streaming thread
- Begins sending frames at 30 FPS

### **3. Video Streaming Loop**
```
1. Capture frame from camera
2. Detect hand using MediaPipe
3. Count fingers
4. Recognize gesture (draw/erase/stop)
5. Update canvas
6. Overlay hand skeleton
7. Encode as JPEG
8. Send to frontend via WebSocket
```

### **4. Frontend Receives Frames**
```javascript
socket.on('video_frame', (data) => {
  // Decode base64 image
  // Display on canvas
});
```

### **5. User Clicks Buttons**
```
Undo Button → POST /api/undo → Backend updates canvas
Next frame sent shows updated canvas
```

---

## 🔧 Troubleshooting

### **Problem: ModuleNotFoundError**

**Solution:**
```bash
pip install -r requirements.txt
```

---

### **Problem: Camera not working**

**Solution:**
1. Make sure webcam is not being used by another app
2. Check if camera index is correct (change 0 to 1 in video_handler.py line 33 if needed)
3. Grant camera permissions

---

### **Problem: Port 5000 already in use**

**Solution:**

Change port in `app.py` (line 124):
```python
socketio.run(
    app,
    host='0.0.0.0',
    port=5001,  # Changed from 5000
    debug=True,
    use_reloader=False
)
```

Also update frontend `.env`:
```
REACT_APP_BACKEND_URL=http://localhost:5001
```

---

### **Problem: CORS errors**

**Solution:**

Backend already has CORS enabled. If issues persist:
1. Make sure backend is running
2. Access frontend from `http://localhost:3000` (not 127.0.0.1)
3. Check browser console for specific error

---

## ✅ Quick Test Checklist

- [ ] `pip install -r requirements.txt` completed
- [ ] `python app.py` runs without errors
- [ ] See "✅ Backend ready!" message
- [ ] Server running on http://localhost:5000
- [ ] Can access http://localhost:5000 in browser (shows JSON)
- [ ] Frontend shows "● Connected"
- [ ] Clicking "Start Whiteboard" activates camera

---

## 🎨 Next Steps

1. ✅ Backend running: `python app.py`
2. ✅ Frontend running: `npm start`
3. ✅ Click "Start Whiteboard" button
4. ✅ Camera activates
5. ✅ Video appears in center of screen
6. ✅ Try drawing with hand gestures!

---

## 📊 Performance Notes

- **FPS:** ~30 frames per second
- **Latency:** <50ms (local network)
- **Frame Size:** ~640x480 pixels
- **JPEG Quality:** 85% (configurable in config.py)

---

## 🚀 You're All Set!

Your Flask backend with WebSocket support is ready to stream video to your React frontend!

**Just run:**
1. `python app.py` (in backend folder)
2. `npm start` (in frontend folder)
3. Click "Start Whiteboard"
4. Draw with your hand! ✋🎨

Enjoy your AI Whiteboard! 🎉
