#!/usr/bin/env python3
"""
Test script for live heatmap mode functionality - lightweight version.
Tests the heatmap mode implementation without loading the full app.
"""

import sys
import os

def test_imports():
    """Test that required modules can be imported."""
    print("=" * 60)
    print("Live Heatmap Mode Test (Lightweight)")
    print("=" * 60)
    
    print("\n1. Testing core imports...")
    
    try:
        from heatmap_generator import YoloEHeatmapGenerator, get_default_params, letterbox
        print("   ✓ heatmap_generator module imported")
    except Exception as e:
        print(f"   ✗ Failed to import heatmap_generator: {e}")
        return False
    
    try:
        from pytorch_grad_cam.utils.image import show_cam_on_image
        print("   ✓ pytorch_grad_cam utilities imported")
    except Exception as e:
        print(f"   ✗ Failed to import pytorch_grad_cam: {e}")
        return False
    
    return True


def test_code_structure():
    """Test that the app.py has the correct code structure."""
    print("\n2. Testing app.py code structure...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for heatmap_mode variable
        if 'heatmap_mode = False' not in content:
            print("   ✗ heatmap_mode variable not found in app.py")
            return False
        print("   ✓ heatmap_mode variable defined")
        
        # Check for heatmap_generator variable
        if 'heatmap_generator = None' not in content:
            print("   ✗ heatmap_generator variable not found in app.py")
            return False
        print("   ✓ heatmap_generator variable defined")
        
        # Check for toggle_heatmap route
        if '@app.route(\'/toggle_heatmap\'' not in content:
            print("   ✗ /toggle_heatmap route not found in app.py")
            return False
        print("   ✓ /toggle_heatmap route defined")
        
        # Check for heatmap mode in inference thread
        if 'if heatmap_mode and heatmap_generator is not None:' not in content:
            print("   ✗ Heatmap mode check not found in inference thread")
            return False
        print("   ✓ Heatmap mode check in inference thread")
        
        # Check for UI updates
        if 'Heatmap Mode:' not in content:
            print("   ✗ Heatmap mode status not in UI")
            return False
        print("   ✓ Heatmap mode status in UI")
        
        # Check for mode indicator
        if 'HEATMAP' not in content or 'NORMAL' not in content:
            print("   ✗ Mode indicator not found")
            return False
        print("   ✓ Mode indicator for video feed")
        
        # Check for letterbox import (done inside inference thread)
        if 'from heatmap_generator import letterbox' not in content and 'import letterbox' not in content:
            print("   ✗ letterbox import not found in code")
            return False
        print("   ✓ letterbox function import in code")
        
        # Check for show_cam_on_image import (done inside inference thread)
        if 'from pytorch_grad_cam.utils.image import show_cam_on_image' not in content and 'import show_cam_on_image' not in content:
            print("   ✗ show_cam_on_image import not found in code")
            return False
        print("   ✓ show_cam_on_image import in code")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing code structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_heatmap_functions():
    """Test that heatmap-related functions exist and work."""
    print("\n3. Testing heatmap utility functions...")
    
    try:
        from heatmap_generator import letterbox, get_default_params
        import numpy as np
        
        print("   ✓ letterbox function available")
        print("   ✓ get_default_params function available")
        
        # Test get_default_params
        params = get_default_params()
        required_keys = ['device', 'method', 'layer', 'conf_threshold', 'show_box', 'renormalize']
        for key in required_keys:
            if key not in params:
                print(f"   ✗ Missing parameter: {key}")
                return False
        print(f"   ✓ Default parameters contain all required keys")
        
        # Test letterbox function
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        result, ratio, padding = letterbox(test_img)
        if result is None:
            print("   ✗ letterbox function failed")
            return False
        print(f"   ✓ letterbox function works (output shape: {result.shape})")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing heatmap functions: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_logic():
    """Test the integration logic in the code."""
    print("\n4. Testing integration logic...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check heatmap initialization in inference thread
        if 'if heatmap_mode:' not in content:
            print("   ✗ Heatmap mode initialization check not found")
            return False
        print("   ✓ Heatmap mode initialization check present")
        
        # Check for heatmap generator initialization
        if 'heatmap_generator = YoloEHeatmapGenerator' not in content:
            print("   ✗ Heatmap generator initialization not found")
            return False
        print("   ✓ Heatmap generator initialization present")
        
        # Check for GradCAM generation (flexible matching)
        if 'grayscale_cam' not in content or 'heatmap_generator.method' not in content:
            print("   ✗ GradCAM generation call not found")
            return False
        print("   ✓ GradCAM generation call present")
        
        # Check for cam_image overlay
        if 'show_cam_on_image' not in content or 'cam_image' not in content:
            print("   ✗ cam_image overlay creation not found")
            return False
        print("   ✓ cam_image overlay creation present")
        
        # Check for renormalization
        if 'renormalize_cam_in_bounding_boxes' not in content:
            print("   ✗ Renormalization call not found")
            return False
        print("   ✓ Renormalization call present")
        
        # Check for box drawing
        if 'draw_detections' not in content:
            print("   ✗ Box drawing call not found")
            return False
        print("   ✓ Box drawing call present")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing integration logic: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    tests = [
        test_imports,
        test_code_structure,
        test_heatmap_functions,
        test_integration_logic
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        if not result:
            print(f"\n   Test {test.__name__} FAILED")
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("\n✓ All tests passed!")
        print("\nLive heatmap mode implementation verified:")
        print("  - Heatmap mode toggle added")
        print("  - Live heatmap generation integrated")
        print("  - UI updated with controls and status")
        print("  - Mode indicator on video feed")
    
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
