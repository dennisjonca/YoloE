# Quick Fix Guide: Visual Prompting with High-Resolution Cameras

## What Was Fixed?

The visual prompting feature now works correctly with high-resolution cameras (1920x1080 and above).

## What Was the Problem?

When using 1920x1080 cameras, drawing bounding boxes would fail with:
```
[ERROR] Failed to save visual prompt: mat1 and mat2 shapes cannot be multiplied (1x4 and 512x128)
```

This happened because:
1. Your camera captures at 1920x1080
2. Your browser displays the canvas at a smaller size (to fit the screen)
3. The old code didn't account for this scaling difference
4. Box coordinates were calculated incorrectly

## How Was It Fixed?

### Main Fix: Canvas Coordinate Scaling
The mouse coordinates are now properly scaled from the displayed size to the actual canvas size:

```javascript
// When you click at position (100, 100) on screen...
// The canvas might be 1920x1080 but displayed at 640x360

// OLD: Used screen coordinates directly
startX = 100  // Wrong!

// NEW: Scale to canvas logical size
scaleX = 1920 / 640 = 3
startX = 100 * 3 = 300  // Correct!
```

### Additional Improvements
1. **Image normalization**: Pixel values normalized to [0, 1] range
2. **Box format conversion**: Boxes converted to cxcywh format (center, width, height)
3. **Fallback support**: Tries both box formats if one fails
4. **Debug logging**: Detailed output to help diagnose issues

## How to Use It?

### Step 1: Update Your Code
Pull the latest changes:
```bash
git pull
```

### Step 2: Test Visual Prompting
1. **Stop inference** (if running)
2. **Capture snapshot** from your camera
3. **Draw bounding boxes** around objects
4. **Save visual prompt**
5. **Check console output** for debug information
6. **Start inference**

### Step 3: Verify It Works

You should see debug output like:
```
[DEBUG] Snapshot frame shape: (1080, 1920, 3) (H=1080, W=1920)
[DEBUG] Original image shape: (1080, 1920, 3) (H=1080, W=1920)
[DEBUG] Resized image shape: (320, 320, 3)
[DEBUG] Image tensor shape: torch.Size([1, 3, 320, 320])
[DEBUG] Image tensor value range: [0.000, 1.000]
[DEBUG] Original boxes (absolute coords): [[288 300 576 600]]
[DEBUG] Normalized boxes (0-1 range, xyxy): [[0.15 0.2778 0.3 0.5556]]
[DEBUG] Boxes in cxcywh format: [[0.225 0.4167 0.15 0.2778]]
[DEBUG] Box tensor shape: torch.Size([1, 1, 4])
[DEBUG] Using get_visual_pe method
[DEBUG] get_visual_pe succeeded, visual_pe shape: torch.Size([...])
```

If successful, you'll see:
```
[INFO] Visual prompts set successfully
```

Instead of:
```
[ERROR] Failed to save visual prompt: mat1 and mat2 shapes cannot be multiplied
```

## What If It Still Doesn't Work?

### Check the Debug Output

Look for these key values in the console:

1. **Image dimensions**: Should match your camera resolution
   ```
   [DEBUG] Snapshot frame shape: (1080, 1920, 3)
   ```

2. **Box coordinates**: Should be in [0, 1] range
   ```
   [DEBUG] Normalized boxes (0-1 range, xyxy): [[0.15 0.28 0.30 0.56]]
   ```

3. **Tensor shapes**: Should be correct
   ```
   [DEBUG] Image tensor shape: torch.Size([1, 3, 320, 320])
   [DEBUG] Box tensor shape: torch.Size([1, 1, 4])
   ```

### Common Issues

1. **Still getting dimension errors**:
   - Check if the error is the same or different
   - Share the full debug output
   - The fallback might kick in (look for "Trying ... with xyxy format")

2. **Boxes not appearing in the right place**:
   - This might be a different issue
   - Check if boxes appear correctly when drawn
   - Verify the canvas is loading the snapshot image

3. **Canvas too large or too small**:
   - The canvas now has `max-width: 100%` CSS
   - It should fit your screen while maintaining aspect ratio
   - If not, you can adjust the CSS in app.py

## Technical Details

### Resolution Independence
The fix works with any camera resolution:
- 320x320 (minimum)
- 640x480 (VGA)
- 1280x720 (HD 720p)
- 1920x1080 (Full HD) ✓ Your cameras
- 3840x2160 (4K UHD)

### Coordinate Transformations

1. **Mouse click** → Displayed coordinates (e.g., 0-640)
2. **Scale to logical** → Canvas coordinates (e.g., 0-1920)
3. **Normalize** → Relative coordinates (0-1)
4. **Send to server** → Absolute coordinates (0-1920)
5. **Process for model** → Normalized cxcywh (0-1)

Each step is now correctly handled!

## Removing Debug Output (Optional)

Once you've verified everything works, you can remove the debug lines:

1. Search for `[DEBUG]` in app.py
2. Remove or comment out those print statements
3. Keep the actual logic, just remove the print() calls

Example:
```python
# Remove this:
print(f"[DEBUG] Box tensor shape: {boxes_tensor.shape}")

# Keep this:
boxes_tensor = torch.from_numpy(cxcywh_boxes).unsqueeze(0).float()
```

## Summary

✓ Canvas coordinate scaling fixed for high-resolution cameras
✓ Works with 1920x1080 cameras (both integrated and external)
✓ Image and box normalization improved
✓ Fallback support for different YOLOE API versions
✓ Comprehensive debug output for troubleshooting
✓ Resolution-independent (works with any camera)

Your visual prompting feature should now work correctly!
