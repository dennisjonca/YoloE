# YoloE
A YoloE project to demonstrate using AI in process.

## Features

### Background Camera Manager
The application includes a background camera manager that improves camera handling:

- **Asynchronous Camera Detection**: Cameras are detected in a background thread without blocking the main application.
- **Pre-opening Cameras**: Cameras can be pre-opened in the background for faster switching and startup.
- **Queue-based Requests**: All camera operations (detection, pre-opening, releasing) are queued and processed asynchronously.

### Architecture

- `app.py` - Main Flask application with YOLO inference
- `camera_manager.py` - Background camera management module

The `CameraManager` runs in a separate daemon thread and handles:
- Initial camera detection on startup
- Asynchronous camera pre-opening when requested
- Camera caching for faster access
- Proper cleanup of camera resources

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
