# Visual Prompting Usage Guide

## Overview

Visual prompting is now fully functional! This guide explains how to use the feature and what to expect.

## How It Works

Visual prompting allows you to "teach" the YOLOE model what to detect by example:
1. Capture a snapshot from your camera
2. Draw bounding boxes around objects you want to track
3. The model uses these examples to detect similar objects in real-time

## Step-by-Step Usage

### 1. Stop Inference

Before capturing a snapshot, make sure inference is stopped:
- Click **"Stop Inference"** if it's currently running
- Wait for the status to show "Stopped"

### 2. Capture Snapshot

- Click **"Capture Snapshot"** button
- The current camera frame will be displayed on the canvas
- You can now draw on this snapshot

### 3. Draw Bounding Boxes

- Click and drag on the snapshot canvas to draw a box
- Position the box tightly around the object you want to track
- Release the mouse to save the box
- Draw multiple boxes for:
  - Multiple instances of the same object
  - Different objects you want to track
- Click **"Clear Boxes"** if you need to start over

### 4. Save Visual Prompts

- Once you've drawn all desired boxes, click **"Save Snapshot with Boxes"**
- The application will:
  - Load the PyTorch model (takes ~10-30 seconds)
  - Prepare visual prompts in the correct format
  - Warm up the model (takes ~30 seconds)
- Status will change to "Visual Prompting" mode
- You'll see "Visual Prompts Active: X boxes" in the status

### 5. Start Inference

- Click **"Start Inference"**
- The model will now detect objects similar to those in your visual prompts
- Detections will be shown with green bounding boxes
- Performance metrics displayed: FPS, inference time, detection count

### 6. Adjust Settings for Better Results

If you're not seeing detections:

#### Lower the Confidence Threshold
- Stop inference
- Set **Confidence Threshold** to `0.15` or `0.20`
- Click **"Update Parameters"**
- Start inference again

#### Recapture with Better Examples
- Stop inference
- Click **"Capture Snapshot"** again
- Draw boxes around clearer, better-lit objects
- Make sure boxes are tight around objects
- Draw multiple examples if possible

### 7. Return to Text Prompting (Optional)

To switch back to text-based class detection:
- Stop inference
- Click **"Clear Visual Prompt"**
- Update class names in the "Custom Classes" field
- Start inference again

## Tips for Best Results

### Snapshot Quality
- ✓ Capture in good lighting conditions
- ✓ Objects should be clearly visible
- ✓ Similar angle/distance to what you'll use during inference
- ✗ Avoid blurry or poorly lit snapshots

### Bounding Box Drawing
- ✓ Draw boxes tightly around objects
- ✓ Include the entire object within the box
- ✓ Draw multiple boxes for better generalization
- ✗ Don't make boxes too small or too large

### Detection Parameters
- Start with **Confidence: 0.15-0.25** for visual prompting
- Use **Confidence: 0.25-0.40** for normal detection
- Adjust **IoU: 0.40-0.50** if you're getting duplicate detections

### Model Selection
- **YoloE-11S**: Fastest, good for real-time (default)
- **YoloE-11M**: Balanced speed/accuracy
- **YoloE-11L**: Most accurate, but slower

## Technical Details

### What Happens Behind the Scenes

1. **Box Conversion**: UI relative coordinates → absolute pixel coordinates
2. **Visual Prompt Format**: 
   ```python
   {
       'bboxes': [[x1, y1, x2, y2], ...],  # Absolute coordinates
       'cls': [0, 0, ...]  # Integer class IDs
   }
   ```
3. **Model Loading**: PyTorch model loaded (not ONNX for visual prompting)
4. **Inference**: Uses `predict()` with `YOLOEVPSegPredictor` per-frame

### Performance Considerations

#### Visual Prompting Mode
- Uses PyTorch model (slower than ONNX)
- Per-frame inference (no cross-frame tracking)
- Best for: Detecting specific objects by example
- Typical FPS: 5-15 FPS on CPU, 30+ FPS on GPU

#### Text Prompting Mode
- Uses ONNX model (faster)
- Cross-frame tracking enabled
- Best for: General object detection with known classes
- Typical FPS: 10-20 FPS on CPU, 60+ FPS on GPU

