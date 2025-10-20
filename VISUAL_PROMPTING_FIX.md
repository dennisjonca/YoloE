# Visual Prompting Fix - Implementation Details

## Problem Statement

The visual prompting feature was not working correctly. It would fall back to generic object detection instead of using the visual prompts provided through the UI. The logs showed:

```
[WARN] Visual prompting not directly supported, using fallback
```

After investigation, the root cause was identified: **the implementation was not using the official YOLOE visual prompting API correctly**.

## Root Causes

The original implementation had several issues:

1. **Wrong Method**: Used `track()` instead of `predict()` with `YOLOEVPSegPredictor`
2. **Wrong API Pattern**: Tried to call `set_prompts()` on the model during loading, but the API requires passing `visual_prompts` parameter to `predict()`
3. **Wrong Coordinate System**: Normalized boxes to 0-1 range, but the API expects absolute pixel coordinates
4. **Missing Class IDs**: Didn't provide the `cls` parameter which is required by the API
5. **Wrong Model Type**: Tried to export to ONNX with visual prompts baked in, but visual prompts need to be passed per-frame

## Solution

### Official YOLOE Visual Prompting API

According to the official Ultralytics documentation, visual prompting should be used like this:

```python
import numpy as np
from ultralytics import YOLOE
from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor

# Define visual prompts
visual_prompts = dict(
    bboxes=[
        np.array([[x1, y1, x2, y2], ...]),  # Absolute pixel coordinates
    ],
    cls=[
        np.array([0, 1, ...]),  # Class IDs for each box
    ],
)

# Run inference with visual prompts
results = model.predict(
    source=image,
    visual_prompts=visual_prompts,
    predictor=YOLOEVPSegPredictor,
)
```

Key observations:
- Uses `predict()`, not `track()`
- Passes `visual_prompts` as a parameter to `predict()`
- Uses `YOLOEVPSegPredictor` explicitly
- Boxes are in absolute pixel coordinates (not normalized)
- Includes class IDs (`cls` parameter)

### Implementation Changes

#### 1. Updated `load_model()` Function

**Before:**
- Tried to call `model.set_prompts(image_tensor, boxes_tensor)`
- Exported model to ONNX with prompts baked in
- Normalized boxes to 0-1 range

**After:**
- For visual prompting: loads PyTorch model (not ONNX)
- Validates visual prompt data structure
- Does NOT try to set prompts on the model during loading
- Keeps boxes in absolute pixel coordinates
- Separate warm-up for visual prompting using `predict()` with `YOLOEVPSegPredictor`

```python
if visual_prompt_data is not None:
    # Load PyTorch model for visual prompting
    loaded_model = YOLOE(pt_model_path)
    # Validate but don't configure - prompts passed per-frame
else:
    # Load ONNX model for text prompting (performance)
    if os.path.exists(onnx_model_path):
        loaded_model = YOLOE(onnx_model_path)
```

#### 2. Added Visual Prompt Dictionary

New global variable to store visual prompts in the official API format:

```python
visual_prompt_dict = None  # Dict with 'bboxes' and 'cls' for predict() API
```

Format:
```python
visual_prompt_dict = {
    'bboxes': [[x1, y1, x2, y2], ...],  # List of lists
    'cls': [0, 1, ...]  # List of integers (0-based class IDs)
}
```

#### 3. Updated Inference Thread

**Before:**
- Always used `model.track()` for both modes

**After:**
- Branches based on `use_visual_prompt` flag
- Visual mode: uses `model.predict()` with `YOLOEVPSegPredictor`
- Text mode: continues using `model.track()` for continuous tracking

```python
if use_visual_prompt and visual_prompt_dict is not None:
    # Visual prompting mode
    from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor
    results = model.predict(
        source=frame,
        visual_prompts=visual_prompt_dict,
        predictor=YOLOEVPSegPredictor,
        conf=current_conf,
        show=False,
        verbose=False
    )
else:
    # Text prompting mode
    results = model.track(
        source=frame,
        conf=current_conf,
        iou=current_iou,
        show=False,
        persist=True
    )
```

#### 4. Updated `/save_visual_prompt` Route

**Before:**
- Normalized boxes to 0-1 range
- Tried various coordinate formats (xyxy, cxcywh)
- Attempted to call `set_prompts()` on the model

**After:**
- Keeps boxes in absolute pixel coordinates (no normalization)
- Creates visual prompt dictionary in official API format
- Assigns class ID 0 to all boxes
- Loads PyTorch model for visual prompting

```python
# Convert from relative UI coordinates to absolute pixel coordinates
snapshot_boxes = []
for box in boxes_data:
    x1 = int(box['x1'] * w)
    y1 = int(box['y1'] * h)
    x2 = int(box['x2'] * w)
    y2 = int(box['y2'] * h)
    snapshot_boxes.append([x1, y1, x2, y2])

# Create visual prompt dictionary (official API format)
# Note: For single image, use flat lists (not nested arrays)
bboxes_list = [box for box in snapshot_boxes]  # List of [x1,y1,x2,y2]
cls_list = [0] * len(snapshot_boxes)  # List of integers (all 0 for generic)

visual_prompt_dict = {
    'bboxes': bboxes_list,
    'cls': cls_list
}
```

#### 5. Updated `/clear_visual_prompt` Route

Added clearing of `visual_prompt_dict` to ensure complete state reset.

