from flask import Flask, Response, request
from ultralytics import YOLOE
import cv2, threading, time, platform, os
import numpy as np
import torch
import traceback
from camera_manager import CameraManager

app = Flask(__name__)

# -------------------------------
# 🔧 YOLO Model Initialization
# -------------------------------
# Available model sizes
available_models = ["s", "m", "l"]
current_model = "s"  # Default model size
current_classes = "person, plant"  # Default class prompts

# Detection parameters
current_conf = 0.25  # Default confidence threshold (0.0 - 1.0)
current_iou = 0.45   # Default IoU threshold for NMS (0.0 - 1.0)

def get_hardware_info():
    """Get information about available hardware for inference."""
    import torch
    info = {
        'cpu_count': os.cpu_count(),
        'cuda_available': torch.cuda.is_available(),
        'cuda_device_count': 0,
        'cuda_device_name': None,
        'device_name': 'CPU'
    }
    
    if info['cuda_available']:
        info['cuda_device_count'] = torch.cuda.device_count()
        if info['cuda_device_count'] > 0:
            info['cuda_device_name'] = torch.cuda.get_device_name(0)
            info['device_name'] = f"GPU: {info['cuda_device_name']}"
    
    return info

def load_model(model_size, class_names=None, visual_prompt_data=None):
    """Load YOLO model with the specified size (s, m, or l) and class names or visual prompts.
    
    Returns:
        tuple: (model, success) where success is True if visual prompts were set successfully,
               or True if text prompts were used (no visual prompts requested)
    """
    if class_names is None:
        class_names = ["person", "plant"]
    
    # Define the ONNX model path
    onnx_model_path = f"yoloe-11{model_size}-seg.onnx"
    pt_model_path = f"yoloe-11{model_size}-seg.pt"
    
    visual_prompt_success = True  # Track if visual prompts were set successfully
    
    # Check if ONNX model already exists to avoid re-exporting
    if os.path.exists(onnx_model_path):
        print(f"[INFO] Loading cached ONNX model from {onnx_model_path}")
        loaded_model = YOLOE(onnx_model_path)
        # ONNX models have classes baked in during export, no need to set them again
        print(f"[INFO] Using cached model with classes: {class_names}")
    else:
        print(f"[INFO] ONNX model not found. Exporting from PyTorch model...")
        loaded_model = YOLOE(pt_model_path)
        
        # Set up prompts based on mode
        if visual_prompt_data is not None:
            # Visual prompting mode: use image and bounding boxes
            print(f"[INFO] Setting up visual prompts with {len(visual_prompt_data['boxes'])} boxes")
            # YOLOE visual prompting: extract features from reference image and boxes
            # The model will learn to track objects similar to those in the boxes
            try:
                # Convert numpy arrays to PyTorch tensors
                # Image: Convert from HWC (Height, Width, Channels) to CHW (Channels, Height, Width)
                image_tensor = torch.from_numpy(visual_prompt_data['image']).permute(2, 0, 1).unsqueeze(0).float()
                # Boxes: Convert to tensor with batch dimension (B, N, D) where B=1, N=num_boxes, D=4
                boxes_tensor = torch.from_numpy(visual_prompt_data['boxes']).unsqueeze(0).float()
                
                # Try using set_prompts if available
                if hasattr(loaded_model, 'set_prompts'):
                    loaded_model.set_prompts(image_tensor, boxes_tensor)
                # Fallback: use get_visual_pe to get visual prompt embeddings
                elif hasattr(loaded_model, 'get_visual_pe'):
                    visual_pe = loaded_model.get_visual_pe(image_tensor, boxes_tensor)
                    loaded_model.set_classes(["object"], visual_pe)
                else:
                    print(f"[WARN] Visual prompting not directly supported, using fallback")
                    # Fallback: use generic class name
                    loaded_model.set_classes(["object"], loaded_model.get_text_pe(["object"]))
            except Exception as e:
                error_msg = str(e) if str(e) else "Unknown error"
                print(f"[ERROR] Failed to set visual prompts: {error_msg}")
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                print(f"[INFO] Falling back to generic object detection")
                loaded_model.set_classes(["object"], loaded_model.get_text_pe(["object"]))
                visual_prompt_success = False
        else:
            # Text prompting mode: use class names
            loaded_model.set_classes(class_names, loaded_model.get_text_pe(class_names))
        
        export_model = loaded_model.export(format="onnx", imgsz=320)
        # Reload with the exported ONNX model
        loaded_model = YOLOE(export_model)
        print(f"[INFO] ONNX model exported and cached at {export_model}")
        if visual_prompt_data is not None:
            if visual_prompt_success:
                print(f"[INFO] Model set up with visual prompts")
            else:
                print(f"[WARN] Model set up with fallback (visual prompts failed)")
        else:
            print(f"[INFO] Model classes set to: {class_names}")
    
    # Warm up the model to initialize ONNX Runtime session
    # This prevents the ~2 minute delay on first inference
    print(f"[INFO] Warming up model {model_size} (initializing ONNX Runtime session)...")
    dummy_frame = np.zeros((320, 320, 3), dtype=np.uint8)
    _ = list(loaded_model.track(source=dummy_frame, conf=0.2, iou=0.4, show=False, persist=True, verbose=False))
    print(f"[INFO] Model {model_size} warm-up complete - ready for inference")
    
    return loaded_model, visual_prompt_success

