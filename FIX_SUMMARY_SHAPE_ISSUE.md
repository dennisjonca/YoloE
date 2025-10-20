# Visual Prompt Shape Fix - Summary

## Problem
User reported an error when saving visual prompts with a single bounding box:
```
[ERROR] Failed to save visual prompt: mat1 and mat2 shapes cannot be multiplied (1x4 and 512x128)
```

## Root Cause
The code had an incorrect fallback path that used `get_visual_pe()` method and then passed its result to `set_classes()`. However:
- `get_visual_pe()` returns the boxes tensor (shape `[1, 1, 4]`), not embeddings
- `set_classes()` expects embeddings with shape `[N, 512]` or similar
- This caused a matrix multiplication dimension mismatch

## Solution
Removed the incorrect `get_visual_pe()` fallback code. Now the code:
1. Uses `set_prompts()` with cxcywh format boxes (primary method)
2. If that fails, retries with xyxy format boxes  
3. If both fail, raises a proper error
4. Only falls back to text prompting if `set_prompts` doesn't exist

## Files Changed
- `app.py`: 26 lines modified (net: -10 lines, simplified the code)
- `VISUAL_PROMPT_SHAPE_FIX.md`: New documentation file (223 lines)

## Testing
All existing tests pass:
- ✓ `test_visual_prompt_resize.py` - Image resize logic
- ✓ `test_box_tensor_fix.py` - Box tensor dimensions
- ✓ Single box scenario test - Verified with user's exact coordinates

## Impact
- ✓ Fixes the shape mismatch error
- ✓ Visual prompting now works with single box
- ✓ Better error handling and retry logic
- ✓ No breaking changes to existing functionality

## Usage
Users can now:
1. Stop inference
2. Capture snapshot
3. Draw ONE or multiple bounding boxes
4. Save snapshot with boxes
5. Start inference - should work without errors!
