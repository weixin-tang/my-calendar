


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


docker build -t calendar-app .


会使用默认值 /calendar
docker run -p 8027:8027 calendar-app



docker container rm -f calendar-app && docker run -itd --name calendar-app --hostname calendar-app --network weixin-network -e PORT=80 -e ROOT_PATH="/calendar" calendar-app


    location /calendar {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://calendar-app:80;
        proxy_redirect default;
     }
