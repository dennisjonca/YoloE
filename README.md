# YoloE
A YoloE project to demonstrate using AI in process.

## Real-time YOLOv8 Webcam Stream with WebSocket

This application provides real-time object detection from a webcam using YOLOv8, streaming the annotated video to a web browser via WebSocket.

### Features
- Real-time object detection using YOLOv8
- WebSocket-based video streaming
- Interactive web interface showing detection results
- FPS counter and detection statistics
- Auto-reconnect functionality

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Python backend:
```bash
python backend.py
```

3. Open the web interface:
   - Open `index.html` in a web browser
   - Or serve it with a simple HTTP server:
```bash
python -m http.server 8080
```
   - Then navigate to `http://localhost:8080`

### Configuration

- **Camera Selection**: Modify `camera_index` in `backend.py` (default is 0 for the first external webcam)
- **WebSocket Port**: Default is 8765, can be changed in `backend.py`
- **Model**: Default is YOLOv8n (nano), can be changed to other variants (s, m, l, x) in `backend.py`

### File Structure
- `backend.py` - Python WebSocket server with YOLOv8 inference
- `index.html` - Web interface for displaying the video stream
- `app.js` - JavaScript client for WebSocket communication
- `requirements.txt` - Python dependencies
