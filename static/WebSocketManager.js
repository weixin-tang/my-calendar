class WebSocketManager {
    constructor(calendar) {
        this.calendar = calendar;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.heartbeatInterval = null;
        this.heartbeatTimeout = null;
        this.isManualClose = false;
        this.isPageVisible = true;
        
        this.setupPageVisibilityHandler();
        this.connect();
    }

    connect() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            return;
        }
        
        this.cleanupWebSocket();
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const pathname = window.location.pathname.replace(/\/$/, '');
            const wsUrl = `${protocol}//${host}${pathname}/ws`;
            this.websocket = new WebSocket( wsUrl );
            this.websocket.onopen = () => this.handleOpen();
            this.websocket.onmessage = (event) => this.handleMessage(event);
            this.websocket.onclose = (event) => this.handleClose(event);
            this.websocket.onerror = (error) => this.handleError(error);
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.calendar.notificationManager.show('连接失败', 'error');
            this.scheduleReconnect();
        }
    }

    handleOpen() {
        console.log('WebSocket连接已建立');
        this.calendar.connectionStatusManager.update('connected');
        this.calendar.notificationManager.show('连接成功', 'success');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.startHeartbeat();
        this.calendar.viewManager.sendViewRange();
    }

    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            this.calendar.eventManager.handleServerMessage(data);
        } catch (error) {
            console.error('解析WebSocket消息失败:', error);
        }
    }

    handleClose(event) {
        console.log('WebSocket连接关闭:', event.code, event.reason);
        this.calendar.connectionStatusManager.update('disconnected');
        this.stopHeartbeat();
        
        if (!this.isManualClose && this.isPageVisible) {
            this.scheduleReconnect();
        }
    }

    handleError(error) {
        console.error('WebSocket错误:', error);
        this.calendar.connectionStatusManager.update('disconnected');
    }

    sendMessage(data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(data));
            return true;
        } else {
            this.calendar.notificationManager.show('连接断开，消息发送失败，正在重连...', 'error');
            this.connect();
            return false;
        }
    }

    setupPageVisibilityHandler() {
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden;
            
            if (this.isPageVisible) {
                if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                    console.log('页面重新可见，检查WebSocket连接');
                    this.connect();
                }
            }
        });
        
        window.addEventListener('online', () => {
            console.log('网络重新连接');
            this.calendar.notificationManager.show('网络已恢复，正在重新连接...', 'info');
            this.connect();
        });
        
        window.addEventListener('offline', () => {
            console.log('网络断开');
            this.calendar.notificationManager.show('网络连接断开', 'error');
            this.calendar.connectionStatusManager.update('disconnected');
        });
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({ type: 'ping' }));
                
                this.heartbeatTimeout = setTimeout(() => {
                    console.log('心跳超时，关闭连接');
                    this.websocket.close();
                }, 5000);
            }
        }, 30000);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('达到最大重连次数，停止重连');
            this.calendar.notificationManager.show('连接失败，请刷新页面重试', 'error');
            return;
        }
        
        this.reconnectAttempts++;
        this.calendar.connectionStatusManager.update('connecting');
        
        setTimeout(() => {
            if (this.isPageVisible) {
                console.log(`第${this.reconnectAttempts}次重连尝试`);
                this.connect();
            }
        }, this.reconnectDelay);
        
        this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, this.maxReconnectDelay);
    }

    cleanupWebSocket() {
        this.stopHeartbeat();
        if (this.websocket) {
            this.websocket.onopen = null;
            this.websocket.onmessage = null;
            this.websocket.onclose = null;
            this.websocket.onerror = null;
            if (this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.close();
            }
            this.websocket = null;
        }
    }

    close() {
        this.isManualClose = true;
        this.cleanupWebSocket();
    }
}