# Load the default model
model, _ = load_model(current_model, current_classes.split(", "))

# -------------------------------
# ⚙️ Shared State
# -------------------------------
latest_frame = None
lock = threading.Lock()
running = False  # inference running flag
thread_alive = False  # to track if thread exists
current_camera = 0
t = None
available_cameras = []
camera_manager = None  # Background camera manager

# Visual prompting state
snapshot_frame = None
snapshot_boxes = []  # List of bounding boxes [(x1, y1, x2, y2), ...]
use_visual_prompt = False

# Performance monitoring
fps_counter = 0
fps_start_time = time.time()
current_fps = 0.0
inference_time = 0.0
detection_count = 0


# -------------------------------
# 🔍 Camera Detection Utility (Deprecated - Now handled by CameraManager)
# -------------------------------
def detect_cameras(max_devices: int = 10):
    """Return a list of indices of available camera devices."""
    # This function is kept for backward compatibility
    # but camera detection is now handled by CameraManager
    if camera_manager:
        return camera_manager.get_available_cameras()

    # Fallback detection with platform-specific backend
    is_windows = platform.system() == 'Windows'
    backend = cv2.CAP_DSHOW if is_windows else cv2.CAP_ANY

    found = []
    for i in range(max_devices):
        cap = cv2.VideoCapture(i, backend)
        if cap.isOpened():
            found.append(i)
            cap.release()
    return found


