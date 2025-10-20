# YoloE
A YoloE project to demonstrate using AI in process.

## Features

### Visual Prompting
The application now supports visual prompting, allowing you to track objects by example:

- **Snapshot Capture**: Take a photo from the camera feed
- **Bounding Box Drawing**: Draw boxes around objects you want to track using mouse
- **Visual Object Tracking**: The model learns to track objects similar to those in your visual prompts
- **Interactive Canvas**: Real-time visual feedback while drawing boxes
- **Dual Mode Support**: Switch between text prompting and visual prompting seamlessly
- **Multiple Objects**: Draw multiple boxes to track different objects or instances
- **Resolution Independent**: Works with cameras of any resolution (snapshots are automatically resized to model input size)

### Custom Class Prompts (Text Prompting)
The application allows users to customize which objects the YOLO model should detect:

- **Flexible Detection**: Enter any comma-separated list of object classes (e.g., "banana, apple, orange")
- **Web Interface**: Simple text input field in the web UI
- **Real-time Updates**: Classes can be changed at any time when inference is stopped
- **No Code Changes**: Users don't need to modify code to detect different objects
- **Default Classes**: Ships with "person, plant" as default, but fully customizable

### ONNX Model Caching
The application now caches the exported ONNX model for faster startup:

- **One-time Export**: The PyTorch model is exported to ONNX format only once on first run
- **Persistent Cache**: The ONNX model file is saved locally and reused on subsequent runs
- **Fast Startup**: Subsequent launches are 10-30x faster by skipping the export step
- **Automatic Detection**: The app automatically checks for the cached ONNX file

### Model Warm-up
The application includes intelligent model warm-up to eliminate first inference delays:

- **ONNX Runtime Pre-initialization**: The model is warmed up during startup to initialize the ONNX Runtime session
- **Instant First Inference**: No ~2 minute delay when user starts inference
- **Better UX**: Delays happen at startup where they're expected, not during first use
- **Automatic**: No user intervention required

### Background Camera Manager
The application includes a background camera manager that improves camera handling:

- **Asynchronous Camera Detection**: Cameras are detected in a background thread without blocking the main application.
- **Pre-opening Cameras**: Cameras can be pre-opened in the background for faster switching and startup.
- **Queue-based Requests**: All camera operations (detection, pre-opening, releasing) are queued and processed asynchronously.
- **Platform-Specific Backends**: Automatically uses DirectShow backend on Windows for better camera detection and compatibility.

### Tracker Reset on Camera Switch
The application automatically resets the YOLO tracker when switching cameras:

- **Clean Tracking State**: Each camera session starts with a fresh tracker state
- **No Warning Messages**: Eliminates the "WARNING not enough matching points" message
- **Proper Bounding Boxes**: Ensures bounding boxes appear correctly after switching cameras
- **Automatic**: No user intervention required

### Windows Camera Support
The camera manager automatically detects Windows and uses the DirectShow (CAP_DSHOW) backend, which provides:
- Better detection of both integrated and external webcams
- More reliable camera enumeration on Windows 11
- Improved compatibility with Logitech and other USB webcams

### Architecture

- `app.py` - Main Flask application with YOLO inference
- `camera_manager.py` - Background camera management module

The `CameraManager` runs in a separate daemon thread and handles:
- Initial camera detection on startup
- Asynchronous camera pre-opening when requested
- Camera caching for faster access
- Proper cleanup of camera resources
- Platform-specific backend selection (DirectShow on Windows)

## Installation

```bash
# Install dependencies
pip install flask opencv-python ultralytics

# Note: You'll also need a YOLO model file (e.g., yoloe-11s-seg.pt)
```

### Windows Users
On Windows, the application automatically uses the DirectShow backend for improved camera detection. If you're still having issues detecting cameras:

1. Make sure your camera drivers are up to date
2. Check that your camera isn't being used by another application
3. Try running the application as administrator if permission issues occur
4. Check Windows Privacy settings to ensure camera access is enabled for applications

## Usage

Run the application:
```bash
python app.py
```

**First run:**
- The app will export the PyTorch model to ONNX format (takes 10-30 seconds)
- The ONNX file will be cached locally as `yoloe-11s-seg.onnx`
- The model will be warmed up to initialize ONNX Runtime (~2 minutes)
- Total first startup: ~2-3 minutes

**Subsequent runs:**
- The app loads the cached ONNX model directly (takes 1-2 seconds)
- The model is warmed up to initialize ONNX Runtime (~2 minutes)
- Total startup: ~2 minutes
- **Note**: The warm-up ensures instant inference when you click "Start"

The camera manager will automatically:
1. Start in the background when the app launches
2. Detect available cameras
3. Pre-open the default camera
4. Pre-open cameras when you switch to them (before starting inference)
5. Clean up resources when the app exits

Then open your browser to: `http://127.0.0.1:8080`

## Using Visual Prompting

