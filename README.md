# YoloE

A YoloE project to demonstrate using AI in process - Real-time object detection and tracking with YOLOv8 on webcam streams.

## Features

- 🎥 Real-time webcam video streaming
- 🎯 YOLOv8 object detection with tracking
- 📦 Bounding boxes with class labels and confidence scores
- 🔢 Object tracking with persistent IDs
- 📊 Live statistics (FPS, object count, tracked objects)
- 🎨 Beautiful modern UI

## Requirements

- Python 3.8 or higher
- Webcam/Camera access
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dennisjonca/YoloE.git
cd YoloE
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

The YOLOv8n model will be automatically downloaded on first run.

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Click "Start Camera" to begin real-time object detection

4. The application will:
   - Access your webcam
   - Process frames using YOLOv8 track method
   - Display bounding boxes around detected objects
   - Show tracking IDs for persistent objects
   - Display real-time statistics

## How It Works

### Backend (`app.py`)
- Flask web server with CORS support
- YOLOv8 model initialization
- `/process_frame` endpoint that:
  - Receives base64-encoded video frames
  - Runs YOLOv8 tracking inference
  - Returns detection results with bounding boxes and track IDs

### Frontend (`templates/index.html`)
- Webcam access using `getUserMedia` API
- Captures frames from video stream
- Sends frames to backend for processing
- Draws bounding boxes and labels on canvas overlay
- Updates statistics in real-time

## API Endpoints

- `GET /` - Serves the main HTML interface
- `POST /process_frame` - Processes a single frame and returns detections
- `GET /health` - Health check endpoint

## Dependencies

- Flask - Web framework
- Flask-CORS - Cross-origin resource sharing
- Ultralytics - YOLOv8 implementation
- OpenCV - Image processing
- NumPy - Numerical operations
- Pillow - Image handling

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
