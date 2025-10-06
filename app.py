from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import base64
import numpy as np
from ultralytics import YOLO
import json

app = Flask(__name__)
CORS(app)

# Initialize YOLOv8 model
# Using yolov8n.pt (nano version) for faster inference
# The model will be downloaded automatically on first run
model = YOLO('yolov8n.pt')

# Store track history
track_history = {}

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a single frame with YOLOv8 tracking"""
    from flask import request
    
    try:
        # Get the image data from the request
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run YOLOv8 tracking on the frame
        results = model.track(frame, persist=True, verbose=False)
        
        # Extract detection information
        detections = []
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()  # Get box coordinates
                conf = float(boxes.conf[i].cpu().numpy())  # Get confidence
                cls = int(boxes.cls[i].cpu().numpy())  # Get class
                class_name = model.names[cls]
                
                # Get track ID if available
                track_id = None
                if boxes.id is not None:
                    track_id = int(boxes.id[i].cpu().numpy())
                
                detection = {
                    'x1': float(box[0]),
                    'y1': float(box[1]),
                    'x2': float(box[2]),
                    'y2': float(box[3]),
                    'confidence': conf,
                    'class': class_name,
                    'track_id': track_id
                }
                detections.append(detection)
        
        return jsonify({
            'success': True,
            'detections': detections
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model': 'yolov8n'})

if __name__ == '__main__':
    print("Starting YOLOv8 Webcam Inference Server...")
    print("Server will run on http://localhost:5000")
    print("Open this URL in your browser to start the webcam stream")
    app.run(debug=True, host='0.0.0.0', port=5000)
