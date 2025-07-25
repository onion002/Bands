#!/usr/bin/env python3
"""
测试强制清理所有未使用图片的API
"""

import requests
import json
import os

API_BASE_URL = "http://localhost:5000"
UPLOAD_DIR = "BandManager/uploads/bands"

def main():
    print("强制清理未使用图片测试")
    print("=" * 50)
    
    # 1. 检查清理前的文件状态
    print("\n1. 清理前的uploads/bands目录:")
    list_files()
    
    # 2. 获取乐队信息
    print("\n2. 获取乐队信息:")
    bands = get_bands()
    if bands:
        for band in bands:
            print(f"  - 乐队: {band['name']}, 图片: {band.get('banner_image_url', '无')}")
    
    # 3. 调用强制清理API
    print("\n3. 调用强制清理API:")
    try:
        response = requests.post(f"{API_BASE_URL}/api/bands/force_cleanup_all_unused_images")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  消息: {result['message']}")
            print(f"  删除的文件数量: {result['deleted_files_count']}")
            if result['deleted_files']:
                print("  删除的文件:")
                for file in result['deleted_files']:
                    print(f"    - {file}")
            if result.get('used_images'):
                print("  正在使用的图片:")
                for file in result['used_images']:
                    print(f"    - {file}")
        else:
            print(f"  错误: {response.text}")
    except Exception as e:
        print(f"  API调用失败: {e}")
    
    # 4. 检查清理后的文件状态
    print("\n4. 清理后的uploads/bands目录:")
    list_files()
    
    print("\n" + "=" * 50)
    print("测试完成")

def list_files():
    """列出uploads/bands目录中的文件"""
    if not os.path.exists(UPLOAD_DIR):
        print("  目录不存在")
        return
    
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    if files:
        for f in files:
            file_path = os.path.join(UPLOAD_DIR, f)
            size = os.path.getsize(file_path)
            print(f"  - {f} ({size} bytes)")
    else:
        print("  (空目录)")

def get_bands():
    """获取乐队列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/bands/")
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"  获取乐队失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"  获取乐队失败: {e}")
        return []

if __name__ == "__main__":
    main()
