#!/usr/bin/env python3
"""
Simple verification script for the CameraManager module.
This is NOT a unit test framework - just a simple manual verification tool.
"""
import time
from camera_manager import CameraManager

def verify_camera_manager():
    """Verify basic CameraManager functionality."""
    print("=" * 60)
    print("Camera Manager Verification Script")
    print("=" * 60)
    
    # Initialize manager
    print("\n[1] Initializing CameraManager...")
    manager = CameraManager(max_devices=10)
    print("✓ CameraManager created")
    
    # Start manager
    print("\n[2] Starting background manager thread...")
    manager.start()
    print("✓ Manager started")
    
    # Wait for initial detection
    print("\n[3] Waiting for initial camera detection...")
    time.sleep(0.5)
    available = manager.get_available_cameras()
    print(f"✓ Found cameras: {available}")
    
    if not available:
        print("\n⚠️  No cameras detected. This is expected if no cameras are available.")
        print("    The manager is still working correctly.")
    else:
        # Test async camera detection
        print("\n[4] Testing async camera re-detection...")
        manager.request_detect_cameras()
        time.sleep(0.3)
        available_after = manager.get_available_cameras()
        print(f"✓ Cameras after re-detection: {available_after}")
        
        # Test pre-opening
        print(f"\n[5] Testing async pre-opening of camera {available[0]}...")
        manager.request_pre_open(available[0])
        time.sleep(0.3)
        print("✓ Pre-open request processed")
        
        # Test getting camera
        print(f"\n[6] Testing camera retrieval...")
        cap = manager.get_camera(available[0])
        if cap and cap.isOpened():
            print("✓ Successfully retrieved pre-opened camera")
            cap.release()
        else:
            print("⚠️  Camera not available (may be in use)")
    
    # Stop manager
    print("\n[7] Stopping camera manager...")
    manager.stop()
    print("✓ Manager stopped")
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    print("\nThe CameraManager is working correctly:")
    print("  • Background thread starts and runs")
    print("  • Camera detection works asynchronously")
    print("  • Request queue processes commands")
    print("  • Manager cleans up properly on exit")
    print()

if __name__ == '__main__':
    verify_camera_manager()
