# 完整部署指南 - 新服务器 47.108.30.30

## 📋 部署前检查清单

在开始部署之前，请确认以下信息：

- [ ] 服务器IP: 47.108.30.30
- [ ] 操作系统: Alibaba Cloud Linux 3
- [ ] 已连接到服务器
- [ ] 有sudo权限
- [ ] 在/www/wwwroot目录下

---

## 🚀 第一步：环境检查和准备

### 1.1 检查系统环境
```bash
# 检查系统版本
lsb_release -a

# 检查当前用户和权限
whoami
sudo whoami

# 检查当前目录
pwd
```

**预期结果**: 
- 系统版本显示 Alibaba Cloud Linux 3
- 当前用户有sudo权限
- 当前目录是 /www/wwwroot

### 1.2 检查基础软件
```bash
# 检查Python版本
python3 --version

# 检查Node.js版本
node --version
npm --version

# 检查Git版本
git --version
```

**预期结果**: 
- Python 3.x (建议3.8+)
- Node.js 18+ 
- npm 8+
- Git 2.x

---

## 📦 第二步：安装基础环境

### 2.1 安装MySQL和Redis
```bash
# 运行快速环境搭建脚本
chmod +x quick_setup.sh
./quick_setup.sh
```

**验证步骤**:
```bash
# 检查MySQL状态
sudo systemctl status mysqld

# 检查Redis状态
sudo systemctl status redis

# 检查端口是否开放
sudo netstat -tlnp | grep -E ':(3306|6379)'
```

**预期结果**: 
- MySQL状态显示 "active (running)"
- Redis状态显示 "active (running)"
- 端口3306和6379被监听

### 2.2 配置MySQL
```bash
# 设置MySQL root密码
sudo mysql_secure_installation
```

**重要提示**: 
- 选择密码强度级别 (建议选择0)
- 设置强密码 (记住这个密码!)
- 删除匿名用户: Y
- 禁止root远程登录: Y
- 删除test数据库: Y
- 重新加载权限表: Y

**验证步骤**:
```bash
# 测试MySQL连接
mysql -u root -p -e "SHOW DATABASES;"

# 创建项目数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS band_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 验证数据库创建
mysql -u root -p -e "SHOW DATABASES LIKE 'band_db';"
```

**预期结果**: 
- 能成功连接MySQL
- band_db数据库被创建
- 字符集为utf8mb4

---

## 🔧 第三步：项目部署

### 3.1 克隆项目
```bash
# 如果还没有项目，先克隆
git clone <your-repository-url> git-bands
cd git-bands

# 如果已有项目，确保在正确目录
pwd
ls -la
```

**验证步骤**:
```bash
# 检查项目结构
ls -la
ls -la BandManager/
ls -la band-manager-front/
```

**预期结果**: 
- 看到deploy.sh、BandManager/、band-manager-front/等文件和目录

### 3.2 配置环境变量
```bash
# 运行环境变量设置脚本
chmod +x setup_env.sh
./setup_env.sh
```

**输入信息**:
- MySQL root密码: (你在2.2步骤设置的密码)
- 邮箱地址: 3137826052@qq.com
- 邮箱应用密码: ptvporstvsbqdegc

**验证步骤**:
```bash
# 检查.env文件是否创建
ls -la BandManager/.env

# 检查文件权限
ls -la BandManager/.env | awk '{print $1}'

# 查看环境变量内容（注意保护敏感信息）
head -20 BandManager/.env
```

**预期结果**: 
- .env文件存在
- 文件权限为600 (-rw-------)
- 包含正确的配置信息

### 3.3 运行部署脚本
```bash
# 运行简化部署脚本
chmod +x simple_deploy.sh
./simple_deploy.sh
```

**验证步骤**:
```bash
# 检查启动脚本是否创建
ls -la start_backend.sh start_frontend.sh

# 检查Python虚拟环境
ls -la BandManager/venv/

# 检查前端构建结果
ls -la band-manager-front/dist/
```

**预期结果**: 
- 启动脚本存在且有执行权限
- Python虚拟环境创建成功
- 前端dist目录存在且包含构建文件

