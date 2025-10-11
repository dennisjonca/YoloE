#!/usr/bin/env python3
"""
Mock demonstration of the custom classes UI feature.
This script creates a simple HTML mock to visualize the new feature.
"""

def generate_mock_html():
    """Generate a mock HTML page showing the new feature."""
    
    # Simulate different states
    status_running = "🟢 Running"
    status_stopped = "🔴 Stopped"
    current_model = "s"
    current_classes = "person, plant"
    
    # Available cameras and models for dropdown
    available_cameras = [0, 1]
    available_models = ["s", "m", "l"]
    
    # Generate camera options
    camera_options_html = "".join(
        [f'<option value="{cam}" {"selected" if cam == 0 else ""}>Camera {cam}</option>'
         for cam in available_cameras]
    )
    
    # Generate model options
    model_options_html = "".join(
        [f'<option value="{model_size}" {"selected" if model_size == current_model else ""}>YoloE-11{model_size.upper()}</option>'
         for model_size in available_models]
    )
    
    # HTML template with the new feature
    html_template = f'''<!DOCTYPE html>
<html>
<head>
    <title>YOLO Live Stream - Custom Classes Feature</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        h3 {{
            color: #666;
            margin: 10px 0;
        }}
        form {{
            margin: 10px 0;
        }}
        label {{
            font-weight: bold;
            margin-right: 10px;
        }}
        input[type="submit"] {{
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }}
        input[type="submit"]:hover {{
            background-color: #45a049;
        }}
        input[type="submit"]:disabled {{
            background-color: #cccccc;
            cursor: not-allowed;
        }}
        input[type="text"] {{
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        select {{
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        .new-feature {{
            background-color: #ffffcc;
            padding: 10px;
            border: 2px solid #ffcc00;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .new-badge {{
            background-color: #ff6600;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .video-placeholder {{
            width: 640px;
            height: 480px;
            background-color: #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #999;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>YOLO Live Stream (Threaded, Controlled)</h1>
    <h3>Status: {status_stopped}</h3>
    <h3>Current Model: YoloE-11{current_model.upper()}</h3>
    <h3>Current Classes: {current_classes} <span class="new-badge">NEW</span></h3>
    
    <form action="/start" method="post" style="display:inline;">
        <input type="submit" value="Start Inference">
    </form>
    <form action="/stop" method="post" style="display:inline;">
        <input type="submit" value="Stop Inference" disabled>
    </form>
    <br><br>
    
    <form action="/set_camera" method="post">
        <label for="camera">Select Camera:</label>
        <select name="camera" id="camera">
            {camera_options_html}
        </select>
        <input type="submit" value="Switch Camera">
    </form>
    <br><br>
    
    <form action="/set_model" method="post">
        <label for="model">Select Model:</label>
        <select name="model" id="model">
            {model_options_html}
        </select>
        <input type="submit" value="Switch Model">
    </form>
    <br><br>
    
    <div class="new-feature">
        <form action="/set_classes" method="post">
            <label for="classes">Custom Classes (comma-separated): <span class="new-badge">NEW FEATURE</span></label>
            <br>
            <input type="text" name="classes" id="classes" value="{current_classes}" size="50">
            <input type="submit" value="Update Classes">
        </form>
        <p style="color: #666; font-size: 14px; margin-top: 10px;">
            💡 <strong>Tip:</strong> Enter any objects you want to detect, separated by commas. 
            For example: "banana, apple, orange" or "car, truck, bus" or "cat, dog, bird"
        </p>
    </div>
    <br>
    
    <div class="video-placeholder">
        <p style="color: #666;">Video feed will appear here</p>
    </div>
</body>
</html>
'''
    
    return html_template


def main():
    """Main function to generate and save the mock HTML."""
    print("=" * 70)
    print("Custom Classes Feature - Mock UI Generator")
    print("=" * 70)
    
    html_content = generate_mock_html()
    
    output_file = "/tmp/custom_classes_ui_mock.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n✓ Mock HTML generated successfully!")
    print(f"  File saved to: {output_file}")
    print("\nThe mock HTML shows:")
    print("  • Current Classes display (with NEW badge)")
    print("  • Custom Classes text input field")
    print("  • Update Classes button")
    print("  • Helpful tip for users")
    print("  • All form elements properly styled")
    print("\nKey Features:")
    print("  ✓ Text input for comma-separated class names")
    print("  ✓ Default value: 'person, plant'")
    print("  ✓ Disabled during inference (like other controls)")
    print("  ✓ Validates input before updating")
    print("  ✓ Reloads model with new classes")
    print("\nExample Usage:")
    print("  1. User types: 'banana, apple, orange'")
    print("  2. Clicks 'Update Classes'")
    print("  3. Model reloads with new object categories")
    print("  4. Start inference to detect custom objects")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
