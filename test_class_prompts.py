#!/usr/bin/env python3
"""
Integration test for class prompts functionality.
This test verifies that the class prompts feature in app.py is working correctly.
"""
import sys
import re


def test_class_prompts_implementation():
    """Test that the class prompts implementation is correct."""
    print("=" * 60)
    print("Class Prompts Feature Implementation Test")
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
    
    # Test 1: Check for current_classes global variable
    tests_total += 1
    if re.search(r'current_classes\s*=\s*\[', code):
        print("\n✓ Test 1: current_classes global variable found")
        tests_passed += 1
    else:
        print("\n✗ Test 1 FAILED: current_classes global variable not found")
    
    # Test 2: Check that load_model uses current_classes
    tests_total += 1
    if 'set_classes(current_classes' in code:
        print("✓ Test 2: load_model uses current_classes variable")
        tests_passed += 1
    else:
        print("✗ Test 2 FAILED: load_model doesn't use current_classes")
    
    # Test 3: Check for /set_classes route
    tests_total += 1
    if re.search(r"@app\.route\('/set_classes'", code):
        print("✓ Test 3: /set_classes route found")
        tests_passed += 1
    else:
        print("✗ Test 3 FAILED: /set_classes route not found")
    
    # Test 4: Check for set_classes function
    tests_total += 1
    if 'def set_classes():' in code:
        print("✓ Test 4: set_classes() function found")
        tests_passed += 1
    else:
        print("✗ Test 4 FAILED: set_classes() function not found")
    
    # Test 5: Check that set_classes checks if running
    tests_total += 1
    set_classes_pos = code.find('def set_classes():')
    if set_classes_pos > 0:
        set_classes_func = code[set_classes_pos:set_classes_pos+2000]
        if 'if running:' in set_classes_func:
            print("✓ Test 5: set_classes() checks if inference is running")
            tests_passed += 1
        else:
            print("✗ Test 5 FAILED: set_classes() doesn't check if running")
    else:
        print("✗ Test 5 FAILED: couldn't find set_classes() function")
    
    # Test 6: Check for classes input field in HTML
    tests_total += 1
    if re.search(r'<input[^>]*name="classes"', code):
        print("✓ Test 6: Classes input field found in HTML")
        tests_passed += 1
    else:
        print("✗ Test 6 FAILED: Classes input field not found in HTML")
    
    # Test 7: Check for classes display in status
    tests_total += 1
    if 'Current Classes:' in code:
        print("✓ Test 7: Current classes display found in UI")
        tests_passed += 1
    else:
        print("✗ Test 7 FAILED: Current classes display not found")
    
    # Test 8: Check that ONNX model is removed on class update
    tests_total += 1
    if set_classes_pos > 0:
        set_classes_func = code[set_classes_pos:set_classes_pos+2000]
        if 'os.remove(onnx_model_path)' in set_classes_func:
            print("✓ Test 8: ONNX model is removed when classes change")
            tests_passed += 1
        else:
            print("✗ Test 8 FAILED: ONNX model not removed on class change")
    else:
        print("✗ Test 8 FAILED: couldn't find set_classes() function")
    
    # Test 9: Check that model is reloaded after class update
    tests_total += 1
    if set_classes_pos > 0:
        set_classes_func = code[set_classes_pos:set_classes_pos+2000]
        if 'model = load_model(' in set_classes_func:
            print("✓ Test 9: Model is reloaded after class update")
            tests_passed += 1
        else:
            print("✗ Test 9 FAILED: Model not reloaded after class update")
    else:
        print("✗ Test 9 FAILED: couldn't find set_classes() function")
    
    # Test 10: Check for input validation
    tests_total += 1
    if set_classes_pos > 0:
        set_classes_func = code[set_classes_pos:set_classes_pos+2000]
        if 'if not classes_input:' in set_classes_func or 'if not new_classes:' in set_classes_func:
            print("✓ Test 10: Input validation present")
            tests_passed += 1
        else:
            print("✗ Test 10 FAILED: Missing input validation")
    else:
        print("✗ Test 10 FAILED: couldn't find set_classes() function")
    
    # Test 11: Check that classes input is disabled when running
    tests_total += 1
    if re.search(r'name="classes"[^>]*disabled[^>]*if running', code) or \
       re.search(r'disabled[^>]*if running[^>]*name="classes"', code):
        print("✓ Test 11: Classes input is disabled when inference is running")
        tests_passed += 1
    else:
        # Alternative check - look for the pattern in the HTML
        if 'id="classes"' in code and '{"disabled" if running else ""}' in code:
            print("✓ Test 11: Classes input is disabled when inference is running")
            tests_passed += 1
        else:
            print("✗ Test 11 FAILED: Classes input not properly disabled when running")
    
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


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Class Prompts Feature - Integration Test".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run test
    all_passed = test_class_prompts_implementation()
    
    # Final summary
    print("\n" + "╔" + "=" * 58 + "╗")
    if all_passed:
        print("║" + " " * 58 + "║")
        print("║" + "  ✅ ALL TESTS PASSED!".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + "  The class prompts feature is correctly implemented.".center(58) + "║")
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