---

## 🚀 第四步：启动服务

### 4.1 启动后端服务
```bash
# 启动后端服务
./start_backend.sh
```

**验证步骤**:
```bash
# 检查后端进程
ps aux | grep python

# 检查端口监听
sudo netstat -tlnp | grep :5000

# 测试API健康检查
curl http://localhost:5000/health
```

**预期结果**: 
- Python进程运行中
- 端口5000被监听
- 健康检查返回成功响应

### 4.2 启动前端服务
```bash
# 新开一个终端，启动前端服务
./start_frontend.sh
```

**验证步骤**:
```bash
# 检查前端进程
ps aux | grep node

# 检查端口监听
sudo netstat -tlnp | grep :3000

# 测试前端访问
curl http://localhost:3000
```

**预期结果**: 
- Node.js进程运行中
- 端口3000被监听
- 前端页面能正常访问

---

## 🌐 第五步：网络配置

### 5.1 配置防火墙
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 检查防火墙状态
sudo firewall-cmd --list-ports
```

**验证步骤**:
```bash
# 检查端口是否开放
sudo firewall-cmd --list-ports | grep -E "(3000|5000)"

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
# 运行状态检查脚本
chmod +x check_status.sh
./check_status.sh
```

**验证步骤**:
```bash
# 手动检查各项服务
echo "=== 后端服务 ==="
curl -s http://47.108.30.30:5000/health | python3 -m json.tool

echo "=== 前端服务 ==="
curl -s -o /dev/null -w "%{http_code}" http://47.108.30.30:3000

echo "=== 数据库连接 ==="
mysql -u root -p -e "USE band_db; SHOW TABLES;"

echo "=== Redis连接 ==="
redis-cli ping
```

**预期结果**: 
- 后端健康检查返回成功
- 前端返回HTTP 200状态码
- 数据库连接正常
- Redis返回PONG

### 6.2 功能测试
```bash
# 测试用户注册功能
curl -X POST http://47.108.30.30:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'

# 测试用户登录功能
curl -X POST http://47.108.30.30:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}'
```

---

## 🚨 故障排除

### 常见问题及解决方案

#### 1. MySQL连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysqld

# 检查MySQL错误日志
sudo tail -f /var/log/mysqld.log

# 重启MySQL服务
sudo systemctl restart mysqld
```

#### 2. Redis连接失败
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 检查Redis配置
sudo cat /etc/redis.conf

# 重启Redis服务
sudo systemctl restart redis
```

#### 3. 端口被占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep -E ':(3000|5000)'

# 杀死占用进程
sudo kill -9 <PID>
```

#### 4. 权限问题
```bash
# 修复上传目录权限
sudo chown -R $USER:$USER uploads/
sudo chmod -R 755 uploads/

# 修复.env文件权限
chmod 600 BandManager/.env
```

---

## 📊 部署完成检查清单

- [ ] 系统环境检查通过
- [ ] MySQL和Redis安装并运行
- [ ] 项目代码部署完成
- [ ] 环境变量配置正确
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 防火墙配置正确
- [ ] 外部访问正常
- [ ] 功能测试通过

---

## 🔗 访问地址

- **前端应用**: http://47.108.30.30:3000
- **后端API**: http://47.108.30.30:5000
- **健康检查**: http://47.108.30.30:5000/health
- **API文档**: http://47.108.30.30:5000/api/

---

## 📞 技术支持

如果在部署过程中遇到问题：

1. 检查本指南的故障排除部分
2. 查看服务日志：`sudo journalctl -u service-name -f`
3. 检查系统资源：`htop`、`df -h`、`free -h`
4. 确认网络连接：`ping 8.8.8.8`

---

## 🎯 下一步

部署完成后，你可以：

1. 配置域名和HTTPS
2. 设置监控和日志
3. 配置备份策略
4. 优化性能参数
5. 设置CI/CD流程

---

**注意**: 请严格按照本指南的步骤执行，每个步骤都要验证结果后再进行下一步。如果某步骤失败，请先解决问题再继续。
