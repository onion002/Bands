#!/usr/bin/env python3
"""
直接测试API的脚本
"""

import requests
import json
import os

API_BASE_URL = "http://localhost:5000"
UPLOAD_DIR = "BandManager/uploads/bands"

def test_api():
    print("直接API测试")
    print("=" * 40)
    
    # 1. 检查文件状态
    print("\n1. 检查uploads/bands目录:")
    if os.path.exists(UPLOAD_DIR):
        files = os.listdir(UPLOAD_DIR)
        for f in files:
            print(f"  - {f}")
    else:
        print("  目录不存在")
    
    # 2. 获取乐队列表
    print("\n2. 获取乐队列表:")
    try:
        response = requests.get(f"{API_BASE_URL}/api/bands/")
        if response.status_code == 200:
            bands = response.json().get('items', [])
            for band in bands:
                print(f"  - ID: {band['id']}, 名称: {band['name']}, 图片: {band.get('banner_image_url', '无')}")
            
            # 3. 如果有乐队，测试强制清理
            if bands:
                test_band = bands[0]
                print(f"\n3. 测试强制清理乐队 {test_band['name']} (ID: {test_band['id']}):")
                
                cleanup_response = requests.post(f"{API_BASE_URL}/api/bands/{test_band['id']}/cleanup_all_images")
                print(f"  状态码: {cleanup_response.status_code}")
                if cleanup_response.status_code == 200:
                    result = cleanup_response.json()
                    print(f"  结果: {result}")
                else:
                    print(f"  错误: {cleanup_response.text}")
                
                # 4. 再次检查文件状态
                print("\n4. 清理后的uploads/bands目录:")
                if os.path.exists(UPLOAD_DIR):
                    files = os.listdir(UPLOAD_DIR)
                    if files:
                        for f in files:
                            print(f"  - {f}")
                    else:
                        print("  (空目录)")
                else:
                    print("  目录不存在")
        else:
            print(f"  获取乐队失败: {response.status_code}")
    except Exception as e:
        print(f"  API调用失败: {e}")

if __name__ == "__main__":
    test_api()
