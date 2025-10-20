# Visual Prompting Workflow

This document illustrates the complete workflow for using visual prompting in YoloE.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     VISUAL PROMPTING WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

Step 1: Initial State
┌───────────────────────────────────┐
│  Status: 🔴 Stopped               │
│  Mode: 📝 Text Prompting          │
│  Classes: "person, plant"         │
│                                   │
│  Camera: 📹 Live Feed             │
└───────────────────────────────────┘
            ↓
    [User Action: Stop Inference if running]
            ↓

Step 2: Capture Snapshot
┌───────────────────────────────────┐
│  Click: "Capture Snapshot"        │
│         ↓                          │
│  📸 Snapshot taken from camera    │
│         ↓                          │
│  Canvas displays snapshot          │
└───────────────────────────────────┘
            ↓

Step 3: Draw Bounding Boxes
┌───────────────────────────────────┐
│  Canvas: Ready for drawing        │
│                                   │
│  🖱️ Click & Drag to draw boxes   │
│                                   │
│  ┌─────────────────────────┐     │
│  │  📸 Snapshot            │     │
│  │                         │     │
│  │    ┌──────┐  ┌──────┐  │     │
│  │    │ Box1 │  │ Box2 │  │     │
│  │    └──────┘  └──────┘  │     │
│  └─────────────────────────┘     │
│                                   │
│  ✓ 2 box(es) drawn                │
└───────────────────────────────────┘
            ↓

Step 4: Save Visual Prompt
┌───────────────────────────────────┐
│  Click: "Save Snapshot with Boxes"│
│         ↓                          │
│  Backend Processing:               │
│  • Convert boxes to absolute coords│
│  • Delete cached ONNX model        │
│  • Load PyTorch model              │
│  • Configure visual prompts        │
│  • Export to ONNX                  │
│  • Warm up model (~2 minutes)      │
│         ↓                          │
│  ✓ Visual prompts configured       │
└───────────────────────────────────┘
            ↓

Step 5: Visual Prompting Active
┌───────────────────────────────────┐
│  Status: 🔴 Stopped               │
│  Mode: 🎯 Visual Prompting        │
│  Visual Prompts: 2 boxes          │
│                                   │
│  Ready to start inference!         │
└───────────────────────────────────┘
            ↓
    [User Action: Start Inference]
            ↓

Step 6: Inference with Visual Prompts
┌───────────────────────────────────┐
│  Status: 🟢 Running               │
│  Mode: 🎯 Visual Prompting        │
│                                   │
│  Live Feed:                        │
│  ┌─────────────────────────┐     │
│  │  📹 Camera Feed          │     │
│  │                         │     │
│  │    ┌──────┐  ┌──────┐  │     │
│  │    │Object│  │Object│  │     │
│  │    │Green │  │Green │  │     │
│  │    └──────┘  └──────┘  │     │
│  │                         │     │
│  │  Objects similar to     │     │
│  │  visual prompts tracked │     │
│  └─────────────────────────┘     │
└───────────────────────────────────┘
            ↓
    [User Action: Stop Inference]
            ↓

Step 7: Return to Text Prompting (Optional)
┌───────────────────────────────────┐
│  Click: "Clear Visual Prompt"     │
│         ↓                          │
│  Backend Processing:               │
│  • Clear visual prompt data        │
│  • Delete cached ONNX model        │
│  • Load PyTorch model              │
│  • Configure text prompts          │
│  • Export to ONNX                  │
│  • Warm up model (~2 minutes)      │
│         ↓                          │
│  ✓ Returned to text mode           │
└───────────────────────────────────┘
            ↓

Back to Step 1
┌───────────────────────────────────┐
│  Status: 🔴 Stopped               │
│  Mode: 📝 Text Prompting          │
│  Classes: "person, plant"         │
└───────────────────────────────────┘
```

## State Transitions

### Text Prompting → Visual Prompting
```
Text Mode
    ↓
Stop Inference (if running)
    ↓
Capture Snapshot
    ↓
Draw Bounding Boxes
    ↓
Save Snapshot with Boxes
    ↓
Wait for Model Re-export (~2 min)
    ↓
Visual Prompting Mode (Ready)
```

### Visual Prompting → Text Prompting
```
Visual Mode
    ↓
Stop Inference (if running)
    ↓
Click "Clear Visual Prompt"
    ↓
Wait for Model Re-export (~2 min)
    ↓
