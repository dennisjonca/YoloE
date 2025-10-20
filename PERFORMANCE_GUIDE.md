# YoloE Performance Guide

## Understanding Tracking Performance

The YoloE application uses YOLO (You Only Look Once) object detection with tracking. Sometimes objects may not be tracked due to various factors related to detection parameters, hardware performance, or scene complexity.

## Key Detection Parameters

### Confidence Threshold (`conf`)
The confidence threshold determines how certain the model must be before reporting a detection.

**Range:** 0.0 - 1.0

**Recommended Values:**
- **0.15 - 0.25**: More sensitive detection, catches more objects but may include false positives
- **0.25 - 0.40**: Balanced detection (recommended for most scenarios)
- **0.40 - 0.60**: High confidence only, fewer false positives but may miss some objects

**If objects are not being detected:**
- Try **lowering** the confidence threshold (e.g., from 0.25 to 0.15)
- Monitor for false positives (incorrect detections)
- Lower values work better for:
  - Small objects
  - Partially occluded objects
  - Objects at unusual angles
  - Low-light conditions

### IoU Threshold (`iou`)
The Intersection over Union (IoU) threshold controls how overlapping bounding boxes are merged during Non-Maximum Suppression (NMS).

**Range:** 0.0 - 1.0

**Recommended Values:**
- **0.40 - 0.50**: More lenient, allows more overlapping detections
- **0.50 - 0.60**: Standard setting (recommended)
- **0.60 - 0.70**: Strict, only keeps very distinct detections

**If multiple objects appear as one:**
- Try **lowering** the IoU threshold (e.g., from 0.45 to 0.35)

**If too many duplicate boxes around one object:**
- Try **raising** the IoU threshold (e.g., from 0.45 to 0.55)

## Hardware Performance Impact

### CPU vs GPU Inference

**CPU-based Inference:**
- Typical inference time: 50-200ms per frame
- Typical FPS: 5-20 FPS
- Suitable for: Real-time monitoring with smaller models (YoloE-11s)
- Limitations: May struggle with larger models or high-resolution video

**GPU-based Inference (CUDA):**
- Typical inference time: 5-30ms per frame
- Typical FPS: 30-60+ FPS
- Suitable for: High-performance applications, larger models, multiple streams
- Requirements: NVIDIA GPU with CUDA support

### Checking Your Hardware

The application automatically detects and displays your hardware in the web interface:
- **CPU mode**: Shows "⚙️ CPU (X cores)"
- **GPU mode**: Shows "⚙️ GPU: [GPU Name] (X cores)"

### Performance Metrics

The application displays real-time performance metrics on the video feed:
- **FPS**: Frames processed per second
- **Inference**: Time taken for model inference per frame (in milliseconds)
- **Detections**: Number of objects detected in the current frame

**Performance Indicators:**
- **Good performance**: FPS > 15, Inference < 100ms
- **Acceptable performance**: FPS 10-15, Inference 100-200ms
- **Poor performance**: FPS < 10, Inference > 200ms

## Model Size Impact

The application supports three model sizes, each with different accuracy/speed tradeoffs:

### YoloE-11s (Small)
- **Size**: ~25MB
- **Speed**: Fastest (5-20ms on GPU, 30-100ms on CPU)
- **Accuracy**: Good for common objects
- **Recommended for**: Real-time applications, CPU inference, resource-constrained systems

### YoloE-11m (Medium)
- **Size**: ~50MB
- **Speed**: Moderate (10-40ms on GPU, 100-200ms on CPU)
- **Accuracy**: Better for complex scenes
- **Recommended for**: Balanced performance, GPU inference

### YoloE-11l (Large)
- **Size**: ~100MB
- **Speed**: Slower (20-80ms on GPU, 200-400ms on CPU)
- **Accuracy**: Best for difficult detections
- **Recommended for**: High accuracy requirements, powerful GPU available

## Troubleshooting: Objects Not Being Tracked

### Problem: No detections at all

**Possible causes:**
1. **Confidence threshold too high**
   - Solution: Lower confidence to 0.15-0.20
   
2. **Wrong object classes**
   - Solution: Verify the class names match what you're trying to detect
   - Example: If detecting cars, make sure "car" or "vehicle" is in your class list

