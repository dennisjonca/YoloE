import asyncio
import cv2
import base64
import json
from ultralytics import YOLO
import websockets
import numpy as np

class YOLOWebcamServer:
    def __init__(self, model_path="yolov8n.pt", camera_index=0):
        self.model = YOLO(model_path)
        self.camera_index = camera_index
        self.cap = None
        self.clients = set()
        
    def initialize_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception(f"Cannot open camera at index {self.camera_index}")
        
    async def handle_client(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_frames(self):
        while True:
            if not self.clients:
                await asyncio.sleep(0.1)
                continue
                
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                await asyncio.sleep(0.1)
                continue
            
            results = self.model(frame, verbose=False)
            
            annotated_frame = results[0].plot()
            
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            detections = []
            for box in results[0].boxes:
                detection = {
                    'class': results[0].names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist()
                }
                detections.append(detection)
            
            message = json.dumps({
                'frame': frame_base64,
                'detections': detections
            })
            
            disconnected_clients = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
            
            for client in disconnected_clients:
                self.clients.discard(client)
            
            await asyncio.sleep(0.03)
    
    async def start_server(self, host="0.0.0.0", port=8765):
        self.initialize_camera()
        print(f"Starting WebSocket server on {host}:{port}")
        
        async with websockets.serve(self.handle_client, host, port):
            await self.broadcast_frames()

if __name__ == "__main__":
    server = YOLOWebcamServer(camera_index=0)
    asyncio.run(server.start_server())
