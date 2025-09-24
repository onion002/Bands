from flask import Flask, request
import os
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
    # 初始化CORS，使用配置中的允许源并明确设置资源路径
    CORS(app, resources={r"/api/*": {
        "origins": app.config.get('CORS_ORIGINS'),
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        # 允许所有必要的HTTP方法
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 86400  # 预检请求缓存24小时
    }})
    
    # 添加额外的CORS头处理
    @app.after_request
    def after_request(response):
        # 确保CORS头被正确设置
        origin = request.headers.get('Origin')
        if origin:
            # 检查是否在允许的源列表中
            allowed_origins = app.config.get('CORS_ORIGINS', [])
            ip_patterns = app.config.get('CORS_IP_PATTERNS', [])
            
            # 检查精确匹配
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            # 检查IP模式匹配（开发环境）
            elif app.config.get('DEBUG', False):
                for pattern in ip_patterns:
                    if _match_ip_pattern(origin, pattern):
                        response.headers['Access-Control-Allow-Origin'] = origin
                        response.headers['Access-Control-Allow-Credentials'] = 'true'
                        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
                        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                        break
        
        return response
    
    def _match_ip_pattern(origin, pattern):
        """检查origin是否匹配IP模式"""
        import re
        # 将通配符模式转换为正则表达式
        regex_pattern = pattern.replace('*', r'\d+').replace('.', r'\.')
        return re.match(regex_pattern, origin) is not None
    # 注册蓝图
    register_blueprints(app)
    
    # 添加静态文件路由 - 必须在create_app函数内部
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """提供上传文件的访问"""
        from flask import send_from_directory
        return send_from_directory('uploads', filename)
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        return {'message': 'Band Manager API is running', 'status': 'healthy'}
    
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
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///sqlite:///band_db.sqlite')
    
    # 邮件服务配置默认值
    app.config.setdefault('MAIL_SERVER', 'smtp.qq.com')
    app.config.setdefault('MAIL_PORT', 587)
    app.config.setdefault('MAIL_USE_TLS', True)
    app.config.setdefault('MAIL_USE_SSL', False)
    app.config.setdefault('MAIL_USERNAME', '3137826052@qq.com')
    app.config.setdefault('MAIL_PASSWORD', 'ptvporstvsbqdegc')
    app.config.setdefault('MAIL_DEFAULT_SENDER', '3137826052@qq.com')
    
    from models import db
    from flask_migrate import Migrate
    from services.email_service import EmailService
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化迁移扩展
    Migrate(app, db)
    
    # 初始化邮件服务
    email_service = EmailService()
    email_service.init_app(app)
    
    # 创建数据库表（如果不存在）只在主进程执行
    if not is_reloader_process():
        with app.app_context():
            try:
                db.create_all()
                print("✅ 数据库表已创建/验证")
                ensure_superadmin_account()
            except Exception as e:
                print(f"⚠️ 数据库初始化失败: {str(e)}")

def ensure_superadmin_account():
    """如果没有超级管理员，则自动创建一个默认的超级管理员账号。
    可通过环境变量 DEFAULT_SUPERADMIN_USERNAME/DEFAULT_SUPERADMIN_PASSWORD/DEFAULT_SUPERADMIN_EMAIL 覆盖。
    """
    import os
    from models import User, UserType, db
    try:
        existing = User.query.filter(User.user_type == UserType.SUPERADMIN).first()
        if existing:
            return
        username = os.environ.get('DEFAULT_SUPERADMIN_USERNAME', 'superadmin')
        password = os.environ.get('DEFAULT_SUPERADMIN_PASSWORD', 'SuperAdmin#2025')
        email = os.environ.get('DEFAULT_SUPERADMIN_EMAIL', 'superadmin@local')
        display_name = 'Super Admin'
        user = User(username=username, email=email, user_type=UserType.SUPERADMIN, display_name=display_name, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✅ 已创建默认超级管理员: {username} / {password}")
    except Exception as e:
        print(f"⚠️ 创建超级管理员失败: {str(e)}")

def register_blueprints(app):
    """注册所有蓝图"""
    # 动态导入蓝图，避免循环导入
    try:
        from api.bands import bands_bp
        from api.members import members_bp
        from api.events import events_bp
        from api.auth import auth_bp
        from api.stats import stats_bp
        from api.music_teacher.routes import music_teacher_bp
        from api.admin import admin_bp
        from api.community import community_bp

        # 统一在此处集中管理所有蓝图前缀
        app.register_blueprint(bands_bp, url_prefix='/api/bands')
        app.register_blueprint(members_bp, url_prefix='/api/members')
        app.register_blueprint(events_bp, url_prefix='/api/events')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(stats_bp, url_prefix='/api/stats')
        app.register_blueprint(music_teacher_bp, url_prefix='/api/music-teacher')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(community_bp, url_prefix='/api/community')

        if not is_reloader_process():
            print("✅ 蓝图注册成功")
    except ImportError as e:
        if not is_reloader_process():
            print(f"⚠️ 注册蓝图失败: {str(e)}")