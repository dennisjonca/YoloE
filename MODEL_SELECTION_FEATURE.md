# Model Selection Feature Implementation Summary

## Overview
Added a dropdown menu and "Switch Model" button to allow users to select between different YoloE model variants (S, M, and L) while the application is stopped.

## Changes Made

### 1. Model Loading Function (`load_model`)
Created a reusable function that:
- Takes a model size parameter (`s`, `m`, or `l`)
- Checks for cached ONNX models (e.g., `yoloe-11s-seg.onnx`)
- Loads from PyTorch if ONNX doesn't exist (e.g., `yoloe-11s-seg.pt`)
- Exports to ONNX and caches for future use
- Warms up the model to initialize ONNX Runtime
- Returns the loaded model

### 2. Global State Variables
- `available_models = ["s", "m", "l"]` - List of supported model sizes
- `current_model = "s"` - Tracks the currently active model

### 3. HTML UI Updates
Added new form section for model selection:
```html
<form action="/set_model" method="post">
    <label for="model">Select Model:</label>
    <select name="model" id="model">
        <option value="s">YoloE-11S</option>
        <option value="m">YoloE-11M</option>
        <option value="l">YoloE-11L</option>
    </select>
    <input type="submit" value="Switch Model">
</form>
```

Also added a status line showing the current model:
```html
<h3>Current Model: YoloE-11{current_model.upper()}</h3>
```

### 4. Model Switching Route (`/set_model`)
New Flask route that:
- Accepts POST requests with the selected model
- Validates that inference is stopped before switching
- Validates that the model is in the available_models list
- Loads the new model using `load_model()`
- Updates the global `current_model` and `model` variables
- Redirects back to the main page

### 5. Behavior Consistency
The model selection follows the same pattern as camera selection:
- Dropdown is disabled when inference is running
- Switch button is disabled when inference is running
- Shows error message if user tries to switch while running
- Fast switching when stopped (uses cached ONNX models)

## Model File Naming Convention
- PyTorch models: `yoloe-11{size}-seg.pt` (e.g., `yoloe-11s-seg.pt`)
- ONNX models: `yoloe-11{size}-seg.onnx` (e.g., `yoloe-11s-seg.onnx`)

## Testing
Verified functionality with:
1. Unit tests for model path generation
2. Unit tests for model validation
3. Unit tests for HTML option generation
4. Manual UI testing with mock Flask app
5. Tested model switching between S, M, and L variants

## Benefits
- Users can easily switch between model sizes based on their performance needs
- Small model (S): Faster inference, lower accuracy
- Medium model (M): Balanced performance
- Large model (L): Higher accuracy, slower inference
- Model caching ensures fast switching (1-2 seconds for cached models)
- Consistent user experience with existing camera selection feature
