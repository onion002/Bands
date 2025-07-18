#!/usr/bin/env python3
"""
测试成员管理API的脚本
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_get_members():
    """测试获取成员列表"""
    print("=== 测试获取成员列表 ===")
    try:
        # 先获取乐队列表
        bands_response = requests.get(f"{BASE_URL}/api/bands/")
        if bands_response.status_code == 200:
            bands_data = bands_response.json()
            print(f"获取到 {len(bands_data.get('items', []))} 个乐队")
            
            # 如果有乐队，获取第一个乐队的成员
            if bands_data.get('items'):
                band_id = bands_data['items'][0]['id']
                members_response = requests.get(f"{BASE_URL}/api/members/band/{band_id}")
                if members_response.status_code == 200:
                    members_data = members_response.json()
                    print(f"乐队 {band_id} 有 {len(members_data.get('items', []))} 个成员")
                    for member in members_data.get('items', []):
                        print(f"  - {member['name']} ({member.get('role', '未设置')})")
                else:
                    print(f"获取成员失败: {members_response.status_code}")
            else:
                print("没有找到乐队")
        else:
            print(f"获取乐队失败: {bands_response.status_code}")
    except Exception as e:
        print(f"测试失败: {e}")

def test_create_member():
    """测试创建成员"""
    print("\n=== 测试创建成员 ===")
    try:
        # 先获取一个乐队ID
        bands_response = requests.get(f"{BASE_URL}/api/bands/")
        if bands_response.status_code == 200:
            bands_data = bands_response.json()
            if bands_data.get('items'):
                band_id = bands_data['items'][0]['id']
                
                # 创建测试成员
                member_data = {
                    "name": "测试成员",
                    "role": "测试角色",
                    "join_date": "2024-01-01",
                    "band_id": band_id
                }
                
                response = requests.post(f"{BASE_URL}/api/members/", json=member_data)
                if response.status_code == 201:
                    created_member = response.json()
                    print(f"成功创建成员: {created_member['name']} (ID: {created_member['id']})")
                    return created_member['id']
                else:
                    print(f"创建成员失败: {response.status_code} - {response.text}")
            else:
                print("没有找到乐队，无法创建成员")
        else:
            print(f"获取乐队失败: {bands_response.status_code}")
    except Exception as e:
        print(f"测试失败: {e}")
    return None

def test_upload_avatar(member_id):
    """测试上传头像"""
    print(f"\n=== 测试上传头像 (成员ID: {member_id}) ===")
    if not member_id:
        print("没有有效的成员ID，跳过头像上传测试")
        return
    
    try:
        # 创建一个简单的测试图片文件
        import io
        from PIL import Image
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test_avatar.jpg', img_bytes, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/members/{member_id}/avatar", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"头像上传成功: {result.get('avatar_url')}")
        else:
            print(f"头像上传失败: {response.status_code} - {response.text}")
    except ImportError:
        print("PIL库未安装，跳过头像上传测试")
    except Exception as e:
        print(f"测试失败: {e}")

def main():
    print("开始测试成员管理API...")
    
    # 测试获取成员
    test_get_members()
    
    # 测试创建成员
    member_id = test_create_member()
    
    # 测试上传头像
    test_upload_avatar(member_id)
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
