# Live Heatmap Mode Feature

## Overview

The live heatmap mode feature extends the existing snapshot-based heatmap generation to support **real-time heatmap visualization** during live camera inference. Users can now toggle between normal detection view and heatmap view while the camera is streaming.

## What Changed

### Before
- Heatmaps could only be generated from static snapshots
- Required stopping inference, capturing a snapshot, and generating a heatmap
- No real-time visualization of model attention

### After
- Heatmaps can be generated in real-time during live inference
- Toggle between normal and heatmap mode with a single button
- See what the model focuses on in real-time as objects move
- Seamless switching between modes

## Features

### Live Heatmap Visualization
- **Real-time GradCAM**: See model attention updated every frame
- **Continuous Detection**: Boxes and labels overlaid on heatmap
- **Performance Metrics**: FPS, inference time, and detection count displayed
- **Mode Indicator**: Clear [HEATMAP] or [NORMAL] indicator on video feed

### Toggle Control
- **Enable/Disable Button**: Simple UI toggle when inference is stopped
- **Status Display**: Shows current heatmap mode (ON/OFF)
- **State Preservation**: Mode setting persists across inference sessions

### Performance Optimizations
- **Hardware Detection**: Automatically uses GPU if available
- **Efficient Processing**: Reuses heatmap generator instance
- **Error Handling**: Falls back to normal mode if heatmap fails

## Usage

### Enabling Live Heatmap Mode

1. **Stop inference** if it's currently running
2. Click the **"Enable Heatmap Mode"** button in the Status & Controls section
3. The status will change to show "Heatmap Mode: ON"
4. **Start inference** to see live heatmap visualization
5. The video feed will show [HEATMAP] indicator and colored attention overlay

### Disabling Live Heatmap Mode

1. **Stop inference** if it's currently running
2. Click the **"Disable Heatmap Mode"** button
3. The status will change to show "Heatmap Mode: OFF"
4. **Start inference** to return to normal detection view
5. The video feed will show [NORMAL] indicator

### Understanding the Heatmap

The live heatmap overlay shows:
- **Red/Yellow regions**: Areas the model focuses on most (high attention)
- **Blue/Purple regions**: Areas the model pays less attention to
- **Green boxes**: Detected objects with labels and confidence
- **Renormalized attention**: Attention values normalized within detection boxes

## Technical Details

### Architecture

The live heatmap mode is integrated into the existing inference thread:

```
┌─────────────────────────────────────┐
│     User clicks "Enable Heatmap"     │
│     (when inference stopped)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   heatmap_mode = True                │
│   (global flag set)                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   User clicks "Start Inference"      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   inference_thread() starts          │
│   - Detects heatmap_mode = True      │
│   - Initializes YoloEHeatmapGenerator│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Main inference loop:               │
│   For each frame:                    │
│     1. Read from camera              │
│     2. Preprocess (letterbox, RGB)   │
│     3. Generate GradCAM              │
│     4. Create heatmap overlay        │
│     5. Run object detection          │
│     6. Draw bounding boxes           │
│     7. Display on video feed         │
└─────────────────────────────────────┘
```

### Implementation Details

#### State Variables

```python
heatmap_mode = False  # Toggle flag for live heatmap
heatmap_generator = None  # HeatmapGenerator instance
```

#### Inference Thread Integration

The `inference_thread()` function checks the `heatmap_mode` flag at startup:

1. **Heatmap Mode ON**: 
   - Initializes `YoloEHeatmapGenerator` with optimal settings
   - Processes each frame through GradCAM pipeline
   - Overlays heatmap on original image
   - Adds detection boxes and labels

2. **Heatmap Mode OFF**:
   - Uses standard YOLO tracking/prediction
   - Shows normal detection boxes
   - Standard performance characteristics

#### Heatmap Generation Pipeline

For each frame in heatmap mode:

```python
# 1. Preprocess image
img = letterbox(frame)[0]
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_float = np.float32(img_rgb) / 255.0
tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0)

# 2. Generate GradCAM
grayscale_cam = heatmap_generator.method(tensor, [heatmap_generator.target])

# 3. Create overlay
cam_image = show_cam_on_image(img_float, grayscale_cam, use_rgb=True)

# 4. Run detection
results = heatmap_generator.yolo_model.predict(frame, conf=current_conf)

# 5. Renormalize and draw boxes
cam_image = heatmap_generator.renormalize_cam_in_bounding_boxes(boxes, img_float, grayscale_cam)

# 6. Draw detection boxes
for box in boxes:
    cam_image = heatmap_generator.draw_detections(box, color, label, cam_image)

# 7. Convert back to BGR for display
frame = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)
```

### UI Changes

#### Status Section
```html
<h3>Heatmap Mode: ON/OFF</h3>
<form action="/toggle_heatmap" method="post">
    <input type="submit" value="Enable/Disable Heatmap Mode">
</form>
```

#### Video Feed Indicator
```python
mode_indicator = "HEATMAP" if heatmap_mode else "NORMAL"
perf_text = f"[{mode_indicator}] FPS: {fps} | ..."
```

### New Route

```python
@app.route('/toggle_heatmap', methods=['POST'])
def toggle_heatmap():
    """Toggle heatmap mode on/off."""
    global heatmap_mode
    if running:
        return "Stop inference first!"
    heatmap_mode = not heatmap_mode
    return redirect('/')
```

