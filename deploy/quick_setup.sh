#!/bin/bash

# 快速环境搭建脚本 - 新服务器专用
# 适用于 Alibaba Cloud Linux 3

echo "🚀 快速搭建新服务器环境..."

# 1. 安装MySQL
echo "📦 安装MySQL..."
sudo yum install -y mysql-server mysql

# 启动MySQL
echo "🔧 启动MySQL服务..."
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 2. 安装Redis
echo "📦 安装Redis..."
sudo yum install -y redis

# 启动Redis
echo "🔧 启动Redis服务..."
sudo systemctl start redis
sudo systemctl enable redis

# 3. 安装其他必要工具
echo "📦 安装其他工具..."
sudo yum install -y python3 python3-pip python3-devel git curl wget

# 4. 配置防火墙
echo "🔧 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=3000/tcp
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
fi

# 5. 显示状态
echo "📋 服务状态:"
echo "MySQL: $(sudo systemctl is-active mysqld)"
echo "Redis: $(sudo systemctl is-active redis)"

echo "✅ 环境搭建完成！"
echo ""
echo "下一步操作:"
echo "1. 设置MySQL密码: sudo mysql_secure_installation"
echo "2. 创建数据库: mysql -u root -p -e 'CREATE DATABASE band_db;'"
echo "3. 运行部署脚本: ./deploy.sh"
