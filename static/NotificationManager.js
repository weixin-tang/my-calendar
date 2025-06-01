class NotificationManager {
    constructor() {
        this.notification = document.getElementById('notification');
        this.notificationText = document.getElementById('notificationText');
    }

    show(message, type = 'info') {
        this.notification.className = `notification notification-${type}`;
        this.notificationText.textContent = message;
        this.notification.classList.add('show');
        
        setTimeout(() => {
            this.notification.classList.remove('show');
        }, 3000);
    }
}