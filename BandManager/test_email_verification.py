#!/usr/bin/env python3
"""
邮箱验证功能测试脚本
"""

import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "18444964944@163.com"  
TEST_USERNAME = "1844496494"
TEST_PASSWORD = "syx123456"

def test_send_verification_code():
    """测试发送验证码"""
    print("🧪 测试发送验证码...")
    
    url = f"{BASE_URL}/api/auth/send-verification-code"
    data = {
        "email": TEST_EMAIL,
        "verification_type": "register"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 发送验证码成功")
            return True
        else:
            print("❌ 发送验证码失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_verify_email(code):
    """测试验证邮箱验证码"""
    print(f"🧪 测试验证邮箱验证码: {code}")
    
    url = f"{BASE_URL}/api/auth/verify-email"
    data = {
        "email": TEST_EMAIL,
        "code": code,
        "verification_type": "register"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 验证邮箱成功")
            return True
        else:
            print("❌ 验证邮箱失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_register_with_verification(code):
    """测试使用验证码注册"""
    print(f"🧪 测试使用验证码注册: {code}")
    
    url = f"{BASE_URL}/api/auth/register-with-verification"
    data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "verification_code": code,
        "user_type": "user",
        "display_name": "测试用户"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 201:
            print("✅ 注册成功")
            return True
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_login():
    """测试登录"""
    print("🧪 测试登录...")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "login": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试邮箱验证功能")
    print("=" * 50)
    
    # 1. 发送验证码
    if not test_send_verification_code():
        print("❌ 测试终止：发送验证码失败")
        return
    
    print("\n⏳ 等待用户输入验证码...")
    verification_code = input("请输入收到的验证码: ").strip()
    
    if not verification_code:
        print("❌ 未输入验证码，测试终止")
        return
    
    # 2. 验证邮箱验证码
    if not test_verify_email(verification_code):
        print("❌ 测试终止：验证邮箱失败")
        return
    
    # 3. 使用验证码注册
    if not test_register_with_verification(verification_code):
        print("❌ 测试终止：注册失败")
        return
    
    # 4. 测试登录
    if not test_login():
        print("❌ 测试终止：登录失败")
        return
    
    print("\n🎉 所有测试通过！邮箱验证功能正常工作")
    print("=" * 50)

if __name__ == "__main__":
    main()
