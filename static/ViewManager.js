class ViewManager {
    constructor(calendar) {
        this.calendar = calendar;
        this.currentDate = new Date();
        this.viewMode = 'month';
        this.currentWeekStart = null;
        this.currentViewRange = { start: null, end: null };
    }

    switchToMonthView() {
        this.viewMode = 'month';
        document.getElementById('monthView').className = 'px-1 md:px-3 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium';
        document.getElementById('weekView').className = 'px-1 md:px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg';
        this.renderCalendar();
        this.updateCurrentPeriod();
        this.calculateViewRange();
        this.sendViewRange();
    }

    switchToWeekView() {
        this.viewMode = 'week';
        document.getElementById('monthView').className = 'px-1 md:px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg';
        document.getElementById('weekView').className = 'px-1 md:px-3 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium';
        this.setCurrentWeek();
        this.renderCalendar();
        this.updateCurrentPeriod();
        this.calculateViewRange();
        this.sendViewRange();
    }

    setCurrentWeek() {
        const today = new Date(this.currentDate);
        const dayOfWeek = today.getDay();
        this.currentWeekStart = new Date(today);
        this.currentWeekStart.setDate(today.getDate() - dayOfWeek);
    }

    renderCalendar() {
        if (this.viewMode === 'month') {
            this.renderMonthView();
        } else {
            this.renderWeekView();
        }
        this.calculateViewRange();
    }

    renderMonthView() {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';
        grid.className = 'calendar-grid';
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        for (let week = 0; week < 6; week++) {
            for (let day = 0; day < 7; day++) {
                const cellDate = new Date(startDate);
                cellDate.setDate(startDate.getDate() + (week * 7) + day);
                
                const cell = this.createDayCell(cellDate, month);
                grid.appendChild(cell);
            }
        }
    }

    renderWeekView() {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';
        grid.className = 'week-grid';
        
        this.updateWeekHeader();
        
        for (let day = 0; day < 7; day++) {
            const cellDate = new Date(this.currentWeekStart);
            cellDate.setDate(this.currentWeekStart.getDate() + day);
            
            const cell = this.createWeekDayCell(cellDate);
            grid.appendChild(cell);
        }
    }

    createDayCell(date, currentMonth) {
        const cell = document.createElement('div');
        const isCurrentMonth = date.getMonth() === currentMonth;
        const isToday = this.isToday(date);
        const dateStr = this.formatDate(date);
        
        cell.className = `day-cell border-r border-b p-2 ${isCurrentMonth ? 'bg-white' : 'bg-gray-50'} hover:bg-gray-100 cursor-pointer`;
        
        const dayNumber = document.createElement('div');
        dayNumber.className = `text-sm font-medium mb-1 ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'} ${isToday ? 'bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : ''}`;
        dayNumber.textContent = date.getDate();
        cell.appendChild(dayNumber);
        
        const dayEvents = this.calendar.eventManager.getEventsForDate(dateStr);
        dayEvents.forEach(event => {
            const eventEl = document.createElement('div');
            eventEl.className = `event truncate md:whitespace-normal w-9 md:w-auto bg-${event.color}-100 text-${event.color}-800 border-l-2 border-${event.color}-500`;
            eventEl.textContent = event.title;
            eventEl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.calendar.modalManager.showEventDetail(event);
            });
            cell.appendChild(eventEl);
        });
        
        cell.addEventListener('click', () => {
            this.calendar.modalManager.openEventModal(dateStr);
        });
        
        return cell;
    }

    createWeekDayCell(date) {
        const cell = document.createElement('div');
        const isToday = this.isToday(date);
        const dateStr = this.formatDate(date);
        
        cell.className = `week-day-cell border-r border-b p-2 last:border-r-0 ${isToday ? 'bg-blue-50' : 'bg-white'} hover:bg-gray-100 cursor-pointer`;
        
        const dayEvents = this.calendar.eventManager.getEventsForDate(dateStr);
        dayEvents.forEach(event => {
            const eventEl = document.createElement('div');
            eventEl.className = `event truncate md:whitespace-normal w-9 md:w-auto bg-${event.color}-100 text-${event.color}-800 border-l-2 border-${event.color}-500 mb-2`;
            eventEl.innerHTML = `
                <div class="font-medium">${event.title}</div>
                ${event.time ? `<div class="text-xs opacity-75">${event.time}</div>` : ''}
            `;
            eventEl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.calendar.modalManager.showEventDetail(event);
            });
            cell.appendChild(eventEl);
        });
        
        cell.addEventListener('click', () => {
            this.calendar.modalManager.openEventModal(dateStr);
        });
        
        return cell;
    }

    updateWeekHeader() {
        const header = document.getElementById('weekHeader');
        header.innerHTML = '';
        
        const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        
        for (let day = 0; day < 7; day++) {
            const cellDate = new Date(this.currentWeekStart);
            cellDate.setDate(this.currentWeekStart.getDate() + day);
            
            const headerCell = document.createElement('div');
            headerCell.className = 'p-4 text-center border-r last:border-r-0';
            headerCell.innerHTML = `
                <div class="font-semibold text-gray-700">${weekDays[day]}</div>
                <div class="text-lg font-bold mt-1 ${this.isToday(cellDate) ? 'text-blue-600' : 'text-gray-900'}">
                    ${cellDate.getDate()}
                </div>
            `;
            header.appendChild(headerCell);
        }
    }

    previousPeriod() {
        if (this.viewMode === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        } else {
            this.currentWeekStart.setDate(this.currentWeekStart.getDate() - 7);
        }
        this.renderCalendar();
        this.updateCurrentPeriod();
        this.sendViewRange();
    }

    nextPeriod() {
        if (this.viewMode === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        } else {
            this.currentWeekStart.setDate(this.currentWeekStart.getDate() + 7);
        }
        this.renderCalendar();
        this.updateCurrentPeriod();
        this.sendViewRange();
    }

    goToToday() {
        this.currentDate = new Date();
        if (this.viewMode === 'week') {
            this.setCurrentWeek();
        }
        this.renderCalendar();
        this.updateCurrentPeriod();
        this.sendViewRange();
    }

    updateCurrentPeriod() {
        const periodElement = document.getElementById('currentPeriod');
        
        if (this.viewMode === 'month') {
            const monthNames = [
                '一月', '二月', '三月', '四月', '五月', '六月',
                '七月', '八月', '九月', '十月', '十一月', '十二月'
            ];
            const monthText = `${this.currentDate.getFullYear()}年 ${monthNames[this.currentDate.getMonth()]}`;
            periodElement.textContent = monthText;
        } else {
            const weekEnd = new Date(this.currentWeekStart);
            weekEnd.setDate(this.currentWeekStart.getDate() + 6);
            
            const startMonth = this.currentWeekStart.getMonth() + 1;
            const startDay = this.currentWeekStart.getDate();
            const endMonth = weekEnd.getMonth() + 1;
            const endDay = weekEnd.getDate();
            const year = this.currentWeekStart.getFullYear();
            
            if (startMonth === endMonth) {
                periodElement.textContent = `${year}年${startMonth}月${startDay}日-${endDay}日`;
            } else {
                periodElement.textContent = `${year}年${startMonth}月${startDay}日-${endMonth}月${endDay}日`;
            }
        }
    }

    calculateViewRange() {
        if (this.viewMode === 'month') {
            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth();
            const firstDay = new Date(`${year}-${String(month + 1).padStart(2, '0')}-01T00:00:00+08:00`);
            const lastDay = new Date(`${year}-${String(month + 2).padStart(2, '0')}-01T00:00:00+08:00`);
            const startDate = new Date(firstDay.getTime());
            startDate.setDate(startDate.getDate() - firstDay.getDay());
            const endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + 41);
            
            this.currentViewRange = {
                start: this.formatDate(startDate),
                end: this.formatDate(endDate)
            };
        } else {
            const endDate = new Date(this.currentWeekStart);
            endDate.setDate(this.currentWeekStart.getDate() + 6);
            
            this.currentViewRange = {
                start: this.formatDate(this.currentWeekStart),
                end: this.formatDate(endDate)
            };
        }
    }

    sendViewRange() {
        if (this.currentViewRange.start && this.currentViewRange.end) {
            this.calendar.webSocketManager.sendMessage({
                type: 'view_range',
                start_date: this.currentViewRange.start,
                end_date: this.currentViewRange.end
            });
        }
    }

    formatDate(date) {
        let year = date.getFullYear();
        let month = String(date.getMonth() + 1).padStart(2, '0');
        let day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    formatDisplayDate(dateStr) {
        const parts = dateStr.split('-');
        const year = parseInt(parts[0]);
        const month = parseInt(parts[1]);
        const day = parseInt(parts[2]);
        return `${year}年${month}月${day}日`;
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }
}