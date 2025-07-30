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