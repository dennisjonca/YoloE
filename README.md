# YoloE
A YoloE project to demonstrate using AI in process.

## Features

### Video Upload & Processing (NEW!)
The application now supports uploading and processing local video files:

- **File Upload**: Upload video files (MP4, AVI, MOV, MKV, WebM, FLV, WMV) up to 500MB
- **Model Integration**: Uses the same YOLO models and detection settings as live inference
- **Custom Classes**: Process videos with custom object classes or visual prompts
- **Heatmap Support**: Optional heatmap overlay for uploaded videos
- **Progress Tracking**: Real-time progress updates during processing
- **Download Results**: Download processed videos with detections and annotations

See [VIDEO_UPLOAD_FEATURE.md](VIDEO_UPLOAD_FEATURE.md) for detailed documentation.

### Live Heatmap Mode
The application now supports real-time heatmap visualization during live camera inference:

- **Real-time Attention**: See what the model focuses on as objects move in real-time
- **Toggle Control**: Switch between normal and heatmap mode with a single button
- **Live Overlay**: Heatmap overlay updated every frame during inference
- **Mode Indicator**: Clear [HEATMAP] or [NORMAL] indicator on video feed
- **Detection Integration**: Bounding boxes and labels shown on heatmap
- **Performance Metrics**: FPS and inference time displayed in both modes
- **Easy Toggle**: Enable/disable heatmap mode when inference is stopped

See [LIVE_HEATMAP_MODE.md](LIVE_HEATMAP_MODE.md) for detailed documentation.

### Heatmap Generation (Snapshot-based)
The application also includes snapshot-based GradCAM heatmap visualization:

- **Visual Explanation**: Generate heatmaps that highlight the regions of the image the model focuses on
- **Snapshot-based**: Works with captured snapshots from the camera feed
- **Multiple Methods**: Supports various GradCAM methods (HiResCAM, GradCAM, XGradCAM, etc.)
- **Detection Overlay**: Optional bounding box overlay showing detected objects
- **Save Results**: Heatmaps are saved to the `heatmaps/` directory with timestamps
- **Easy to Use**: Single button click to generate heatmaps from any captured snapshot

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
pip install -r requirements.txt

# Or install individually:
pip install flask opencv-python ultralytics grad-cam matplotlib Pillow tqdm

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

## Using Live Heatmap Mode

To enable real-time heatmap visualization during live inference:

1. **Stop inference** if it's currently running
2. Click the **"Enable Heatmap Mode"** button in the Status & Controls section
3. The status will update to show "Heatmap Mode: ON"
4. **Start inference** to see live heatmap visualization
5. The video feed will show a **[HEATMAP]** indicator and colored attention overlay
6. Watch as the heatmap updates in real-time showing where the model focuses

To disable heatmap mode and return to normal view:
1. **Stop inference**
2. Click **"Disable Heatmap Mode"**
3. **Start inference** to see normal detection view with **[NORMAL]** indicator

**Performance Note:** Heatmap mode is more computationally intensive:
- CPU: 2-5 FPS (vs 15-30 FPS normal mode)
- GPU: 10-20 FPS (vs 30-60 FPS normal mode)

See [LIVE_HEATMAP_MODE.md](LIVE_HEATMAP_MODE.md) for detailed usage and troubleshooting.

## Using Video Upload

To process a local video file with YOLO detection:
1. Stop live inference if it's running
2. Click on the "Video Upload" tab
3. Click "Choose File" and select your video (MP4, AVI, MOV, MKV, WebM, FLV, WMV)
4. Optional: Check "Enable Heatmap Mode for Video" for heatmap overlay
5. Click "Upload and Process" to start processing
6. Wait for processing to complete (progress shown on page)
7. Click "Download Processed Video" when ready

**Tips:**
- Maximum file size: 500MB
- Processing uses current model, classes, and settings
- Enable heatmap for visualization (slower but shows model attention)
- Use custom classes or visual prompting before uploading for specific detection

See [VIDEO_UPLOAD_FEATURE.md](VIDEO_UPLOAD_FEATURE.md) for detailed documentation and examples.

## Using Heatmap Generation (Snapshot)

To generate a heatmap visualization showing what the model focuses on:
1. Stop inference if it's running
2. Click "Capture Snapshot" to take a photo from the camera
3. Click "Generate Heatmap" to create a GradCAM visualization
4. The heatmap will be displayed and saved to the `heatmaps/` directory with a timestamp
5. Heatmaps show highlighted regions where the model pays attention when making detections

**What heatmaps show:**
- Bright/warm colors (red, yellow) indicate areas the model focuses on most
- Dark/cool colors indicate areas the model ignores
- Optional bounding boxes show detected objects
- Helps understand and debug model behavior

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

## Testing Video Upload Feature

Run the video upload test suite:
```bash
python test_video_upload.py
```

This will test:
- Required imports and dependencies
- Video upload configuration
- File validation and security
- Processing functions
- UI integration
- Heatmap and visual prompting support

## Testing Heatmap Generation

Run the heatmap unit tests to verify the module:
```bash
python test_heatmap_unit.py
```

This will test:
- Module imports and dependencies
- Default parameters configuration
- App integration points

**Note**: To test actual heatmap generation, you need a model file (e.g., `yoloe-11s-seg.pt`). The heatmap generation test can be run with:
```bash
python test_heatmap_generation.py
```

## Testing Live Heatmap Mode

Run the live heatmap mode tests:
```bash
python test_live_heatmap_lightweight.py
```

This will test:
- Core imports (heatmap_generator, pytorch_grad_cam)
- Code structure (heatmap_mode flag, toggle route)
- Utility functions (letterbox, get_default_params)
- Integration logic (GradCAM generation, overlay creation)

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

- [VIDEO_UPLOAD_FEATURE.md](VIDEO_UPLOAD_FEATURE.md) - **NEW!** Video upload and processing feature documentation
- [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) - Performance improvements for faster inference FPS
- [LIVE_HEATMAP_MODE.md](LIVE_HEATMAP_MODE.md) - Real-time heatmap visualization feature
- [HEATMAP_FEATURE.md](HEATMAP_FEATURE.md) - Snapshot-based heatmap generation documentation
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
├── heatmap_generator.py          # GradCAM heatmap generation module
├── requirements.txt              # Python dependencies
├── test_custom_classes.py        # Custom classes test suite
├── test_tracker_reset.py         # Tracker reset test suite
├── test_visual_prompting.py      # Visual prompting test suite
├── test_visual_prompt_resize.py  # Visual prompt resize test suite
├── test_box_tensor_fix.py        # Box tensor dimension test suite
├── test_heatmap_unit.py          # Heatmap module unit tests
├── test_heatmap_generation.py    # Heatmap generation integration test
├── test_live_heatmap_lightweight.py  # Live heatmap mode test suite
├── test_video_upload.py          # Video upload feature test suite
├── verify_camera_manager.py      # Camera manager verification script
├── verify_model_caching.py       # Model caching verification script
├── verify_model_warmup.py        # Model warm-up verification script
├── README.md                     # This file
├── VIDEO_UPLOAD_FEATURE.md       # Video upload feature documentation
├── LIVE_HEATMAP_MODE.md          # Live heatmap mode feature documentation
├── HEATMAP_FEATURE.md            # Snapshot-based heatmap documentation
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