3. **Visual prompting not well defined**
   - Solution: Draw clearer bounding boxes around objects in the snapshot
   - Solution: Include multiple examples of the object you want to track

4. **Objects too small or too far**
   - Solution: Move objects closer to camera
   - Solution: Use larger model (YoloE-11m or YoloE-11l)

### Problem: Intermittent detections (objects appear/disappear)

**Possible causes:**
1. **Confidence threshold at borderline**
   - Solution: Lower confidence slightly (e.g., from 0.25 to 0.20)
   
2. **Motion blur or low light**
   - Solution: Improve lighting conditions
   - Solution: Use slower camera movements
   - Solution: Lower confidence threshold

3. **Hardware performance issues**
   - Solution: Use smaller model (YoloE-11s)
   - Solution: Ensure no other CPU-intensive applications are running
   - Solution: Consider upgrading to GPU if on CPU

### Problem: Too many false positives

**Possible causes:**
1. **Confidence threshold too low**
   - Solution: Raise confidence to 0.30-0.40
   
2. **Background confusion**
   - Solution: Simplify background or improve lighting
   - Solution: Use more specific class names

## Visual Prompting vs Text Prompting

### Text Prompting (Recommended for common objects)
- **Pros**: Fast, reliable for known object classes
- **Cons**: Limited to predefined classes in YOLO training
- **Best for**: Common objects like "person", "car", "dog", "cat", "bottle"

### Visual Prompting (Recommended for specific/unusual objects)
- **Pros**: Can detect any object by example
- **Cons**: Requires good reference images, more sensitive to lighting/angle changes
- **Best for**: Specific items, unusual objects, custom objects

**Tips for visual prompting:**
1. Capture snapshot with good lighting
2. Draw tight bounding boxes around the object
3. Include multiple examples if object appears in different orientations
4. Ensure object is clearly visible (not occluded)
5. Start with larger, more distinct objects

## Hardware Upgrade Recommendations

### If you're experiencing poor performance:

**Current setup: CPU only**
- **Budget option**: Upgrade to a desktop with modern CPU (Intel i5/i7 or AMD Ryzen 5/7)
- **Recommended option**: Add NVIDIA GPU (minimum GTX 1650, recommended RTX 3060 or better)
- **Expected improvement**: 5-10x faster inference, enabling larger models and higher FPS

**Current setup: Older GPU**
- **Upgrade to**: NVIDIA RTX 30-series or 40-series
- **Expected improvement**: 2-5x faster inference, better support for larger models

**Current setup: Modern GPU but still slow**
- Check if CUDA is properly installed and detected
- Verify PyTorch is using GPU (check hardware status in UI)
- Close other GPU-intensive applications
- Consider using smaller model or lowering resolution

## Best Practices

1. **Start with default parameters** (conf=0.25, iou=0.45) and adjust based on results
2. **Monitor performance metrics** displayed on the video feed
3. **Use smallest model** that meets your accuracy requirements
4. **Ensure good lighting** for better detection
5. **Keep objects at reasonable distance** from camera
6. **For text prompting**: Use specific, common class names
7. **For visual prompting**: Provide clear examples with tight bounding boxes
8. **Test different confidence levels** if objects aren't being detected
9. **Check hardware status** - GPU provides much better performance than CPU

## Performance Optimization Checklist

- [ ] Verify hardware being used (CPU vs GPU)
- [ ] Select appropriate model size for your hardware
- [ ] Adjust confidence threshold based on detection results
- [ ] Ensure good lighting conditions
- [ ] Close unnecessary background applications
- [ ] Use text prompting for common objects
- [ ] Use visual prompting with clear examples
- [ ] Monitor FPS and inference time on video feed
- [ ] Consider hardware upgrade if consistently <10 FPS

## Getting Help

If you're still experiencing tracking issues after trying these solutions:

1. **Check the status display** in the web interface
2. **Review the performance metrics** on the video feed
3. **Try different detection parameters** systematically
4. **Verify your hardware** capabilities
5. **Report issues** with:
   - Hardware information (CPU/GPU model)
   - Model size being used
   - Detection parameters (conf, iou)
   - Performance metrics (FPS, inference time)
   - Description of what you're trying to detect
   - Whether using text or visual prompting
