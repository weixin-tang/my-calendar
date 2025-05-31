from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import json
import asyncio
from datetime import datetime, date
from typing import List, Dict, Optional
import uuid
from pydantic import BaseModel
import logging
# 添加时区支持
import pytz

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

app = FastAPI(title="在线日历系统", description="基于FastAPI和WebSocket的实时日历应用")

# 数据模型
class Event(BaseModel):
    id: Optional[str] = None
    title: str
    date: str
    time: Optional[str] = None
    description: Optional[str] = None
    color: str = "blue"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ViewRange(BaseModel):
    start_date: str
    end_date: str

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_view_ranges: Dict[WebSocket, ViewRange] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新客户端连接，当前在线用户: {len(self.active_connections)}")
        await self.broadcast_online_users()
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.client_view_ranges:
            del self.client_view_ranges[websocket]
        logger.info(f"客户端断开连接，当前在线用户: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            await self.disconnect_websocket(websocket)
    
    async def broadcast(self, message: dict, exclude: WebSocket = None):
        disconnected = []
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_text(json.dumps(message, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
                    disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            await self.disconnect_websocket(conn)
    
    async def broadcast_to_interested_clients(self, message: dict, event_date: str, exclude: WebSocket = None):
        """只向查看范围包含该事件日期的客户端广播"""
        disconnected = []
        for connection in self.active_connections:
            if connection != exclude and connection in self.client_view_ranges:
                view_range = self.client_view_ranges[connection]
                if view_range.start_date <= event_date <= view_range.end_date:
                    try:
                        await connection.send_text(json.dumps(message, ensure_ascii=False))
                    except Exception as e:
                        logger.error(f"广播消息失败: {e}")
                        disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            await self.disconnect_websocket(conn)
    
    async def broadcast_online_users(self):
        message = {
            "type": "online_users",
            "count": len(self.active_connections)
        }
        await self.broadcast(message)
    
    async def disconnect_websocket(self, websocket: WebSocket):
        self.disconnect(websocket)
        await self.broadcast_online_users()
    
    def update_client_view_range(self, websocket: WebSocket, view_range: ViewRange):
        self.client_view_ranges[websocket] = view_range
        logger.info(f"客户端视图范围更新: {view_range.start_date} - {view_range.end_date}")

manager = ConnectionManager()

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

# WebSocket处理
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "view_range":
                # 客户端更新视图范围
                view_range = ViewRange(
                    start_date=message["start_date"],
                    end_date=message["end_date"]
                )
                manager.update_client_view_range(websocket, view_range)
                
                # 发送该范围内的事件
                events = db.get_events_in_range(view_range.start_date, view_range.end_date)
                await manager.send_personal_message({
                    "type": "events_list",
                    "events": [event.dict() for event in events]
                }, websocket)
            
            elif message_type == "get_events":
                # 获取所有事件
                events = db.get_all_events()
                await manager.send_personal_message({
                    "type": "events_list",
                    "events": [event.dict() for event in events]
                }, websocket)
            
            elif message_type == "create_event":
                # 创建新事件
                try:
                    event_data = message["event"]
                    event = Event(**event_data)
                    created_event = db.create_event(event)
                    
                    # 广播给所有相关客户端
                    await manager.broadcast_to_interested_clients({
                        "type": "event_created",
                        "event": created_event.dict()
                    }, created_event.date, exclude=websocket)
                    
                    # 确认给发送者
                    await manager.send_personal_message({
                        "type": "event_created",
                        "event": created_event.dict()
                    }, websocket)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"创建事件失败: {str(e)}"
                    }, websocket)
            
            elif message_type == "update_event":
                # 更新事件
                try:
                    event_data = message["event"]
                    event = Event(**event_data)
                    updated_event = db.update_event(event)
                    
                    if updated_event:
                        # 广播给所有相关客户端
                        await manager.broadcast_to_interested_clients({
                            "type": "event_updated",
                            "event": updated_event.dict()
                        }, updated_event.date, exclude=websocket)
                        
                        # 确认给发送者
                        await manager.send_personal_message({
                            "type": "event_updated",
                            "event": updated_event.dict()
                        }, websocket)
                    else:
                        await manager.send_personal_message({
                            "type": "error",
                            "message": "事件不存在"
                        }, websocket)
                        
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"更新事件失败: {str(e)}"
                    }, websocket)
            
            elif message_type == "delete_event":
                # 删除事件
                try:
                    event_id = message["event_id"]
                    
                    # 先获取事件信息用于广播
                    event = db.get_event_by_id(event_id)
                    if event:
                        deleted = db.delete_event(event_id)
                        
                        if deleted:
                            # 广播给所有相关客户端
                            await manager.broadcast_to_interested_clients({
                                "type": "event_deleted",
                                "event_id": event_id
                            }, event.date, exclude=websocket)
                            
                            # 确认给发送者
                            await manager.send_personal_message({
                                "type": "event_deleted",
                                "event_id": event_id
                            }, websocket)
                        else:
                            await manager.send_personal_message({
                                "type": "error",
                                "message": "删除事件失败"
                            }, websocket)
                    else:
                        await manager.send_personal_message({
                            "type": "error",
                            "message": "事件不存在"
                        }, websocket)
                        
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"删除事件失败: {str(e)}"
                    }, websocket)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "未知的消息类型"
                }, websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await manager.disconnect_websocket(websocket)

# 静态文件服务
app.mount("/static", StaticFiles(directory="."), name="static")

# 根路径返回HTML文件
@app.get("/")
async def read_index():
    response = FileResponse('index.html')
    # 禁用缓存的响应头
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# REST API端点（可选，用于调试和管理）
@app.get("/api/events")
async def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """获取事件列表"""
    if start_date and end_date:
        events = db.get_events_in_range(start_date, end_date)
    else:
        events = db.get_all_events()
    return {"events": [event.dict() for event in events]}

@app.post("/api/events")
async def create_event_api(event: Event):
    """创建事件（REST API）"""
    try:
        created_event = db.create_event(event)
        
        # 通过WebSocket广播
        await manager.broadcast_to_interested_clients({
            "type": "event_created",
            "event": created_event.dict()
        }, created_event.date)
        
        return {"event": created_event.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/events/{event_id}")
async def update_event_api(event_id: str, event: Event):
    """更新事件（REST API）"""
    event.id = event_id
    updated_event = db.update_event(event)
    
    if not updated_event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 通过WebSocket广播
    await manager.broadcast_to_interested_clients({
        "type": "event_updated",
        "event": updated_event.dict()
    }, updated_event.date)
    
    return {"event": updated_event.dict()}

@app.delete("/api/events/{event_id}")
async def delete_event_api(event_id: str):
    """删除事件（REST API）"""
    event = db.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    deleted = db.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="删除失败")
    
    # 通过WebSocket广播
    await manager.broadcast_to_interested_clients({
        "type": "event_deleted",
        "event_id": event_id
    }, event.date)
    
    return {"message": "事件已删除"}

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "online_users": len(manager.active_connections),
        "timestamp": datetime.now(SHANGHAI_TZ).isoformat(),
        "timezone": "Asia/Shanghai"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8027, log_level="info")
