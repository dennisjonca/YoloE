# Video Upload Feature - UI Overview

## Main Interface Changes

### Tab Navigation
The application now has 5 tabs instead of 4:
```
┌──────────────────────────────────────────────────────────────────┐
│ [Status & Live Feed] [Configuration] [Prompting] [Video Upload] [Console] │
└──────────────────────────────────────────────────────────────────┘
```

### Video Upload Tab (NEW)

#### Upload Section
```
┌─────────────────────────────────────────────────────────────┐
│ Upload Video File                                            │
├─────────────────────────────────────────────────────────────┤
│ Upload a local video file to analyze with YOLO detection.   │
│ Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV       │
│                                                              │
│ Select Video File (max 500MB):                              │
│ [Choose File] No file chosen                                │
│                                                              │
│ ☐ Enable Heatmap Mode for Video                            │
│                                                              │
│ [Upload and Process]                                         │
│                                                              │
│ Processing in progress... Please wait. (if processing)       │
│ Status: Processing 450/1000 frames (45%)                    │
│ Progress: 45%                                               │
└─────────────────────────────────────────────────────────────┘
```

#### Download Section (appears when video is ready)
```
┌─────────────────────────────────────────────────────────────┐
│ Processed Video                                              │
├─────────────────────────────────────────────────────────────┤
│ Your processed video is ready for download:                 │
│                                                              │
│ [Download Processed Video]                                   │
│                                                              │
│ Note: Processed videos are saved in the                     │
│ 'processed_videos' folder.                                  │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Example

### Step 1: Navigate to Video Upload Tab
User clicks on "Video Upload" tab

### Step 2: Select Video
User clicks "Choose File" and selects a video:
- Example: `traffic_scene.mp4` (125 MB)

### Step 3: Optional - Enable Heatmap
User checks "Enable Heatmap Mode for Video" checkbox

### Step 4: Upload and Process
User clicks "Upload and Process" button

### Step 5: Monitor Progress
Status updates appear:
```
Processing in progress... Please wait.
Status: Processing 300/1000 frames (30%)
Progress: 30%
```

### Step 6: Download Result
When complete:
```
Status: Complete! Processed 1000 frames
Progress: 100%

[Download Processed Video] button appears
```

## Integration with Other Features

### Using Custom Classes
Before uploading video:
1. Go to "Prompting" tab
2. Update classes to "car, truck, bus"
3. Return to "Video Upload" tab
4. Upload video → detections use custom classes

### Using Visual Prompting
Before uploading video:
1. Go to "Prompting" tab
2. Capture snapshot
3. Draw boxes around target objects
4. Save visual prompt
5. Return to "Video Upload" tab
6. Upload video → detections use visual prompts

### Using Heatmap Mode
During upload:
1. Check "Enable Heatmap Mode for Video"
2. Upload and process
3. Download video with heatmap overlay

## Technical Flow

```
User Action                  System Response
──────────────────────────────────────────────────────
Select file                  → Validate extension
                            
Click Upload                → Secure filename
                            → Generate UUID
                            → Save to uploads/
                            → Start background thread
                            
Processing                  → Frame-by-frame analysis
                            → Apply current model
                            → Apply current settings
                            → Update progress (0-100%)
                            
Complete                    → Save to processed_videos/
                            → Show download link
                            
Click Download              → Validate path
                            → Send file to browser
```

## File Naming Convention

### Uploaded Files
```
Format: {original_name}_{timestamp}_{uuid}.{ext}
Example: my_video_20231031_143052_a1b2c3d4.mp4
```

### Processed Files
```
Format: processed_{original_name}_{timestamp}_{uuid}.mp4
Example: processed_my_video_20231031_143052_a1b2c3d4.mp4
```

## User Experience Notes

1. **Cannot process while live inference is running**
   - Must stop live camera inference first
   - Prevents resource conflicts

2. **Progress tracking**
   - Real-time percentage updates
   - Frame count displayed
   - Status messages

3. **Error handling**
   - Generic user-facing messages
   - Detailed errors in console log
   - No sensitive information exposed

4. **File size limit**
   - 500MB maximum
   - Clear error if exceeded

5. **Supported formats**
   - Multiple common formats supported
   - Clear list shown in UI
   - Validation on upload

## Expected Output

### Normal Mode
Processed video shows:
- Green bounding boxes around detected objects
- Labels with class names
- Confidence scores (if configured)

### Heatmap Mode
Processed video shows:
- Colored heatmap overlay (red/yellow = high attention)
- Bounding boxes (optional)
- Labels and scores
- Visual representation of model focus

### Visual Prompting Mode
Processed video shows:
- Detection of objects similar to visual prompts
- Bounding boxes around matched objects
- Labels based on prompt classes