### Why Visual Prompting vs Text Prompting?

**Use Visual Prompting when:**
- You have a specific object to detect
- The object doesn't have a standard class name
- You want to detect your custom objects (e.g., specific product, tool, etc.)
- You have a good example image

**Use Text Prompting when:**
- Detecting common objects (person, car, dog, etc.)
- You need faster inference
- You want cross-frame tracking with IDs
- You can describe objects with class names

## Troubleshooting

### No Detections

**Problem**: Model doesn't detect anything after starting inference

**Solutions**:
1. Lower confidence threshold to 0.15-0.20
2. Recapture snapshot with clearer examples
3. Draw more boxes around the objects
4. Ensure lighting is similar between snapshot and inference
5. Try a larger model (M or L)

### Slow Inference

**Problem**: FPS is very low

**Solutions**:
1. Switch to smaller model (S instead of L)
2. Increase confidence threshold to reduce detections
3. Use text prompting mode for better performance
4. Check if GPU is available (CPU is slower)

### Wrong Objects Detected

**Problem**: Model detects objects that aren't in your visual prompts

**Solutions**:
1. Increase confidence threshold
2. Recapture with more specific examples
3. Draw boxes more tightly around target objects
4. Use multiple clear examples

### Model Loading Takes Too Long

**Problem**: "Save Snapshot with Boxes" takes a long time

**Expected Behavior**:
- This is normal for first-time loading
- PyTorch model: 10-30 seconds to load
- Model warm-up: ~30 seconds
- Total: ~1 minute

**If too slow**:
- Be patient - this only happens when switching modes
- Subsequent inferences will be fast
- Consider using text prompting if you need instant switching

## Examples

### Example 1: Detecting Your Pet

1. Stop inference
2. Capture snapshot with your pet in frame
3. Draw tight box around your pet
4. Save visual prompts (wait ~1 minute)
5. Start inference
6. Model will detect your pet in real-time

### Example 2: Detecting Specific Objects

1. Stop inference
2. Capture snapshot with your target object
3. Draw boxes around multiple instances if available
4. Adjust confidence to 0.20
5. Save and start inference
6. Model detects similar objects

### Example 3: Multi-Object Tracking

1. Stop inference
2. Capture snapshot with multiple object types
3. Draw boxes around each object type
4. Save visual prompts
5. Start inference
6. Model tracks all similar objects

## FAQ

### Q: Can I use visual prompting with text prompting?
**A**: Not simultaneously. You can switch between modes, but only one is active at a time.

### Q: How many boxes can I draw?
**A**: No strict limit, but 1-5 boxes typically work best. More boxes = more processing.

### Q: Can I edit boxes after drawing?
**A**: Not yet. Click "Clear Boxes" and redraw if needed.

### Q: Does it work with high-resolution cameras?
**A**: Yes! The snapshot is automatically resized to match the model's input size.

### Q: Can I save visual prompts for later?
**A**: Not yet. This is a potential future enhancement.

### Q: Why is visual prompting slower than text prompting?
**A**: Visual prompting uses the PyTorch model and per-frame inference, while text prompting uses optimized ONNX model with cross-frame tracking.

## Known Limitations

1. **Single snapshot only**: Can't use multiple snapshots for better generalization
2. **All boxes same class**: All boxes get class ID 0 (generic object)
3. **No box editing**: Must clear and redraw if mistakes
4. **No template saving**: Visual prompts not persisted between sessions
5. **Slower than text prompting**: PyTorch model is slower than ONNX

## Future Enhancements

Potential improvements in future versions:
- Multi-class support (assign different IDs to different boxes)
- Box editing (move, resize, delete individual boxes)
- Template saving and loading
- Multiple snapshot support
- Hybrid visual + text prompting
- Real-time detection preview during box drawing

## Summary

Visual prompting is now fully functional and provides a powerful way to detect custom objects by example. Follow the steps in this guide for best results, and don't hesitate to adjust parameters if needed!

**Key Takeaways**:
- ✓ Capture clear snapshots in good lighting
- ✓ Draw tight boxes around target objects  
- ✓ Use confidence 0.15-0.25 for visual prompting
- ✓ Be patient during initial model loading (~1 minute)
- ✓ Switch to text prompting for better performance if needed
