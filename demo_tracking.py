"""
Standalone demo of YOLOv8 tracking on a video file
This demonstrates the track() method used in the web application
"""
import cv2
from ultralytics import YOLO
import sys

def demo_tracking(video_source=0):
    """
    Demonstrate YOLOv8 tracking on a video source
    
    Args:
        video_source: 0 for webcam, or path to video file
    """
    # Load YOLOv8 model
    print("Loading YOLOv8 model...")
    model = YOLO('yolov8n.pt')
    
    # Open video source
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {video_source}")
        return
    
    print(f"Processing video from: {video_source}")
    print("Press 'q' to quit")
    
    frame_count = 0
    
    # Process video frames
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("End of video or error reading frame")
            break
        
        frame_count += 1
        
        # Run YOLOv8 tracking
        # persist=True maintains track IDs across frames
        results = model.track(frame, persist=True, verbose=False)
        
        # Get annotated frame with bounding boxes
        annotated_frame = results[0].plot()
        
        # Display frame info
        cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow('YOLOv8 Tracking Demo', annotated_frame)
        
        # Print detection info
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            print(f"\nFrame {frame_count}:")
            for i in range(len(boxes)):
                cls = int(boxes.cls[i])
                conf = float(boxes.conf[i])
                track_id = int(boxes.id[i]) if boxes.id is not None else None
                class_name = model.names[cls]
                print(f"  {class_name} (ID:{track_id}): {conf:.2f}")
        
        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nQuitting...")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessed {frame_count} frames")

if __name__ == '__main__':
    # Use webcam by default, or provide video file path as argument
    source = 0 if len(sys.argv) < 2 else sys.argv[1]
    
    print("="*50)
    print("YOLOv8 Tracking Demo")
    print("="*50)
    print()
    
    try:
        demo_tracking(source)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
