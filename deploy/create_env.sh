#!/bin/bash

# 创建生产环境.env文件脚本

echo "🚀 创建生产环境配置文件..."

# 检查是否在BandManager目录
if [ ! -d "BandManager" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

cd BandManager

# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)

# 创建.env文件
cat > .env << EOF
# ========================================
# 乐队管理系统 - 生产环境配置文件
# 服务器: 47.107.79.244
# 生成时间: $(date)
# ========================================

# ====== 基础环境配置 ======
FLASK_ENV=production
FLASK_APP=app_production.py

# ====== 数据库配置 ======
# 请修改下面的密码为你的实际MySQL密码
DATABASE_URL=mysql+mysqlconnector://root:002101@localhost:3306/band_db

# ====== 安全配置 ======
# 已自动生成的强密钥
SECRET_KEY=${SECRET_KEY}

# 邮件配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=3137826052@qq.com
MAIL_PASSWORD=ptvporstvsbqdegc
MAIL_DEFAULT_SENDER=3137826052@qq.com

# 验证码配置
VERIFICATION_CODE_EXPIRE=300
VERIFICATION_CODE_LENGTH=6

# ====== Redis配置 ======
REDIS_URL=redis://localhost:6379/0

# ====== API配置 ======
API_BASE_URL=http://47.107.79.244:5000

# ====== 验证码配置 ======
VERIFICATION_CODE_EXPIRE=300
VERIFICATION_CODE_LENGTH=6

# ====== 认证配置 ======
DEVELOPER_SECRET_KEYS=dev-key-123,admin-key-456,oninon466
JWT_EXPIRATION_HOURS=24

# ====== 上传配置 ======
MAX_CONTENT_LENGTH=8388608

# ====== 日志配置 ======
LOG_LEVEL=INFO
LOG_FILE=/var/log/band-manager/app.log

# ====== 性能配置 ======
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600

# ====== 监控配置 ======
ENABLE_METRICS=true
METRICS_PORT=9090

# ====== 备份配置 ======
BACKUP_ENABLED=true
BACKUP_PATH=/var/backups/band-manager
BACKUP_RETENTION_DAYS=30
EOF

echo "✅ .env文件创建成功！"
echo ""
echo "📋 重要提醒:"
echo "1. 请修改 DATABASE_URL 中的 MySQL 密码"
echo "2. 请修改 MAIL_USERNAME 和 MAIL_PASSWORD 为你的实际邮箱"
echo "3. SECRET_KEY 已自动生成，请妥善保管"
echo ""
echo "🔧 编辑配置文件:"
echo "   nano .env"
echo ""
echo "📖 查看配置文件:"
echo "   cat .env"