# Bounding Box Tensor Dimension Fix

## Problem
When using visual prompting by drawing bounding boxes on a snapshot, the application crashed with the following error:

```
AssertionError at line 724 in ultralytics/nn/modules/head.py:
assert vpe.ndim == 3  # (B, N, D)
```

The full error trace showed:
```
File "app.py", line 88, in load_model
    visual_pe = loaded_model.get_visual_pe(image_tensor, boxes_tensor)
File "ultralytics/nn/tasks.py", line 1056, in get_visual_pe
    return self(img, vpe=visual, return_vpe=True)
File "ultralytics/nn/modules/head.py", line 724, in get_vpe
    assert vpe.ndim == 3  # (B, N, D)
```

## Root Cause
The `boxes_tensor` was being created as a 2-dimensional tensor with shape `(N, 4)` where:
- N = number of boxes
- 4 = coordinates (x1, y1, x2, y2)

However, the YOLOE API expects a 3-dimensional tensor with shape `(B, N, D)` where:
- B = batch size (typically 1)
- N = number of boxes
- D = dimensions (4 coordinates)

## Solution
Added `.unsqueeze(0)` to the `boxes_tensor` creation to add the batch dimension.

### Before (Incorrect):
```python
boxes_tensor = torch.from_numpy(visual_prompt_data['boxes']).float()
# Shape: (N, 4) - 2D tensor
```

### After (Correct):
```python
boxes_tensor = torch.from_numpy(visual_prompt_data['boxes']).unsqueeze(0).float()
# Shape: (1, N, 4) - 3D tensor with batch dimension
```

## Changes Made
- **File**: `app.py`
- **Line**: 79
- **Change**: Added `.unsqueeze(0)` to add batch dimension
- **Comment**: Updated to clarify expected tensor shape

## Example
With 3 bounding boxes:

**Before (2D - Incorrect):**
```
boxes_tensor.shape = (3, 4)
boxes_tensor.ndim = 2
❌ Fails assertion: vpe.ndim == 3
```

**After (3D - Correct):**
```
boxes_tensor.shape = (1, 3, 4)
boxes_tensor.ndim = 3
✅ Passes assertion: vpe.ndim == 3
```

## Testing
Run the test to verify the fix:
```bash
python3 test_box_tensor_fix.py
```

This test demonstrates:
1. Original boxes are 2D: `(N, 4)`
2. OLD code produces 2D tensor (fails)
3. NEW code produces 3D tensor (works)

## Impact
- **Minimal Change**: Only one line modified
- **Backwards Compatible**: Does not affect other functionality
- **Fixes Visual Prompting**: Users can now successfully draw bounding boxes and configure visual prompts
- **API Compliant**: Matches YOLOE's expected tensor format

## Related
This fix is consistent with the `image_tensor` creation on line 77, which already includes `.unsqueeze(0)` to add the batch dimension:
```python
image_tensor = torch.from_numpy(visual_prompt_data['image']).permute(2, 0, 1).unsqueeze(0).float()
```

Both tensors now have matching batch dimensions for proper API usage.
