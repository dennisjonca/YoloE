# Heatmap Generation Feature

## Overview

The heatmap generation feature adds GradCAM-based visualization capabilities to YoloE, allowing users to visualize what regions of an image the model focuses on when making object detection predictions. This is useful for understanding model behavior, debugging detection issues, and explaining AI decisions.

## What are Heatmaps?

Heatmaps are visual representations that highlight which parts of an image the neural network pays attention to when making predictions:

- **Bright/warm colors (red, yellow)**: Areas the model focuses on most
- **Dark/cool colors (blue, black)**: Areas the model largely ignores
- **Overlay with detections**: Shows correlation between attention and detected objects

## Features

### GradCAM Integration
- Uses pytorch-grad-cam library for gradient-based attention visualization
- Supports multiple GradCAM methods:
  - **HiResCAM** (default): High-resolution class activation mapping
  - **GradCAM**: Standard gradient-weighted class activation mapping
  - **GradCAM++**: Improved version with better localization
  - **XGradCAM**: Axiom-based GradCAM
  - **EigenCAM**: Eigen-decomposition based
  - **LayerCAM**: Layer-wise relevance
  - **EigenGradCAM**: Combination of Eigen and Grad approaches

### Snapshot-Based Workflow
1. Capture a snapshot from the camera feed
2. Click "Generate Heatmap" button
3. Heatmap is generated and displayed
4. Saved automatically to `heatmaps/` directory with timestamp

### Configurable Parameters
The heatmap generator supports various configuration options:
- **Device**: CPU or GPU (automatically detected)
- **Method**: Choice of GradCAM algorithm
- **Layers**: Which model layers to analyze
- **Confidence**: Detection threshold
- **Show Boxes**: Overlay bounding boxes on heatmap
- **Renormalize**: Normalize attention within detected regions

### Output
- High-quality JPG images saved to `heatmaps/heatmap_YYYYMMDD_HHMMSS.jpg`
- Visual overlay showing attention regions
- Optional bounding boxes with class labels and confidence scores
- Viewable directly in browser after generation

## Technical Implementation

### Architecture

```
┌─────────────────┐
│   app.py        │
│  (Flask app)    │
└────────┬────────┘
         │
         │ /generate_heatmap
         ▼
┌─────────────────────────┐
│ heatmap_generator.py    │
│                         │
│  YoloEHeatmapGenerator  │
│  ├─ YOLO model loader   │
│  ├─ GradCAM setup       │
│  ├─ Image processing    │
│  └─ Heatmap rendering   │
└─────────────────────────┘
         │
         │ uses
         ▼
┌─────────────────────────┐
│  pytorch-grad-cam       │
│  (External library)     │
└─────────────────────────┘
```

### Key Components

#### `YoloEHeatmapGenerator` Class
Main class that handles heatmap generation:

```python
generator = YoloEHeatmapGenerator(
    weight='yoloe-11s-seg.pt',
    device='cpu',
    method='HiResCAM',
    layer=[10, 12, 14, 16, 18],
    show_box=True,
    renormalize=True
)

success = generator.generate(image_array, 'output.jpg')
```

#### Flask Routes
- `POST /generate_heatmap`: Generates heatmap from current snapshot
- `GET /view_heatmap?path=<path>`: Serves generated heatmap images

#### UI Integration
Added to the "Visual Prompting & Heatmap Generation" section:
- "Generate Heatmap" button (enabled when snapshot exists)
- Automatic display of generated heatmap
- Link to view full-size image

### Image Processing Pipeline

1. **Input**: BGR image from snapshot (NumPy array)
2. **Letterboxing**: Resize and pad to model input size (640x640)
3. **Color Conversion**: BGR → RGB
4. **Normalization**: Scale to [0, 1] float
5. **Tensor Conversion**: NumPy → PyTorch tensor
6. **GradCAM Generation**: Compute attention map
7. **Overlay**: Blend attention map with original image
8. **Detection**: Run object detection
9. **Box Drawing**: Optionally draw detections
10. **Save**: Export as JPG image

## Usage

### Basic Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open browser** to `http://127.0.0.1:8080`

3. **Stop inference** if running

4. **Capture snapshot**:
   - Click "Capture Snapshot" button
   - Snapshot appears in canvas

5. **Generate heatmap**:
   - Click "Generate Heatmap" button
   - Wait for processing (5-15 seconds)
   - Heatmap displays in new page

6. **View results**:
   - Heatmap shows attention regions
   - Check `heatmaps/` directory for saved files

### Advanced Configuration

To customize heatmap generation, modify `get_default_params()` in `heatmap_generator.py`:

