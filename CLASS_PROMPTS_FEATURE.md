# Class Prompts Feature Implementation

## Overview
Added a text field to the web interface that allows users to customize the class prompts (object categories) that the YOLO model should detect. Users can now look for any objects they want (e.g., "banana", "car", "dog") instead of being limited to the hardcoded "person" and "plant" classes.

## Changes Made

### 1. Global State Variable
Added `current_classes` variable to store the active class prompts:
```python
# Class prompts for YOLO model
current_classes = ["person", "plant"]  # Default class prompts
```

### 2. Updated `load_model()` Function
Modified the model loading function to use `current_classes` instead of hardcoded values:
```python
loaded_model.set_classes(current_classes, loaded_model.get_text_pe(current_classes))
```

### 3. HTML UI Updates
Added new form section for class prompts editing:
```html
<h3>Current Classes: {classes_str}</h3>
...
<form action="/set_classes" method="post">
    <label for="classes">Class Prompts (comma-separated):</label><br>
    <input type="text" name="classes" id="classes" value="{classes_str}" size="50" {"disabled" if running else ""}>
    <input type="submit" value="Update Classes" {"disabled" if running else ""}>
</form>
```

Also added a status line showing the current classes:
```html
<h3>Current Classes: {classes_str}</h3>
```

### 4. Class Update Route (`/set_classes`)
New Flask route that:
- Accepts POST requests with the comma-separated class list
- Validates that inference is stopped before updating
- Validates that at least one class is provided
- Parses and trims the class names
- Removes the cached ONNX model to force re-export with new classes
- Reloads the model using `load_model()`
- Updates the global `current_classes` variable
- Redirects back to the main page

### 5. Safety Features
The class prompts update follows the same safety pattern as model and camera selection:
- Input field is disabled when inference is running
- Update button is disabled when inference is running
- Shows error message if user tries to update while running
- Validates input to ensure at least one class is provided
- Cached ONNX models are removed to ensure new classes are applied

## Input Format
Classes should be entered as a comma-separated list. Whitespace is automatically trimmed.

**Examples:**
- `person, plant`
- `banana, apple, orange`
- `car, truck, bus, motorcycle`
- `dog, cat, bird`

## Workflow

### Updating Classes
1. Stop inference if it's running
2. Enter new class names in the text field (comma-separated)
3. Click "Update Classes" button
4. The cached ONNX model is removed
5. Model is reloaded and re-exported with new classes
6. Start inference to detect the new objects

### What Happens Behind the Scenes
When you update the classes:
1. The input string is parsed and split by commas
2. Each class name is trimmed of whitespace
3. The cached ONNX model file is deleted (e.g., `yoloe-11s-seg.onnx`)
4. The model is reloaded from the PyTorch file (e.g., `yoloe-11s-seg.pt`)
5. New classes are applied using `set_classes()`
6. The model is re-exported to ONNX format
7. The model is warmed up and ready for inference

## Performance Impact
- **First time with new classes**: Takes ~20-25 seconds to re-export the ONNX model
- **Subsequent runs with same classes**: Uses cached ONNX model (~1-2 seconds)
- **Changing classes**: Requires re-export since ONNX models are class-specific

## Error Handling
- **Empty input**: Shows error "Classes cannot be empty!"
- **Running inference**: Shows error "Stop inference first!"
- **Invalid format**: Automatically filters out empty entries from comma-separated list

## Example Use Cases
1. **Fruit detection**: `banana, apple, orange, grape, strawberry`
2. **Vehicle detection**: `car, truck, bus, motorcycle, bicycle`
3. **Animal detection**: `dog, cat, bird, fish, rabbit`
4. **Custom objects**: `bottle, cup, laptop, phone, keyboard`

## Testing
Created comprehensive test suite in `test_class_prompts.py` that verifies:
- Global variable is defined
- Model loading uses the variable
- UI elements are present
- Route handler exists and works correctly
- Safety checks are in place
- Input validation works
- ONNX cache invalidation works
- Model reloading works

## Benefits
- ✅ Users can detect any objects they want
- ✅ No code changes needed to switch detection targets
- ✅ Changes only allowed when inference is stopped (safe)
- ✅ Automatic model re-export ensures new classes are applied
- ✅ Consistent with existing UI patterns (camera/model selection)
- ✅ Clear visual feedback of current classes
- ✅ Simple, intuitive interface

## Limitations
- Changing classes requires re-exporting the ONNX model (~20 seconds)
- YOLO model can only detect objects it was trained on (you can't add completely arbitrary classes that the base model doesn't know about)
- The feature allows you to *select which classes to look for* from the model's knowledge, not add new classes it doesn't know
