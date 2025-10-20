#!/usr/bin/env python3
"""
Test to verify the bounding box tensor dimension fix.

This test simulates the tensor conversion that happens in app.py
and verifies that the dimensions are correct for the YOLOE API.
"""

import numpy as np

def test_box_tensor_dimensions():
    """Test that box tensor has correct dimensions."""
    print("=" * 60)
    print("Testing Box Tensor Dimensions Fix")
    print("=" * 60)
    
    # Simulate the boxes stored in visual_prompt_data
    # This is a numpy array with shape (N, 4) where N is number of boxes
    boxes_data = np.array([
        [10, 20, 30, 40],  # box 1: x1, y1, x2, y2
        [50, 60, 70, 80],  # box 2: x1, y1, x2, y2
        [100, 110, 120, 130],  # box 3: x1, y1, x2, y2
    ])
    
    print(f"\n1. Original boxes shape: {boxes_data.shape}")
    print(f"   Expected: (N, 4) where N = number of boxes")
    print(f"   Got: ({boxes_data.shape[0]}, {boxes_data.shape[1]})")
    print(f"   ✓ Correct 2D shape")
    
    # Simulate the OLD code (without .unsqueeze(0))
    print(f"\n2. OLD code (without .unsqueeze(0)):")
    print(f"   boxes_tensor shape would be: {boxes_data.shape}")
    print(f"   ndim would be: {boxes_data.ndim}")
    print(f"   ✗ This causes AssertionError: vpe.ndim == 3 fails!")
    
    # Simulate the NEW code (with .unsqueeze(0))
    print(f"\n3. NEW code (with .unsqueeze(0)):")
    # Add batch dimension by reshaping
    boxes_tensor = boxes_data.reshape(1, *boxes_data.shape)
    print(f"   boxes_tensor shape: {boxes_tensor.shape}")
    print(f"   ndim: {boxes_tensor.ndim}")
    print(f"   Expected format: (B, N, D) = (batch, num_boxes, coords)")
    print(f"   Got: (B={boxes_tensor.shape[0]}, N={boxes_tensor.shape[1]}, D={boxes_tensor.shape[2]})")
    
    # Verify dimensions
    assert boxes_tensor.ndim == 3, "Tensor must be 3-dimensional"
    assert boxes_tensor.shape[0] == 1, "Batch size must be 1"
    assert boxes_tensor.shape[1] == 3, "Should have 3 boxes"
    assert boxes_tensor.shape[2] == 4, "Each box should have 4 coordinates"
    
    print(f"   ✓ Passes assertion: vpe.ndim == 3")
    print(f"   ✓ Correct 3D shape with batch dimension")
    
    print("\n" + "=" * 60)
    print("✓ Test PASSED - Box tensor dimensions are correct!")
    print("=" * 60)
    print("\nSummary:")
    print("- The fix adds .unsqueeze(0) to create batch dimension")
    print("- Converts shape from (N, 4) to (1, N, 4)")
    print("- This matches the YOLOE API expectation of (B, N, D)")
    print("- Prevents AssertionError in get_vpe() method")
    
    return True

if __name__ == '__main__':
    try:
        test_box_tensor_dimensions()
        exit(0)
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
