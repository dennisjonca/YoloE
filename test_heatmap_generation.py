#!/usr/bin/env python3
"""
Test script for heatmap generation functionality.
Tests the heatmap_generator module with a synthetic test image.
"""

import os
import sys
import cv2
import numpy as np
from heatmap_generator import YoloEHeatmapGenerator, get_default_params


def create_test_image():
    """Create a simple test image with some shapes."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some colored shapes for testing
    cv2.rectangle(img, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue square
    cv2.circle(img, (400, 240), 80, (0, 255, 0), -1)  # Green circle
    cv2.rectangle(img, (450, 300), (580, 400), (0, 0, 255), -1)  # Red rectangle
    return img


def test_heatmap_generation():
    """Test heatmap generation with a synthetic image."""
    print("=" * 60)
    print("Heatmap Generation Test")
    print("=" * 60)
    
    # Check if model file exists
    model_path = "yoloe-11s-seg.pt"
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        print("  Please ensure the model file is present in the current directory.")
        return False
    
    print(f"✓ Model file found: {model_path}")
    
    # Create test image
    print("\n1. Creating test image...")
    test_img = create_test_image()
    print(f"   ✓ Test image created: {test_img.shape}")
    
    # Create output directory
    os.makedirs('heatmaps', exist_ok=True)
    output_path = 'heatmaps/test_heatmap.jpg'
    
    try:
        # Get default parameters
        print("\n2. Initializing heatmap generator...")
        params = get_default_params()
        params['show_box'] = True
        params['device'] = 'cpu'  # Use CPU for testing
        
        print(f"   Parameters:")
        print(f"   - Device: {params['device']}")
        print(f"   - Method: {params['method']}")
        print(f"   - Layers: {params['layer']}")
        print(f"   - Confidence: {params['conf_threshold']}")
        
        # Create generator
        generator = YoloEHeatmapGenerator(model_path, **params)
        print(f"   ✓ Generator initialized")
        
        # Generate heatmap
        print("\n3. Generating heatmap...")
        success = generator.generate(test_img, output_path)
        
        if success:
            print(f"   ✓ Heatmap generated successfully")
            print(f"   ✓ Saved to: {output_path}")
            
            # Verify file exists and has reasonable size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✓ File size: {file_size / 1024:.2f} KB")
                
                if file_size > 1000:  # At least 1KB
                    print("\n" + "=" * 60)
                    print("✓ All tests passed!")
                    print("=" * 60)
                    return True
                else:
                    print(f"   ✗ Generated file is too small (may be corrupted)")
                    return False
            else:
                print(f"   ✗ Output file not found after generation")
                return False
        else:
            print(f"   ✗ Heatmap generation failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error during heatmap generation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_heatmap_generation()
    sys.exit(0 if success else 1)
