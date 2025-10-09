# Usage Examples for CameraManager

## Basic Usage in Flask App

```python
from camera_manager import CameraManager

# Initialize the manager
camera_manager = CameraManager(max_devices=10)

# Start the background thread
camera_manager.start()

# Wait a moment for initial detection
time.sleep(0.3)

# Get available cameras
cameras = camera_manager.get_available_cameras()
print(f"Available cameras: {cameras}")

# Pre-open a camera asynchronously
camera_manager.request_pre_open(0)

# Later, get the pre-opened camera
cap = camera_manager.get_camera(0)
if cap and cap.isOpened():
    # Use the camera
    success, frame = cap.read()
    # ... process frame ...
    cap.release()

# Clean up on exit
camera_manager.stop()
```

## How Pre-Opening Works

### Without Camera Manager (Old Way)
```python
# This blocks the main thread while opening the camera
cap = cv2.VideoCapture(0)  # ← Blocking operation
if cap.isOpened():
    # Camera is ready
```

### With Camera Manager (New Way)
```python
# Request pre-opening in background (non-blocking)
camera_manager.request_pre_open(0)  # ← Returns immediately

# Do other work...
time.sleep(0.2)  # Give manager time to pre-open

# Get the already-opened camera (fast!)
cap = camera_manager.get_camera(0)  # ← Returns pre-opened camera
```

## Async Camera Detection

### Without Camera Manager (Old Way)
```python
# This blocks while checking all camera devices
def detect_cameras(max_devices=10):
    found = []
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)  # ← Blocking
        if cap.isOpened():
            found.append(i)
            cap.release()
    return found

cameras = detect_cameras()  # ← Blocks main thread
```

### With Camera Manager (New Way)
```python
# Request detection in background (non-blocking)
camera_manager.request_detect_cameras()  # ← Returns immediately

# Do other work...
time.sleep(0.2)  # Give manager time to detect

# Get the results
cameras = camera_manager.get_available_cameras()  # ← Fast
```

## Integration with Flask Routes

```python
@app.route('/start', methods=['POST'])
def start_inference():
    global running, current_camera
    
    if not running:
        # Pre-open camera before starting inference
        camera_manager.request_pre_open(current_camera)
        time.sleep(0.2)  # Brief wait for pre-opening
        
        running = True
        t = threading.Thread(target=inference_thread, daemon=True)
        t.start()
    
    return redirect('/')

def inference_thread():
    # Get pre-opened camera (fast startup!)
    cap = camera_manager.get_camera(current_camera)
    
    # Start processing...
    while running:
        success, frame = cap.read()
        # ... inference code ...
```

## Benefits Demonstrated

1. **Non-blocking UI**: Camera operations happen in background
2. **Faster startup**: Cameras are pre-opened before they're needed
3. **Better UX**: No freezing while detecting/opening cameras
4. **Resource management**: Centralized cleanup and caching

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│           Flask Application (Main Thread)        │
├─────────────────────────────────────────────────┤
│  • Web routes (/start, /stop, /set_camera)      │
│  • Calls camera_manager methods                 │
│  • Never blocks on camera operations            │
└─────────────────────────────────────────────────┘
                      ↓ (async requests)
┌─────────────────────────────────────────────────┐
│         CameraManager (Background Thread)        │
├─────────────────────────────────────────────────┤
│  • Processes request queue                      │
│  • Detects cameras asynchronously               │
│  • Pre-opens cameras in background              │
│  • Manages camera cache                         │
└─────────────────────────────────────────────────┘
                      ↓ (uses)
┌─────────────────────────────────────────────────┐
│              OpenCV VideoCapture                 │
├─────────────────────────────────────────────────┤
│  • Camera 0, Camera 1, Camera 2, etc.           │
└─────────────────────────────────────────────────┘
```
