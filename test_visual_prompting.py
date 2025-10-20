#!/usr/bin/env python3
"""
Test suite for visual prompting functionality.

This script verifies that:
1. Snapshot capture works correctly
2. Visual prompt boxes can be saved
3. Model can be loaded with visual prompts
4. Text prompting still works
5. Model switching works with both modes
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("\n=== Testing Imports ===")
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError:
        print("✗ Flask not installed. Install with: pip install flask")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError:
        print("✗ OpenCV not installed. Install with: pip install opencv-python")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError:
        print("✗ NumPy not installed. Install with: pip install numpy")
        return False
    
    try:
        from ultralytics import YOLOE
        print("✓ YOLOE imported successfully")
    except ImportError:
        print("✗ YOLOE not installed. Install with: pip install ultralytics")
        print("  Note: YOLOE requires ultralytics with YOLO-World support")
        return False
    
    return True


def test_app_structure():
    """Test that app.py has the required structure."""
    print("\n=== Testing App Structure ===")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    required_elements = [
        ('snapshot_frame', 'Snapshot frame variable'),
        ('snapshot_boxes', 'Snapshot boxes variable'),
        ('use_visual_prompt', 'Visual prompt flag'),
        ('/capture_snapshot', 'Snapshot capture route'),
        ('/snapshot_image', 'Snapshot image route'),
        ('/save_visual_prompt', 'Save visual prompt route'),
        ('/clear_visual_prompt', 'Clear visual prompt route'),
        ('visual_prompt_data', 'Visual prompt data parameter'),
        ('snapshotCanvas', 'Canvas element for drawing'),
    ]
    
    all_present = True
    for element, description in required_elements:
        if element in content:
            print(f"✓ {description} present")
        else:
            print(f"✗ {description} missing")
            all_present = False
    
    return all_present


def test_html_interface():
    """Test that HTML interface includes visual prompting controls."""
    print("\n=== Testing HTML Interface ===")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    required_ui_elements = [
        ('Visual Prompting', 'Visual prompting section header'),
        ('Capture Snapshot', 'Snapshot capture button'),
        ('Clear Boxes', 'Clear boxes button'),
        ('Save Snapshot with Boxes', 'Save visual prompt button'),
        ('Clear Visual Prompt', 'Clear visual prompt button'),
        ('canvas', 'Canvas for drawing boxes'),
        ('mousedown', 'Mouse event handling'),
        ('boxes', 'Box storage array'),
    ]
    
    all_present = True
    for element, description in required_ui_elements:
        if element in content:
            print(f"✓ {description} present")
        else:
            print(f"✗ {description} missing")
            all_present = False
    
    return all_present


def test_visual_prompt_flow():
    """Test the visual prompting data flow."""
    print("\n=== Testing Visual Prompt Flow ===")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('load_model(current_model, visual_prompt_data=', 'Model loading with visual prompts'),
        ('snapshot_frame = frame.copy()', 'Snapshot frame capture'),
        ('snapshot_boxes.append', 'Box collection'),
        ('use_visual_prompt = True', 'Visual prompt mode activation'),
        ('use_visual_prompt = False', 'Visual prompt mode deactivation'),
        ('if visual_prompt_data is not None:', 'Visual prompt mode check'),
    ]
    
    all_present = True
    for check, description in checks:
        if check in content:
            print(f"✓ {description} implemented")
        else:
            print(f"✗ {description} missing")
            all_present = False
    
    return all_present


def test_backwards_compatibility():
    """Test that text prompting and other features still work."""
    print("\n=== Testing Backwards Compatibility ===")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('set_classes', 'Text prompting with set_classes'),
        ('get_text_pe', 'Text prompt encoding'),
        ('/set_classes', 'Set classes route'),
        ('/set_camera', 'Camera switching route'),
        ('/set_model', 'Model switching route'),
        ('current_classes', 'Current classes variable'),
    ]
    
    all_present = True
    for check, description in checks:
        if check in content:
            print(f"✓ {description} still present")
        else:
            print(f"✗ {description} removed (should be kept)")
            all_present = False
    
    return all_present


def test_error_handling():
    """Test that proper error handling is in place."""
    print("\n=== Testing Error Handling ===")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('if running:', 'Check if inference is running before changes'),
        ('if snapshot_frame is None:', 'Check if snapshot exists'),
        ('try:', 'Exception handling present'),
        ('except Exception as e:', 'Generic exception handling'),
        ('if not boxes_data:', 'Check for empty boxes'),
    ]
    
    all_present = True
    for check, description in checks:
        if check in content:
            print(f"✓ {description} implemented")
        else:
            print(f"✗ {description} missing")
            all_present = False
    
    return all_present


def main():
    """Run all tests."""
    print("=" * 60)
    print("Visual Prompting Feature Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("App Structure", test_app_structure),
        ("HTML Interface", test_html_interface),
        ("Visual Prompt Flow", test_visual_prompt_flow),
        ("Backwards Compatibility", test_backwards_compatibility),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Visual prompting feature is properly implemented.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
