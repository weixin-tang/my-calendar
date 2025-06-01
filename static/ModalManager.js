class ModalManager {
    constructor(calendar) {
        this.calendar = calendar;
        this.bindModalEvents();
    }

    bindModalEvents() {
        // 模态框控制
        document.getElementById('addEventBtn').addEventListener('click', () => this.openEventModal());
        document.getElementById('closeModal').addEventListener('click', () => this.closeEventModal());
        document.getElementById('cancelEvent').addEventListener('click', () => this.closeEventModal());
        document.getElementById('closeDetailModal').addEventListener('click', () => this.closeDetailModal());
        
        // 表单提交
        document.getElementById('eventForm').addEventListener('submit', (e) => this.saveEvent(e));
        
        // 颜色选择
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectColor(e));
        });
        
        // 事件操作
        document.getElementById('deleteEvent').addEventListener('click', () => this.deleteEvent());
        document.getElementById('editEvent').addEventListener('click', () => this.editEvent());
        
        // 默认选择蓝色
        document.querySelector('[data-color="blue"]').classList.add('border-gray-800');
    }

    openEventModal(date = null) {
        const modal = document.getElementById('eventModal');
        const dateInput = document.getElementById('eventDate');
        const modalTitle = document.getElementById('modalTitle');
        
        if (this.calendar.eventManager.getCurrentEventId()) {
            modalTitle.textContent = '编辑事件';
        } else {
            modalTitle.textContent = '添加新事件';
        }
        
        if (date) {
            dateInput.value = date;
        } else {
            dateInput.value = this.calendar.viewManager.formatDate(new Date());
        }
        
        modal.classList.add('show');
    }

    closeEventModal() {
        const modal = document.getElementById('eventModal');
        modal.classList.remove('show');
        document.getElementById('eventForm').reset();
        this.calendar.eventManager.setCurrentEventId(null);
        
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.classList.remove('border-gray-800');
        });
        document.querySelector('[data-color="blue"]').classList.add('border-gray-800');
        this.calendar.eventManager.setSelectedColor('blue');
    }

    selectColor(e) {
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.classList.remove('border-gray-800');
        });
        e.target.classList.add('border-gray-800');
        this.calendar.eventManager.setSelectedColor(e.target.dataset.color);
    }

    saveEvent(e) {
        e.preventDefault();
        
        const title = document.getElementById('eventTitle').value;
        const date = document.getElementById('eventDate').value;
        const time = document.getElementById('eventTime').value;
        const description = document.getElementById('eventDescription').value;
        
        const eventData = {
            title,
            date,
            time,
            description,
            color: this.calendar.eventManager.getSelectedColor()
        };
        
        const currentEventId = this.calendar.eventManager.getCurrentEventId();
        if (currentEventId) {
            eventData.id = currentEventId;
            this.calendar.eventManager.updateEvent(eventData);
        } else {
            this.calendar.eventManager.createEvent(eventData);
        }
        
        this.closeEventModal();
    }

    showEventDetail(event) {
        const modal = document.getElementById('eventDetailModal');
        const content = document.getElementById('eventDetailContent');
        
        content.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="font-semibold text-gray-900 text-lg">${event.title}</h4>
                </div>
                <div class="flex items-center text-gray-600">
                    <i class="fas fa-calendar mr-2"></i>
                    <span>${this.calendar.viewManager.formatDisplayDate(event.date)}</span>
                </div>
                ${event.time ? `
                    <div class="flex items-center text-gray-600">
                        <i class="fas fa-clock mr-2"></i>
                        <span>${event.time} (上海时间)</span>
                    </div>
                ` : ''}
                ${event.description ? `
                    <div>
                        <h5 class="font-medium text-gray-700 mb-2">描述</h5>
                        <p class="text-gray-600">${event.description}</p>
                    </div>
                ` : ''}
                <div class="flex items-center">
                    <span class="w-4 h-4 rounded-full bg-${event.color}-500 mr-2"></span>
                    <span class="text-gray-600 capitalize">${event.color}</span>
                </div>
            </div>
        `;
        
        this.calendar.eventManager.setCurrentEventId(event.id);
        modal.classList.add('show');
    }

    closeDetailModal() {
        const modal = document.getElementById('eventDetailModal');
        modal.classList.remove('show');
        this.calendar.eventManager.setCurrentEventId(null);
    }

    editEvent() {
        const event = this.calendar.eventManager.getEventById(this.calendar.eventManager.getCurrentEventId());
        if (!event) return;
        
        document.getElementById('eventTitle').value = event.title;
        document.getElementById('eventDate').value = event.date;
        document.getElementById('eventTime').value = event.time || '';
        document.getElementById('eventDescription').value = event.description || '';
        
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.classList.remove('border-gray-800');
        });
        document.querySelector(`[data-color="${event.color}"]`).classList.add('border-gray-800');
        this.calendar.eventManager.setSelectedColor(event.color);
        
        this.closeDetailModal();
        this.openEventModal(event.date);
    }

    deleteEvent() {
        if (confirm('确定要删除这个事件吗？')) {
            this.calendar.eventManager.deleteEvent(this.calendar.eventManager.getCurrentEventId());
            this.closeDetailModal();
        }
    }
}