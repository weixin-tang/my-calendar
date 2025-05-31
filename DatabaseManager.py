import sqlite3
from Event import Event
import uuid 
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import pytz
from logger import logger


# 设置上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

# 数据库管理器
class DatabaseManager:
    def __init__(self, db_path: str = "calendar.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                description TEXT,
                color TEXT DEFAULT 'blue',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date_range ON events(date, created_at)")
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_event(self, event: Event) -> Event:
        """创建新事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        event.id = str(uuid.uuid4())
        # 使用上海时区的当前时间
        now = datetime.now(SHANGHAI_TZ).isoformat()
        event.created_at = now
        event.updated_at = now
        
        cursor.execute("""
            INSERT INTO events (id, title, date, time, description, color, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id, event.title, event.date, event.time, 
            event.description, event.color, event.created_at, event.updated_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"创建事件: {event.title} ({event.date}) - 上海时间: {now}")
        return event
    
    def get_events_in_range(self, start_date: str, end_date: str) -> List[Event]:
        """获取指定日期范围内的事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, date, time, description, color, created_at, updated_at
            FROM events
            WHERE date >= ? AND date <= ?
            ORDER BY date, time
        """, (start_date, end_date))
        
        events = []
        for row in cursor.fetchall():
            events.append(Event(
                id=row[0], title=row[1], date=row[2], time=row[3],
                description=row[4], color=row[5], created_at=row[6], updated_at=row[7]
            ))
        
        conn.close()
        return events
    
    def get_all_events(self) -> List[Event]:
        """获取所有事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, date, time, description, color, created_at, updated_at
            FROM events
            ORDER BY date, time
        """)
        
        events = []
        for row in cursor.fetchall():
            events.append(Event(
                id=row[0], title=row[1], date=row[2], time=row[3],
                description=row[4], color=row[5], created_at=row[6], updated_at=row[7]
            ))
        
        conn.close()
        return events
    
    def update_event(self, event: Event) -> Optional[Event]:
        """更新事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 使用上海时区的当前时间
        event.updated_at = datetime.now(SHANGHAI_TZ).isoformat()
        
        cursor.execute("""
            UPDATE events
            SET title=?, date=?, time=?, description=?, color=?, updated_at=?
            WHERE id=?
        """, (
            event.title, event.date, event.time, event.description, 
            event.color, event.updated_at, event.id
        ))
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        conn.commit()
        conn.close()
        
        logger.info(f"更新事件: {event.title} ({event.date}) - 上海时间: {event.updated_at}")
        return event
    
    def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先获取事件信息用于日志
        cursor.execute("SELECT title, date FROM events WHERE id=?", (event_id,))
        event_info = cursor.fetchone()
        
        cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted and event_info:
            logger.info(f"删除事件: {event_info[0]} ({event_info[1]})")
        
        return deleted
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """根据ID获取事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, date, time, description, color, created_at, updated_at
            FROM events
            WHERE id=?
        """, (event_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Event(
                id=row[0], title=row[1], date=row[2], time=row[3],
                description=row[4], color=row[5], created_at=row[6], updated_at=row[7]
            )
        return None

db = DatabaseManager()
