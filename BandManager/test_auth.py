#!/usr/bin/env python3
"""
认证系统测试脚本
"""

import os
import sys
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试配置
BASE_URL = 'http://localhost:5000'
DEVELOPER_KEY = 'dev-key-123'  # 从配置文件中获取的开发者密钥

class AuthTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        
    def test_register_admin(self):
        """测试管理员注册"""
        print("🧪 测试管理员注册...")
        
        data = {
            'username': 'testadmin',
            'email': 'testadmin@example.com',
            'password': 'admin123456',
            'user_type': 'admin',
            'display_name': '测试管理员',
            'developer_key': DEVELOPER_KEY
        }
        
        response = self.session.post(f'{self.base_url}/api/auth/register', json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.admin_token = result['token']
            print(f"✅ 管理员注册成功: {result['user']['username']}")
            return True
        else:
            print(f"❌ 管理员注册失败: {response.status_code} - {response.text}")
            return False
    
    def test_register_user(self):
        """测试普通用户注册"""
        print("🧪 测试普通用户注册...")
        
        data = {
            'username': 'normaluser',
            'email': 'normaluser@example.com',
            'password': 'user123456',
            'user_type': 'user',
            'display_name': '普通用户'
        }
        
        response = self.session.post(f'{self.base_url}/api/auth/register', json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.user_token = result['token']
            print(f"✅ 普通用户注册成功: {result['user']['username']}")
            return True
        else:
            print(f"❌ 普通用户注册失败: {response.status_code} - {response.text}")
            return False
    
    def test_login_admin(self):
        """测试管理员登录"""
        print("🧪 测试管理员登录...")
        
        data = {
            'login': 'admin',  # 使用默认管理员账户
            'password': 'admin123'
        }
        
        response = self.session.post(f'{self.base_url}/api/auth/login', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.admin_token = result['token']
            print(f"✅ 管理员登录成功: {result['user']['username']}")
            return True
        else:
            print(f"❌ 管理员登录失败: {response.status_code} - {response.text}")
            return False
    
    def test_login_user(self):
        """测试普通用户登录"""
        print("🧪 测试普通用户登录...")
        
        data = {
            'login': 'testuser',  # 使用默认测试用户
            'password': 'test123'
        }
        
        response = self.session.post(f'{self.base_url}/api/auth/login', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.user_token = result['token']
            print(f"✅ 普通用户登录成功: {result['user']['username']}")
            return True
        else:
            print(f"❌ 普通用户登录失败: {response.status_code} - {response.text}")
            return False
    
    def test_admin_create_band(self):
        """测试管理员创建乐队"""
        print("🧪 测试管理员创建乐队...")
        
        if not self.admin_token:
            print("❌ 没有管理员token")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        data = {
            'name': '测试乐队',
            'year': 2024,
            'genre': '摇滚',
            'member_count': 4,
            'bio': '这是一个测试乐队',
            'primary_color': '#667eea'
        }
        
        response = self.session.post(f'{self.base_url}/api/bands/', json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 乐队创建成功: {result['name']}")
            return True
        else:
            print(f"❌ 乐队创建失败: {response.status_code} - {response.text}")
            return False
    
    def test_user_access_bands(self):
        """测试普通用户访问乐队（应该失败）"""
        print("🧪 测试普通用户访问管理员API...")
        
        if not self.user_token:
            print("❌ 没有普通用户token")
            return False
        
        headers = {'Authorization': f'Bearer {self.user_token}'}
        response = self.session.get(f'{self.base_url}/api/bands/', headers=headers)
        
        if response.status_code == 403:
            print("✅ 普通用户正确被拒绝访问管理员API")
            return True
        else:
            print(f"❌ 权限控制失败: {response.status_code} - {response.text}")
            return False
    
    def test_public_access(self):
        """测试公开访问"""
        print("🧪 测试公开访问...")
        
        # 测试访问管理员的公开乐队
        response = self.session.get(f'{self.base_url}/api/bands/public/admin')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 公开访问成功，找到 {len(result['items'])} 个乐队")
            return True
        else:
            print(f"❌ 公开访问失败: {response.status_code} - {response.text}")
            return False
    
    def test_token_verification(self):
        """测试token验证"""
        print("🧪 测试token验证...")
        
        if not self.admin_token:
            print("❌ 没有管理员token")
            return False
        
        data = {'token': self.admin_token}
        response = self.session.post(f'{self.base_url}/api/auth/verify-token', json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['valid']:
                print(f"✅ Token验证成功: {result['user']['username']}")
                return True
            else:
                print("❌ Token无效")
                return False
        else:
            print(f"❌ Token验证失败: {response.status_code} - {response.text}")
            return False
    
    def test_profile_access(self):
        """测试用户信息访问"""
        print("🧪 测试用户信息访问...")
        
        if not self.admin_token:
            print("❌ 没有管理员token")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.session.get(f'{self.base_url}/api/auth/profile', headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户信息获取成功: {result['user']['username']}")
            return True
        else:
            print(f"❌ 用户信息获取失败: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 开始认证系统测试")
        print("=" * 60)
        
        tests = [
            ("管理员登录", self.test_login_admin),
            ("普通用户登录", self.test_login_user),
            ("Token验证", self.test_token_verification),
            ("用户信息访问", self.test_profile_access),
            ("管理员创建乐队", self.test_admin_create_band),
            ("普通用户访问限制", self.test_user_access_bands),
            ("公开访问", self.test_public_access),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed}/{total} 通过")
        print("=" * 60)
        
        if passed == total:
            print("🎉 所有测试通过！认证系统工作正常。")
        else:
            print("⚠️  部分测试失败，请检查系统配置。")
        
        return passed == total

def main():
    """主测试函数"""
    print("认证系统测试工具")
    print("确保后端服务正在运行在 http://localhost:5000")
    
    # 检查服务是否可用
    try:
        response = requests.get(f'{BASE_URL}/api/auth/verify-token', timeout=5)
        print("✅ 后端服务连接正常")
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("请确保后端服务正在运行")
        sys.exit(1)
    
    # 运行测试
    tester = AuthTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
