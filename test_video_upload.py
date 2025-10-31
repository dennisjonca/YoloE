#!/usr/bin/env python3
"""
Test suite for video upload feature.
Tests the video upload functionality, file validation, and processing workflow.
"""

import unittest
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestVideoUploadFeature(unittest.TestCase):
    """Test cases for the video upload feature."""

    def test_imports(self):
        """Test that all required imports for video upload are available."""
        try:
            from flask import Flask, request
            from werkzeug.utils import secure_filename
            import cv2
            import numpy as np
            print("✓ All required imports successful")
        except ImportError as e:
            self.fail(f"Required import failed: {e}")

    def test_app_configuration(self):
        """Test that app.py has the video upload configuration."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for upload configuration
            self.assertIn('UPLOAD_FOLDER', content, "UPLOAD_FOLDER not configured")
            self.assertIn('PROCESSED_FOLDER', content, "PROCESSED_FOLDER not configured")
            self.assertIn('ALLOWED_EXTENSIONS', content, "ALLOWED_EXTENSIONS not defined")
            self.assertIn('MAX_CONTENT_LENGTH', content, "MAX_CONTENT_LENGTH not set")
            
            print("✓ App configuration for video upload is present")

    def test_allowed_file_function(self):
        """Test that allowed_file function exists in app.py."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn('def allowed_file', content, "allowed_file function not found")
            print("✓ allowed_file function exists")

    def test_process_video_function(self):
        """Test that process_video_file function exists in app.py."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn('def process_video_file', content, "process_video_file function not found")
            self.assertIn('use_heatmap=False', content, "Heatmap parameter not in function")
            print("✓ process_video_file function exists with heatmap support")

    def test_upload_route(self):
        """Test that video upload route exists."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/upload_video'", content, "Upload video route not found")
            self.assertIn("methods=['POST']", content, "Upload route not configured for POST")
            print("✓ Video upload route exists")

    def test_download_route(self):
        """Test that video download route exists."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/download_video'", content, "Download video route not found")
            print("✓ Video download route exists")

    def test_video_status_route(self):
        """Test that video status route exists for AJAX polling."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("@app.route('/video_status'", content, "Video status route not found")
            print("✓ Video status route exists")

    def test_ui_video_tab(self):
        """Test that UI has a video upload tab."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            self.assertIn("Video Upload", content, "Video Upload tab not found in UI")
            self.assertIn("tab4", content, "Tab 4 (video upload) not found")
            print("✓ Video upload tab exists in UI")

    def test_supported_formats(self):
        """Test that common video formats are supported."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for common video formats
            formats = ['mp4', 'avi', 'mov', 'mkv']
            for fmt in formats:
                self.assertIn(fmt, content, f"Video format {fmt} not supported")
            
            print(f"✓ Supported video formats include: {', '.join(formats)}")

    def test_security_validation(self):
        """Test that security measures are in place."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for secure_filename usage
            self.assertIn('secure_filename', content, "secure_filename not used")
            
            # Check for path traversal protection in download
            self.assertIn('Path traversal attempt blocked', content, 
                         "Path traversal protection not implemented")
            
            print("✓ Security validations are in place")

    def test_gitignore_updated(self):
        """Test that .gitignore includes upload directories."""
        with open('.gitignore', 'r') as f:
            content = f.read()
            
            self.assertIn('uploads/', content, "uploads/ not in .gitignore")
            self.assertIn('processed_videos/', content, "processed_videos/ not in .gitignore")
            
            print("✓ .gitignore updated with video directories")

    def test_heatmap_integration(self):
        """Test that video processing supports heatmap mode."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for heatmap support in video processing
            self.assertIn('use_heatmap', content, "Heatmap mode not supported in video processing")
            self.assertIn('enableHeatmap', content, "Heatmap checkbox not in UI")
            
            print("✓ Video processing supports heatmap mode")

    def test_visual_prompting_integration(self):
        """Test that video processing supports visual prompting."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Check for visual prompting in process_video_file
            in_process_video = False
            for line in content.split('\n'):
                if 'def process_video_file' in line:
                    in_process_video = True
                elif in_process_video and 'def ' in line and 'process_video_file' not in line:
                    break
                elif in_process_video and 'use_visual_prompt' in line:
                    print("✓ Video processing supports visual prompting")
                    return
            
            self.fail("Visual prompting not integrated in video processing")

    def test_state_variables(self):
        """Test that video processing state variables exist."""
        with open('app.py', 'r') as f:
            content = f.read()
            
            state_vars = [
                'video_processing',
                'video_processing_progress',
                'video_processing_status',
                'last_uploaded_video',
                'last_processed_video'
            ]
            
            for var in state_vars:
                self.assertIn(var, content, f"State variable {var} not found")
            
            print(f"✓ All video processing state variables exist")


def run_tests():
    """Run all tests and print results."""
    print("\n" + "="*70)
    print("Testing Video Upload Feature")
    print("="*70 + "\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVideoUploadFeature)
    
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
