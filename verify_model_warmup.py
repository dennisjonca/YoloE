#!/usr/bin/env python3
"""
Verification script to demonstrate model warm-up functionality.
This shows that the ONNX Runtime session is initialized during startup,
preventing the ~2 minute delay on first inference.
"""
import time
import numpy as np
from ultralytics import YOLOE
import os


def verify_model_warmup():
    """Verify that model warm-up works correctly."""
    print("=" * 60)
    print("Model Warm-up Verification Script")
    print("=" * 60)
    
    onnx_model_path = "yoloe-11s-seg.onnx"
    
    # Check if ONNX model exists
    if not os.path.exists(onnx_model_path):
        print(f"\n⚠️  ONNX model not found at {onnx_model_path}")
        print("Please run the main app.py first to generate the ONNX model.")
        return
    
    print(f"\n[1] Loading ONNX model from {onnx_model_path}...")
    start_load = time.time()
    model = YOLOE(onnx_model_path)
    load_time = time.time() - start_load
    print(f"✓ Model loaded in {load_time:.2f} seconds")
    
    print("\n[2] Warming up model (initializing ONNX Runtime session)...")
    start_warmup = time.time()
    dummy_frame = np.zeros((320, 320, 3), dtype=np.uint8)
    _ = list(model.track(source=dummy_frame, conf=0.3, iou=0.5, show=False, persist=True, verbose=False))
    warmup_time = time.time() - start_warmup
    print(f"✓ Model warm-up completed in {warmup_time:.2f} seconds")
    
    print("\n[3] Running first real inference (should be fast now)...")
    start_inference = time.time()
    test_frame = np.zeros((640, 480, 3), dtype=np.uint8)
    _ = list(model.track(source=test_frame, conf=0.3, iou=0.5, show=False, persist=True, verbose=False))
    inference_time = time.time() - start_inference
    print(f"✓ First inference completed in {inference_time:.2f} seconds")
    
    print("\n[4] Running second inference (for comparison)...")
    start_inference2 = time.time()
    _ = list(model.track(source=test_frame, conf=0.3, iou=0.5, show=False, persist=True, verbose=False))
    inference_time2 = time.time() - start_inference2
    print(f"✓ Second inference completed in {inference_time2:.2f} seconds")
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    print("\nTiming Summary:")
    print(f"  • Model loading:        {load_time:.2f}s")
    print(f"  • Model warm-up:        {warmup_time:.2f}s  (ONNX Runtime initialization)")
    print(f"  • First inference:      {inference_time:.2f}s  (after warm-up)")
    print(f"  • Second inference:     {inference_time2:.2f}s")
    print(f"\n  • Total startup time:   {load_time + warmup_time:.2f}s")
    
    print("\n💡 Key Insight:")
    print("  Without warm-up, the ONNX Runtime initialization (~2 minutes)")
    print("  would happen on the first real inference, causing a long delay.")
    print("  With warm-up, it happens at startup, making inference instant!")
    
    if warmup_time > 60:
        print(f"\n⏱️  Warm-up took {warmup_time:.0f} seconds - this is the delay")
        print("   that would have occurred on first inference without warm-up!")
    else:
        print(f"\n✅ Warm-up was fast ({warmup_time:.2f}s), model is ready!")
    
    print()


if __name__ == '__main__':
    verify_model_warmup()
