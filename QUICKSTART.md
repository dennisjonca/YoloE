# Quick Start Guide

## What This Application Does

This is a real-time object detection system that:
1. Captures video from an external webcam using OpenCV
2. Runs YOLOv8 object detection on each frame
3. Streams the annotated video to a web browser via WebSocket
4. Displays detection results with confidence scores

## How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `ultralytics` - YOLOv8 model
- `opencv-python` - Webcam capture
- `websockets` - WebSocket server
- `numpy` - Array operations

### Step 2: Start the Backend Server
```bash
python backend.py
```

The server will:
- Download YOLOv8n model on first run (if not already downloaded)
- Open webcam at index 0 (change in backend.py if needed)
- Start WebSocket server on port 8765
- Begin streaming frames to connected clients

### Step 3: Open the Web Interface

Option A - Direct file access:
- Simply open `index.html` in your web browser

Option B - Local server (recommended):
```bash
python -m http.server 8080
```
Then navigate to `http://localhost:8080`

## Customization

### Change Camera Source
Edit `backend.py` line 10:
```python
camera_index=0  # Change to 1, 2, etc. for other cameras
```

### Change YOLO Model
Edit `backend.py` line 10:
```python
model_path="yolov8n.pt"  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
```
(n=nano, s=small, m=medium, l=large, x=xlarge)

### Change WebSocket Port
Edit `backend.py` line 69 and `app.js` line 24:
```python
# backend.py
port=8765  # Change to desired port

# app.js
const wsUrl = `ws://${window.location.hostname}:8765`;  # Match port here
```

## Architecture

```
┌─────────────────┐
│   External      │
│   Webcam        │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Python Backend │
│  (backend.py)   │
│                 │
│  - OpenCV       │
│  - YOLOv8       │
│  - WebSocket    │
└────────┬────────┘
         │
         │ WebSocket (port 8765)
         │ JSON: {frame: base64, detections: [...]}
         │
         v
┌─────────────────┐
│  Web Frontend   │
│  (index.html)   │
│                 │
│  - WebSocket    │
│  - Image Display│
│  - Stats UI     │
└─────────────────┘
```

## Troubleshooting

**Camera not opening:**
- Check camera index (try 0, 1, 2)
- Ensure camera is not in use by another application
- Check permissions

**WebSocket connection fails:**
- Verify backend is running
- Check firewall settings
- Ensure port 8765 is available

**Low FPS:**
- Use lighter model (yolov8n.pt)
- Reduce frame quality in backend.py (JPEG quality parameter)
- Use better hardware (GPU if available)
