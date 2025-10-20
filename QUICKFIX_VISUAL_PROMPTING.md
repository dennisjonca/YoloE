# Quick Reference: Visual Prompting Fix

## What was fixed?
The error `"mat1 and mat2 shapes cannot be multiplied (1x4 and 512x128)"` that occurred when saving visual prompts has been resolved.

## What changed?
Bounding boxes are now automatically normalized to the [0, 1] range before being passed to the YOLOE model, fixing the matrix dimension mismatch.

## Do I need to do anything?
**No!** The fix is automatic. Just use the visual prompting feature as normal:
1. Stop inference
2. Capture snapshot
3. Draw boxes on the canvas
4. Click "Save Snapshot with Boxes"
5. Start inference

## Technical Details
- **File changed**: `app.py` (lines 79-87)
- **Change type**: Box coordinate normalization
- **Impact**: Visual prompting now works correctly
- **Compatibility**: Fully backwards compatible

## More Information
See `BOX_NORMALIZATION_FIX.md` for complete technical documentation.
