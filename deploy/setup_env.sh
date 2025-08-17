#!/bin/bash

# 交互式环境变量设置脚本

echo "🚀 设置生产环境变量..."

# 检查是否在BandManager目录
if [ ! -d "BandManager" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

cd BandManager

# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)

echo "📝 请输入以下配置信息:"
echo ""

# 获取MySQL密码
read -p "请输入MySQL root密码: " MYSQL_PASSWORD
if [ -z "$MYSQL_PASSWORD" ]; then
    echo "❌ MySQL密码不能为空"
    exit 1
fi

# 获取邮箱配置
read -p "请输入邮箱地址 (如: your-email@qq.com): " EMAIL_ADDRESS
if [ -z "$EMAIL_ADDRESS" ]; then
    EMAIL_ADDRESS="your-email@qq.com"
    echo "⚠️  使用默认邮箱地址: $EMAIL_ADDRESS"
fi

read -p "请输入邮箱应用密码: " EMAIL_PASSWORD
if [ -z "$EMAIL_PASSWORD" ]; then
    EMAIL_PASSWORD="your-email-app-password"
    echo "⚠️  使用默认邮箱密码: $EMAIL_PASSWORD"
fi

# 确认配置
echo ""
echo "📋 配置确认:"
echo "MySQL密码: $MYSQL_PASSWORD"
echo "邮箱地址: $EMAIL_ADDRESS"
echo "邮箱密码: $EMAIL_PASSWORD"
echo "SECRET_KEY: $SECRET_KEY"
echo ""

read -p "确认以上配置正确吗? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ 配置已取消"
    exit 1
fi

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
DATABASE_URL=mysql+mysqlconnector://root:${MYSQL_PASSWORD}@localhost:3306/band_db

# ====== 安全配置 ======
SECRET_KEY=${SECRET_KEY}

# ====== 邮件配置 ======
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=${EMAIL_ADDRESS}
MAIL_PASSWORD=${EMAIL_PASSWORD}
MAIL_DEFAULT_SENDER=${EMAIL_ADDRESS}

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
echo "📋 文件位置: BandManager/.env"
echo "🔒 文件权限: 600 (仅所有者可读写)"
echo ""
echo "🔧 设置文件权限:"
echo "   chmod 600 .env"
echo ""
echo "📖 查看配置文件:"
echo "   cat .env"
echo ""
echo "🚀 现在可以运行部署脚本了:"
echo "   cd .. && ./deploy.sh"
