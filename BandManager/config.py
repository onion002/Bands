import os

# 获取基础目录
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ====== 数据库配置 ======
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:002101@localhost/band_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ====== 安全配置 ======
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    WTF_CSRF_ENABLED = True
    
    # ====== 上传配置 ======
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB
    API_BASE_URL = 'http://localhost:5000'
    
    # ====== 开发调试配置 ======
    SQLALCHEMY_ECHO = True  # 打印SQL语句到控制台
    DEBUG = True

    # CORS 配置 --------
    # 允许前端跨域访问
    CORS_ORIGINS = ["http://118.25.219.26:5173", "http://localhost:5173"]