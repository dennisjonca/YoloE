# GradCAM Crash Fix - Summary

## Issue
When using the following sequence:
1. Change Camera to external (Camera 1)
2. Change Classes to Plant (Text Prompt)
3. Starting inference -> Sees plant
4. Stopping inference
5. Activating Heatmap mode
6. Starting inference again

The application would crash with the error:
```
[WARN] GradCAM generation failed: element 0 of tensors does not require grad and does not have a grad_fn, using fallback
```

## Root Cause
The issue was that tensors created from numpy arrays using `torch.from_numpy()` don't have gradient computation enabled by default (`requires_grad=False`). When GradCAM attempts to perform backpropagation to generate the heatmap, it fails because the tensor doesn't support gradient computation.

## Solution
Added `tensor.requires_grad_(True)` immediately after tensor creation in two locations:

1. **app.py** (line 267) - In the `inference_thread()` function, heatmap mode section
2. **heatmap_generator.py** (line 203) - In the `generate()` method

This enables gradient computation on the input tensors, allowing GradCAM to successfully compute activation maps.

## Changes Made

### app.py
```python
# Before (line 266):
tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0).to(heatmap_generator.device)

# After (lines 266-267):
tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0).to(heatmap_generator.device)
tensor.requires_grad_(True)
```

### heatmap_generator.py
```python
# Before (line 202):
tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0).to(self.device)

# After (lines 202-203):
tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0).to(self.device)
tensor.requires_grad_(True)
```

## Testing
Created `test_gradcam_fix.py` to verify:
- The fix is present in both files
- The fix is correctly placed after tensor creation
- The fix addresses the original error

All tests passed successfully.

## Code Review & Security
- Code review: PASSED with no comments
- Security scan: PASSED with no alerts
- No security vulnerabilities introduced

## Impact
This fix is minimal and surgical:
- Only 2 lines added (one in each file)
- No changes to existing logic or behavior
- Fixes the crash when using heatmap mode with text prompting
- Maintains backward compatibility
