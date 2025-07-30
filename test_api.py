#!/usr/bin/env python3
"""
测试统计API
"""

import requests
import json

# 从浏览器控制台复制的token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNzIyNDI2NjA5fQ.taN4iLCJieHAiOjE3MjI0MjY2MDl9"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

base_url = 'http://localhost:5000'

def test_dashboard_stats():
    """测试仪表板统计API"""
    print("测试仪表板统计API...")
    try:
        response = requests.get(f'{base_url}/api/stats/dashboard', headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_recent_activities():
    """测试最近活动API"""
    print("\n测试最近活动API...")
    try:
        response = requests.get(f'{base_url}/api/stats/recent-activities', headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"最近活动: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == '__main__':
    test_dashboard_stats()
    test_recent_activities()
