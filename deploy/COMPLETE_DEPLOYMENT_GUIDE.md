# 完整部署指南 - 新服务器 47.108.30.30

## 📋 部署前检查清单

在开始部署之前，请确认以下信息：

- [ ] 服务器IP: 47.108.30.30
- [ ] 操作系统: CentOS Stream 9
- [ ] 已连接到服务器
- [ ] 有root权限
- [ ] Python 3.13, Node.js v22.15.1, MySQL, Redis 已安装

---

## 🚀 第一步：环境检查和准备

### 1.1 检查系统环境
```bash
# 检查系统版本
cat /etc/centos-release

# 检查当前用户和权限
whoami

# 检查当前目录
pwd
```

**预期结果**: 
- 系统版本显示 CentOS Stream 9
- 当前用户是 root
- 当前目录是 /opt

### 1.2 检查基础软件
```bash
# 检查Python版本
python3 --version

# 检查Node.js版本
node --version
npm --version

# 检查MySQL状态
systemctl status mysqld

# 检查Redis状态
systemctl status redis

# 测试Redis连接
redis-cli ping
```

**预期结果**: 
- Python 3.13
- Node.js v22.15.1
- npm 10.9.2
- MySQL服务运行中
- Redis服务运行中，返回PONG

---

## 📦 第二步：数据库配置

### 2.1 检查MySQL连接
```bash
# 测试MySQL连接
mysql -u root -p -e "SHOW DATABASES;"
```

**输入密码**: 002101

### 2.2 验证数据库
```bash
# 检查band_db数据库是否存在
mysql -u root -p -e "SHOW DATABASES LIKE 'band_db';"

# 如果不存在，创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS band_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

**预期结果**: 
- 能成功连接MySQL
- band_db数据库存在
- 字符集为utf8mb4

---

## 🔧 第三步：项目部署

### 3.1 克隆项目
```bash
# 克隆项目到/opt目录
cd /opt
git clone https://github.com/onion002/Bands.git
cd Bands
```

**验证步骤**:
```bash
# 检查项目结构
ls -la
ls -la BandManager/
ls -la band-manager-front/
```

**预期结果**: 
- 看到BandManager/、band-manager-front/等目录

### 3.2 配置后端环境
```bash
# 进入后端目录
cd BandManager

# 创建.env文件
cat > .env << 'EOF'
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=002101
DB_NAME=band_db

# 邮件服务配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=3137826052@qq.com
MAIL_PASSWORD=ptvporstvsbqdegc

# API配置
API_BASE_URL=http://47.108.30.30:5000

# 应用配置
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Redis配置
REDIS_URL=redis://localhost:6379/0

# AI配置
OPENAI_API_KEY=your-openai-api-key-here
EOF
```

### 3.3 安装后端依赖
```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 如果遇到click版本冲突，先安装兼容版本
pip3 install click==8.1.7
pip3 install -r requirements.txt
```

### 3.4 初始化数据库
```bash
# 初始化数据库表
python3 -c "
from app_factory import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ 数据库表创建成功')
"
```

### 3.5 配置前端环境
```bash
# 进入前端目录
cd ../band-manager-front

# 创建环境变量文件
echo "VITE_API_BASE_URL=http://47.108.30.30:5000" > .env.production

# 安装前端依赖
npm install

# 构建前端
npm run build
```

---

## 🚀 第四步：启动服务

### 4.1 启动后端服务
```bash
# 进入后端目录
cd /opt/Bands/BandManager

# 启动后端服务
nohup python3 app.py > backend.log 2>&1 &
```

**验证步骤**:
```bash
# 检查后端进程
ps aux | grep python

# 检查端口监听
netstat -tlnp | grep :5000

# 测试API健康检查
curl http://localhost:5000/health
```

**预期结果**: 
- Python进程运行中
- 端口5000被监听
- 健康检查返回成功响应

### 4.2 启动前端服务
```bash
# 进入前端目录
cd /opt/Bands/band-manager-front

# 启动前端服务
nohup npm run preview > frontend.log 2>&1 &
```

**验证步骤**:
```bash
# 检查前端进程
ps aux | grep node

# 检查端口监听
netstat -tlnp | grep :3000

# 测试前端访问
curl http://localhost:3000
```

**预期结果**: 
- Node.js进程运行中
- 端口3000被监听
- 前端页面能正常访问

---

## 🌐 第五步：网络配置

### 5.1 检查防火墙状态
```bash
# 检查防火墙状态
firewall-cmd --list-ports

# 如果端口未开放，添加端口
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

