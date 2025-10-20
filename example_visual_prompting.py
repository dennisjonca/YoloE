#!/usr/bin/env python3
"""
Example script demonstrating the correct YOLOE visual prompting API usage.

This script shows how visual prompting works with the official Ultralytics API,
which is now implemented in app.py.

Based on official documentation:
https://docs.ultralytics.com/models/yoloe/#visual-prompting
"""

import numpy as np
import cv2

def example_single_image():
    """
    Example: Visual prompting with a single image.
    
    This is the basic pattern from the official documentation.
    """
    print("=" * 60)
    print("Example 1: Single Image Visual Prompting")
    print("=" * 60)
    
    try:
        from ultralytics import YOLOE
        from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor
        
        # Load model
        print("\n1. Loading YOLOE model...")
        model = YOLOE("yoloe-11s-seg.pt")
        
        # Create a dummy image (in real usage, this would be your actual image)
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(image, (100, 100), (200, 200), (255, 255, 255), -1)
        
        # Define visual prompts with absolute pixel coordinates
        print("\n2. Creating visual prompts...")
        visual_prompts = dict(
            bboxes=[[100, 100, 200, 200]],  # List of boxes (absolute coordinates)
            cls=[0],  # List of class IDs (integers, 0-based)
        )
        
        print(f"   Bounding boxes: {visual_prompts['bboxes']}")
        print(f"   Class names: {visual_prompts['cls']}")
        
        # Run inference with visual prompts
        print("\n3. Running inference with visual prompts...")
        results = model.predict(
            source=image,
            visual_prompts=visual_prompts,
            predictor=YOLOEVPSegPredictor,
            conf=0.25,
            show=False,
            verbose=False
        )
        
        print(f"   ✓ Inference completed")
        print(f"   Number of results: {len(results)}")
        
        # Process results
        for i, result in enumerate(results):
            boxes = result.boxes.xyxy.cpu().numpy()
            print(f"   Result {i}: {len(boxes)} detections")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_video_stream():
    """
    Example: Visual prompting with video stream (continuous frames).
    
    This is how app.py uses visual prompting for camera feed.
    """
    print("\n" + "=" * 60)
    print("Example 2: Video Stream Visual Prompting")
    print("=" * 60)
    
    try:
        from ultralytics import YOLOE
        from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor
        
        # Load model
        print("\n1. Loading YOLOE model...")
        model = YOLOE("yoloe-11s-seg.pt")
        
        # Define visual prompts once (from captured snapshot)
        print("\n2. Creating visual prompts from snapshot...")
        visual_prompts = dict(
            bboxes=[[150, 120, 250, 220]],  # List of boxes
            cls=[0],  # List of class IDs
        )
        
        print(f"   Visual prompts defined: {len(visual_prompts['bboxes'])} boxes")
        
        # Simulate video stream (in real usage, this would be camera frames)
        print("\n3. Processing video frames with visual prompts...")
        for frame_num in range(3):
            # Create dummy frame
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Run inference with the same visual prompts for each frame
            results = model.predict(
                source=frame,
                visual_prompts=visual_prompts,  # Same prompts used for all frames
                predictor=YOLOEVPSegPredictor,
                conf=0.25,
                show=False,
                verbose=False
            )
            
            detections = len(results[0].boxes.xyxy) if results else 0
            print(f"   Frame {frame_num + 1}: {detections} detections")
        
        print(f"   ✓ Video stream processing completed")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_multiple_boxes():
    """
    Example: Visual prompting with multiple bounding boxes.
    
    Shows how to track multiple objects or object types.
    """
    print("\n" + "=" * 60)
    print("Example 3: Multiple Boxes Visual Prompting")
    print("=" * 60)
    
    try:
        from ultralytics import YOLOE
        from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor
        
        # Load model
        print("\n1. Loading YOLOE model...")
        model = YOLOE("yoloe-11s-seg.pt")
        
        # Create image with multiple objects
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (150, 150), (255, 0, 0), -1)  # Blue square
        cv2.rectangle(image, (300, 200), (400, 300), (0, 255, 0), -1)  # Green square
        cv2.circle(image, (500, 100), 50, (0, 0, 255), -1)  # Red circle
        
        # Define visual prompts for multiple objects
        print("\n2. Creating visual prompts for multiple objects...")
        visual_prompts = dict(
            bboxes=[
                [50, 50, 150, 150],    # Box around blue square
                [300, 200, 400, 300],  # Box around green square
                [450, 50, 550, 150],   # Box around red circle
            ],
            cls=[0, 0, 0],  # All same class ID (generic object)
        )
        
        print(f"   Number of boxes: {len(visual_prompts['bboxes'])}")
        print(f"   Box 1: {visual_prompts['bboxes'][0]}")
        print(f"   Box 2: {visual_prompts['bboxes'][1]}")
        print(f"   Box 3: {visual_prompts['bboxes'][2]}")
        
        # Run inference
        print("\n3. Running inference with multiple visual prompts...")
        results = model.predict(
            source=image,
            visual_prompts=visual_prompts,
            predictor=YOLOEVPSegPredictor,
            conf=0.25,
            show=False,
            verbose=False
        )
        
        print(f"   ✓ Inference completed")
        detections = len(results[0].boxes.xyxy) if results else 0
        print(f"   Detections: {detections}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def explain_coordinate_system():
    """
    Explain the coordinate system used in visual prompting.
    """
    print("\n" + "=" * 60)
    print("Understanding Coordinate Systems")
    print("=" * 60)
    
    print("\n1. UI Coordinates (Relative 0-1):")
    print("   - JavaScript canvas uses relative coordinates")
    print("   - x and y are in range [0, 1]")
    print("   - Example: {x1: 0.2, y1: 0.3, x2: 0.4, y2: 0.5}")
    
    print("\n2. Absolute Pixel Coordinates:")
    print("   - YOLOE API expects absolute pixel coordinates")
    print("   - x and y are actual pixel positions")
    print("   - Example for 640x480 image: [128, 144, 256, 240]")
    
    print("\n3. Conversion (in app.py save_visual_prompt):")
    print("   ```python")
    print("   h, w = image.shape[:2]  # Get image dimensions")
    print("   x1 = int(box['x1'] * w)  # Convert relative to absolute")
    print("   y1 = int(box['y1'] * h)")
    print("   x2 = int(box['x2'] * w)")
    print("   y2 = int(box['y2'] * h)")
    print("   ```")
    
    print("\n4. Important Notes:")
    print("   - NO normalization after conversion to absolute")
    print("   - Boxes stay in pixel coordinates")
    print("   - YOLOE API handles any internal normalization")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("YOLOE Visual Prompting Examples")
    print("=" * 60)
    print("\nThese examples demonstrate the correct usage of YOLOE visual")
    print("prompting API, which is now implemented in app.py")
    
    examples = [
        ("Single Image", example_single_image),
        ("Video Stream", example_video_stream),
        ("Multiple Boxes", example_multiple_boxes),
    ]
    
    results = []
    for name, func in examples:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} example failed: {e}")
            results.append((name, False))
    
    # Explain coordinates
    explain_coordinate_system()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print(f"\nExamples completed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All examples ran successfully!")
        print("\nKey Takeaways:")
        print("1. Use predict() with YOLOEVPSegPredictor")
        print("2. Pass visual_prompts dict with bboxes and cls")
        print("3. Boxes in absolute pixel coordinates")
        print("4. Visual prompts passed per-frame for video")
        return 0
    else:
        print(f"\n✗ {total - passed} example(s) failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
