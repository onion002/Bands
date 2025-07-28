#!/usr/bin/env python3
"""
生产环境启动脚本
"""
import os
from app_factory import create_app
from flask import send_from_directory, current_app

# 设置生产环境
os.environ['FLASK_ENV'] = 'production'
os.environ['API_BASE_URL'] = 'http://47.108.249.242:5000'

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
    print("🚀 启动生产环境 Flask 应用...")
    print(f"🌐 服务器地址: http://47.108.249.242:5000")
    
    # 生产环境配置
    app.run(
        host='0.0.0.0',  # 监听所有网络接口
        port=5000,
        debug=False,     # 关闭调试模式
        threaded=True    # 启用多线程
    )
