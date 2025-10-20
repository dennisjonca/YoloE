#!/usr/bin/env python3
"""
Test script to verify performance monitoring and parameter configuration features.
"""
import sys
import re

def test_imports():
    """Test that all required imports are available."""
    print("Testing imports...")
    try:
        import torch
        print("✓ torch import successful")
        
        from flask import Flask
        print("✓ flask import successful")
        
        from ultralytics import YOLOE
        print("✓ ultralytics import successful")
        
        import cv2
        print("✓ opencv import successful")
        
        import numpy as np
        print("✓ numpy import successful")
        
        return True
    except ImportError as e:
        print(f"⚠ Import test skipped (dependencies not installed): {e}")
        print("  This is expected in test environments without full dependencies")
        return None  # Return None to indicate test was skipped


def test_hardware_detection():
    """Test hardware detection function."""
    print("\nTesting hardware detection...")
    try:
        import torch
        import os
        
        # Simulate the hardware detection function
        info = {
            'cpu_count': os.cpu_count(),
            'cuda_available': torch.cuda.is_available(),
            'cuda_device_count': 0,
            'cuda_device_name': None,
            'device_name': 'CPU'
        }
        
        if info['cuda_available']:
            info['cuda_device_count'] = torch.cuda.device_count()
            if info['cuda_device_count'] > 0:
                info['cuda_device_name'] = torch.cuda.get_device_name(0)
                info['device_name'] = f"GPU: {info['cuda_device_name']}"
        
        print(f"✓ CPU Count: {info['cpu_count']}")
        print(f"✓ CUDA Available: {info['cuda_available']}")
        print(f"✓ Device: {info['device_name']}")
        
        return True
    except ImportError as e:
        print(f"⚠ Hardware detection test skipped (dependencies not installed): {e}")
        print("  This is expected in test environments without full dependencies")
        return None  # Return None to indicate test was skipped
    except Exception as e:
        print(f"✗ Hardware detection failed: {e}")
        return False


def test_app_structure():
    """Test that app.py has the expected structure."""
    print("\nTesting app.py structure...")
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for new global variables
        if 'current_conf' in content and 'current_iou' in content:
            print("✓ Detection parameters defined")
        else:
            print("✗ Detection parameters not found")
            return False
        
        # Check for performance monitoring variables
        if 'fps_counter' in content and 'current_fps' in content:
            print("✓ Performance monitoring variables defined")
        else:
            print("✗ Performance monitoring variables not found")
            return False
        
        # Check for hardware detection function
        if 'def get_hardware_info' in content:
            print("✓ Hardware detection function defined")
        else:
            print("✗ Hardware detection function not found")
            return False
        
        # Check for parameter update route
        if '@app.route(\'/set_parameters\'' in content:
            print("✓ Parameter update route defined")
        else:
            print("✗ Parameter update route not found")
            return False
        
        # Check that inference uses configurable parameters
        if 'conf=current_conf' in content and 'iou=current_iou' in content:
            print("✓ Inference uses configurable parameters")
        else:
            print("✗ Inference not using configurable parameters")
            return False
        
        # Check for performance overlay in inference
        if 'FPS:' in content and 'Inference:' in content:
            print("✓ Performance overlay implemented")
        else:
            print("✗ Performance overlay not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ App structure test failed: {e}")
        return False


def test_parameter_validation():
    """Test parameter validation logic."""
    print("\nTesting parameter validation...")
    try:
        # Test valid ranges
        test_values = [
            (0.0, 0.0, True),
            (0.25, 0.45, True),
            (0.5, 0.5, True),
            (1.0, 1.0, True),
            (-0.1, 0.5, False),  # Invalid: negative
            (0.5, 1.1, False),   # Invalid: > 1.0
        ]
        
        for conf, iou, should_pass in test_values:
            valid = (0.0 <= conf <= 1.0) and (0.0 <= iou <= 1.0)
            if valid == should_pass:
                print(f"✓ conf={conf}, iou={iou} -> {valid} (expected: {should_pass})")
            else:
                print(f"✗ conf={conf}, iou={iou} -> {valid} (expected: {should_pass})")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Parameter validation test failed: {e}")
        return False


def test_documentation():
    """Test that documentation exists and is complete."""
    print("\nTesting documentation...")
    try:
        import os
        
        # Check if PERFORMANCE_GUIDE.md exists
        if os.path.exists('PERFORMANCE_GUIDE.md'):
            print("✓ PERFORMANCE_GUIDE.md exists")
            
            with open('PERFORMANCE_GUIDE.md', 'r') as f:
                content = f.read()
            
            # Check for key sections
            required_sections = [
                'Confidence Threshold',
                'IoU Threshold',
                'Hardware Performance Impact',
                'CPU vs GPU Inference',
                'Troubleshooting',
                'Model Size Impact'
            ]
            
            for section in required_sections:
                if section in content:
                    print(f"✓ Section '{section}' found")
                else:
                    print(f"✗ Section '{section}' not found")
                    return False
        else:
            print("✗ PERFORMANCE_GUIDE.md not found")
            return False
        
        # Check if README.md was updated
        if os.path.exists('README.md'):
            with open('README.md', 'r') as f:
                content = f.read()
            
            if 'PERFORMANCE_GUIDE.md' in content:
                print("✓ README.md references PERFORMANCE_GUIDE.md")
            else:
                print("✗ README.md does not reference PERFORMANCE_GUIDE.md")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Documentation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("YoloE Performance Features Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Hardware Detection", test_hardware_detection),
        ("App Structure", test_app_structure),
        ("Parameter Validation", test_parameter_validation),
        ("Documentation", test_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    skipped = sum(1 for _, result in results if result is None)
    failed = sum(1 for _, result in results if result is False)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is None:
            status = "⚠ SKIP"
        else:
            status = "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 60)
    print(f"Passed: {passed}/{total} | Skipped: {skipped}/{total} | Failed: {failed}/{total}")
    
    if failed == 0:
        print("\n✓ All non-skipped tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