To track objects by visual example:
1. Stop inference if it's running
2. Click "Capture Snapshot" to take a photo from the camera
3. Draw bounding boxes around objects you want to track by clicking and dragging on the snapshot
4. Click "Save Snapshot with Boxes" to configure the model
5. Wait for the model to re-export and warm up (~2 minutes)
6. Start inference to track objects similar to your visual prompts

To return to text prompting:
1. Stop inference if it's running
2. Click "Clear Visual Prompt"
3. Update the class names in the "Custom Classes" field if desired

## Using Custom Classes (Text Prompting)

To detect custom objects using text:
1. Stop inference if it's running
2. Enter your desired object classes in the "Custom Classes" field (comma-separated)
   - Example: `banana, apple, orange` for fruit detection
   - Example: `car, truck, bus` for vehicle detection
   - Example: `cat, dog, bird` for animal detection
3. Click "Update Classes" to reload the model
4. Start inference to detect your custom objects

The model will be reloaded with the new classes (takes a few seconds with cached models).

## Testing Custom Classes

Run the custom classes test suite:
```bash
python test_custom_classes.py
```

This verifies that the custom classes functionality is properly implemented.

## Testing the Camera Manager

Run the verification script to test the camera manager:
```bash
python verify_camera_manager.py
```

This will test:
- Background thread startup/shutdown
- Async camera detection
- Camera pre-opening
- Request queue processing

## Testing Model Caching

Run the model caching verification script:
```bash
python verify_model_caching.py
```

This explains how the ONNX model caching works and shows the performance benefit.

## Testing Model Warm-up

Run the model warm-up verification script:
```bash
python verify_model_warmup.py
```

This demonstrates the model warm-up functionality and shows timing breakdown.

## Testing Tracker Reset

Run the tracker reset test suite:
```bash
python test_tracker_reset.py
```

This verifies that the tracker reset functionality is properly implemented to prevent tracking issues when switching cameras.

## Performance Tuning

The application now includes configurable detection parameters to optimize tracking performance:

- **Confidence Threshold**: Adjust how certain the model must be to report a detection (default: 0.25)
- **IoU Threshold**: Control how overlapping detections are merged (default: 0.45)
- **Real-time Metrics**: View FPS, inference time, and detection count on the video feed
- **Hardware Detection**: Automatic detection of CPU vs GPU for performance optimization

**If objects are not being tracked:**
1. Lower the confidence threshold (e.g., from 0.25 to 0.15)
2. Check the performance metrics on the video feed
3. Verify your hardware capabilities (CPU vs GPU)
4. See [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) for detailed optimization tips

## Documentation

- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Complete guide to detection parameters, hardware, and troubleshooting
- [VISUAL_PROMPTING_FEATURE.md](VISUAL_PROMPTING_FEATURE.md) - Visual prompting feature documentation
- [VISUAL_PROMPT_SHAPE_FIX.md](VISUAL_PROMPT_SHAPE_FIX.md) - Fix for visual prompt shape mismatch error
- [CUSTOM_CLASSES_FEATURE.md](CUSTOM_CLASSES_FEATURE.md) - Custom class prompts feature documentation
- [TRACKER_RESET_FIX.md](TRACKER_RESET_FIX.md) - Explanation of tracker reset fix for camera switching
- [MODEL_WARMUP_FIX.md](MODEL_WARMUP_FIX.md) - Explanation of model warm-up fix for first inference delay
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Camera detection troubleshooting guide for Windows
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details of the implementation
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Code examples showing how to use the camera manager
- [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) - Comparison of old vs new approach

## Project Structure

```
YoloE/
├── app.py                        # Main Flask application with visual prompting
├── camera_manager.py             # Background camera manager
├── test_custom_classes.py        # Custom classes test suite
├── test_tracker_reset.py         # Tracker reset test suite
├── test_visual_prompting.py      # Visual prompting test suite
├── test_visual_prompt_resize.py  # Visual prompt resize test suite
├── test_box_tensor_fix.py        # Box tensor dimension test suite
├── verify_camera_manager.py      # Camera manager verification script
├── verify_model_caching.py       # Model caching verification script
├── verify_model_warmup.py        # Model warm-up verification script
├── README.md                     # This file
├── VISUAL_PROMPTING_FEATURE.md   # Visual prompting feature documentation
├── VISUAL_PROMPT_SHAPE_FIX.md    # Visual prompt shape fix documentation
├── FIX_SUMMARY_SHAPE_ISSUE.md    # Shape issue fix summary
├── CUSTOM_CLASSES_FEATURE.md     # Custom classes feature documentation
├── TRACKER_RESET_FIX.md          # Tracker reset fix documentation
├── MODEL_WARMUP_FIX.md           # Model warm-up fix documentation
├── IMPLEMENTATION_SUMMARY.md     # Technical documentation
├── USAGE_EXAMPLES.md             # Usage examples
├── BEFORE_AFTER_COMPARISON.md    # Before/after comparison
└── .gitignore                    # Git ignore rules
```
