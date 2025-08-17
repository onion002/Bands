#!/bin/bash

# MySQL和Redis安装配置脚本
# 适用于 Alibaba Cloud Linux 3

echo "🚀 开始安装和配置MySQL和Redis..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 安装MySQL
echo -e "\n${YELLOW}📦 安装MySQL...${NC}"

# 检查是否已安装
if rpm -qa | grep -q mysql; then
    echo -e "${BLUE}MySQL已安装，跳过安装步骤${NC}"
else
    # 安装MySQL
    sudo yum install -y mysql-server mysql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ MySQL安装成功${NC}"
    else
        echo -e "${RED}❌ MySQL安装失败${NC}"
        exit 1
    fi
fi

# 启动MySQL服务
echo -e "\n${YELLOW}🔧 启动MySQL服务...${NC}"
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 检查MySQL状态
if sudo systemctl is-active --quiet mysqld; then
    echo -e "${GREEN}✅ MySQL服务启动成功${NC}"
else
    echo -e "${RED}❌ MySQL服务启动失败${NC}"
    sudo systemctl status mysqld
    exit 1
fi

# 2. 安装Redis
echo -e "\n${YELLOW}📦 安装Redis...${NC}"

# 检查是否已安装
if rpm -qa | grep -q redis; then
    echo -e "${BLUE}Redis已安装，跳过安装步骤${NC}"
else
    # 安装Redis
    sudo yum install -y redis
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis安装成功${NC}"
    else
        echo -e "${RED}❌ Redis安装失败${NC}"
        exit 1
    fi
fi

# 启动Redis服务
echo -e "\n${YELLOW}🔧 启动Redis服务...${NC}"
sudo systemctl start redis
sudo systemctl enable redis

# 检查Redis状态
if sudo systemctl is-active --quiet redis; then
    echo -e "${GREEN}✅ Redis服务启动成功${NC}"
else
    echo -e "${RED}❌ Redis服务启动失败${NC}"
    sudo systemctl status redis
    exit 1
fi

# 3. 配置MySQL
echo -e "\n${YELLOW}🔧 配置MySQL...${NC}"

# 获取MySQL临时密码
echo -e "${BLUE}获取MySQL临时密码...${NC}"
sudo grep 'temporary password' /var/log/mysqld.log | tail -1

# 安全配置MySQL
echo -e "${BLUE}运行MySQL安全配置...${NC}"
echo -e "${YELLOW}⚠️  请按照提示设置MySQL root密码和其他安全选项${NC}"
echo -e "${YELLOW}⚠️  建议设置强密码，并回答 'Y' 到所有安全相关问题${NC}"

# 创建MySQL配置文件
echo -e "\n${BLUE}创建MySQL配置文件...${NC}"
sudo tee /etc/my.cnf.d/band-manager.cnf > /dev/null << 'EOF'
[mysqld]
# 字符集配置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接配置
max_connections = 200
max_connect_errors = 1000

# 缓冲配置
innodb_buffer_pool_size = 128M
innodb_log_file_size = 64M

# 超时配置
wait_timeout = 28800
interactive_timeout = 28800

# 日志配置
log-error = /var/log/mysqld.log
slow_query_log = 1
slow_query_log_file = /var/log/mysqld-slow.log
long_query_time = 2

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
EOF

# 重启MySQL以应用配置
sudo systemctl restart mysqld

# 4. 配置Redis
echo -e "\n${YELLOW}🔧 配置Redis...${NC}"

# 创建Redis配置文件
echo -e "${BLUE}创建Redis配置文件...${NC}"
sudo tee /etc/redis.conf.d/band-manager.conf > /dev/null << 'EOF'
# 网络配置
bind 127.0.0.1
port 6379
timeout 300

# 内存配置
maxmemory 128mb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# 日志配置
loglevel notice
logfile /var/log/redis/redis.log

# 安全配置
requirepass ""

# 其他配置
tcp-keepalive 300
EOF

# 重启Redis以应用配置
sudo systemctl restart redis

# 5. 创建数据库和用户
echo -e "\n${YELLOW}🔧 创建数据库和用户...${NC}"

# 创建数据库脚本
cat > setup_database.sql << 'EOF'
-- 创建数据库
CREATE DATABASE IF NOT EXISTS band_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，如果不想创建可以注释掉）
-- CREATE USER IF NOT EXISTS 'band_user'@'localhost' IDENTIFIED BY 'BandManager2024!';
-- GRANT ALL PRIVILEGES ON band_db.* TO 'band_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 显示数据库
SHOW DATABASES;
EOF

echo -e "${BLUE}数据库设置脚本已创建: setup_database.sql${NC}"
echo -e "${YELLOW}⚠️  请手动运行以下命令来设置数据库:${NC}"
echo -e "${BLUE}mysql -u root -p < setup_database.sql${NC}"

# 6. 防火墙配置
echo -e "\n${YELLOW}🔧 配置防火墙...${NC}"

# 检查防火墙状态
if command -v firewall-cmd &> /dev/null; then
    echo -e "${BLUE}配置firewalld...${NC}"
    sudo firewall-cmd --permanent --add-port=3306/tcp
    sudo firewall-cmd --permanent --add-port=6379/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✅ 防火墙配置完成${NC}"
elif command -v ufw &> /dev/null; then
    echo -e "${BLUE}配置ufw...${NC}"
    sudo ufw allow 3306/tcp
    sudo ufw allow 6379/tcp
    echo -e "${GREEN}✅ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到防火墙，请手动配置端口3306和6379${NC}"
fi

# 7. 显示服务状态
echo -e "\n${GREEN}🎉 安装和配置完成！${NC}"
echo -e "\n${BLUE}📋 服务状态:${NC}"

echo -e "\n${YELLOW}MySQL状态:${NC}"
sudo systemctl status mysqld --no-pager -l

echo -e "\n${YELLOW}Redis状态:${NC}"
sudo systemctl status redis --no-pager -l

echo -e "\n${BLUE}📋 下一步操作:${NC}"
echo -e "1. 设置MySQL root密码:"
echo -e "   ${YELLOW}sudo mysql_secure_installation${NC}"
echo -e ""
echo -e "2. 创建数据库:"
echo -e "   ${YELLOW}mysql -u root -p < setup_database.sql${NC}"
echo -e ""
echo -e "3. 测试连接:"
echo -e "   ${YELLOW}mysql -u root -p -e 'USE band_db; SHOW TABLES;'${NC}"
echo -e "   ${YELLOW}redis-cli ping${NC}"
echo -e ""
echo -e "4. 检查端口:"
echo -e "   ${YELLOW}sudo netstat -tlnp | grep -E ':(3306|6379)'${NC}"

echo -e "\n${GREEN}✨ 脚本执行完成！${NC}"
