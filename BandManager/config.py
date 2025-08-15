import os

# 获取基础目录
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ====== 数据库配置 ======
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:002101@localhost/band_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ====== 安全配置 ======
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    WTF_CSRF_ENABLED = True

    # ====== 邮件配置 ======
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-email-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'your-email@qq.com'
    
    # ====== Redis配置 ======
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # ====== 验证码配置 ======
    VERIFICATION_CODE_EXPIRE = int(os.environ.get('VERIFICATION_CODE_EXPIRE') or 300)  # 5分钟过期
    VERIFICATION_CODE_LENGTH = int(os.environ.get('VERIFICATION_CODE_LENGTH') or 6)  # 6位验证码

    # ====== 上传配置 ======
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://localhost:5000'

    # ====== 认证配置 ======
    DEVELOPER_SECRET_KEYS = os.environ.get('DEVELOPER_SECRET_KEYS') or 'dev-key-123,admin-key-456,oninon466'
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

    # ====== 开发调试配置 ======
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') != 'production'  # 生产环境不打印SQL
    DEBUG = os.environ.get('FLASK_ENV') != 'production'  # 生产环境关闭调试

    # CORS 配置 --------
    # 允许前端跨域访问
    CORS_ORIGINS = [
        "http://47.108.249.242:3000",  # 生产环境前端
        "https://47.108.249.242:3000", # HTTPS版本
        "http://47.108.249.242",       # 不带端口
        "https://47.108.249.242",      # HTTPS不带端口
        "http://118.25.219.26:5173",   # 原有配置保留
        "http://localhost:5173",       # 本地开发
        "http://localhost:3000"        # 本地生产构建测试
    ]

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    API_BASE_URL = 'http://localhost:5000'
    # 按用户要求，保持原有默认数据库配置（不改动为 SQLite）

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    API_BASE_URL = 'http://47.108.249.242:5000'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-IN-PRODUCTION-VERY-IMPORTANT'

    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:002101@localhost/band_db'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}