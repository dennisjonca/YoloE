class YOLOWebcamClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 3000;
        this.reconnectTimer = null;
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();
        this.fpsInterval = 1000;
        
        this.videoStream = document.getElementById('videoStream');
        this.statusElement = document.getElementById('status');
        this.statusText = document.getElementById('statusText');
        this.detectionList = document.getElementById('detectionList');
        this.fpsCounter = document.getElementById('fpsCounter');
        this.detectionCounter = document.getElementById('detectionCounter');
        this.reconnectBtn = document.getElementById('reconnectBtn');
        
        this.reconnectBtn.addEventListener('click', () => this.connect());
        
        this.connect();
    }
    
    connect() {
        const wsUrl = `ws://${window.location.hostname}:8765`;
        
        this.updateStatus('connecting', 'Connecting to server...');
        this.reconnectBtn.style.display = 'none';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateStatus('connected', 'Connected to server');
                this.frameCount = 0;
                this.lastFpsUpdate = Date.now();
                if (this.reconnectTimer) {
                    clearTimeout(this.reconnectTimer);
                    this.reconnectTimer = null;
                }
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateStatus('disconnected', 'Disconnected from server');
                this.reconnectBtn.style.display = 'block';
                this.scheduleReconnect();
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateStatus('disconnected', 'Failed to connect');
            this.reconnectBtn.style.display = 'block';
            this.scheduleReconnect();
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectTimer) return;
        
        this.reconnectTimer = setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.reconnectTimer = null;
            this.connect();
        }, this.reconnectInterval);
    }
    
    updateStatus(status, text) {
        this.statusElement.className = `status ${status}`;
        this.statusText.textContent = text;
    }
    
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            if (message.frame) {
                this.videoStream.src = `data:image/jpeg;base64,${message.frame}`;
                this.updateFPS();
            }
            
            if (message.detections) {
                this.updateDetections(message.detections);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }
    
    updateFPS() {
        this.frameCount++;
        const now = Date.now();
        const elapsed = now - this.lastFpsUpdate;
        
        if (elapsed >= this.fpsInterval) {
            const fps = Math.round((this.frameCount / elapsed) * 1000);
            this.fpsCounter.textContent = fps;
            this.frameCount = 0;
            this.lastFpsUpdate = now;
        }
    }
    
    updateDetections(detections) {
        this.detectionCounter.textContent = detections.length;
        
        if (detections.length === 0) {
            this.detectionList.innerHTML = '<p style="color: #666;">No detections</p>';
            return;
        }
        
        const sortedDetections = detections.sort((a, b) => b.confidence - a.confidence);
        
        this.detectionList.innerHTML = sortedDetections.map(det => `
            <div class="detection-item">
                <div class="detection-class">${det.class}</div>
                <div class="detection-confidence">
                    Confidence: ${(det.confidence * 100).toFixed(1)}%
                </div>
            </div>
        `).join('');
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
}

const client = new YOLOWebcamClient();

window.addEventListener('beforeunload', () => {
    client.disconnect();
});
