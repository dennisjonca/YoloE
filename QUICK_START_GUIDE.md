# Quick Start Guide - Performance Tuning

## Problem: Objects Not Being Tracked?

If your inference sometimes doesn't track objects, here's how to fix it:

### Step 1: Check Detection Count

Start inference and look at the video feed. You'll see:
```
FPS: 15.3 | Inference: 65.4ms | Detections: 0
Conf: 0.25 | IoU: 0.45
```

If **Detections: 0**, proceed to Step 2.

### Step 2: Adjust Confidence Threshold

1. Stop inference
2. Find the "Detection Parameters" section
3. Lower the **Confidence Threshold** from 0.25 to 0.15
4. Click "Update Parameters"
5. Start inference again

**Result**: You should now see detections!

### Step 3: Check Performance

Look at the status section:
- **Hardware**: Shows CPU or GPU being used
- **Performance**: Shows FPS and inference time

**Performance Indicators:**
- ✅ **Good**: FPS > 15, Inference < 100ms
- ⚠️ **Acceptable**: FPS 10-15, Inference 100-200ms  
- ❌ **Poor**: FPS < 10, Inference > 200ms

If performance is poor, see PERFORMANCE_GUIDE.md for optimization tips.

## Common Scenarios

### Scenario 1: No Objects Detected
**Solution**: Lower confidence to 0.15-0.20

### Scenario 2: Too Many False Positives
**Solution**: Raise confidence to 0.35-0.45

### Scenario 3: Multiple Objects Appearing as One
**Solution**: Lower IoU to 0.35-0.40

### Scenario 4: Slow Performance (FPS < 10)
**Solutions**:
- Use smaller model (YoloE-11s)
- Check if GPU is available
- Consider hardware upgrade

## Parameter Cheat Sheet

| Confidence | Effect | Use When |
|------------|--------|----------|
| 0.15-0.20  | Very sensitive | Small/difficult objects |
| 0.25-0.35  | Balanced | Most scenarios (default) |
| 0.40-0.60  | High confidence | Reduce false positives |

| IoU | Effect | Use When |
|-----|--------|----------|
| 0.35-0.40 | Lenient overlap | Many overlapping objects |
| 0.45-0.50 | Balanced | Most scenarios (default) |
| 0.55-0.65 | Strict overlap | Distinct objects only |

## Hardware Impact

**CPU-based inference:**
- Expected: 10-20 FPS with YoloE-11s
- Limitation: Cannot use larger models effectively

**GPU-based inference:**
- Expected: 30-60+ FPS with any model size
- Benefit: 5-10x faster than CPU

Check your hardware in the status section!

## Need More Help?

See detailed documentation:
- **PERFORMANCE_GUIDE.md** - Complete troubleshooting guide
- **INFERENCE_PERFORMANCE_FIX.md** - Technical details
- **UI_CHANGES_SUMMARY.md** - UI feature descriptions

## Quick Test

After updating parameters, you should see:
1. ✅ Hardware type displayed (CPU/GPU)
2. ✅ Real-time FPS counter
3. ✅ Detection count
4. ✅ Active parameters (Conf/IoU)

All visible on the video feed and status section!
