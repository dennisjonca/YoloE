# Video Viewer Feature

## Overview

The Video Upload tab now includes a built-in video viewer that allows users to watch processed videos directly in the web browser. This is especially useful when running the application on an edge device where local file access may not be available.

## Features

### Video List
- Displays all processed videos in a table format
- Shows video filename, file size (MB), and last modified date
- Automatic sorting by modification date (newest first)
- Refresh button to update the list

### In-Browser Video Player
- HTML5 video player with standard controls (play, pause, seek, volume)
- Supports all processed video formats (MP4, AVI, MOV, MKV, WebM)
- Click "View" button to play any video from the list
- Click "Close Player" to hide the player

### Download Option
- Each video in the list has a download button
- Download processed videos for offline viewing or transfer

## How to Use

### Viewing Processed Videos

1. **Navigate to Video Upload Tab**
   - Open the web interface at `http://127.0.0.1:8080`
   - Click on the "Video Upload" tab

2. **Video List Section**
   - Scroll down to "View Processed Videos" section
   - The list automatically loads when you visit the tab
   - Click "Refresh Video List" to update the list

3. **Play a Video**
   - Click the "View" button next to any video in the list
   - The video player will appear below the list
   - Video automatically starts playing
   - Use standard video controls (play/pause, volume, seek)

4. **Close the Player**
   - Click "Close Player" button to hide the video player
   - Select another video to watch

## UI Components

### Video List Table

```
┌─────────────────────────────────────────────────────────────────┐
│ Video Name                     │ Size (MB) │ Modified          │ Actions │
├─────────────────────────────────────────────────────────────────┤
│ processed_traffic_20231102...  │ 45.2      │ 2023-11-02 14:30 │ [View] [Download] │
│ processed_crowd_20231102...    │ 32.8      │ 2023-11-02 13:15 │ [View] [Download] │
└─────────────────────────────────────────────────────────────────┘
```

### Video Player

When you click "View", a video player appears:

```
┌─────────────────────────────────────────────────────────────────┐
│ Playing: processed_traffic_20231102_143052_a1b2c3d4.mp4        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              [▶ Video Player with Controls]                     │
│                                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        [Close Player]                           │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Details

### New API Endpoints

#### GET /list_videos
Returns a JSON list of all processed videos.

**Response Format:**
```json
{
  "videos": [
    {
      "filename": "processed_video_20231102_143052_a1b2c3d4.mp4",
      "size_mb": 45.23,
      "modified": "2023-11-02 14:30:52"
    }
  ]
}
```

#### GET /view_video?filename=<name>
Streams a video file for in-browser playback.

**Parameters:**
- `filename` (required): Name of the video file to stream

**Returns:** Video file with appropriate mimetype for browser playback

**Security:** Path traversal protection ensures files are only served from the `processed_videos` folder.

### JavaScript Functions

- `refreshVideoList()`: Fetches and displays the list of videos
- `playVideo(filename)`: Loads and plays a video in the player
- `closeVideoPlayer()`: Stops and hides the video player

### Supported Video Formats

The viewer supports all formats that are processed:
- **MP4** (video/mp4) - Best browser compatibility
- **WebM** (video/webm) - Good browser support
- **AVI** (video/x-msvideo) - Limited browser support
- **MOV** (video/quicktime) - Limited browser support
- **MKV** (video/x-matroska) - Limited browser support

**Note:** For best browser compatibility, MP4 format is recommended. Other formats may not play in all browsers.

### Browser Compatibility

The HTML5 video player works in:
- ✓ Chrome/Edge (all formats with appropriate codecs)
- ✓ Firefox (MP4, WebM)
- ✓ Safari (MP4, MOV)
- ⚠ Other browsers may have limited format support

## Workflow Example

### Complete Workflow: Upload, Process, and View

1. **Upload a video** in the "Upload Video File" section
2. **Wait for processing** to complete (progress shown)
3. **Video automatically appears** in the video list
4. **Click "View"** to watch the processed video
5. **See detections** in the video (bounding boxes, labels)
6. **Download if needed** using the Download button

### Edge Device Scenario

When running on an edge device (e.g., Raspberry Pi, NVIDIA Jetson):
1. Access web interface from another device on the network
2. Upload videos via the web interface
3. Process videos on the edge device
4. View results directly in the browser
5. No need for SSH, file transfer, or local video player

## Security

### Path Validation
- All video requests are validated against the `processed_videos` directory
- Path traversal attempts are blocked and logged
- Only files within the processed videos folder can be accessed

### File Type Validation
- Only video files with valid extensions are listed
- Mimetype is determined by file extension
- Unknown formats default to 'video/mp4'

## Performance Considerations

### Streaming
- Videos are streamed, not downloaded entirely before playback
- Supports seeking (jumping to different parts of the video)
- Browser handles buffering automatically

### File Size
- Larger videos may take longer to start playing
- Network speed affects streaming performance
- Consider video compression for better streaming performance

### Refresh
- Video list refreshes automatically on page load
- Manual refresh available via button
- No automatic polling (manual refresh only)

## Troubleshooting

### Video List is Empty
**Cause:** No videos have been processed yet
**Solution:** Upload and process a video first

### Video Won't Play
**Cause:** Browser doesn't support the video format/codec
**Solution:** 
- Try a different browser (Chrome recommended)
- Re-process the video (will be saved as MP4)
- Download and play in a local video player

### Video Loads Slowly
**Cause:** Large file size or slow network
**Solution:**
- Wait for buffering to complete
- Check network connection
- Consider processing smaller/shorter videos

### "Error loading video list"
**Cause:** Server error or network issue
**Solution:**
- Check console logs for errors
- Refresh the page
- Restart the application if needed

## Tips

1. **Format Compatibility**: Use MP4 for best browser compatibility
2. **File Management**: Regularly clean up old processed videos to save disk space
3. **Network Access**: When running on edge device, ensure network access from viewing device
4. **Video Length**: Shorter videos load and play faster
5. **Refresh List**: Click refresh after processing completes to see new videos

## Integration with Existing Features

The video viewer integrates seamlessly with:
- **All Detection Modes**: View videos processed with text prompting, visual prompting, or heatmap
- **Custom Classes**: Videos show detections based on configured classes
- **Heatmap Overlay**: Videos processed with heatmap show the attention visualization
- **Download Feature**: Still available alongside the viewer

## Related Documentation

- [VIDEO_UPLOAD_FEATURE.md](VIDEO_UPLOAD_FEATURE.md) - Main video upload documentation
- [VIDEO_UPLOAD_UI.md](VIDEO_UPLOAD_UI.md) - UI overview
- [README.md](README.md) - General application documentation
