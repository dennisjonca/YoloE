# Video Upload Feature

## Overview

The YoloE application now supports uploading and processing local video files with YOLO detection. This feature allows users to analyze pre-recorded videos using the same detection capabilities available for live camera streams.

## Features

- **Video File Upload**: Upload local video files through a web interface
- **Supported Formats**: MP4, AVI, MOV, MKV, WebM, FLV, WMV
- **Size Limit**: Maximum file size of 500MB
- **Model Integration**: Uses the currently selected YOLO model (s, m, or l)
- **Custom Classes**: Supports both text prompting and visual prompting modes
- **Heatmap Mode**: Optional heatmap overlay for uploaded videos
- **Progress Tracking**: Real-time progress updates during video processing
- **Download Results**: Download processed videos with detections

## How to Use

### Basic Video Processing

1. **Navigate to Video Upload Tab**
   - Open the web interface at `http://127.0.0.1:8080`
   - Click on the "Video Upload" tab

2. **Stop Live Inference** (if running)
   - Video processing cannot run while live inference is active
   - Click "Stop Inference" on the Status & Live Feed tab

3. **Upload Video**
   - Click "Choose File" and select your video file
   - Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV
   - Maximum size: 500MB

4. **Optional: Enable Heatmap Mode**
   - Check the "Enable Heatmap Mode for Video" checkbox
   - This will generate a heatmap overlay showing model attention

5. **Process Video**
   - Click "Upload and Process"
   - Wait for processing to complete (progress shown on page)

6. **Download Results**
   - Once complete, click "Download Processed Video"
   - Video will be saved to your downloads folder

### Advanced Options

#### Using Custom Classes

Before uploading your video:
1. Go to the "Prompting" tab
2. Update the "Custom Classes" field (e.g., "car, truck, bus")
3. Click "Update Classes"
4. Return to "Video Upload" tab and upload your video

The video will be processed with your custom object classes.

#### Using Visual Prompting

Before uploading your video:
1. Go to the "Prompting" tab
2. Capture a snapshot from your camera
3. Draw bounding boxes around objects you want to track
4. Click "Save Snapshot with Boxes"
5. Wait for model reload
6. Return to "Video Upload" tab and upload your video

The video will be processed using visual prompting to find similar objects.

#### Using Heatmap Mode

To visualize model attention on video frames:
1. Check "Enable Heatmap Mode for Video" when uploading
2. Process the video
3. The output will show colored overlays indicating where the model focuses

## Technical Details

### Processing Pipeline

1. **Upload**: Video file is uploaded via HTTP POST and saved to `uploads/` folder
2. **Validation**: File extension and size are validated
3. **Processing**: Video is processed frame-by-frame with YOLO detection
4. **Output**: Processed video is saved to `processed_videos/` folder
5. **Download**: User can download the processed video

### Video Processing Modes

The video processor supports three modes:

1. **Text Prompting Mode** (default)
   - Uses custom class names
   - Provides object tracking across frames
   - Best for general object detection

2. **Visual Prompting Mode**
   - Uses bounding boxes as visual examples
   - Tracks objects similar to visual prompts
   - Best for specific object instances

3. **Heatmap Mode**
   - Shows model attention via GradCAM
   - Visualizes decision-making process
   - More computationally intensive

### Performance Considerations

- **Processing Time**: Depends on video length and hardware
  - CPU: ~2-5 FPS processing speed
  - GPU: ~10-30 FPS processing speed
- **Memory**: Entire video is not loaded into memory
  - Frames are processed one at a time
  - Memory usage scales with frame resolution, not video length
- **Disk Space**: Processed videos are stored in `processed_videos/`
  - Clean up old processed videos manually if needed

### File Storage

- **Uploaded Videos**: `uploads/` (git-ignored)
- **Processed Videos**: `processed_videos/` (git-ignored)
- **Naming Convention**: Files are timestamped to prevent conflicts
  - Example: `my_video_20231031_143052.mp4`

## Security

### File Validation

- **Extension Check**: Only allowed video formats are accepted
- **Filename Sanitization**: Filenames are sanitized using `secure_filename()`
- **Size Limit**: Maximum upload size is 500MB
- **Path Traversal Protection**: Download paths are validated to prevent directory traversal attacks

### Best Practices

1. Only upload trusted video files
2. Be aware of the 500MB size limit
3. Clean up old uploads and processed videos periodically
4. Ensure sufficient disk space for processing

## Troubleshooting

### Video Won't Upload

**Issue**: "No file selected" or upload fails
- **Solution**: Ensure file format is supported (MP4, AVI, MOV, MKV, WebM, FLV, WMV)
- **Solution**: Check file size is under 500MB

### Processing Fails

**Issue**: "Video processing failed" error
- **Solution**: Check console output for detailed error
- **Solution**: Ensure video file is not corrupted
- **Solution**: Try a different video format (MP4 recommended)

### Slow Processing

**Issue**: Video processing is very slow
- **Solution**: Use a GPU if available (much faster)
- **Solution**: Try a smaller model (YoloE-11S vs YoloE-11L)
- **Solution**: Disable heatmap mode for faster processing
- **Solution**: Process shorter videos or reduce video resolution

### Cannot Download Processed Video

**Issue**: Download link doesn't work
- **Solution**: Wait for processing to complete (100% progress)
- **Solution**: Check that processed video exists in `processed_videos/`
- **Solution**: Check browser console for errors

## Examples

### Example 1: Basic Car Detection

```bash
# Setup
1. Configure custom classes: "car, truck, bus, motorcycle"
2. Upload traffic video (e.g., "traffic.mp4")
3. Process video
4. Download result
```

### Example 2: Person Tracking with Heatmap

```bash
# Setup
1. Keep default classes: "person, plant"
2. Upload video with people (e.g., "crowd.mp4")
3. Enable "Heatmap Mode for Video"
4. Process video
5. Download result with heatmap overlay
```

### Example 3: Visual Prompting for Specific Object

```bash
# Setup
1. Capture snapshot of object you want to track
2. Draw bounding box around the object
3. Save visual prompt
4. Upload video containing similar objects
5. Process video
6. Download result
```

## API Endpoints

### POST /upload_video
Upload and process a video file.

**Parameters**:
- `videoFile` (file): The video file to upload
- `enableHeatmap` (checkbox): Enable heatmap mode (optional)

**Returns**: Redirect to main page with processing started

### GET /download_video
Download a processed video file.

**Parameters**:
- `filename` (string): Name of the processed video file

**Returns**: Video file for download

### GET /video_status
Get current video processing status (for AJAX polling).

**Returns** (JSON):
```json
{
  "processing": true/false,
  "progress": 0-100,
  "status": "Status message",
  "has_result": true/false
}
```

## Future Enhancements

Potential improvements for future versions:

1. **Real-time Preview**: Show processing progress with preview frames
2. **Batch Processing**: Upload and process multiple videos at once
3. **Custom Output Settings**: Control output resolution, FPS, codec
4. **Video Trimming**: Select specific sections of video to process
5. **Cloud Storage**: Integration with cloud storage (S3, Google Drive)
6. **Format Conversion**: Automatic conversion to optimal format

## Related Documentation

- [README.md](README.md) - Main project documentation
- [HEATMAP_FEATURE.md](HEATMAP_FEATURE.md) - Heatmap generation details
- [VISUAL_PROMPTING_FEATURE.md](VISUAL_PROMPTING_FEATURE.md) - Visual prompting guide
- [CUSTOM_CLASSES_FEATURE.md](CUSTOM_CLASSES_FEATURE.md) - Custom classes documentation
- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Performance optimization tips
