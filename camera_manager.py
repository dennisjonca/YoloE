"""
Camera Manager Module
Handles background camera detection, pre-opening, and asynchronous camera management.
"""
import cv2
import threading
import time
import platform
from typing import List, Optional, Dict
from queue import Queue


class CameraManager:
    """
    Background camera manager that pre-opens cameras and queues new ones asynchronously.
    """
    
    def __init__(self, max_devices: int = 10):
        """
        Initialize the camera manager.
        
        Args:
            max_devices: Maximum number of camera devices to scan
        """
        self.max_devices = max_devices
        self.available_cameras: List[int] = []
        self.camera_cache: Dict[int, Optional[cv2.VideoCapture]] = {}
        self.lock = threading.Lock()
        self.running = False
        self.manager_thread = None
        self.request_queue = Queue()
        
        # Detect platform and set appropriate backend
        self.is_windows = platform.system() == 'Windows'
        self.backend = cv2.CAP_DSHOW if self.is_windows else cv2.CAP_ANY
        
    def start(self):
        """Start the background camera manager thread."""
        if not self.running:
            self.running = True
            self.manager_thread = threading.Thread(target=self._manager_loop, daemon=True)
            self.manager_thread.start()
            backend_name = "DirectShow" if self.is_windows else "default"
            print(f"[CameraManager] Background manager started (using {backend_name} backend)")
    
    def stop(self):
        """Stop the background camera manager thread."""
        if self.running:
            self.running = False
            if self.manager_thread and self.manager_thread.is_alive():
                self.manager_thread.join(timeout=2.0)
            self._cleanup_all_cameras()
            print("[CameraManager] Background manager stopped")
    
    def _manager_loop(self):
        """Main loop for the background camera manager."""
        # Initial camera detection
        self._detect_cameras()
        
        while self.running:
            # Process any queued camera requests
            while not self.request_queue.empty():
                try:
                    request = self.request_queue.get_nowait()
                    action = request.get('action')
                    
                    if action == 'detect':
                        self._detect_cameras()
                    elif action == 'pre_open':
                        camera_id = request.get('camera_id')
                        if camera_id is not None:
                            self._pre_open_camera(camera_id)
                    elif action == 'release':
                        camera_id = request.get('camera_id')
                        if camera_id is not None:
                            self._release_camera(camera_id)
                except Exception as e:
                    print(f"[CameraManager] Error processing request: {e}")
            
            time.sleep(0.1)
    
    def _detect_cameras(self):
        """Detect available camera devices in background."""
        print("[CameraManager] Scanning for cameras...")
        found = []
        
        for i in range(self.max_devices):
            cap = cv2.VideoCapture(i, self.backend)
            if cap.isOpened():
                found.append(i)
                cap.release()
        
        with self.lock:
            self.available_cameras = found
        
        print(f"[CameraManager] Found cameras: {found}")
    
    def _pre_open_camera(self, camera_id: int):
        """
        Pre-open a camera and cache it for faster access.
        
        Args:
            camera_id: Camera device ID to pre-open
        """
        with self.lock:
            if camera_id in self.camera_cache and self.camera_cache[camera_id] is not None:
                print(f"[CameraManager] Camera {camera_id} already pre-opened")
                return
        
        print(f"[CameraManager] Pre-opening camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id, self.backend)
        
        if cap.isOpened():
            with self.lock:
                self.camera_cache[camera_id] = cap
            print(f"[CameraManager] Camera {camera_id} pre-opened successfully")
        else:
            print(f"[CameraManager] Failed to pre-open camera {camera_id}")
            cap.release()
    
    def _release_camera(self, camera_id: int):
        """
        Release a pre-opened camera from cache.
        
        Args:
            camera_id: Camera device ID to release
        """
        with self.lock:
            if camera_id in self.camera_cache and self.camera_cache[camera_id] is not None:
                self.camera_cache[camera_id].release()
                self.camera_cache[camera_id] = None
                print(f"[CameraManager] Released camera {camera_id}")
    
    def _cleanup_all_cameras(self):
        """Release all cached cameras."""
        with self.lock:
            for camera_id, cap in self.camera_cache.items():
                if cap is not None:
                    cap.release()
                    print(f"[CameraManager] Released camera {camera_id}")
            self.camera_cache.clear()
    
    def get_available_cameras(self) -> List[int]:
        """
        Get list of available camera IDs.
        
        Returns:
            List of available camera device IDs
        """
        with self.lock:
            return self.available_cameras.copy()
    
    def request_detect_cameras(self):
        """Request async camera detection."""
        self.request_queue.put({'action': 'detect'})
    
    def request_pre_open(self, camera_id: int):
        """
        Request async pre-opening of a camera.
        
        Args:
            camera_id: Camera device ID to pre-open
        """
        self.request_queue.put({'action': 'pre_open', 'camera_id': camera_id})
    
    def request_release(self, camera_id: int):
        """
        Request async release of a camera.
        
        Args:
            camera_id: Camera device ID to release
        """
        self.request_queue.put({'action': 'release', 'camera_id': camera_id})
    
    def get_camera(self, camera_id: int) -> Optional[cv2.VideoCapture]:
        """
        Get a pre-opened camera from cache, or open it if not cached.
        
        Args:
            camera_id: Camera device ID
            
        Returns:
            VideoCapture object or None if failed
        """
        with self.lock:
            # Check if camera is already cached
            if camera_id in self.camera_cache and self.camera_cache[camera_id] is not None:
                cap = self.camera_cache[camera_id]
                # Remove from cache so it won't be released by manager
                self.camera_cache[camera_id] = None
                print(f"[CameraManager] Retrieved pre-opened camera {camera_id}")
                return cap
        
        # Camera not in cache, open it now
        print(f"[CameraManager] Camera {camera_id} not pre-opened, opening now...")
        cap = cv2.VideoCapture(camera_id, self.backend)
        if cap.isOpened():
            return cap
        else:
            cap.release()
            return None
