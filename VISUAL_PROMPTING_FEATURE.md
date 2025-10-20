# Visual Prompting Feature

## Overview

The Visual Prompting feature allows you to capture a snapshot from the camera and draw bounding boxes around objects you want to track. The YOLOE model will then use these visual prompts to detect and track similar objects in the live video stream.

## Features

### Snapshot Capture
- **Capture Snapshot**: Takes a snapshot of the current camera feed when inference is stopped
- **Visual Display**: The snapshot is displayed on a canvas where you can draw bounding boxes

### Bounding Box Drawing
- **Mouse-based Drawing**: Click and drag on the snapshot canvas to draw bounding boxes
- **Multiple Boxes**: Draw multiple boxes to indicate different objects or multiple instances
- **Visual Feedback**: Boxes are drawn in lime green color with 2px borders
- **Clear Boxes**: Remove all drawn boxes with the "Clear Boxes" button

### Visual Prompt Activation
- **Save Snapshot with Boxes**: Captures the drawn bounding boxes and uses them as visual prompts
- **Model Re-export**: The ONNX model is re-exported with the visual prompts baked in
- **Tracking Mode**: The model will track objects similar to those in the visual prompts

### Mode Switching
- **Text Prompting Mode**: Use comma-separated class names (default: "person, plant")
- **Visual Prompting Mode**: Use captured snapshot with bounding boxes
- **Seamless Switching**: Switch between modes by updating classes or saving visual prompts
- **Clear Visual Prompt**: Return to text prompting mode anytime

## How to Use

### Step 1: Prepare for Snapshot
1. Stop inference if it's currently running
2. Ensure your camera is positioned to capture the objects you want to track
3. Make sure the objects are clearly visible in the frame

### Step 2: Capture Snapshot
1. Click the **"Capture Snapshot"** button
2. The current camera frame will be captured and displayed on the canvas
3. The snapshot canvas will appear with a crosshair cursor

### Step 3: Draw Bounding Boxes
1. Click and drag on the snapshot canvas to draw a bounding box
2. Position the box around the object you want to track
3. Release the mouse to save the box
4. Repeat to draw multiple boxes for different objects
5. Use **"Clear Boxes"** if you need to start over

### Step 4: Save Visual Prompt
1. Once you've drawn all desired boxes, click **"Save Snapshot with Boxes"**
2. The application will:
   - Delete the cached ONNX model
   - Re-export the model with visual prompts
   - Warm up the model (this may take 1-2 minutes)
3. The status will change to "Visual Prompting" mode

### Step 5: Start Inference
1. Click **"Start Inference"**
2. The model will now track objects similar to those in your visual prompts
3. Detected objects will be highlighted with green bounding boxes

### Returning to Text Prompting
1. Stop inference if running
2. Click **"Clear Visual Prompt"** to remove visual prompts
3. The application will return to text prompting mode
4. Update the class names using the "Custom Classes" field if desired

## Technical Details

### Visual Prompt Processing
1. **Snapshot Storage**: The captured frame is stored in memory as `snapshot_frame`
2. **Box Normalization**: Bounding boxes are normalized to 0-1 range relative to image dimensions
3. **Model Configuration**: Visual prompts are passed to the YOLOE model using:
   - `set_prompts(image, boxes)` if available
   - `get_visual_pe(image, boxes)` for visual prompt embeddings
   - Fallback to generic "object" class if visual prompting not supported

### Model Export Process
When visual prompts are saved:
1. The cached ONNX model is deleted
2. The PyTorch model is loaded
3. Visual prompts are configured
4. Model is exported to ONNX format with prompts baked in
5. Model is warmed up for instant inference

### API Compatibility
The implementation supports multiple YOLOE APIs:
- **Primary**: `set_prompts(image, boxes)` - Direct visual prompt setting
- **Secondary**: `get_visual_pe(image, boxes)` - Visual prompt embedding extraction
- **Fallback**: `get_text_pe(["object"])` - Generic object detection if visual prompting not available

## User Interface

### Control Sections

#### 1. Status & Controls
- Shows current inference status (Running/Stopped)
- Shows current model (YoloE-11S/M/L)
- Shows prompt mode (Text Prompting/Visual Prompting)
- Start/Stop inference buttons