## Technical Details

### Why Use `predict()` Instead of `track()`?

- **`track()`**: Designed for continuous video tracking with object IDs across frames
- **`predict()`**: Designed for single-frame inference, which is what visual prompting is built for
- Visual prompting in YOLOE is designed to work with `predict()` and the `YOLOEVPSegPredictor` class

### Why Absolute Coordinates?

The official API expects boxes in absolute pixel coordinates because:
1. Visual prompts reference specific regions in a reference image
2. The predictor needs to extract features from those exact regions
3. Normalization is handled internally by the predictor

### Why PyTorch Model for Visual Prompting?

- Visual prompts need to be passed per-frame to `predict()`
- ONNX models have their inputs/outputs fixed at export time
- PyTorch models allow dynamic inputs, including the visual prompts parameter

### Why Use Integer Class IDs?

- Despite the documentation showing strings like `cls=["person"]`, the implementation expects integers
- The `get_visuals()` method tries to convert cls to `torch.tensor(category, dtype=torch.int)`
- Strings cause a "too many dimensions 'str'" error
- All boxes get class ID 0 for generic object detection
- The model internally maps these to `object0`, `object1`, etc.
- In the future, this could be extended to support multiple object classes with different IDs

## Testing

### Validation Tests

All structural tests pass:

```
✓ PASS: API Compatibility
✓ PASS: Inference Modes
✓ PASS: Coordinate Handling
✓ PASS: Model Loading
```

### Expected Behavior

1. **Capture Snapshot**: Take a photo from camera feed ✓
2. **Draw Boxes**: Draw bounding boxes on the snapshot ✓
3. **Save Visual Prompt**: Convert to absolute coordinates and create API-compliant dict ✓
4. **Load Model**: Load PyTorch model (not ONNX) ✓
5. **Run Inference**: Use `predict()` with `YOLOEVPSegPredictor` and visual prompts ✓
6. **Detect Objects**: Should now detect objects similar to those in the visual prompts ✓

## Backward Compatibility

All existing features continue to work:
- ✓ Text prompting with class names
- ✓ Camera switching
- ✓ Model switching (S, M, L)
- ✓ ONNX model caching for text prompting
- ✓ Object tracking with `track()`
- ✓ Detection parameter adjustment (conf, iou)

## Performance Considerations

### Visual Prompting Mode
- Uses PyTorch model (slightly slower than ONNX)
- Uses `predict()` per-frame (no cross-frame tracking)
- Suitable for detecting objects similar to visual examples

### Text Prompting Mode
- Uses ONNX model (faster inference)
- Uses `track()` with cross-frame tracking
- Suitable for continuous object tracking

## Usage

### How to Use Visual Prompting

1. **Stop inference** if running
2. **Click "Capture Snapshot"** to capture current frame
3. **Draw bounding boxes** around objects you want to track
   - Click and drag on the snapshot canvas
   - Draw multiple boxes for multiple objects
4. **Click "Save Snapshot with Boxes"**
   - This will load the PyTorch model
   - Create visual prompts in the correct format
   - Warm up the model (~30 seconds)
5. **Click "Start Inference"**
   - Model will use `predict()` with visual prompts
   - Objects similar to those in boxes should be detected

### Tips for Best Results

1. **Clear Examples**: Draw boxes tightly around clear, well-defined objects
2. **Good Lighting**: Capture snapshot in similar lighting to inference
3. **Multiple Examples**: Draw multiple boxes for better generalization
4. **Similar Angles**: Capture objects from the angle you'll use during inference
5. **Lower Confidence**: Start with lower confidence threshold (0.15-0.25) to see if detection works

## Troubleshooting

### No Detections with Visual Prompts

**Possible causes:**
1. Objects in video differ too much from snapshot examples
2. Confidence threshold too high
3. Lighting conditions changed
4. Objects at different scale/angle

**Solutions:**
1. Recapture snapshot with better examples
2. Lower confidence threshold to 0.15-0.25
3. Try capturing snapshot in similar conditions to inference
4. Draw multiple boxes at different scales/angles

### Slow Inference

**Expected behavior:**
- Visual prompting uses PyTorch model which is slower than ONNX
- No cross-frame tracking, so each frame is independent

**If too slow:**
- Switch to text prompting mode for faster inference
- Use smaller model (S instead of L)
- Increase confidence threshold to reduce detections

### Model Loading Takes Long

**Expected behavior:**
- First time loading PyTorch model may take 10-30 seconds
- Model warm-up takes ~30 seconds
- This only happens when switching modes

## Future Enhancements

Possible improvements:
1. **Multi-class Support**: Allow assigning different class IDs to different boxes
2. **Per-box Confidence**: Allow setting different confidence thresholds per box
3. **Template Matching**: Save visual prompts as templates for reuse
4. **Hybrid Mode**: Combine visual and text prompts
5. **Visual Prompt Refinement**: Allow editing boxes after saving

## Conclusion

The visual prompting feature now uses the official YOLOE API correctly:
- ✓ Uses `predict()` with `YOLOEVPSegPredictor`
- ✓ Passes visual prompts per-frame in correct format
- ✓ Keeps boxes in absolute pixel coordinates
- ✓ Provides class IDs for all boxes
- ✓ Loads appropriate model type for each mode

This should resolve the issue where visual prompting was falling back to generic object detection.
