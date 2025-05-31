import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class CalendarAPIClient:
    """日历API客户端，封装所有日历操作"""
    
    def __init__(self, base_url: str = "http://localhost:8027"):
        """
        初始化API客户端
        
        Args:
            base_url: 日历服务的基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
    
    def get_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """
        获取事件列表
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD格式)
            end_date: 结束日期 (YYYY-MM-DD格式)
            
        Returns:
            事件列表
        """
        url = f"{self.api_base}/events"
        params = {}
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()['events']
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取事件失败: {e}")
    
    def create_event(self, title: str, date: str, time: Optional[str] = None, 
                    description: Optional[str] = None, color: str = "blue") -> Dict:
        """
        创建新事件
        
        Args:
            title: 事件标题
            date: 事件日期 (YYYY-MM-DD格式)
            time: 事件时间 (HH:MM格式)
            description: 事件描述
            color: 事件颜色
            
        Returns:
            创建的事件信息
        """
        url = f"{self.api_base}/events"
        
        event_data = {
            "title": title,
            "date": date,
            "color": color
        }
        
        if time:
            event_data["time"] = time
        if description:
            event_data["description"] = description
            
        try:
            response = requests.post(url, json=event_data)
            response.raise_for_status()
            return response.json()['event']
        except requests.exceptions.RequestException as e:
            raise Exception(f"创建事件失败: {e}")
    
    def update_event(self, event_id: str, title: str, date: str, 
                    time: Optional[str] = None, description: Optional[str] = None, 
                    color: str = "blue") -> Dict:
        """
        更新事件
        
        Args:
            event_id: 事件ID
            title: 事件标题
            date: 事件日期 (YYYY-MM-DD格式)
            time: 事件时间 (HH:MM格式)
            description: 事件描述
            color: 事件颜色
            
        Returns:
            更新后的事件信息
        """
        url = f"{self.api_base}/events/{event_id}"
        
        event_data = {
            "title": title,
            "date": date,
            "color": color
        }
        
        if time:
            event_data["time"] = time
        if description:
            event_data["description"] = description
            
        try:
            response = requests.put(url, json=event_data)
            response.raise_for_status()
            return response.json()['event']
        except requests.exceptions.RequestException as e:
            raise Exception(f"更新事件失败: {e}")
    
    def delete_event(self, event_id: str) -> bool:
        """
        删除事件
        
        Args:
            event_id: 事件ID
            
        Returns:
            删除是否成功
        """
        url = f"{self.api_base}/events/{event_id}"
        
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"删除事件失败: {e}")
    
    def get_health_status(self) -> Dict:
        """
        获取服务健康状态
        
        Returns:
            健康状态信息
        """
        url = f"{self.api_base}/health"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取健康状态失败: {e}")
    
    def delete_events_in_range(self, start_date: str, end_date: str) -> Dict:
        """
        删除指定时间区域内的所有事件
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD格式)
            end_date: 结束日期 (YYYY-MM-DD格式)
            
        Returns:
            删除操作的结果信息，包含删除的事件数量和详情
        """
        try:
            # 1. 获取指定时间区域的所有事件
            events = self.get_events(start_date, end_date)
            
            if not events:
                return {
                    "success": True,
                    "message": f"在 {start_date} 到 {end_date} 期间没有找到任何事件",
                    "deleted_count": 0,
                    "deleted_events": []
                }
            
            # 2. 提取事件ID并删除每个事件
            deleted_events = []
            failed_deletions = []
            
            for event in events:
                event_id = event.get('id')
                if event_id:
                    try:
                        # 删除单个事件
                        success = self.delete_event(event_id)
                        if success:
                            deleted_events.append({
                                "id": event_id,
                                "title": event.get('title', ''),
                                "date": event.get('date', ''),
                                "time": event.get('time', '')
                            })
                        else:
                            failed_deletions.append(event_id)
                    except Exception as e:
                        failed_deletions.append({
                            "id": event_id,
                            "error": str(e)
                        })
                else:
                    failed_deletions.append({
                        "event": event,
                        "error": "事件缺少ID"
                    })
            
            # 3. 返回删除结果
            result = {
                "success": len(failed_deletions) == 0,
                "message": f"成功删除 {len(deleted_events)} 个事件",
                "deleted_count": len(deleted_events),
                "deleted_events": deleted_events
            }
            
            if failed_deletions:
                result["failed_deletions"] = failed_deletions
                result["message"] += f"，{len(failed_deletions)} 个事件删除失败"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"删除指定区域事件失败: {str(e)}",
                "deleted_count": 0,
                "deleted_events": []
            }


# 示例用法
if __name__ == "__main__":
    # 创建客户端
    calendar = CalendarAPIClient(base_url = "http://localhost:8027" )
    
    try:
        # 检查服务状态
        health = calendar.get_health_status()
        print(f"服务状态: {health}")
        
        # 创建事件
        new_event = calendar.create_event(
            title="Python API测试",
            date="2024-01-20",
            time="14:00",
            description="测试Python API封装",
            color="green"
        )
        print(f"创建事件: {new_event}")
        
        # 获取所有事件
        events = calendar.get_events()
        print(f"所有事件: {events}")
        
        # 获取特定时间区域的事件示例
        # 示例5: 获取指定月份的事件（如2024年3月）
        march_events = calendar.get_events("2024-03-01", "2024-03-31")
        print(f"2024年3月事件: {march_events}")

        # 更新事件
        if new_event.get('id'):
            updated_event = calendar.update_event(
                event_id=new_event['id'],
                title="更新后的Python API测试",
                date="2024-01-20",
                time="15:00",
                description="更新后的描述",
                color="red"
            )
            print(f"更新事件: {updated_event}")
            
            # 删除事件
            deleted = calendar.delete_event(new_event['id'])
            print(f"删除事件: {deleted}")
        
        delete_result = calendar.delete_events_in_range("2024-01-01", "2024-01-31")
        print(f"删除2024年1月事件结果: {delete_result}")

    except Exception as e:
        print(f"操作失败: {e}")