#### 2. Configuration
- Camera selection dropdown
- Model selection dropdown (S, M, L)

#### 3. Text Prompting
- Text field for comma-separated class names
- "Update Classes" button to apply changes

#### 4. Visual Prompting
- "Capture Snapshot" button
- Canvas for drawing bounding boxes
- "Clear Boxes" button
- "Save Snapshot with Boxes" button
- "Clear Visual Prompt" button
- Box counter showing number of drawn boxes

#### 5. Live Feed
- Real-time video stream with detected objects

## Limitations

1. **Inference Must Be Stopped**: All configuration changes require inference to be stopped
2. **Model Re-export**: Changing prompts requires re-exporting the ONNX model (10-30 seconds)
3. **Warm-up Time**: After changing prompts, the model needs to warm up (~2 minutes)
4. **Box Size**: Very small boxes (< 1% of image size) are ignored
5. **Single Snapshot**: Only one snapshot can be active at a time

## Best Practices

1. **Clear Objects**: Capture snapshots with clear, well-lit objects
2. **Tight Boxes**: Draw bounding boxes tightly around objects
3. **Multiple Angles**: For better tracking, capture objects from the angle you'll use in inference
4. **Similar Lighting**: Keep lighting conditions similar between snapshot and inference
5. **Multiple Boxes**: Draw boxes around multiple instances for better generalization

## Troubleshooting

### Snapshot Not Appearing
- Ensure inference is stopped before capturing
- Check that your camera is working properly
- Try switching to a different camera

### Boxes Not Drawing
- Ensure you've captured a snapshot first
- Check that inference is stopped
- Try reloading the page

### Objects Not Being Tracked
- Ensure boxes are drawn tightly around objects
- Try capturing a clearer snapshot
- Draw multiple boxes for better results
- Consider using text prompting if visual prompting doesn't work well

### Model Re-export Takes Too Long
- This is normal; the process includes:
  - Deleting cached model
  - Loading PyTorch model
  - Configuring prompts
  - Exporting to ONNX
  - Warming up (~2 minutes)
- Be patient and wait for "Visual prompts set successfully" message

## Example Use Cases

### 1. Person Tracking
- Capture a snapshot with a person in frame
- Draw a box around the person
- Model will track all people in the scene

### 2. Object Detection
- Capture a snapshot with a specific object (e.g., a cup)
- Draw a box around the object
- Model will detect similar objects

### 3. Multi-Object Tracking
- Capture a snapshot with multiple object types
- Draw boxes around each object type
- Model will track all similar objects

### 4. Pet Monitoring
- Capture a snapshot of your pet
- Draw a box around the pet
- Model will track your pet's movement

## Compatibility with Other Features

Visual prompting works seamlessly with:
- ✓ Camera switching (stop inference, switch camera, capture new snapshot)
- ✓ Model switching (S, M, L models all support visual prompting)
- ✓ Text prompting (can switch back and forth)
- ✓ Tracker reset (tracker resets when switching cameras)
- ✓ Model caching (ONNX models are cached per configuration)

## Technical Architecture

### State Management
```python
# Global state variables
snapshot_frame = None          # Captured snapshot image
snapshot_boxes = []           # List of bounding boxes [(x1,y1,x2,y2), ...]
use_visual_prompt = False     # Flag indicating current mode
```

### Routes
- `GET /` - Main page with UI
- `POST /capture_snapshot` - Capture current frame
- `GET /snapshot_image` - Serve snapshot as JPEG
- `POST /save_visual_prompt` - Save boxes and configure model
- `POST /clear_visual_prompt` - Clear visual prompts
- `GET /video_feed` - Live video stream

### JavaScript Components
- Canvas drawing with mouse events
- Box storage and normalization
- Visual feedback during drawing
- Box counter display

## Future Enhancements

Potential improvements for future versions:
- Support for box editing (move, resize, delete individual boxes)
- Multiple snapshots for better generalization
- Visual prompt templates (save and load common prompts)
- Real-time preview of tracking results
- Confidence threshold adjustment per box
- Color coding for different object types
