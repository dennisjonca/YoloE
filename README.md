# YoloE
A YoloE project to demonstrate using AI in process.

## Features

### Background Camera Manager
The application includes a background camera manager that improves camera handling:

- **Asynchronous Camera Detection**: Cameras are detected in a background thread without blocking the main application.
- **Pre-opening Cameras**: Cameras can be pre-opened in the background for faster switching and startup.
- **Queue-based Requests**: All camera operations (detection, pre-opening, releasing) are queued and processed asynchronously.
- **Platform-Specific Backends**: Automatically uses DirectShow backend on Windows for better camera detection and compatibility.

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

The camera manager will automatically:
1. Start in the background when the app launches
2. Detect available cameras
3. Pre-open the default camera
4. Pre-open cameras when you switch to them (before starting inference)
5. Clean up resources when the app exits

Then open your browser to: `http://127.0.0.1:8080`

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

## Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Camera detection troubleshooting guide for Windows
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details of the implementation
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Code examples showing how to use the camera manager
- [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) - Comparison of old vs new approach

## Project Structure

```
YoloE/
├── app.py                        # Main Flask application
├── camera_manager.py             # Background camera manager
├── verify_camera_manager.py     # Verification script
├── README.md                     # This file
├── IMPLEMENTATION_SUMMARY.md     # Technical documentation
├── USAGE_EXAMPLES.md             # Usage examples
├── BEFORE_AFTER_COMPARISON.md    # Before/after comparison
└── .gitignore                    # Git ignore rules
```
