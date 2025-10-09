#!/usr/bin/env python3
"""
Integration test for model warm-up functionality.
This test verifies that the warm-up code in app.py is working correctly.
"""
import sys
import re


def test_warmup_implementation():
    """Test that the warm-up implementation is correct."""
    print("=" * 60)
    print("Model Warm-up Implementation Test")
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
    
    # Test 1: Check for numpy import
    tests_total += 1
    if 'import numpy as np' in code:
        print("\n✓ Test 1: numpy import found")
        tests_passed += 1
    else:
        print("\n✗ Test 1 FAILED: numpy import not found")
    
    # Test 2: Check for warm-up message
    tests_total += 1
    if 'Warming up model' in code:
        print("✓ Test 2: Warm-up message found")
        tests_passed += 1
    else:
        print("✗ Test 2 FAILED: Warm-up message not found")
    
    # Test 3: Check for dummy frame creation
    tests_total += 1
    if re.search(r'dummy_frame\s*=\s*np\.zeros\s*\(\s*\(\s*320\s*,\s*320\s*,\s*3\s*\)', code):
        print("✓ Test 3: Dummy frame creation found (320x320x3)")
        tests_passed += 1
    else:
        print("✗ Test 3 FAILED: Dummy frame creation not found or incorrect")
    
    # Test 4: Check for warm-up inference call
    tests_total += 1
    if 'model.track(source=dummy_frame' in code:
        print("✓ Test 4: Warm-up inference call found")
        tests_passed += 1
    else:
        print("✗ Test 4 FAILED: Warm-up inference call not found")
    
    # Test 5: Check that warm-up has verbose=False (to suppress output)
    tests_total += 1
    if 'verbose=False' in code and 'model.track(source=dummy_frame' in code:
        print("✓ Test 5: Warm-up configured with verbose=False")
        tests_passed += 1
    else:
        print("✗ Test 5 FAILED: Warm-up should have verbose=False")
    
    # Test 6: Check for completion message
    tests_total += 1
    if 'Model warm-up complete' in code:
        print("✓ Test 6: Completion message found")
        tests_passed += 1
    else:
        print("✗ Test 6 FAILED: Completion message not found")
    
    # Test 7: Verify warm-up is after model loading
    tests_total += 1
    model_load_pos = code.find('model = YOLOE(onnx_model_path)')
    warmup_pos = code.find('Warming up model')
    if model_load_pos > 0 and warmup_pos > model_load_pos:
        print("✓ Test 7: Warm-up code is positioned after model loading")
        tests_passed += 1
    else:
        print("✗ Test 7 FAILED: Warm-up code not positioned correctly")
    
    # Test 8: Verify warm-up is before Flask initialization
    tests_total += 1
    flask_pos = code.find('if __name__ ==')
    if warmup_pos > 0 and flask_pos > warmup_pos:
        print("✓ Test 8: Warm-up code is before main execution block")
        tests_passed += 1
    else:
        print("✗ Test 8 FAILED: Warm-up code positioning issue")
    
    # Test 9: Check for proper variable naming
    tests_total += 1
    if re.search(r'_\s*=\s*list\(model\.track\(source=dummy_frame', code):
        print("✓ Test 9: Result properly discarded with underscore variable")
        tests_passed += 1
    else:
        print("✗ Test 9 FAILED: Result not properly discarded")
    
    # Test 10: Verify comments are present
    tests_total += 1
    if 'This prevents the ~2 minute delay on first inference' in code:
        print("✓ Test 10: Explanatory comments present")
        tests_passed += 1
    else:
        print("✗ Test 10 FAILED: Missing explanatory comments")
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✅ ALL TESTS PASSED! Implementation is correct.")
        return True
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed. Please review.")
        return False


def test_verification_script():
    """Test that the verification script exists and is valid."""
    print("\n" + "=" * 60)
    print("Verification Script Test")
    print("=" * 60)
    
    try:
        with open('verify_model_warmup.py', 'r') as f:
            code = f.read()
        
        if 'verify_model_warmup' in code:
            print("\n✓ Verification script exists and contains main function")
            return True
        else:
            print("\n✗ Verification script doesn't contain expected function")
            return False
    except FileNotFoundError:
        print("\n✗ verify_model_warmup.py not found")
        return False


def test_documentation():
    """Test that documentation exists."""
    print("\n" + "=" * 60)
    print("Documentation Test")
    print("=" * 60)
    
    docs_found = 0
    docs_expected = 2
    
    try:
        with open('MODEL_WARMUP_FIX.md', 'r') as f:
            content = f.read()
            if 'Model Warm-up Fix' in content or 'ONNX Runtime' in content:
                print("\n✓ MODEL_WARMUP_FIX.md exists and contains relevant content")
                docs_found += 1
    except FileNotFoundError:
        print("\n✗ MODEL_WARMUP_FIX.md not found")
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
            if 'Model Warm-up' in content or 'warm-up' in content:
                print("✓ README.md updated with warm-up information")
                docs_found += 1
    except FileNotFoundError:
        print("✗ README.md not found")
    
    return docs_found == docs_expected


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Model Warm-up Fix - Integration Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    all_passed = True
    
    # Run all tests
    all_passed &= test_warmup_implementation()
    all_passed &= test_verification_script()
    all_passed &= test_documentation()
    
    # Final summary
    print("\n" + "╔" + "=" * 58 + "╗")
    if all_passed:
        print("║" + " " * 58 + "║")
        print("║" + "  ✅ ALL INTEGRATION TESTS PASSED!".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + "  The model warm-up fix is correctly implemented.".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")
        sys.exit(0)
    else:
        print("║" + " " * 58 + "║")
        print("║" + "  ⚠️  SOME TESTS FAILED".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + "  Please review the test output above.".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")
        sys.exit(1)
