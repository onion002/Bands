from app_factory import create_app
import os
from flask_cors import CORS
from flask import send_from_directory

app = create_app()

def run_app():
    """运行应用的主函数"""
    # 仅在主进程打印启动信息
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("🚀 启动 Flask 应用...")
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    run_app()