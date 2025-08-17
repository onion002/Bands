#!/usr/bin/env python3
"""
生产环境启动脚本
"""
import os
from app_factory import create_app
from flask import send_from_directory, current_app

# 设置生产环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['API_BASE_URL'] = 'http://47.107.79.244:5000'

app = create_app()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """静态文件服务"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@app.route('/health')
def health_check():
    """健康检查端点"""
    return {'status': 'healthy', 'message': 'Band Manager API is running'}

if __name__ == '__main__':
    print("🚀 乐队管理系统后端服务启动中...")
    print(f"🌐 服务器地址: http://47.107.79.244:5000")
    print(f"🔧 环境模式: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"🐛 调试模式: {app.config.get('DEBUG', False)}")
    print(f"📊 数据库: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
