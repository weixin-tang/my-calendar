# 数据模型
from typing import Optional
from pydantic import BaseModel

class Event(BaseModel):
    id: Optional[str] = None
    title: str
    date: str
    time: Optional[str] = None
    description: Optional[str] = None
    color: str = "blue"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
