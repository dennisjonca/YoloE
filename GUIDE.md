# YOLOv8 Webcam Inference - Quick Start Guide

## Overview
This application provides real-time object detection and tracking using YOLOv8 on webcam video streams. It features a modern web interface with live bounding boxes and tracking IDs.

## Architecture

### Backend (app.py)
- **Framework**: Flask web server
- **Model**: YOLOv8n (nano version for fast inference)
- **Key Features**:
  - Real-time object tracking using YOLOv8's `track()` method
  - Processes base64-encoded video frames
  - Returns bounding box coordinates, class labels, confidence scores, and track IDs
  - CORS enabled for cross-origin requests

### Frontend (templates/index.html)
- **Technology**: Pure JavaScript with HTML5 Canvas
- **Key Features**:
  - WebRTC webcam access via `getUserMedia` API
  - Captures frames at video frame rate
  - Sends frames to backend for processing
  - Draws bounding boxes and labels on canvas overlay
  - Real-time statistics: FPS, object count, tracked objects
  - Beautiful gradient UI with responsive design

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/dennisjonca/YoloE.git
cd YoloE
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0 (web framework)
- Flask-CORS 4.0.0 (CORS support)
- Ultralytics 8.1.0 (YOLOv8 implementation)
- OpenCV-Python 4.9.0.80 (image processing)
- NumPy 1.26.4 (numerical operations)
- Pillow 10.2.0 (image handling)
- PyTorch 2.5.1 (deep learning framework)
- TorchVision 0.20.1 (vision utilities)
- LAPX 0.5.2+ (tracking algorithms)

The YOLOv8n model (~6.3MB) will be automatically downloaded on first run.

## Usage

### Starting the Server

**Option 1**: Use the start script
```bash
./start.sh
```

**Option 2**: Run directly with Python
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Click the "Start Camera" button
3. Grant camera permissions when prompted
4. The application will:
   - Access your webcam
   - Process frames in real-time using YOLOv8
   - Display bounding boxes around detected objects
   - Show persistent tracking IDs for objects
   - Update live statistics (FPS, object count, tracked objects)

### Controls

- **Start Camera**: Begin webcam capture and detection
- **Stop Camera**: Stop webcam and clear detections

### Understanding the Display

- **Bounding Boxes**: Colored rectangles around detected objects
- **Labels**: Show "ID:X ClassName Confidence%" format
  - Track ID: Persistent ID for tracked objects
  - Class Name: Object type (e.g., person, car, cat)
  - Confidence: Detection confidence percentage
- **Statistics**:
  - FPS: Frames processed per second
  - Objects Detected: Current number of detected objects
  - Tracked Objects: Number of unique tracked objects

## API Endpoints

### GET /
Serves the main HTML interface

### POST /process_frame
Processes a single video frame

**Request**:
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response**:
```json
{
  "success": true,
  "detections": [
    {
      "x1": 100.0,
      "y1": 150.0,
      "x2": 300.0,
      "y2": 400.0,
      "confidence": 0.95,
      "class": "person",
      "track_id": 1
    }
  ]
}
```

### GET /health
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "model": "yolov8n"
}
```

## Testing

### Run All Tests
```bash
python test_app.py
```

This tests:
- Flask and dependency imports
- YOLOv8 model loading
- Inference on dummy images

### Test API Endpoint
```bash
python test_endpoint.py
```

This tests:
- The /process_frame endpoint with a test image
- Verifies detection results

## Customization

### Using a Different YOLOv8 Model

Edit `app.py` and change the model:
```python
# Options: yolov8n.pt (nano), yolov8s.pt (small), 
#          yolov8m.pt (medium), yolov8l.pt (large), yolov8x.pt (extra-large)
model = YOLO('yolov8s.pt')  # Use small model for better accuracy
```

### Adjusting Video Quality

Edit `templates/index.html` in the `startCamera()` function:
```javascript
stream = await navigator.mediaDevices.getUserMedia({ 
    video: { 
        width: { ideal: 1920 },  // Change resolution
        height: { ideal: 1080 }
    } 
});
```

### Changing Detection Threshold

Add confidence threshold in `app.py`:
```python
results = model.track(frame, persist=True, verbose=False, conf=0.5)  # 50% confidence
```

## Browser Compatibility

- ✓ Chrome/Chromium 53+
- ✓ Firefox 36+
- ✓ Edge 12+
- ✓ Safari 11+
- ✓ Opera 40+

All modern browsers with WebRTC support should work.

## Performance Tips

1. **Lighting**: Good lighting improves detection accuracy
2. **Camera Position**: Position camera to clearly see objects
3. **Model Selection**: 
   - yolov8n: Fastest, lower accuracy
   - yolov8x: Slowest, highest accuracy
4. **Resolution**: Lower resolution = faster processing
5. **Hardware**: GPU acceleration significantly improves speed

## Troubleshooting

### Camera Access Denied
- Check browser permissions
- Ensure HTTPS or localhost (required for webcam access)
- Try different browser

### Slow Performance
- Use smaller model (yolov8n)
- Reduce video resolution
- Close other applications
- Check CPU/GPU usage

### Model Download Fails
- Check internet connection
- Manually download from: https://github.com/ultralytics/assets/releases/
- Place .pt file in project directory

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

## Security Notes

- The application uses `weights_only=False` for PyTorch model loading
- Only use YOLOv8 models from trusted sources (official Ultralytics repository)
- For production, use HTTPS and proper authentication
- Consider rate limiting for the /process_frame endpoint

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Check the Ultralytics documentation: https://docs.ultralytics.com/
- Review Flask documentation: https://flask.palletsprojects.com/

## Credits

- **YOLOv8**: Ultralytics (https://github.com/ultralytics/ultralytics)
- **Flask**: Pallets Projects (https://palletsprojects.com/p/flask/)
- **Icons/Emoji**: Unicode Consortium
