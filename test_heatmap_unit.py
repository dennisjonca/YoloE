#!/usr/bin/env python3
"""
Unit tests for heatmap generation module.
Tests imports and basic functionality without requiring model files.
"""

import sys
import os


def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("Testing Heatmap Module Imports")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test heatmap_generator imports
    print("\n1. Testing heatmap_generator module...")
    try:
        from heatmap_generator import YoloEHeatmapGenerator, get_default_params
        print("   ✓ YoloEHeatmapGenerator imported")
        print("   ✓ get_default_params imported")
        tests_passed += 2
    except ImportError as e:
        print(f"   ✗ Failed to import from heatmap_generator: {e}")
        tests_failed += 2
        return False
    
    # Test pytorch_grad_cam
    print("\n2. Testing pytorch_grad_cam imports...")
    try:
        from pytorch_grad_cam import GradCAMPlusPlus, GradCAM, HiResCAM
        print("   ✓ GradCAMPlusPlus imported")
        print("   ✓ GradCAM imported")
        print("   ✓ HiResCAM imported")
        tests_passed += 3
    except ImportError as e:
        print(f"   ✗ Failed to import pytorch_grad_cam: {e}")
        tests_failed += 3
        return False
    
    # Test other dependencies
    print("\n3. Testing other dependencies...")
    try:
        import cv2
        print("   ✓ cv2 (opencv) imported")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Failed to import cv2: {e}")
        tests_failed += 1
    
    try:
        import numpy as np
        print("   ✓ numpy imported")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Failed to import numpy: {e}")
        tests_failed += 1
    
    try:
        from PIL import Image
        print("   ✓ PIL (Pillow) imported")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Failed to import PIL: {e}")
        tests_failed += 1
    
    try:
        from tqdm import trange
        print("   ✓ tqdm imported")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Failed to import tqdm: {e}")
        tests_failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)
    
    return tests_failed == 0


def test_default_params():
    """Test that default parameters are returned correctly."""
    print("\n" + "=" * 60)
    print("Testing Default Parameters")
    print("=" * 60)
    
    try:
        from heatmap_generator import get_default_params
        params = get_default_params()
        
        required_keys = ['device', 'method', 'layer', 'backward_type', 
                        'conf_threshold', 'ratio', 'show_box', 'renormalize']
        
        print("\nChecking default parameters...")
        all_present = True
        for key in required_keys:
            if key in params:
                print(f"   ✓ {key}: {params[key]}")
            else:
                print(f"   ✗ Missing key: {key}")
                all_present = False
        
        if all_present:
            print("\n✓ All required parameters present")
            return True
        else:
            print("\n✗ Some parameters missing")
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing default parameters: {e}")
        return False


def test_app_integration():
    """Test that app.py has the heatmap integration."""
    print("\n" + "=" * 60)
    print("Testing App Integration")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('heatmap_generator import', 'from heatmap_generator import'),
            ('generate_heatmap route', '@app.route(\'/generate_heatmap\''),
            ('view_heatmap route', '@app.route(\'/view_heatmap\''),
            ('last_heatmap_path variable', 'last_heatmap_path'),
        ]
        
        all_passed = True
        print("\nChecking app.py integration...")
        for name, pattern in checks:
            if pattern in app_content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ Missing: {name}")
                all_passed = False
        
        if all_passed:
            print("\n✓ All integration points present")
            return True
        else:
            print("\n✗ Some integration points missing")
            return False
            
    except Exception as e:
        print(f"\n✗ Error checking app integration: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("YoloE Heatmap Generation - Unit Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Default Parameters", test_default_params()))
    results.append(("App Integration", test_app_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    if passed == total:
        print(f"✓ All {total} test suites passed!")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {total - passed} of {total} test suites failed")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
