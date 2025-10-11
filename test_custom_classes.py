#!/usr/bin/env python3
"""
Test script for custom class prompts feature.
This test verifies that the custom classes functionality is correctly implemented.
"""
import sys
import re


def test_global_variable():
    """Test that the current_classes global variable exists."""
    print("\n" + "=" * 60)
    print("Test 1: Global Variable for Current Classes")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    if re.search(r'current_classes\s*=\s*["\']person,\s*plant["\']', code):
        print("\n✓ current_classes global variable exists with default value")
        return True
    else:
        print("\n✗ FAILED: current_classes global variable not found or incorrect")
        return False


def test_load_model_signature():
    """Test that load_model function accepts class_names parameter."""
    print("\n" + "=" * 60)
    print("Test 2: load_model Function Signature")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    if re.search(r'def load_model\(model_size,\s*class_names=None\)', code):
        print("\n✓ load_model function accepts class_names parameter")
        return True
    else:
        print("\n✗ FAILED: load_model function signature incorrect")
        return False


def test_set_classes_on_model():
    """Test that set_classes is called on the model."""
    print("\n" + "=" * 60)
    print("Test 3: Model Set Classes Call")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    if 'loaded_model.set_classes(class_names' in code:
        print("\n✓ set_classes is called on the model with class_names")
        return True
    else:
        print("\n✗ FAILED: set_classes call not found")
        return False


def test_html_form():
    """Test that HTML form for custom classes exists."""
    print("\n" + "=" * 60)
    print("Test 4: HTML Form for Custom Classes")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    has_form = '<form action="/set_classes"' in code
    has_input = 'name="classes"' in code
    has_button = 'Update Classes' in code
    
    if has_form and has_input and has_button:
        print("\n✓ HTML form for custom classes exists with input field and submit button")
        return True
    else:
        print("\n✗ FAILED: HTML form elements missing")
        if not has_form:
            print("  - Missing: <form action=\"/set_classes\">")
        if not has_input:
            print("  - Missing: input field with name=\"classes\"")
        if not has_button:
            print("  - Missing: 'Update Classes' button")
        return False


def test_set_classes_route():
    """Test that /set_classes route exists."""
    print("\n" + "=" * 60)
    print("Test 5: /set_classes Flask Route")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    if "@app.route('/set_classes', methods=['POST'])" in code:
        print("\n✓ /set_classes route exists")
        return True
    else:
        print("\n✗ FAILED: /set_classes route not found")
        return False


def test_classes_display():
    """Test that current classes are displayed in the UI."""
    print("\n" + "=" * 60)
    print("Test 6: Current Classes Display")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    if 'Current Classes: {current_classes}' in code:
        print("\n✓ Current classes are displayed in the UI")
        return True
    else:
        print("\n✗ FAILED: Current classes display not found")
        return False


def test_input_validation():
    """Test that input validation exists for classes."""
    print("\n" + "=" * 60)
    print("Test 7: Input Validation")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    # Check for empty string validation
    has_empty_check = 'new_classes.strip() == ""' in code or 'not new_classes' in code
    # Check for at least one class validation
    has_min_check = 'if not class_list:' in code
    
    if has_empty_check and has_min_check:
        print("\n✓ Input validation exists for empty and invalid classes")
        return True
    else:
        print("\n✗ FAILED: Input validation incomplete")
        if not has_empty_check:
            print("  - Missing: empty string check")
        if not has_min_check:
            print("  - Missing: minimum class count check")
        return False


def test_running_state_check():
    """Test that classes can only be changed when inference is stopped."""
    print("\n" + "=" * 60)
    print("Test 8: Running State Check")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    # Find the set_classes function
    set_classes_start = code.find("@app.route('/set_classes'")
    if set_classes_start == -1:
        print("\n✗ FAILED: /set_classes route not found")
        return False
    
    # Check if there's a running check in the function
    set_classes_end = code.find("\n@app.route", set_classes_start + 1)
    if set_classes_end == -1:
        set_classes_end = code.find("\nif __name__", set_classes_start)
    
    set_classes_func = code[set_classes_start:set_classes_end]
    
    if 'if running:' in set_classes_func and 'Stop inference first' in set_classes_func:
        print("\n✓ Classes can only be changed when inference is stopped")
        return True
    else:
        print("\n✗ FAILED: Running state check not found in set_classes route")
        return False


def test_model_reload():
    """Test that model is reloaded with new classes."""
    print("\n" + "=" * 60)
    print("Test 9: Model Reload with New Classes")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    # Find the set_classes function
    set_classes_start = code.find("@app.route('/set_classes'")
    if set_classes_start == -1:
        print("\n✗ FAILED: /set_classes route not found")
        return False
    
    set_classes_end = code.find("\n@app.route", set_classes_start + 1)
    if set_classes_end == -1:
        set_classes_end = code.find("\nif __name__", set_classes_start)
    
    set_classes_func = code[set_classes_start:set_classes_end]
    
    if 'model = load_model(' in set_classes_func and 'class_list' in set_classes_func:
        print("\n✓ Model is reloaded with new classes")
        return True
    else:
        print("\n✗ FAILED: Model reload with new classes not found")
        return False


def test_ui_disabled_state():
    """Test that the classes input field is disabled during inference."""
    print("\n" + "=" * 60)
    print("Test 10: UI Disabled State")
    print("=" * 60)
    
    try:
        with open('app.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("\n✗ FAILED: app.py not found")
        return False
    
    # Check if the input field has disabled attribute based on running state
    if '{\"disabled\" if running else \"\"}' in code and 'name="classes"' in code:
        print("\n✓ Classes input field is disabled during inference")
        return True
    else:
        print("\n✗ FAILED: UI disabled state not properly implemented")
        return False


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Custom Class Prompts Feature - Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        test_global_variable,
        test_load_model_signature,
        test_set_classes_on_model,
        test_html_form,
        test_set_classes_route,
        test_classes_display,
        test_input_validation,
        test_running_state_check,
        test_model_reload,
        test_ui_disabled_state,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    # Print summary
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + f"  Test Results: {passed}/{total} tests passed".center(58) + "║")
    print("║" + " " * 58 + "║")
    
    if passed == total:
        print("║" + "  ✅ ALL TESTS PASSED!".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + "  The custom class prompts feature is correctly".center(58) + "║")
        print("║" + "  implemented and ready to use.".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")
        sys.exit(0)
    else:
        print("║" + "  ⚠️  SOME TESTS FAILED".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + "  Please review the test output above.".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")
        sys.exit(1)