```python
def get_default_params():
    return {
        'device': 'cpu',           # or 'cuda:0' for GPU
        'method': 'HiResCAM',      # GradCAM method
        'layer': [10, 12, 14, 16, 18],  # Target layers
        'backward_type': 'class',  # 'class', 'box', or 'all'
        'conf_threshold': 0.2,     # Detection confidence
        'ratio': 0.02,             # Processing ratio
        'show_box': False,         # Show detections
        'renormalize': True        # Normalize in boxes
    }
```

## Use Cases

### 1. Model Debugging
**Problem**: Model not detecting expected objects  
**Solution**: Generate heatmap to see if model is looking at correct regions

Example: If detecting cars but heatmap shows attention on sky, model may need retraining.

### 2. Understanding Detections
**Problem**: Want to understand why model made certain prediction  
**Solution**: Heatmap reveals which features influenced the decision

Example: Cat detection shows attention on ears and whiskers, confirming correct features.

### 3. Model Comparison
**Problem**: Comparing different model sizes (s, m, l)  
**Solution**: Generate heatmaps for same image across models

Example: Compare attention patterns to see which model focuses better.

### 4. Training Data Insights
**Problem**: Need to improve training dataset  
**Solution**: Analyze heatmaps to identify missing features

Example: Heatmaps show model ignores certain object parts, add more training examples.

## Dependencies

Required Python packages (listed in `requirements.txt`):
```
grad-cam         # GradCAM implementation
torch            # PyTorch (already required)
torchvision      # Vision utilities (usually with torch)
opencv-python    # Image processing (already required)
numpy            # Array operations (already required)
Pillow           # Image I/O
matplotlib       # Optional, for advanced visualization
tqdm             # Progress bars
```

Install with:
```bash
pip install -r requirements.txt
```

## Testing

### Unit Tests
Test module imports and basic functionality:
```bash
python test_heatmap_unit.py
```

Tests:
- ✓ Module imports (YoloEHeatmapGenerator, pytorch_grad_cam)
- ✓ Default parameters configuration
- ✓ App integration (routes, imports)

### Integration Test
Test actual heatmap generation (requires model file):
```bash
python test_heatmap_generation.py
```

Tests:
- Model loading
- Generator initialization
- Heatmap creation from test image
- File output verification

## Performance Considerations

### Generation Time
- **CPU**: 5-15 seconds per heatmap
- **GPU**: 2-5 seconds per heatmap
- Depends on model size and image resolution

### Memory Usage
- Temporary spike during generation
- ~500MB-1GB depending on model
- Gradients require additional memory

### Optimization Tips
1. Use GPU if available for faster generation
2. Close browser tab after viewing to free memory
3. Delete old heatmaps periodically from `heatmaps/` directory
4. Use smaller model (s) for faster generation

## Troubleshooting

### Common Issues

**Issue**: "Module pytorch_grad_cam not found"
```bash
Solution: pip install grad-cam
```

**Issue**: "Model file not found"
```
Solution: Ensure .pt model file exists in project directory
Example: yoloe-11s-seg.pt
```

**Issue**: "Heatmap generation failed"
```
Possible causes:
- No snapshot captured
- Model incompatibility
- Insufficient memory
Check console output for detailed error messages
```

**Issue**: "Heatmap shows random noise"
```
Possible causes:
- GradCAM method incompatible with model architecture
- Wrong layer indices specified
Try changing method in get_default_params()
```

**Issue**: "Out of memory error"
```
Solutions:
- Close other applications
- Use CPU instead of GPU (less memory)
- Use smaller model size (s instead of m or l)
- Restart application
```

## Limitations

1. **Real-time Generation**: Not designed for real-time (use on snapshots only)
2. **Model Compatibility**: Works best with YOLOv8/YOLOv11 architectures
3. **Layer Access**: Some model architectures may not support layer-specific analysis
4. **Accuracy**: Heatmaps are approximations, not exact attention maps
5. **Inference**: Requires inference pass, so needs loaded model

## Future Enhancements

Potential improvements for future versions:

1. **Batch Processing**: Generate heatmaps for multiple images
2. **Video Heatmaps**: Create heatmap videos from camera feed
3. **Comparison View**: Side-by-side original vs heatmap
4. **Custom Layers**: UI to select which layers to visualize
5. **Export Options**: PDF, PNG, different color schemes
6. **Annotations**: Add notes/markings to heatmaps
7. **History**: View previously generated heatmaps
8. **Statistics**: Attention distribution graphs

## References

- [GradCAM Paper](https://arxiv.org/abs/1610.02391)
- [pytorch-grad-cam Library](https://github.com/jacobgil/pytorch-grad-cam)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)

## Contributing

To contribute improvements to the heatmap feature:

1. Test changes with `test_heatmap_unit.py`
2. Ensure backward compatibility
3. Update documentation
4. Add new tests for new features
5. Follow existing code style

## License

Same as parent YoloE project.
