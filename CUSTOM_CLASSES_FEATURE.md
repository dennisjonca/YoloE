# Custom Classes Feature Implementation

## Overview
Added a text field to the web interface that allows users to customize the class prompts (object categories) that the YOLO model should detect. Users can now look for any objects they want instead of being limited to hardcoded classes.

## What Changed

### Previous Behavior
- Classes were hardcoded to `["person", "plant"]` in the `load_model()` function
- Users could not change what objects the model detects without modifying code

### New Behavior
- Users can enter any comma-separated list of object classes through the web interface
- Classes can be changed at any time when inference is stopped
- The model is automatically reloaded with the new classes

## Features

### 1. **Custom Classes Input Field**
- Text input field for entering comma-separated class names
- Default value: "person, plant"
- Size: 50 characters wide for comfortable input
- Disabled during inference (prevents changes while running)

### 2. **Current Classes Display**
- Shows the currently active classes at the top of the page
- Helps users know what the model is currently configured to detect

### 3. **Update Classes Button**
- Reloads the model with the new classes
- Only enabled when inference is stopped
- Validates input before applying changes

### 4. **Input Validation**
- Checks for empty input
- Ensures at least one valid class name is provided
- Trims whitespace from class names
- Shows error messages for invalid input

## Usage Examples

### Example 1: Detect Fruits
1. Stop inference if running
2. Enter: `banana, apple, orange`
3. Click "Update Classes"
4. Start inference to detect fruits

### Example 2: Detect Vehicles
1. Stop inference if running
2. Enter: `car, truck, bus, motorcycle`
3. Click "Update Classes"
4. Start inference to detect vehicles

### Example 3: Detect Animals
1. Stop inference if running
2. Enter: `cat, dog, bird, horse`
3. Click "Update Classes"
4. Start inference to detect animals

## Technical Implementation

### Code Changes

#### 1. Global State Variable
```python
current_classes = "person, plant"  # Default class prompts
```

#### 2. Updated `load_model()` Function
```python
def load_model(model_size, class_names=None):
    """Load YOLO model with the specified size (s, m, or l) and class names."""
    if class_names is None:
        class_names = ["person", "plant"]
    
    # ... model loading logic ...
    
    # Set classes on the loaded model (whether cached or freshly exported)
    loaded_model.set_classes(class_names, loaded_model.get_text_pe(class_names))
    print(f"[INFO] Model classes set to: {class_names}")
```

#### 3. New Flask Route: `/set_classes`
```python
@app.route('/set_classes', methods=['POST'])
def set_classes():
    """Change the object classes to detect (only allowed when stopped)."""
    global current_classes, model

    # Get classes from form
    new_classes = request.form.get("classes")
    
    # Validate input
    if running:
        return "Stop inference first!"
    
    if not new_classes or new_classes.strip() == "":
        return "Classes cannot be empty."
    
    # Parse and apply new classes
    class_list = [name.strip() for name in new_classes.split(",") if name.strip()]
    
    if not class_list:
        return "Please provide at least one class name."
    
    # Reload model with new classes
    current_classes = new_classes.strip()
    model = load_model(current_model, class_list)
    
    return redirect('/')
```

#### 4. Updated HTML Interface
```html
<h3>Current Classes: {current_classes}</h3>

<form action="/set_classes" method="post">
    <label for="classes">Custom Classes (comma-separated):</label>
    <input type="text" name="classes" id="classes" value="{current_classes}" size="50" {"disabled" if running else ""}>
    <input type="submit" value="Update Classes" {"disabled" if running else ""}>
</form>
```

## Benefits

1. **Flexibility**: Users can detect any objects without code changes
2. **User-Friendly**: Simple text input with helpful tooltip
3. **Safe**: Input validation prevents errors
4. **Consistent**: Follows same pattern as camera/model selection
5. **Real-time**: Changes apply immediately when stopped

## Testing

Created comprehensive test suite (`test_custom_classes.py`) with 10 tests:
- ✓ Global variable for current classes
- ✓ load_model function signature
- ✓ Model set_classes call
- ✓ HTML form for custom classes
- ✓ /set_classes Flask route
- ✓ Current classes display
- ✓ Input validation
- ✓ Running state check
- ✓ Model reload with new classes
- ✓ UI disabled state

All tests passing ✅

## Screenshots

![Custom Classes Feature](https://github.com/user-attachments/assets/17dfe4c4-532e-43a9-8621-435be840ec60)

The screenshot shows:
- Current Classes display with "NEW" badge
- Custom Classes input field with default value
- Update Classes button
- Helpful tip for users explaining the format
- All controls properly styled and positioned

## Limitations

1. **Model Reload Required**: Changing classes requires reloading the model (takes a few seconds with cached models)
2. **Must Stop Inference**: Cannot change classes while inference is running
3. **No Class Validation**: The system doesn't validate if the entered class names are valid object types

## Future Enhancements

Potential improvements for future versions:
- Auto-suggest common object categories
- Save/load class presets
- Hot-reload classes without stopping inference
- Visual class selection with checkboxes
- Class name validation against YOLO-supported objects
