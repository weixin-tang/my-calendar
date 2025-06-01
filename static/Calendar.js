class Calendar {
    constructor() {
        this.init();
    }

    init() {
        // 初始化各个管理器
        this.notificationManager = new NotificationManager();
        this.connectionStatusManager = new ConnectionStatusManager();
        this.eventManager = new EventManager(this);
        this.viewManager = new ViewManager(this);
        this.modalManager = new ModalManager(this);
        this.webSocketManager = new WebSocketManager(this);
        
        // 绑定导航事件
        this.bindNavigationEvents();
        
        // 初始化视图
        this.viewManager.renderCalendar();
        this.viewManager.updateCurrentPeriod();
    }

    bindNavigationEvents() {
        // 导航按钮
        document.getElementById('prevPeriod').addEventListener('click', () => this.viewManager.previousPeriod());
        document.getElementById('nextPeriod').addEventListener('click', () => this.viewManager.nextPeriod());
        document.getElementById('todayBtn').addEventListener('click', () => this.viewManager.goToToday());
        
        // 视图切换
        document.getElementById('monthView').addEventListener('click', () => this.viewManager.switchToMonthView());
        document.getElementById('weekView').addEventListener('click', () => this.viewManager.switchToWeekView());
    }
}