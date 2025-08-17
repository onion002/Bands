# 新服务器部署指南

## 服务器信息
- **服务器IP**: 47.107.79.244
- **操作系统**: Alibaba Cloud Linux 3 (OpenAnolis Edition)
- **架构**: x86_64

## 部署前准备

### 1. 系统环境检查
```bash
# 检查系统版本
lsb_release -a

# 检查Python版本
python3 --version

# 检查Node.js版本
node --version
npm --version

# 检查MySQL状态
systemctl status mysqld

# 检查Redis状态
systemctl status redis
```

### 2. 安装必要软件包
```bash
# 更新系统
sudo yum update -y

# 安装Python3和相关工具
sudo yum install -y python3 python3-pip python3-devel

# 安装Node.js (如果没有)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安装MySQL (如果没有)
sudo yum install -y mysql-server mysql

# 安装Redis (如果没有)
sudo yum install -y redis

# 安装其他必要工具
sudo yum install -y git nginx curl wget
```

### 3. 配置防火墙
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-port=22/tcp      # SSH
sudo firewall-cmd --permanent --add-port=80/tcp      # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp     # HTTPS
sudo firewall-cmd --permanent --add-port=3000/tcp    # 前端服务
sudo firewall-cmd --permanent --add-port=5000/tcp    # 后端服务
sudo firewall-cmd --permanent --add-port=3306/tcp    # MySQL
sudo firewall-cmd --permanent --add-port=6379/tcp    # Redis

# 重新加载防火墙规则
sudo firewall-cmd --reload
```

## 部署步骤

### 1. 克隆项目
```bash
cd /wwwroot
git clone <your-repository-url> git-bands
cd git-bands
```

### 2. 运行部署脚本
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 3. 配置数据库
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE band_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（可选）
CREATE USER 'band_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON band_db.* TO 'band_user'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 4. 配置环境变量
```bash
# 创建环境变量文件
cd BandManager
cat > .env << EOF
FLASK_ENV=production
DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost/band_db
SECRET_KEY=$(openssl rand -hex 32)
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-email-password
REDIS_URL=redis://localhost:6379/0
API_BASE_URL=http://47.107.79.244:5000
EOF
```

### 5. 启动服务

#### 方式1: 直接启动
```bash
# 启动后端
./start_backend.sh

# 启动前端（新终端）
./start_frontend.sh
```

#### 方式2: 系统服务（推荐）
```bash
# 复制服务文件
sudo cp band-manager-*.service /etc/systemd/system/

# 重新加载系统服务
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable band-manager-backend
sudo systemctl enable band-manager-frontend

# 启动服务
sudo systemctl start band-manager-backend
sudo systemctl start band-manager-frontend

# 检查状态
sudo systemctl status band-manager-backend
sudo systemctl status band-manager-frontend
```

## 验证部署

### 1. 检查服务状态
```bash
# 使用状态检查脚本
./check_status.sh

# 或手动检查
curl http://47.107.79.244:5000/health
curl http://47.107.79.244:3000
```

### 2. 检查日志
```bash
# 查看后端日志
sudo journalctl -u band-manager-backend -f

# 查看前端日志
sudo journalctl -u band-manager-frontend -f
```

## 访问地址

- **前端应用**: http://47.107.79.244:3000
- **后端API**: http://47.107.79.244:5000
- **健康检查**: http://47.107.79.244:5000/health

## 常见问题解决

### 1. 端口被占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :3000

# 杀死占用进程
sudo kill -9 <PID>
```

### 2. 权限问题
```bash
# 修复上传目录权限
sudo chown -R $USER:$USER uploads/
sudo chmod -R 755 uploads/
```

### 3. 数据库连接问题
```bash
# 检查MySQL服务状态
sudo systemctl status mysqld

# 检查MySQL配置
sudo cat /etc/my.cnf
```

### 4. Redis连接问题
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 检查Redis配置
sudo cat /etc/redis.conf
```

## 维护命令

```bash
# 重启服务
sudo systemctl restart band-manager-backend
sudo systemctl restart band-manager-frontend

# 查看服务状态
sudo systemctl status band-manager-*

# 查看日志
sudo journalctl -u band-manager-backend --since "1 hour ago"
sudo journalctl -u band-manager-frontend --since "1 hour ago"

# 更新代码后重启
git pull
sudo systemctl restart band-manager-backend
sudo systemctl restart band-manager-frontend
```

## 安全建议

1. **更改默认密码**: 修改MySQL root密码
2. **限制访问**: 只开放必要端口
3. **定期更新**: 保持系统和软件包更新
4. **备份数据**: 定期备份数据库和上传文件
5. **监控日志**: 定期检查服务日志

## 联系信息

如有问题，请检查：
1. 服务状态和日志
2. 防火墙配置
3. 数据库连接
4. 环境变量配置
