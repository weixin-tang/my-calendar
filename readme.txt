


# 获取所有事件
curl http://localhost:8027/api/events

# 创建新事件
curl -X POST http://localhost:8027/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试事件",
    "date": "2024-01-20",
    "time": "10:00",
    "description": "这是一个测试事件",
    "color": "green"
  }'

# 更新事件（需要先获取event_id）
curl -X PUT http://localhost:8027/api/events/{event_id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新的事件",
    "date": "2024-01-20",
    "time": "11:00",
    "description": "更新后的描述",
    "color": "blue"
  }'

# 删除事件
curl -X DELETE http://localhost:8027/api/events/{event_id}

