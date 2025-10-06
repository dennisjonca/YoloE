"""
Test script to verify the /process_frame endpoint
"""
import requests
import cv2
import numpy as np
import base64
import json

# Create a test image
def create_test_image():
    """Create a simple test image with some shapes"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 255  # White background
    
    # Draw some shapes to give YOLOv8 something to detect
    cv2.rectangle(img, (100, 100), (300, 300), (255, 0, 0), -1)  # Blue rectangle
    cv2.circle(img, (500, 250), 80, (0, 255, 0), -1)  # Green circle
    
    return img

# Encode image to base64
def encode_image(img):
    """Encode image to base64 string"""
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

# Test the endpoint
def test_process_frame():
    """Test the /process_frame endpoint"""
    print("Testing /process_frame endpoint...")
    
    # Create and encode test image
    img = create_test_image()
    img_data = encode_image(img)
    
    # Send request
    url = "http://localhost:5000/process_frame"
    payload = {"image": img_data}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"\n✓ Processing successful!")
            print(f"  Detections: {len(result.get('detections', []))}")
            return True
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

if __name__ == '__main__':
    test_process_frame()