Text Prompting Mode (Ready)
```

## User Actions by State

### When Inference is STOPPED
**Available Actions:**
- ✅ Capture Snapshot
- ✅ Draw Bounding Boxes
- ✅ Clear Boxes
- ✅ Save Snapshot with Boxes
- ✅ Clear Visual Prompt
- ✅ Update Classes (text mode)
- ✅ Switch Camera
- ✅ Switch Model
- ✅ Start Inference

### When Inference is RUNNING
**Available Actions:**
- ✅ Stop Inference
- ❌ All configuration actions disabled

## Data Flow

```
┌──────────────┐
│   Camera     │
│   Feed       │
└──────┬───────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│ Live Stream  │      │  Snapshot   │
│ (Video Feed) │      │  Capture    │
└──────────────┘      └─────┬───────┘
                            │
                            ▼
                      ┌─────────────┐
                      │  Canvas     │
                      │  Display    │
                      └─────┬───────┘
                            │
                    [User draws boxes]
                            │
                            ▼
                      ┌─────────────┐
                      │ Bounding    │
                      │ Boxes       │
                      └─────┬───────┘
                            │
                    [Save Visual Prompt]
                            │
                            ▼
                      ┌─────────────┐
                      │ Backend     │
                      │ Processing  │
                      └─────┬───────┘
                            │
                            ├──────────┐
                            │          │
                            ▼          ▼
                   ┌─────────────┐  ┌──────────────┐
                   │ Convert     │  │ Delete       │
                   │ Coordinates │  │ Cached Model │
                   └─────┬───────┘  └──────┬───────┘
                         │                  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Load PyTorch    │
                         │ Model           │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Configure       │
                         │ Visual Prompts  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Export to       │
                         │ ONNX            │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Warm Up Model   │
                         │ (~2 minutes)    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Ready for       │
                         │ Inference       │
                         └─────────────────┘
```

## Timeline

### First-Time Visual Prompt Setup
```
T+0s    User clicks "Capture Snapshot"
T+1s    Snapshot displayed on canvas
T+5s    User draws 2 bounding boxes
T+6s    User clicks "Save Snapshot with Boxes"
T+7s    Backend starts processing
T+10s   Cached ONNX model deleted
T+15s   PyTorch model loaded
T+16s   Visual prompts configured
T+30s   Model exported to ONNX
T+150s  Model warm-up complete (~2 min)
T+151s  Ready to start inference
```

### Subsequent Use (Same Prompts)
```
T+0s    User starts inference
T+0.1s  Inference begins (model already loaded)
```

### Switching Back to Text Mode
```
T+0s    User clicks "Clear Visual Prompt"
T+1s    Backend starts processing
T+5s    Cached ONNX model deleted
T+10s   PyTorch model loaded
T+11s   Text prompts configured
T+25s   Model exported to ONNX
T+145s  Model warm-up complete (~2 min)
T+146s  Ready for text prompting
```

## Error Handling

### Common Errors and Solutions

```
Error: "Stop inference first!"
Solution: Click "Stop Inference" before making changes
Status: Inference is running
Action: Stop inference, then retry

Error: "Please capture a snapshot first."
Solution: Click "Capture Snapshot" before drawing boxes
Status: No snapshot available
Action: Capture snapshot, then draw boxes

Error: "Please draw at least one bounding box."
Solution: Draw boxes on the snapshot canvas
Status: No boxes drawn
Action: Draw boxes, then save

Error: "Could not open camera to capture snapshot."
Solution: Check camera connection and permissions
Status: Camera not accessible
Action: Fix camera, restart app
```

## Best Practices

### For Best Results

1. **Clear Snapshot**
   - Ensure good lighting
   - Objects should be clearly visible
   - Avoid motion blur

2. **Accurate Boxes**
   - Draw boxes tightly around objects
   - Include all important features
   - Avoid including too much background

3. **Multiple Instances**
   - Draw boxes around multiple instances
   - Helps model generalize better
   - Improves tracking accuracy

4. **Similar Angles**
   - Capture from angle you'll use in inference
   - Keep lighting conditions similar
   - Use same camera if possible

5. **Patience**
   - Wait for model re-export to complete
   - Don't interrupt the warm-up process
   - Check console for "ready" message

## Quick Reference

### Button States

| Button                     | Enabled When           | Action                          |
|----------------------------|------------------------|---------------------------------|
| Start Inference            | Stopped                | Begin object tracking           |
| Stop Inference             | Running                | Stop object tracking            |
| Capture Snapshot           | Stopped                | Take snapshot from camera       |
| Clear Boxes                | Stopped, has snapshot  | Remove all drawn boxes          |
| Save Snapshot with Boxes   | Stopped, has snapshot  | Configure visual prompts        |
| Clear Visual Prompt        | Stopped, visual mode   | Return to text prompting        |
| Update Classes             | Stopped, text mode     | Change text prompts             |
| Switch Camera              | Stopped                | Change camera source            |
| Switch Model               | Stopped                | Change model size (S/M/L)       |

### Keyboard Shortcuts
Currently no keyboard shortcuts are implemented. All actions require button clicks.

### Browser Compatibility
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Requires HTML5 Canvas support
- ⚠️ Requires JavaScript enabled

## Conclusion

This workflow demonstrates the complete visual prompting feature, from capturing a snapshot to tracking objects in real-time. The process is intuitive and requires only a few clicks, making it accessible to users without technical knowledge while maintaining powerful object tracking capabilities.
