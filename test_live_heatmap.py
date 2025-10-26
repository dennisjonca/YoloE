#!/usr/bin/env python3
"""
Test script for live heatmap mode functionality.
Tests the heatmap mode toggle and integration with the app.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("Live Heatmap Mode Test")
    print("=" * 60)
    
    print("\n1. Testing imports...")
    
    try:
        import app
        print("   ✓ app module imported")
    except Exception as e:
        print(f"   ✗ Failed to import app: {e}")
        return False
    
    try:
        from heatmap_generator import YoloEHeatmapGenerator, get_default_params
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


def test_heatmap_state():
    """Test heatmap mode state variables."""
    print("\n2. Testing heatmap mode state...")
    
    try:
        import app
        
        # Check heatmap_mode exists
        if not hasattr(app, 'heatmap_mode'):
            print("   ✗ heatmap_mode variable not found")
            return False
        print("   ✓ heatmap_mode variable exists")
        
        # Check heatmap_generator exists
        if not hasattr(app, 'heatmap_generator'):
            print("   ✗ heatmap_generator variable not found")
            return False
        print("   ✓ heatmap_generator variable exists")
        
        # Check initial state
        if app.heatmap_mode is not False:
            print(f"   ✗ heatmap_mode should be False initially, got {app.heatmap_mode}")
            return False
        print("   ✓ heatmap_mode is False by default")
        
        if app.heatmap_generator is not None:
            print(f"   ✗ heatmap_generator should be None initially, got {app.heatmap_generator}")
            return False
        print("   ✓ heatmap_generator is None by default")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing heatmap state: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_toggle_route():
    """Test the /toggle_heatmap route exists."""
    print("\n3. Testing /toggle_heatmap route...")
    
    try:
        import app
        from flask import Flask
        
        # Get all routes
        routes = [str(rule) for rule in app.app.url_map.iter_rules()]
        
        if '/toggle_heatmap' not in routes:
            print(f"   ✗ /toggle_heatmap route not found")
            print(f"   Available routes: {routes}")
            return False
        print("   ✓ /toggle_heatmap route exists")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing toggle route: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_heatmap_functions():
    """Test that heatmap-related functions exist."""
    print("\n4. Testing heatmap utility functions...")
    
    try:
        from heatmap_generator import letterbox, get_default_params
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
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing heatmap functions: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_updates():
    """Test that UI has heatmap mode controls."""
    print("\n5. Testing UI updates...")
    
    try:
        import app
        
        # Temporarily set test mode to generate UI
        app.running = False
        app.heatmap_mode = False
        app.available_cameras = [0]
        
        with app.app.test_client() as client:
            response = client.get('/')
            html = response.data.decode('utf-8')
            
            # Check for heatmap mode status
            if 'Heatmap Mode:' not in html:
                print("   ✗ Heatmap mode status not found in UI")
                return False
            print("   ✓ Heatmap mode status displayed in UI")
            
            # Check for toggle button
            if 'toggle_heatmap' not in html:
                print("   ✗ Heatmap toggle button not found in UI")
                return False
            print("   ✓ Heatmap toggle button present in UI")
            
            # Check for mode indicator text
            if 'Enable Heatmap Mode' not in html and 'Disable Heatmap Mode' not in html:
                print("   ✗ Heatmap mode toggle text not found")
                return False
            print("   ✓ Heatmap mode toggle text present")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Error testing UI updates: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    tests = [
        test_imports,
        test_heatmap_state,
        test_toggle_route,
        test_heatmap_functions,
        test_ui_updates
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
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
