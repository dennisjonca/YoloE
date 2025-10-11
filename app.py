from flask import Flask, Response, request
from ultralytics import YOLOE
import cv2, threading, time, platform, os
import numpy as np
from camera_manager import CameraManager

app = Flask(__name__)

# -------------------------------
# 🔧 YOLO Model Initialization
# -------------------------------
# Available model sizes
available_models = ["s", "m", "l"]
current_model = "s"  # Default model size
current_classes = "person, plant"  # Default class prompts

def load_model(model_size, class_names=None):
    """Load YOLO model with the specified size (s, m, or l) and class names."""
    if class_names is None:
        class_names = ["person", "plant"]
    
    # Define the ONNX model path
    onnx_model_path = f"yoloe-11{model_size}-seg.onnx"
    pt_model_path = f"yoloe-11{model_size}-seg.pt"
    
    # Check if ONNX model already exists to avoid re-exporting
    if os.path.exists(onnx_model_path):
        print(f"[INFO] Loading cached ONNX model from {onnx_model_path}")
        loaded_model = YOLOE(onnx_model_path)
        # ONNX models have classes baked in during export, no need to set them again
        print(f"[INFO] Using cached model with classes: {class_names}")
    else:
        print(f"[INFO] ONNX model not found. Exporting from PyTorch model...")
        loaded_model = YOLOE(pt_model_path)
        loaded_model.set_classes(class_names, loaded_model.get_text_pe(class_names))
        export_model = loaded_model.export(format="onnx", imgsz=320)
        # Reload with the exported ONNX model
        loaded_model = YOLOE(export_model)
        print(f"[INFO] ONNX model exported and cached at {export_model}")
        print(f"[INFO] Model classes set to: {class_names}")
    
    # Warm up the model to initialize ONNX Runtime session
    # This prevents the ~2 minute delay on first inference
    print(f"[INFO] Warming up model {model_size} (initializing ONNX Runtime session)...")
    dummy_frame = np.zeros((320, 320, 3), dtype=np.uint8)
    _ = list(loaded_model.track(source=dummy_frame, conf=0.2, iou=0.4, show=False, persist=True, verbose=False))
    print(f"[INFO] Model {model_size} warm-up complete - ready for inference")
    
    return loaded_model

# Load the default model
model = load_model(current_model, current_classes.split(", "))

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

    thread_alive = True
    print(f"[INFO] Starting inference on camera {current_camera}")

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

    while running:
        success, frame = cap.read()
        if not success:
            print(f"[WARN] Camera {current_camera} read() failed, retrying...")
            time.sleep(2)
            continue

        # Run inference
        for result in model.track(source=frame, conf=0.1, iou=0.5, show=False, persist=True):
            frame = result.orig_img.copy()
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            names = result.names
            for box, cls_id in zip(boxes, result.boxes.cls):
                x1, y1, x2, y2 = box
                label = names[int(cls_id)]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

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
    status = "🟢 Running" if running else "🔴 Stopped"

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
        <body>
        <h1>YOLO Live Stream (Threaded, Controlled)</h1>
        <h3>Status: {status}</h3>
        <h3>Current Model: YoloE-11{current_model.upper()}</h3>
        <h3>Current Classes: {current_classes}</h3>
        <form action="/start" method="post" style="display:inline;">
            <input type="submit" value="Start Inference" {"disabled" if running else ""}>
        </form>
        <form action="/stop" method="post" style="display:inline;">
            <input type="submit" value="Stop Inference" {"disabled" if not running else ""}>
        </form>
        <br><br>
        <form action="/set_camera" method="post">
            <label for="camera">Select Camera:</label>
            <select name="camera" id="camera" {"disabled" if running else ""}>
                {camera_options_html}
            </select>
            <input type="submit" value="Switch Camera" {"disabled" if running else ""}>
        </form>
        <br><br>
        <form action="/set_model" method="post">
            <label for="model">Select Model:</label>
            <select name="model" id="model" {"disabled" if running else ""}>
                {model_options_html}
            </select>
            <input type="submit" value="Switch Model" {"disabled" if running else ""}>
        </form>
        <br><br>
        <form action="/set_classes" method="post">
            <label for="classes">Custom Classes (comma-separated):</label>
            <input type="text" name="classes" id="classes" value="{current_classes}" size="50" {"disabled" if running else ""}>
            <input type="submit" value="Update Classes" {"disabled" if running else ""}>
        </form>
        <br><br>
        <img src="/video_feed" width="640" height="480">
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
    model = load_model(current_model, current_classes.split(", "))
    print(f"[INFO] Model changed to YoloE-11{current_model.upper()}")
    
    return '<meta http-equiv="refresh" content="0; url=/" />'


@app.route('/set_classes', methods=['POST'])
def set_classes():
    """Change the object classes to detect (only allowed when stopped)."""
    global current_classes, model

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
    
    # Delete cached ONNX model to force re-export with new classes
    onnx_model_path = f"yoloe-11{current_model}-seg.onnx"
    if os.path.exists(onnx_model_path):
        os.remove(onnx_model_path)
        print(f"[INFO] Removed cached ONNX model to re-export with new classes")
    
    # Reload the model with new classes
    print(f"[INFO] Updating classes to: {class_list}")
    model = load_model(current_model, class_list)
    print(f"[INFO] Classes updated successfully")
    
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
