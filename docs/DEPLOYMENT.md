# 🚀 乐队管理系统部署指南

## 📋 服务器信息
- **服务器IP**: 47.108.249.242
- **后端端口**: 5000
- **前端端口**: 3000

## 🔧 环境要求

### 系统要求
- Linux 服务器 (Ubuntu/CentOS)
- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (可选，默认使用SQLite)

### 安装依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm mysql-server

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm mysql-server
```

## 🚀 快速部署

### 方法一：一键部署 (推荐)
```bash
# 1. 上传项目到服务器
scp -r git-bands/ user@47.108.249.242:/home/user/

# 2. 登录服务器
ssh user@47.108.249.242

# 3. 进入项目目录
cd git-bands

# 4. 设置执行权限
chmod +x *.sh

# 5. 执行部署脚本
./deploy.sh
```

### 方法二：快速启动 (环境已配置)
```bash
# 快速启动服务
./quick_deploy.sh

# 检查服务状态
./check_status.sh

# 停止服务
./stop_services.sh
```

## 📝 手动部署步骤

### 1. 后端部署
```bash
cd BandManager

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export FLASK_ENV=production
export API_BASE_URL=http://47.108.249.242:5000

# 创建上传目录
mkdir -p uploads/bands uploads/members

# 启动后端
python app_production.py
```

### 2. 前端部署
```bash
cd band-manager-front

# 安装依赖
npm install

# 构建生产版本
npm run build

# 启动前端服务
npm run preview -- --host 0.0.0.0 --port 3000
```

## 🔧 配置说明

### 环境变量
```bash
# 后端环境变量
export FLASK_ENV=production
export API_BASE_URL=http://47.108.249.242:5000
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=mysql+mysqlconnector://user:password@localhost/band_db

# 前端环境变量 (.env.production)
VITE_API_BASE_URL=http://47.108.249.242:5000
VITE_APP_TITLE=乐队管理系统
VITE_APP_ENV=production
```

### 数据库配置
```bash
# MySQL配置 (可选)
mysql -u root -p
CREATE DATABASE band_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'banduser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON band_db.* TO 'banduser'@'localhost';
FLUSH PRIVILEGES;
```

## 🛡️ 防火墙配置
```bash
# Ubuntu (ufw)
sudo ufw allow 3000
sudo ufw allow 5000

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 🔄 系统服务配置

### 安装为系统服务
```bash
# 复制服务文件
sudo cp band-manager-*.service /etc/systemd/system/

# 重载系统服务
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

### 服务管理命令
```bash
# 启动服务
sudo systemctl start band-manager-backend
sudo systemctl start band-manager-frontend

# 停止服务
sudo systemctl stop band-manager-backend
sudo systemctl stop band-manager-frontend

# 重启服务
sudo systemctl restart band-manager-backend
sudo systemctl restart band-manager-frontend

# 查看日志
sudo journalctl -u band-manager-backend -f
sudo journalctl -u band-manager-frontend -f
```

## 📊 监控和维护

### 健康检查
```bash
# 后端健康检查
curl http://47.108.249.242:5000/health

# 前端访问检查
curl -I http://47.108.249.242:3000
```

### 日志查看
```bash
# 查看应用日志
tail -f backend.log
tail -f frontend.log

# 查看系统服务日志
sudo journalctl -u band-manager-backend -f
sudo journalctl -u band-manager-frontend -f
```

### 状态检查脚本
```bash
# 使用提供的状态检查脚本
./check_status.sh
```

## 🌐 访问地址

部署完成后，可以通过以下地址访问：

- **前端应用**: http://47.108.249.242:3000
- **后端API**: http://47.108.249.242:5000
- **健康检查**: http://47.108.249.242:5000/health
- **API文档**: http://47.108.249.242:5000/api/

## 🔧 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查看端口占用
lsof -i:5000
lsof -i:3000

# 杀死占用进程
sudo kill -9 $(lsof -ti:5000)
sudo kill -9 $(lsof -ti:3000)
```

2. **权限问题**
```bash
# 设置上传目录权限
chmod 755 BandManager/uploads
chmod 755 BandManager/uploads/bands
chmod 755 BandManager/uploads/members
```

3. **数据库连接问题**
```bash
# 检查MySQL服务
sudo systemctl status mysql

# 测试数据库连接
mysql -u root -p -e "SHOW DATABASES;"
```

4. **前端构建失败**
```bash
# 清理缓存重新构建
cd band-manager-front
rm -rf node_modules dist
npm install
npm run build
```

## 📚 更多信息

- 项目源码：当前目录
- 配置文件：`BandManager/config.py`
- 环境配置：`.env.production`, `.env.development`
- 部署脚本：`deploy.sh`, `quick_deploy.sh`
- 管理脚本：`check_status.sh`, `stop_services.sh`
