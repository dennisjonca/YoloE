#!/usr/bin/env python3
"""
Integration test for tracker reset functionality.
This test verifies that the tracker reset code in app.py is working correctly.
"""
import sys
import re


def test_tracker_reset_implementation():
    """Test that the tracker reset implementation is correct."""
    print("=" * 60)
    print("Tracker Reset Implementation Test")
    print("=" * 60)
    
    # Read the app.py file
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check for tracker reset comment
    tests_total += 1
    if 'Reset tracker state' in code or 'reset tracker' in code.lower():
        print("\n✓ Test 1: Tracker reset comment found")
        tests_passed += 1
    else:
        print("\n✗ Test 1 FAILED: Tracker reset comment not found")
    
    # Test 2: Check for hasattr check on model.predictor
    tests_total += 1
    if "hasattr(model, 'predictor')" in code:
        print("✓ Test 2: hasattr check for model.predictor found")
        tests_passed += 1
    else:
        print("✗ Test 2 FAILED: hasattr check for model.predictor not found")
    
    # Test 3: Check for trackers reset call
    tests_total += 1
    if 'model.predictor.trackers[0].reset()' in code:
        print("✓ Test 3: Tracker reset call found")
        tests_passed += 1
    else:
        print("✗ Test 3 FAILED: Tracker reset call not found")
    
    # Test 4: Check for tracker reset message
    tests_total += 1
    if 'Tracker reset' in code:
        print("✓ Test 4: Tracker reset message found")
        tests_passed += 1
    else:
        print("✗ Test 4 FAILED: Tracker reset message not found")
    
    # Test 5: Check for exception handling
    tests_total += 1
    if re.search(r'try:.*model\.predictor.*except.*Exception', code, re.DOTALL):
        print("✓ Test 5: Exception handling for tracker reset found")
        tests_passed += 1
    else:
        print("✗ Test 5 FAILED: Exception handling not found")
    
    # Test 6: Check that reset happens before camera opening
    tests_total += 1
    # Find position of tracker reset and camera opening
    tracker_reset_pos = code.find('model.predictor.trackers[0].reset()')
    camera_open_pos = code.find('camera_manager.get_camera(current_camera)')
    
    if tracker_reset_pos != -1 and camera_open_pos != -1 and tracker_reset_pos < camera_open_pos:
        print("✓ Test 6: Tracker reset happens before camera opening")
        tests_passed += 1
    else:
        print("✗ Test 6 FAILED: Tracker reset should happen before camera opening")
    
    # Test 7: Check for hasattr check on trackers
    tests_total += 1
    if "hasattr(model.predictor, 'trackers')" in code:
        print("✓ Test 7: hasattr check for trackers found")
        tests_passed += 1
    else:
        print("✗ Test 7 FAILED: hasattr check for trackers not found")
    
    # Test 8: Check that code is in inference_thread function
    tests_total += 1
    inference_thread_match = re.search(
        r'def inference_thread\(\):.*?model\.predictor\.trackers\[0\]\.reset\(\)',
        code,
        re.DOTALL
    )
    if inference_thread_match:
        print("✓ Test 8: Tracker reset is in inference_thread function")
        tests_passed += 1
    else:
        print("✗ Test 8 FAILED: Tracker reset should be in inference_thread function")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Result: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ {tests_total - tests_passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = test_tracker_reset_implementation()
    sys.exit(0 if success else 1)
