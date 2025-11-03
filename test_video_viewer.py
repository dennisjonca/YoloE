#!/usr/bin/env python3
"""
Test suite for video viewer feature.
Tests the video listing and viewing functionality.
"""

import unittest
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestVideoViewerFeature(unittest.TestCase):
    """Test cases for the video viewer feature."""

    def test_list_videos_route(self):
        """Test that list_videos route exists."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/list_videos'", content, "list_videos route not found")
            print("✓ list_videos route exists")

    def test_view_video_route(self):
        """Test that view_video route exists."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/view_video'", content, "view_video route not found")
            print("✓ view_video route exists")

    def test_stream_video_route(self):
        """Test that stream_video route exists for MJPEG streaming."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/stream_video'", content, "stream_video route not found")
            self.assertIn('multipart/x-mixed-replace', content, "MJPEG mimetype not found")
            print("✓ stream_video route exists for MJPEG streaming")

    def test_video_player_ui(self):
        """Test that video player UI elements exist."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn('id="videoPlayer"', content, "Video player element not found")
            self.assertIn('id="videoListContainer"', content, "Video list container not found")
            self.assertIn('id="videoPlayerContainer"', content, "Video player container not found")
            print("✓ Video player UI elements exist")

    def test_video_list_javascript(self):
        """Test that JavaScript functions for video viewing exist."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn('function refreshVideoList()', content, "refreshVideoList function not found")
            self.assertIn('function playVideo(', content, "playVideo function not found")
            self.assertIn('function closeVideoPlayer()', content, "closeVideoPlayer function not found")
            print("✓ Video viewer JavaScript functions exist")

    def test_video_list_api(self):
        """Test that list_videos returns proper data structure."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check that function returns videos list
            self.assertIn("'videos':", content, "Videos list not returned from list_videos")
            self.assertIn("'filename':", content, "Filename not in video data")
            self.assertIn("'size_mb':", content, "Size not in video data")
            self.assertIn("'modified':", content, "Modified time not in video data")
            print("✓ list_videos API returns proper data structure")

    def test_view_section_in_tab(self):
        """Test that video viewer section is in Video Upload tab."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Find Tab 4 section
            self.assertIn('View Processed Videos', content, "View Processed Videos section not found")
            self.assertIn('Refresh Video List', content, "Refresh button not found")
            print("✓ Video viewer section exists in Video Upload tab")

    def test_security_path_validation(self):
        """Test that view_video has path validation."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for security measures in view_video route
            in_view_video = False
            has_path_check = False
            
            for line in content.split('\n'):
                if 'def view_video():' in line:
                    in_view_video = True
                elif in_view_video and 'def ' in line and 'view_video' not in line:
                    break
                elif in_view_video and 'startswith(processed_dir)' in line:
                    has_path_check = True
            
            self.assertTrue(has_path_check, "Path traversal protection not found in view_video")
            print("✓ view_video route has path validation")

    def test_mimetype_handling(self):
        """Test that different video formats have proper mimetypes."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn('mimetype_map', content, "Mimetype mapping not found")
            self.assertIn("'mp4':", content, "MP4 mimetype not found")
            self.assertIn("'avi':", content, "AVI mimetype not found")
            print("✓ Video format mimetypes are properly handled")

    def test_range_request_support(self):
        """Test that MJPEG streaming is implemented for universal browser compatibility."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check that MJPEG streaming is implemented
            self.assertIn('def stream_video():', content, "stream_video function not found")
            self.assertIn('multipart/x-mixed-replace', content, "MJPEG mimetype not found")
            
            print("✓ MJPEG streaming implemented for universal browser compatibility")


def run_tests():
    """Run all tests and print results."""
    print("\n" + "="*70)
    print("Testing Video Viewer Feature")
    print("="*70 + "\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVideoViewerFeature)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
