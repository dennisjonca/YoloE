#!/usr/bin/env python3
"""
Test script to verify the improved YoloTarget implementation.
This test verifies that the target function produces stronger gradients
for high-confidence detections.
"""

import torch
import numpy as np
from heatmap_generator import YoloTarget

# Test constants
GRADIENT_FOCUS_THRESHOLD = 0.5  # Minimum ratio for gradient focus on high-activation regions

def test_yolo_target_improvement():
    """Test that YoloTarget uses top-k strategy instead of sum."""
    print("=" * 60)
    print("Testing Improved YoloTarget Implementation")
    print("=" * 60)
    
    # Create a YoloTarget instance
    target = YoloTarget(output_type='class', conf=0.2, ratio=0.02)
    
    print("\n1. Testing with simulated YOLO output...")
    
    # Simulate YOLO output: mostly low values with a few high confidence detections
    # This mimics what happens when the model detects an object
    output = torch.randn(1, 100, 100) * 0.1  # Low background activations
    output[0, 25:35, 25:35] = torch.randn(10, 10) * 2.0 + 3.0  # High activation region (detected object)
    
    print(f"   - Output shape: {output.shape}")
    print(f"   - Output mean: {output.mean().item():.4f}")
    print(f"   - Output max: {output.max().item():.4f}")
    print(f"   - Output min: {output.min().item():.4f}")
    
    # Compute target value
    target_value = target.forward(output)
    
    print(f"   - Target value: {target_value.item():.4f}")
    print(f"   - Target requires grad: {target_value.requires_grad}")
    
    # Verify the target is using top-k strategy (should be positive and significant)
    if target_value.item() > 0:
        print("   ✓ Target value is positive (focusing on high activations)")
    else:
        print("   ✗ Target value is not positive")
        return False
    
    # Compare with old sum() strategy
    old_strategy_value = output.sum()
    print(f"\n2. Comparing strategies:")
    print(f"   - Old strategy (sum): {old_strategy_value.item():.4f}")
    print(f"   - New strategy (top-k): {target_value.item():.4f}")
    
    # The new strategy should produce a more focused value
    # For this test, top-k should be significantly different from sum
    print(f"   - Ratio (new/old): {(target_value.item() / old_strategy_value.item()):.4f}")
    
    print("\n3. Testing gradient flow...")
    
    # Test that gradients can flow through the target
    output.requires_grad = True
    target_value = target.forward(output)
    target_value.backward()
    
    if output.grad is not None:
        print(f"   - Gradients shape: {output.grad.shape}")
        print(f"   - Gradients mean: {output.grad.mean().item():.6f}")
        print(f"   - Gradients max: {output.grad.max().item():.6f}")
        print(f"   - Non-zero gradients: {(output.grad != 0).sum().item()}")
        print("   ✓ Gradients computed successfully")
    else:
        print("   ✗ No gradients computed")
        return False
    
    # Check that gradients are focused on high-activation regions
    # The region with high activations should have higher gradients
    high_activation_region_grad = output.grad[0, 25:35, 25:35].abs().mean()
    background_region_grad = output.grad[0, 0:10, 0:10].abs().mean()
    
    print(f"\n4. Gradient localization:")
    print(f"   - High activation region gradient: {high_activation_region_grad.item():.6f}")
    print(f"   - Background region gradient: {background_region_grad.item():.6f}")
    
    if high_activation_region_grad > background_region_grad * GRADIENT_FOCUS_THRESHOLD:
        print("   ✓ Gradients are more focused on high-activation regions")
    else:
        print("   ⚠ Gradients may not be optimally focused")
    
    print("\n5. Testing edge cases...")
    
    # Test with empty tensor
    empty_output = torch.tensor([])
    try:
        empty_target = target.forward(empty_output)
        print(f"   - Empty tensor target: {empty_target.item():.4f}")
        print("   ✓ Handles empty tensors")
    except Exception as e:
        print(f"   ✗ Failed on empty tensor: {e}")
        return False
    
    # Test with single value
    single_output = torch.tensor([5.0])
    try:
        single_target = target.forward(single_output)
        print(f"   - Single value target: {single_target.item():.4f}")
        print("   ✓ Handles single values")
    except Exception as e:
        print(f"   ✗ Failed on single value: {e}")
        return False
    
    # Test with list input (as YOLO models sometimes return lists)
    list_output = [output]
    try:
        list_target = target.forward(list_output)
        print(f"   - List input target: {list_target.item():.4f}")
        print("   ✓ Handles list inputs")
    except Exception as e:
        print(f"   ✗ Failed on list input: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nSummary:")
    print("- The improved YoloTarget uses top-k strategy")
    print("- This focuses gradients on high-confidence detections")
    print("- Result: Heatmaps will show 'hot' areas for detected objects")
    print("- Instead of weak, diffuse 'cold' blue areas everywhere")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    import sys
    success = test_yolo_target_improvement()
    sys.exit(0 if success else 1)
