class ConnectionStatusManager {
    constructor() {
        this.statusElement = document.getElementById('connectionStatus');
        this.statusText = document.getElementById('statusText');
    }

    update(status) {
        this.statusElement.className = `connection-status status-${status}`;
        
        switch (status) {
            case 'connected':
                this.statusText.textContent = '已连接';
                break;
            case 'connecting':
                this.statusText.textContent = '连接中...';
                break;
            case 'disconnected':
                this.statusText.textContent = '已断开';
                break;
        }
    }
}