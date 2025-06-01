class EventManager {
    constructor(calendar) {
        this.calendar = calendar;
        this.events =  []; //  JSON.parse(localStorage.getItem('calendarEvents')) ||
        this.selectedColor = 'blue';
        this.currentEventId = null;
    }

    handleServerMessage(data) {
        switch (data.type) {
            case 'events':
                this.events = data.events || [];
                // this.saveToLocalStorage();
                this.calendar.viewManager.renderCalendar();
                break;
            case 'event_created':
                if (data.event) {
                    this.events.push(data.event);
                    // this.saveToLocalStorage();
                    this.calendar.viewManager.renderCalendar();
                    this.calendar.notificationManager.show('事件创建成功', 'success');
                }
                break;
            case 'event_updated':
                if (data.event) {
                    const index = this.events.findIndex(e => e.id === data.event.id);
                    if (index !== -1) {
                        this.events[index] = data.event;
                        // this.saveToLocalStorage();
                        this.calendar.viewManager.renderCalendar();
                        this.calendar.notificationManager.show('事件更新成功', 'success');
                    }
                }
                break;
            case 'event_deleted':
                if (data.event_id) {
                    this.events = this.events.filter(e => e.id !== data.event_id);
                    // this.saveToLocalStorage();
                    this.calendar.viewManager.renderCalendar();
                    this.calendar.notificationManager.show('事件删除成功', 'success');
                }
                break;
            case 'online_users':
                this.updateOnlineUsers(data.count);
                break;
            case 'pong':
                if (this.calendar.webSocketManager.heartbeatTimeout) {
                    clearTimeout(this.calendar.webSocketManager.heartbeatTimeout);
                    this.calendar.webSocketManager.heartbeatTimeout = null;
                }
                break;
            case 'error':
                this.calendar.notificationManager.show(data.message || '操作失败', 'error');
                break;
        }
    }

    saveToLocalStorage() {
        localStorage.setItem('calendarEvents', JSON.stringify(this.events));
    }

    updateOnlineUsers(count) {
        const element = document.getElementById('onlineUsers');
        if (element) {
            element.textContent = count;
        }
    }

    createEvent(eventData) {
        this.calendar.webSocketManager.sendMessage({
            type: 'create_event',
            event: eventData
        });
    }

    updateEvent(eventData) {
        this.calendar.webSocketManager.sendMessage({
            type: 'update_event',
            event: eventData
        });
    }

    deleteEvent(eventId) {
        this.calendar.webSocketManager.sendMessage({
            type: 'delete_event',
            event_id: eventId
        });
    }

    requestEvents() {
        this.calendar.webSocketManager.sendMessage({ type: 'get_events' });
    }

    getEventsForDate(dateStr) {
        return this.events.filter(event => event.date === dateStr);
    }

    getEventById(id) {
        return this.events.find(event => event.id === id);
    }

    setCurrentEventId(id) {
        this.currentEventId = id;
    }

    getCurrentEventId() {
        return this.currentEventId;
    }

    setSelectedColor(color) {
        this.selectedColor = color;
    }

    getSelectedColor() {
        return this.selectedColor;
    }
}