# -------------------------------
# 🧠 Inference Thread
# -------------------------------
def inference_thread():
    """Runs YOLO inference in a background thread."""
    global latest_frame, running, current_camera, thread_alive
    global fps_counter, fps_start_time, current_fps, inference_time, detection_count

    thread_alive = True
    print(f"[INFO] Starting inference on camera {current_camera}")
    print(f"[INFO] Detection parameters: conf={current_conf}, iou={current_iou}")

    # Reset tracker state to avoid tracking issues when switching cameras
    try:
        if hasattr(model, 'predictor') and model.predictor is not None:
            if hasattr(model.predictor, 'trackers') and model.predictor.trackers:
                model.predictor.trackers[0].reset()
                print(f"[INFO] Tracker reset for camera {current_camera}")
    except Exception as e:
        print(f"[WARN] Could not reset tracker: {e}")

    # Get camera from manager (pre-opened if available)
    cap = camera_manager.get_camera(current_camera) if camera_manager else cv2.VideoCapture(current_camera)

    if cap is None or not cap.isOpened():
        print(f"[ERROR] Could not open camera {current_camera}")
        thread_alive = False
        return

    # Reset performance counters
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0.0

    while running:
        success, frame = cap.read()
        if not success:
            print(f"[WARN] Camera {current_camera} read() failed, retrying...")
            time.sleep(2)
            continue

        # Measure inference time
        inference_start = time.time()
        
        # Run inference with configurable parameters
        detections_found = 0
        for result in model.track(source=frame, conf=current_conf, iou=current_iou, show=False, persist=True):
            frame = result.orig_img.copy()
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            names = result.names
            detections_found = len(boxes)
            
            for box, cls_id in zip(boxes, result.boxes.cls):
                x1, y1, x2, y2 = box
                label = names[int(cls_id)]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Calculate and display performance info on frame
            inference_time = time.time() - inference_start
            fps_counter += 1
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                current_fps = fps_counter / elapsed
                fps_counter = 0
                fps_start_time = time.time()
            
            detection_count = detections_found
            
            # Add performance overlay
            perf_text = f"FPS: {current_fps:.1f} | Inference: {inference_time*1000:.1f}ms | Detections: {detection_count}"
            cv2.putText(frame, perf_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Add parameter info
            param_text = f"Conf: {current_conf:.2f} | IoU: {current_iou:.2f}"
            cv2.putText(frame, param_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            with lock:
                latest_frame = frame.copy()

        time.sleep(0.001)

    if cap is not None:
        cap.release()
    thread_alive = False
    print(f"[INFO] Stopped inference on camera {current_camera}")


# -------------------------------
# 🌐 Web Stream Generator
# -------------------------------
def gen_frames():
    """Continuously yields the latest frame for Flask MJPEG stream."""
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.01)


# -------------------------------
# 🖥️ Flask Routes
# -------------------------------
@app.route('/')
def index():
    """Main HTML page with control buttons."""
    status = "Running" if running else "Stopped"
    prompt_mode = "Visual Prompting" if use_visual_prompt else "Text Prompting"
    has_snapshot = snapshot_frame is not None
    
    # Get hardware information
    hw_info = get_hardware_info()
    hardware_status = f"{hw_info['device_name']} ({hw_info['cpu_count']} CPU cores)"

    camera_options_html = "".join(
        [f'<option value="{cam}" {"selected" if cam == current_camera else ""}>Camera {cam}</option>'
         for cam in available_cameras]
    )

    model_options_html = "".join(
        [f'<option value="{model_size}" {"selected" if model_size == current_model else ""}>YoloE-11{model_size.upper()}</option>'
         for model_size in available_models]
    )

    return f'''
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                .section {{
                    border: 1px solid #ccc;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .canvas-container {{
                    position: relative;
                    display: inline-block;
                }}
                #snapshotCanvas {{
                    border: 2px solid #333;
                    cursor: crosshair;
                }}
                .button {{
                    padding: 8px 16px;
                    margin: 5px;
                    cursor: pointer;
                }}
                .disabled {{
                    opacity: 0.5;
                    cursor: not-allowed;
                }}
            </style>
        </head>
        <body>
        <h1>YOLO Stream with Live Inference</h1>
        
        <div class="section">
            <h2>Status & Controls</h2>
            <h3>Status: {status}</h3>
            <h3>Hardware: {hardware_status}</h3>
            <h3>Current Model: YoloE-11{current_model.upper()}</h3>
            <h3>Prompt Mode: {prompt_mode}</h3>
            {"<h3>Current Classes: " + current_classes + "</h3>" if not use_visual_prompt else "<h3>Visual Prompts Active: " + str(len(snapshot_boxes)) + " boxes</h3>"}
            {f"<h3>Performance: {current_fps:.1f} FPS | {inference_time*1000:.1f}ms inference | {detection_count} detections</h3>" if running else ""}
            
            <form action="/start" method="post" style="display:inline;">
                <input type="submit" value="Start Inference" {"disabled" if running else ""} class="button">
            </form>
            <form action="/stop" method="post" style="display:inline;">
                <input type="submit" value="Stop Inference" {"disabled" if not running else ""} class="button">
            </form>
        </div>
        
        <div class="section">
            <h2>Configuration</h2>
            <form action="/set_camera" method="post">
                <label for="camera">Select Camera:</label>
                <select name="camera" id="camera" {"disabled" if running else ""}>
                    {camera_options_html}
                </select>
                <input type="submit" value="Switch Camera" {"disabled" if running else ""} class="button">
            </form>
            <br><br>
            <form action="/set_model" method="post">
                <label for="model">Select Model:</label>
                <select name="model" id="model" {"disabled" if running else ""}>
                    {model_options_html}
                </select>
                <input type="submit" value="Switch Model" {"disabled" if running else ""} class="button">
            </form>
        </div>
        
        <div class="section">
            <h2>Detection Parameters</h2>
            <p>Adjust these parameters to improve detection performance. Lower confidence detects more objects but may include false positives.</p>
            <form action="/set_parameters" method="post">
                <label for="conf">Confidence Threshold (0.0 - 1.0):</label>
                <input type="number" name="conf" id="conf" value="{current_conf}" min="0.0" max="1.0" step="0.05" {"disabled" if running else ""}><br><br>
                
                <label for="iou">IoU Threshold (0.0 - 1.0):</label>
                <input type="number" name="iou" id="iou" value="{current_iou}" min="0.0" max="1.0" step="0.05" {"disabled" if running else ""}><br><br>
                
                <input type="submit" value="Update Parameters" {"disabled" if running else ""} class="button">
            </form>
            <p style="font-size: 0.9em; color: #666;">
                <strong>Tips:</strong><br>
                • Confidence 0.15-0.25: More detections, may include false positives<br>
                • Confidence 0.25-0.40: Balanced (recommended for most cases)<br>
                • Confidence 0.40-0.60: High confidence, fewer false positives<br>
                • IoU 0.40-0.50: More lenient overlap detection<br>
                • IoU 0.50-0.60: Standard overlap detection
            </p>
        </div>
        
        <div class="section">
            <h2>Text Prompting</h2>
            <form action="/set_classes" method="post">
                <label for="classes">Custom Classes (comma-separated):</label>
                <input type="text" name="classes" id="classes" value="{current_classes}" size="50" {"disabled" if running else ""}>
                <input type="submit" value="Update Classes" {"disabled" if running else ""} class="button">
            </form>
        </div>
        
        <div class="section">
            <h2>Visual Prompting</h2>
            <p>Capture a snapshot from the camera and draw bounding boxes around objects you want to track.</p>
            
            <form action="/capture_snapshot" method="post" style="display:inline;">
                <input type="submit" value="Capture Snapshot" {"disabled" if running else ""} class="button">
            </form>
            
            <button onclick="clearBoxes()" {"disabled" if running or not has_snapshot else ""} class="button">Clear Boxes</button>
            <button onclick="saveVisualPrompt()" {"disabled" if running or not has_snapshot else ""} class="button">Save Snapshot with Boxes</button>
            
            <form action="/clear_visual_prompt" method="post" style="display:inline;">
                <input type="submit" value="Clear Visual Prompt" {"disabled" if running or not use_visual_prompt else ""} class="button">
            </form>
            
            <br><br>
            
            <div class="canvas-container">
                <canvas id="snapshotCanvas" width="640" height="480"></canvas>
            </div>
            
            <p id="boxInfo">No boxes drawn</p>
        </div>
        
        <div class="section">
            <h2>Live Feed</h2>
            <img src="/video_feed" width="640" height="480">
        </div>
        
        <script>
            const canvas = document.getElementById('snapshotCanvas');
            const ctx = canvas.getContext('2d');
            let boxes = [];
            let isDrawing = false;
            let startX, startY;
            let snapshotLoaded = {str(has_snapshot).lower()};
            
            // Load snapshot image
            function loadSnapshot() {{
                const img = new Image();
                img.onload = function() {{
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    redrawBoxes();
                }};
                img.src = '/snapshot_image?t=' + new Date().getTime();
            }}
            
            if (snapshotLoaded) {{
                loadSnapshot();
            }}
            
            // Mouse event handlers for drawing boxes
            canvas.addEventListener('mousedown', (e) => {{
                if ({str(running).lower()} || !snapshotLoaded) return;
                
                const rect = canvas.getBoundingClientRect();
                startX = e.clientX - rect.left;
                startY = e.clientY - rect.top;
                isDrawing = true;
            }});
            
            canvas.addEventListener('mousemove', (e) => {{
                if (!isDrawing) return;
                
                const rect = canvas.getBoundingClientRect();
                const currentX = e.clientX - rect.left;
                const currentY = e.clientY - rect.top;
                
                // Redraw everything
                loadSnapshot();
                
                // Draw current box being drawn
                ctx.strokeStyle = 'lime';
                ctx.lineWidth = 2;
                ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
            }});
            
            canvas.addEventListener('mouseup', (e) => {{
                if (!isDrawing) return;
                
                const rect = canvas.getBoundingClientRect();
                const endX = e.clientX - rect.left;
                const endY = e.clientY - rect.top;
                
                // Save the box (normalize to 0-1 range)
                const x1 = Math.min(startX, endX) / canvas.width;
                const y1 = Math.min(startY, endY) / canvas.height;
                const x2 = Math.max(startX, endX) / canvas.width;
                const y2 = Math.max(startY, endY) / canvas.height;
                
                // Only save if box has some size
                if (Math.abs(x2 - x1) > 0.01 && Math.abs(y2 - y1) > 0.01) {{
                    boxes.push({{ x1, y1, x2, y2 }});
                    updateBoxInfo();
                    redrawBoxes();
                }}
                
                isDrawing = false;
            }});
            
            function redrawBoxes() {{
                for (const box of boxes) {{
                    const x1 = box.x1 * canvas.width;
                    const y1 = box.y1 * canvas.height;
                    const x2 = box.x2 * canvas.width;
                    const y2 = box.y2 * canvas.height;
                    
                    ctx.strokeStyle = 'lime';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                }}
            }}
            
            function clearBoxes() {{
                boxes = [];
                loadSnapshot();
                updateBoxInfo();
            }}
            
            function updateBoxInfo() {{
                const info = document.getElementById('boxInfo');
                if (boxes.length === 0) {{
                    info.textContent = 'No boxes drawn';
                }} else {{
                    info.textContent = `${{boxes.length}} box(es) drawn`;
                }}
            }}
            
            function saveVisualPrompt() {{
                if (boxes.length === 0) {{
                    alert('Please draw at least one bounding box first.');
                    return;
                }}
                
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/save_visual_prompt';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'boxes';
                input.value = JSON.stringify(boxes);
                
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }}
        </script>
        </body>
    </html>
    '''


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start', methods=['POST'])
def start_inference():
    """Start inference thread."""
    global running, t
    if not running:
        running = True
        # Request camera manager to pre-open the camera before starting inference
        if camera_manager:
            camera_manager.request_pre_open(current_camera)
            time.sleep(2)  # Give manager a moment to pre-open
        t = threading.Thread(target=inference_thread, daemon=True)
        t.start()
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/stop', methods=['POST'])
def stop_inference():
    """Stop inference thread."""
    global running, t
    if running:
        running = False
        if t and t.is_alive():
            t.join(timeout=2.0)
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/set_camera', methods=['POST'])
def set_camera():
    """Change the active camera device (only allowed when stopped)."""
    global current_camera, available_cameras

    try:
        new_cam = int(request.form.get("camera"))
    except (TypeError, ValueError):
        return "Invalid camera ID", 400

    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"

    # Request camera manager to refresh camera list asynchronously
    if camera_manager:
        camera_manager.request_detect_cameras()
        time.sleep(0.2)  # Give manager a moment to detect
        available_cameras = camera_manager.get_available_cameras()
    else:
        available_cameras = detect_cameras()

    if new_cam not in available_cameras:
        return f"<html><body><h3>Camera {new_cam} not available.</h3><a href='/'>Back</a></body></html>"

    current_camera = new_cam

    # Request pre-opening of the new camera in background
    if camera_manager:
        camera_manager.request_pre_open(new_cam)

    print(f"[INFO] Camera changed to {current_camera}")
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/set_model', methods=['POST'])
def set_model():
    """Change the active YOLO model (only allowed when stopped)."""
    global current_model, model

    try:
        new_model = request.form.get("model")
    except (TypeError, ValueError):
        return "Invalid model", 400

    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"

    if new_model not in available_models:
        return f"<html><body><h3>Model {new_model} not available.</h3><a href='/'>Back</a></body></html>"

    current_model = new_model
    
    # Load the new model with current classes
    print(f"[INFO] Switching to model: YoloE-11{current_model.upper()}")
    model, _ = load_model(current_model, current_classes.split(", "))
    print(f"[INFO] Model changed to YoloE-11{current_model.upper()}")
    
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    """Change detection parameters (only allowed when stopped)."""
    global current_conf, current_iou

    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"

    try:
        new_conf = float(request.form.get("conf"))
        new_iou = float(request.form.get("iou"))
    except (TypeError, ValueError):
        return "Invalid parameters", 400

    # Validate ranges
    if not (0.0 <= new_conf <= 1.0):
        return "<html><body><h3>Confidence must be between 0.0 and 1.0</h3><a href='/'>Back</a></body></html>"
    
    if not (0.0 <= new_iou <= 1.0):
        return "<html><body><h3>IoU must be between 0.0 and 1.0</h3><a href='/'>Back</a></body></html>"

    current_conf = new_conf
    current_iou = new_iou
    
    print(f"[INFO] Detection parameters updated: conf={current_conf}, iou={current_iou}")
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/set_classes', methods=['POST'])
def set_classes():
    """Change the object classes to detect (only allowed when stopped)."""
    global current_classes, model, use_visual_prompt

    try:
        new_classes = request.form.get("classes")
    except (TypeError, ValueError):
        return "Invalid classes", 400

    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"

    if not new_classes or new_classes.strip() == "":
        return "<html><body><h3>Classes cannot be empty.</h3><a href='/'>Back</a></body></html>"

    current_classes = new_classes.strip()
    
    # Parse class names from comma-separated string
    class_list = [name.strip() for name in current_classes.split(",") if name.strip()]
    
    if not class_list:
        return "<html><body><h3>Please provide at least one class name.</h3><a href='/'>Back</a></body></html>"
    
    # Switch to text prompting mode
    use_visual_prompt = False
    
    # Delete cached ONNX model to force re-export with new classes
    onnx_model_path = f"yoloe-11{current_model}-seg.onnx"
    if os.path.exists(onnx_model_path):
        os.remove(onnx_model_path)
        print(f"[INFO] Removed cached ONNX model to re-export with new classes")
    
    # Reload the model with new classes
    print(f"[INFO] Updating classes to: {class_list}")
    model, _ = load_model(current_model, class_list)
    print(f"[INFO] Classes updated successfully")
    
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/capture_snapshot', methods=['POST'])
def capture_snapshot():
    """Capture the current frame as a snapshot."""
    global snapshot_frame
    
    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"
    
    # Get current frame from camera
    cap = camera_manager.get_camera(current_camera) if camera_manager else cv2.VideoCapture(current_camera)
    
    if cap is None or not cap.isOpened():
        return "<html><body><h3>Could not open camera to capture snapshot.</h3><a href='/'>Back</a></body></html>"
    
    success, frame = cap.read()
    if not success:
        return "<html><body><h3>Failed to capture frame from camera.</h3><a href='/'>Back</a></body></html>"
    
    with lock:
        snapshot_frame = frame.copy()
    
    print(f"[INFO] Snapshot captured")
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/snapshot_image')
def snapshot_image():
    """Return the captured snapshot as JPEG."""
    global snapshot_frame
    
    with lock:
        if snapshot_frame is None:
            # Return a blank image if no snapshot
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            ret, buffer = cv2.imencode('.jpg', blank)
        else:
            ret, buffer = cv2.imencode('.jpg', snapshot_frame)
    
    if not ret:
        return "Error encoding image", 500
    
    return Response(buffer.tobytes(), mimetype='image/jpeg')


@app.route('/save_visual_prompt', methods=['POST'])
def save_visual_prompt():
    """Save the snapshot with drawn bounding boxes as visual prompt."""
    global snapshot_boxes, use_visual_prompt, model, snapshot_frame
    
    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"
    
    if snapshot_frame is None:
        return "<html><body><h3>Please capture a snapshot first.</h3><a href='/'>Back</a></body></html>"
    
    try:
        # Get bounding boxes from request
        boxes_json = request.form.get("boxes", "[]")
        import json
        boxes_data = json.loads(boxes_json)
        
        if not boxes_data:
            return "<html><body><h3>Please draw at least one bounding box.</h3><a href='/'>Back</a></body></html>"
        
        # Convert boxes from relative coordinates to absolute coordinates
        h, w = snapshot_frame.shape[:2]
        snapshot_boxes = []
        for box in boxes_data:
            x1 = int(box['x1'] * w)
            y1 = int(box['y1'] * h)
            x2 = int(box['x2'] * w)
            y2 = int(box['y2'] * h)
            snapshot_boxes.append([x1, y1, x2, y2])
        
        # Switch to visual prompting mode
        use_visual_prompt = True
        
        # Delete cached ONNX model to force re-export with visual prompts
        onnx_model_path = f"yoloe-11{current_model}-seg.onnx"
        if os.path.exists(onnx_model_path):
            os.remove(onnx_model_path)
            print(f"[INFO] Removed cached ONNX model to re-export with visual prompts")
        
        # Prepare visual prompt data
        visual_prompt_data = {
            'image': snapshot_frame,
            'boxes': np.array(snapshot_boxes)
        }
        
        # Reload the model with visual prompts
        print(f"[INFO] Setting up visual prompts with {len(snapshot_boxes)} boxes")
        model, success = load_model(current_model, visual_prompt_data=visual_prompt_data)
        
        if success:
            print(f"[INFO] Visual prompts set successfully")
        else:
            print(f"[WARN] Visual prompts could not be set - using fallback generic detection")
        
        return '<meta http-equiv="refresh" content="0; url=/" />'
        
    except Exception as e:
        print(f"[ERROR] Failed to save visual prompt: {e}")
        return f"<html><body><h3>Error: {str(e)}</h3><a href='/'>Back</a></body></html>"


@app.route('/clear_visual_prompt', methods=['POST'])
def clear_visual_prompt():
    """Clear visual prompts and return to text prompting mode."""
    global use_visual_prompt, snapshot_frame, snapshot_boxes, model
    
    if running:
        return "<html><body><h3>Stop inference first!</h3><a href='/'>Back</a></body></html>"
    
    use_visual_prompt = False
    snapshot_frame = None
    snapshot_boxes = []
    
    # Delete cached ONNX model to force re-export with text prompts
    onnx_model_path = f"yoloe-11{current_model}-seg.onnx"
    if os.path.exists(onnx_model_path):
        os.remove(onnx_model_path)
        print(f"[INFO] Removed cached ONNX model to re-export with text prompts")
    
    # Reload the model with text prompts
    class_list = [name.strip() for name in current_classes.split(",") if name.strip()]
    print(f"[INFO] Returning to text prompting mode with classes: {class_list}")
    model, _ = load_model(current_model, class_list)
    print(f"[INFO] Switched back to text prompting mode")
    
    return '<meta http-equiv="refresh" content="0; url=/" />'


# -------------------------------
# 🏁 Main Entry
# -------------------------------
if __name__ == '__main__':
    # Initialize camera manager
    camera_manager = CameraManager(max_devices=10)
    camera_manager.start()

    # Detect available cameras using the camera manager
    print("[INFO] Scanning for available cameras...")
    time.sleep(5)  # Give manager time for initial detection
    available_cameras = camera_manager.get_available_cameras()

    if not available_cameras:
        print("[ERROR] No cameras detected!")
        camera_manager.stop()
        exit(1)

    print(f"[INFO] Found cameras: {available_cameras}")
    current_camera = available_cameras[0]

    # Pre-open the default camera in background
    camera_manager.request_pre_open(current_camera)

    try:
        app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)
    finally:
        # Cleanup camera manager on exit
        camera_manager.stop()
