"""
Test script to verify YOLOv8 model loading and basic functionality
"""
import sys
import numpy as np
from ultralytics import YOLO

def test_model_loading():
    """Test if YOLOv8 model can be loaded"""
    print("Testing YOLOv8 model loading...")
    try:
        model = YOLO('yolov8n.pt')
        print("✓ Model loaded successfully")
        print(f"  Model type: {type(model)}")
        print(f"  Model names: {len(model.names)} classes")
        return True
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False

def test_inference():
    """Test if inference works on a dummy image"""
    print("\nTesting inference on dummy image...")
    try:
        model = YOLO('yolov8n.pt')
        
        # Create a dummy image (640x480 RGB)
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Run inference with tracking
        results = model.track(dummy_image, persist=True, verbose=False)
        
        print("✓ Inference successful")
        print(f"  Results type: {type(results)}")
        print(f"  Number of detections: {len(results[0].boxes) if results[0].boxes is not None else 0}")
        return True
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        return False

def test_flask_imports():
    """Test if Flask and dependencies can be imported"""
    print("\nTesting Flask imports...")
    try:
        from flask import Flask, render_template, Response, jsonify
        from flask_cors import CORS
        import base64
        print("✓ All Flask imports successful")
        return True
    except Exception as e:
        print(f"✗ Flask import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("YOLOv8 Webcam Inference - Test Suite")
    print("="*50)
    
    tests = [
        test_flask_imports,
        test_model_loading,
        test_inference
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("="*50)
    
    if all(results):
        print("\n✓ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nThen open http://localhost:5000 in your browser")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
