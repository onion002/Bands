from flask import Flask
import os
from flask_cors import CORS

def create_app():
    # 创建 Flask 应用实例
    app = Flask(__name__)
    
    # 确保所有进程都加载配置
    load_config(app)
    
    # 确保主进程执行一次的操作
    if not is_reloader_process():
        # 确保上传目录存在（只在主进程执行）
        ensure_upload_folder(app)
    
    # 初始化扩展
    init_extensions(app)
    CORS(app, supports_credentials=True)
    # 注册蓝图
    register_blueprints(app)
    
    return app

def is_reloader_process():
    """检查当前是否是重载进程"""
    return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

def load_config(app):
    """加载应用配置（所有进程都需要）"""
    try:
        # 根据环境变量选择配置
        config_name = os.environ.get('FLASK_ENV', 'development')

        from config import config
        app.config.from_object(config.get(config_name, config['default']))

        # 仅在主进程打印配置
        if not is_reloader_process():
            print("=" * 50)
            print(f"🌍 环境: {config_name}")
            print(f"📊 数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print(f"📁 上传目录: {app.config.get('UPLOAD_FOLDER')}")
            print(f"🌐 API地址: {app.config.get('API_BASE_URL')}")
            print(f"🔧 调试模式: {app.config.get('DEBUG')}")
            print("=" * 50)

        # 验证必要配置
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            raise ValueError("SQLALCHEMY_DATABASE_URI 配置未设置")

    except ImportError as e:
        if not is_reloader_process():
            print(f"⚠️ 导入配置错误: {str(e)}")
            print("⚠️ 警告：找不到config.py，使用默认配置")
        # 设置基本配置
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///band_db.sqlite')
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        app.config.setdefault('SECRET_KEY', 'dev-secret-key')
    except ValueError as e:
        if not is_reloader_process():
            print(f"⚠️ 配置错误: {str(e)}")
        # 设置回退配置
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///band_db.sqlite')

def ensure_upload_folder(app):
    """确保上传目录存在（只在主进程执行）"""
    if not is_reloader_process():
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            print(f"📁 创建上传目录: {upload_folder}")
            os.makedirs(upload_folder)

def init_extensions(app):
    """初始化扩展"""
    # 确保配置已设置
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        # 如果还没有设置，使用默认值
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///band_db.sqlite')
    
    from models import db
    from flask_migrate import Migrate
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化迁移扩展
    Migrate(app, db)
    
    # 创建数据库表（如果不存在）只在主进程执行
    if not is_reloader_process():
        with app.app_context():
            try:
                db.create_all()
                print("✅ 数据库表已创建/验证")
            except Exception as e:
                print(f"⚠️ 数据库初始化失败: {str(e)}")

def register_blueprints(app):
    """注册所有蓝图"""
    # 动态导入蓝图，避免循环导入
    try:
        from api.bands import bands_bp
        from api.members import members_bp
        
        app.register_blueprint(bands_bp, url_prefix='/api/bands')
        app.register_blueprint(members_bp, url_prefix='/api/members')
        
        if not is_reloader_process():
            print("✅ 蓝图注册成功")
    except ImportError as e:
        if not is_reloader_process():
            print(f"⚠️ 注册蓝图失败: {str(e)}")