## Performance Considerations

### Expected Performance

- **CPU Mode**: 2-5 FPS (depending on CPU speed)
- **GPU Mode**: 10-20 FPS (with dedicated GPU)
- **Inference Time**: 200-500ms per frame (heatmap mode)
- **Normal Mode**: 15-30 FPS (for comparison)

### Performance Impact

Heatmap mode is computationally intensive:
- **GradCAM computation**: Requires forward and backward passes
- **Gradient calculation**: Needs gradient computation enabled
- **Image processing**: Additional preprocessing and overlay rendering
- **Memory usage**: ~2x normal mode (gradients + activations)

### Optimization Tips

1. **Use GPU**: 5-10x faster than CPU
2. **Reduce confidence**: Lower thresholds = more detections = slower
3. **Close other apps**: Free up system resources
4. **Use smaller model**: yoloe-11s is faster than 11m or 11l
5. **Adjust layers**: Fewer target layers = faster GradCAM

## Troubleshooting

### Common Issues

**Issue**: FPS drops significantly in heatmap mode
```
Expected: Heatmap mode is slower than normal mode
Solution: Use GPU if available, or accept lower FPS
Normal FPS: 15-30 | Heatmap FPS: 2-10
```

**Issue**: "Failed to initialize heatmap generator"
```
Possible causes:
- Model file missing
- Insufficient memory
- GPU out of memory
Check console for detailed error, falls back to normal mode
```

**Issue**: Heatmap shows random noise
```
Possible causes:
- GradCAM method incompatible
- Model architecture issue
Fallback: Shows simple activation pattern
```

**Issue**: Toggle button doesn't work
```
Reason: Can only toggle when inference is stopped
Solution: Click "Stop Inference" first, then toggle
```

**Issue**: Video feed frozen in heatmap mode
```
Possible causes:
- Camera disconnected
- Out of memory
Check console for errors, restart application
```

## Comparing Modes

### Normal Mode
✓ Fast (15-30 FPS)  
✓ Low resource usage  
✓ Clear detection boxes  
✗ No attention visualization  

### Heatmap Mode
✓ Visual explanation of detections  
✓ See model focus areas  
✓ Debug model behavior  
✗ Slower (2-10 FPS)  
✗ Higher resource usage  

## Use Cases

### 1. Model Understanding
**Scenario**: Want to understand why model detects certain objects  
**Solution**: Enable heatmap mode to see attention regions  
**Example**: See that model focuses on car wheels, not entire car

### 2. Debugging False Positives
**Scenario**: Model detecting objects that aren't there  
**Solution**: Check heatmap to see what model is looking at  
**Example**: False person detection shows attention on tree shadows

### 3. Model Comparison
**Scenario**: Comparing different model sizes (s, m, l)  
**Solution**: Enable heatmap mode for each, compare attention  
**Example**: Larger models may have more precise attention

### 4. Training Data Analysis
**Scenario**: Improving training dataset  
**Solution**: Analyze heatmap patterns to identify weaknesses  
**Example**: Model ignores certain object features → add training data

### 5. Demo and Presentation
**Scenario**: Explaining AI to non-technical audience  
**Solution**: Toggle between normal and heatmap to show "what model sees"  
**Example**: Live demonstration of attention mechanism

## Testing

### Manual Testing Checklist

- [ ] Toggle heatmap mode when inference stopped
- [ ] Verify status shows "Heatmap Mode: ON"
- [ ] Start inference in heatmap mode
- [ ] Verify [HEATMAP] indicator on video feed
- [ ] Verify colored overlay appears
- [ ] Verify detection boxes still work
- [ ] Stop inference
- [ ] Disable heatmap mode
- [ ] Verify status shows "Heatmap Mode: OFF"
- [ ] Start inference in normal mode
- [ ] Verify [NORMAL] indicator

### Automated Testing

Run the test suite:
```bash
python test_live_heatmap_lightweight.py
```

Tests verify:
- Core imports work
- Code structure correct
- Integration logic present
- UI elements added

## Future Enhancements

Potential improvements for future versions:

1. **Adjustable FPS**: Reduce GradCAM frequency (e.g., every 3rd frame)
2. **Color schemes**: Different heatmap color palettes
3. **Layer selection**: UI to choose which layers to visualize
4. **Dual view**: Side-by-side normal and heatmap
5. **Recording**: Save heatmap video to file
6. **Attention statistics**: Show attention distribution graphs
7. **Comparison mode**: Compare attention across different models

## References

- Original heatmap feature: `HEATMAP_FEATURE.md`
- GradCAM paper: https://arxiv.org/abs/1610.02391
- pytorch-grad-cam: https://github.com/jacobgil/pytorch-grad-cam

## Related Files

- `app.py` - Main application with live heatmap integration
- `heatmap_generator.py` - Heatmap generation module
- `test_live_heatmap_lightweight.py` - Test suite for live mode
- `HEATMAP_FEATURE.md` - Original snapshot-based heatmap docs

## Summary

The live heatmap mode transforms the snapshot-based heatmap feature into a real-time visualization tool. Users can now see what the YOLO model focuses on as objects move through the camera frame, making it easier to understand, debug, and demonstrate the model's behavior.

**Key Benefits:**
- Real-time attention visualization
- Simple toggle interface
- Seamless mode switching
- Performance monitoring
- Educational and debugging tool