**验证步骤**:
```bash
# 检查端口是否开放
firewall-cmd --list-ports | grep -E "(3000|5000)"

# 从外部测试连接
curl http://47.108.30.30:5000/health
curl http://47.108.30.30:3000
```

**预期结果**: 
- 防火墙显示端口3000和5000开放
- 外部能正常访问服务

---

## ✅ 第六步：最终验证

### 6.1 服务状态检查
```bash
# 使用管理脚本检查状态
cd /opt/Bands
chmod +x deploy/manage.sh
./deploy/manage.sh status
```

**验证步骤**:
```bash
# 手动检查各项服务
echo "=== 后端服务 ==="
curl -s http://47.108.30.30:5000/health

echo "=== 前端服务 ==="
curl -s -o /dev/null -w "%{http_code}" http://47.108.30.30:3000

echo "=== 数据库连接 ==="
mysql -u root -p002101 -e "USE band_db; SHOW TABLES;"

echo "=== Redis连接 ==="
redis-cli ping
```

**预期结果**: 
- 后端健康检查返回成功
- 前端返回HTTP 200状态码
- 数据库连接正常，显示表结构
- Redis返回PONG

### 6.2 功能测试
```bash
# 测试管理员登录功能
curl -X POST http://47.108.30.30:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin-syx","password":"syx002101"}'
```

**预期结果**: 
- 返回JWT token和用户信息
- 登录成功

---

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 邮件验证码发送失败
**问题**: 500 Internal Server Error
**原因**: 环境变量未正确加载
**解决**: 确保 `app_factory.py` 中有 `load_dotenv()` 调用

#### 2. Python依赖冲突
**问题**: `click==8.2.1` 版本不兼容
**解决**: 
```bash
pip3 install click==8.1.7
pip3 install -r requirements.txt
```

#### 3. 前端构建失败
**问题**: 缺少 `EmailVerificationDemo.vue` 文件
**解决**: 创建占位符组件文件

#### 4. 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep -E ':(3000|5000)'

# 杀死占用进程
kill -9 <PID>
```

#### 5. API地址配置错误
**问题**: 前端硬编码了错误的IP地址
**解决**: 
```bash
# 创建环境变量文件
echo "VITE_API_BASE_URL=http://47.108.30.30:5000" > .env.production

# 重新构建前端
npm run build
```

#### 6. 使用管理脚本
```bash
# 检查服务状态
./deploy/manage.sh status

# 重启服务
./deploy/manage.sh restart

# 查看日志
./deploy/manage.sh logs all
```

---

## 📊 部署完成检查清单

- [ ] 系统环境检查通过 (CentOS Stream 9)
- [ ] MySQL和Redis服务运行正常
- [ ] 项目代码克隆到 /opt/Bands
- [ ] 后端环境变量配置正确 (.env文件)
- [ ] 前端环境变量配置正确 (.env.production文件)
- [ ] Python依赖安装成功
- [ ] 数据库表初始化成功
- [ ] 前端构建成功
- [ ] 后端服务启动成功 (端口5000)
- [ ] 前端服务启动成功 (端口3000)
- [ ] 防火墙端口开放 (3000, 5000)
- [ ] 外部访问正常
- [ ] 管理员登录功能正常
- [ ] 邮件验证功能正常

---

## 🔗 访问地址

- **前端应用**: http://47.108.30.30:3000
- **后端API**: http://47.108.30.30:5000
- **健康检查**: http://47.108.30.30:5000/health
- **管理员账户**: admin-syx / syx002101

---

## 📞 技术支持

如果在部署过程中遇到问题：

1. 检查本指南的故障排除部分
2. 使用管理脚本检查状态：`./deploy/manage.sh status`
3. 查看服务日志：`./deploy/manage.sh logs all`
4. 重启服务：`./deploy/manage.sh restart`
5. 检查系统资源：`htop`、`df -h`、`free -h`
6. 确认网络连接：`ping 8.8.8.8`

---

## 🎯 下一步

部署完成后，你可以：

1. 使用管理脚本进行日常维护：`./deploy/manage.sh`
2. 配置域名和HTTPS
3. 设置监控和日志
4. 配置备份策略：`./deploy/manage.sh backup`
5. 优化性能参数
6. 设置CI/CD流程

## 🚀 一键部署

如果需要在其他服务器上快速部署，可以使用一键部署脚本：

```bash
# 克隆项目
git clone https://github.com/onion002/Bands.git
cd Bands

# 运行一键部署脚本
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

---

**注意**: 本指南基于实际部署经验编写，请严格按照步骤执行，每个步骤都要验证结果后再进行下一步。如果某步骤失败，请先解决问题再继续。
